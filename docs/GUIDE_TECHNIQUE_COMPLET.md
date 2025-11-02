# 📖 Guide Technique Complet - Battlefield Meta Aggregator

> **Détails techniques, historique des phases et procédures opérationnelles**

---

## Table des Matières

1. [Contexte & Décisions Techniques](#contexte--décisions-techniques)
2. [Extraction Détaillée](#extraction-détaillée)
3. [Historique des Phases](#historique-des-phases)
4. [Schéma Complet des Données](#schéma-complet-des-données)
5. [Configuration DBT](#configuration-dbt)
6. [Déploiement Dashboard](#déploiement-dashboard)
7. [Troubleshooting](#troubleshooting)

---

## Contexte & Décisions Techniques

### Pourquoi Web Scraping vs API ?

**API Tracker.gg** : Non fonctionnelle en production
- Clé API fournie : retourne toujours `401 Unauthorized`
- Documentation obsolète : endpoints non maintenus
- **Décision** : Abandonner l'API, utiliser web scraping comme solution principale

**Web Scraping avec Selenium** :
- ✅ Bypass Cloudflare avec `undetected-chromedriver`
- ✅ 100% de taux de succès sur 50+ joueurs
- ✅ Extraction complète : leaderboard + top 3 armes par joueur
- ⚠️ Limitation : Délai 15s par page (attente résolution Cloudflare)

### Pourquoi BigQuery vs PostgreSQL/MinIO ?

**MinIO** (archivé) :
- ❌ Complexité : nécessite Docker, gestion S3-like
- ❌ Pas de valeur ajoutée : NDJSON déjà structuré
- ❌ Coût opérationnel : maintenance locale

**BigQuery** (choisi) :
- ✅ Free tier généreux : 10 GB stockage, 1 TB queries/mois gratuit
- ✅ Intégration native DBT
- ✅ Scaling automatique
- ✅ Serverless : zéro maintenance

### Pourquoi GitHub Actions vs Airflow ?

**Airflow** (planifié V2) :
- ❌ Complexité : nécessite serveur dédié, Docker, maintenance
- ❌ Overkill pour 1 workflow hebdomadaire
- ❌ Coût : si hébergé (Cloud Composer = $300+/mois)

**GitHub Actions** (MVP) :
- ✅ Gratuit : 2000 min/mois (usage ~30 min/mois)
- ✅ Zero setup : déjà intégré au repo
- ✅ CI/CD natif : auto-deploy dashboard
- ✅ Logs centralisés : GitHub UI

---

## Extraction Détaillée

### Technique de Bypass Cloudflare

**Problème** : Tracker.gg protégé par Cloudflare Challenge (détection bot)

**Solution** : `undetected-chromedriver` + attente intelligente

```python
import undetected_chromedriver as uc
import time

# Configuration Chrome headless
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options)
driver.get("https://tracker.gg/battlefield-2042/profile/...")

# Attente critique : résolution Cloudflare
time.sleep(15)  # Challenge résolu en 10-15s

# HTML maintenant accessible
html = driver.page_source
```

### Regex Extraction des Armes

**Pattern** : Extraction depuis `<img>` tags + `<span>` kills

```python
import re

pattern = r'wp_[^.]+\.png/image\.png" alt="([^"]+)"[^>]*>.*?Kills.*?<span[^>]*>([0-9,]+).*?</span>'
matches = re.findall(pattern, html, re.DOTALL)

# Exemple output :
# [('SG 553R', '86,897'), ('TR-7', '50,394'), ('M4A1', '39,049')]

# Transformation en dict
weapons = [
    {
        "weapon_name": name,
        "kills": int(kills.replace(',', '')),
        "weapon_rank": idx + 1
    }
    for idx, (name, kills) in enumerate(matches[:3])
]
```

### Format NDJSON (Newline Delimited JSON)

**Pourquoi NDJSON vs JSON array ?**
- ✅ BigQuery native : `LOAD DATA FORMAT=NEWLINE_DELIMITED_JSON`
- ✅ Streaming : pas besoin de charger le fichier complet en mémoire
- ✅ Append facile : `cat file1.ndjson file2.ndjson > merged.ndjson`

**Exemple fichier** :
```json
{"player_id":"abc123","username":"ProGamer","platform":"PC","profile_url":"https://...","snapshot_utc":"2025-10-30T14:32:00Z","snapshot_date":"2025-10-30"}
{"player_id":"def456","username":"EliteSniper","platform":"PS5","profile_url":"https://...","snapshot_utc":"2025-10-30T14:33:15Z","snapshot_date":"2025-10-30"}
```

### Gestion des Erreurs & Retry

**Stratégie actuelle** :
1. **Timeout** : 30s max par page
2. **Retry** : 3 tentatives avec backoff exponentiel (1s, 2s, 4s)
3. **Logging** : Tous les échecs dans `data/logs/extraction.log`
4. **Checkpointing** : Sauvegarde après chaque joueur (reprise possible)

**À améliorer (Phase 7.3)** :
- Librairie `tenacity` pour retry automatique
- Monitoring temps réel avec `tqdm` progress bars
- Tests unitaires pytest sur validation données

---

## Historique des Phases

### Phase 0.5 - Exploration & POC ✅

**Objectif** : Valider faisabilité extraction Tracker.gg

**Résultats** :
- 🔍 API Tracker.gg testée → Non fonctionnelle (401)
- 🕷️ Web scraping testé → 100% succès avec Selenium
- 📊 Extraction 100 joueurs + 300 armes (3 par joueur)
- 📁 Fichier NDJSON : `bf6_top_weapons_2025-10-20_200220.ndjson` (22.66 KB)
- ⏱️ Durée : 31 min (~17s par joueur)

### Phase 1 - MinIO Upload (ARCHIVÉE) ❌

**Objectif** : Stockage S3-like local avec MinIO

**Résultat** : Abandonné
- ❌ Complexité non justifiée pour MVP
- ❌ Docker Desktop requis (dépendance lourde)
- ✅ Remplacé par : stockage NDJSON local + BigQuery direct

### Phase 2 - BigQuery Setup ✅

**Date** : 22 octobre 2025

**Actions** :
1. Création projet GCP `battlefield-meta-aggregator`
2. Dataset BigQuery `bf6_meta`
3. Service account `bigquery-admin-service-882@...` (rôle BigQuery Admin)
4. Tables Bronze :
   - `bronze_leaderboard` : 7 champs (player_id PK, username, platform, etc.)
   - `bronze_weapons` : 7 champs (player_id FK, weapon_name, kills, etc.)

**Validation** :
```sql
SELECT COUNT(*) FROM `bf6_meta.bronze_leaderboard`;  -- 50 rows
SELECT COUNT(*) FROM `bf6_meta.bronze_weapons`;      -- 150 rows
```

### Phase 3 - DBT Transformations ✅

**Date** : 22-25 octobre 2025

**Modèles créés** :
- **Bronze** : `bronze_leaderboard.sql`, `bronze_weapons.sql` (sources)
- **Silver** : 
  - `silver_players.sql` : Déduplication + calcul best_weapon
  - `silver_weapons.sql` : Agrégation par arme
  - `silver_player_weapons.sql` : Jointure enrichie (player + armes)
- **Gold** :
  - `gold_top_weapons_global.sql` : Top 10 armes par kills totaux
  - `gold_player_performance.sql` : Classement joueurs avec métriques
  - `gold_weapon_diversity.sql` : Métriques de diversité du méta

**Tests DBT** : 44 total
- `not_null` : 18 tests (tous PKs/FKs)
- `unique` : 8 tests (player_id, weapon_name)
- `accepted_values` : 6 tests (platform, weapon_type)
- `relationships` : 6 tests (FK integrity)
- Custom : 6 tests (business logic)

**Commandes** :
```bash
cd dbt
dbt run    # Exécute toutes les transformations
dbt test   # Valide les 44 tests → 44/44 PASS ✅
```

### Phase 4 - Dashboard Streamlit Local ✅

**Date** : 26-28 octobre 2025

**Features** :
- 🏠 Page Home : Métriques clés + Top 10 armes (bar chart Plotly)
- 🔫 Page All Weapons : Table interactive + scatter plot kills vs usage
- 👥 Page All Players : Classement avec best weapon + métriques

**Architecture** :
```
dashboard/
├── app.py              # Point d'entrée (copié vers racine streamlit_app.py)
├── pages/
│   ├── 1_🔫_All_Weapons.py
│   └── 2_👥_All_Players.py
└── utils/
    └── bigquery.py     # Connexion + queries BigQuery
```

**Déploiement local** :
```bash
streamlit run streamlit_app.py
# Accessible : http://localhost:8501
```

### Phase 4.5 - Cloud Deploy ✅

**Date** : 29-30 octobre 2025

**Actions** :
1. Création compte Streamlit Cloud
2. Connexion GitHub repo
3. Configuration secrets (`GOOGLE_APPLICATION_CREDENTIALS` via BigQuery connector)
4. Auto-deploy depuis `main` branch

**URL Production** : https://battlefieldmetaaggregator.streamlit.app

**Bugs résolus** :
- ❌ Erreur `weapon_type` : Colonne manquante dans Gold tables
- ✅ Fix : Ajout `weapon_type` dans `gold_top_weapons_global.sql` avec `COALESCE(wt.weapon_type, 'Unknown')`
- ✅ Tests : 3 pages validées sans erreur Plotly

### Phase 5.1 - Extraction Optimization ✅

**Date** : 30 octobre 2025

**Objectif** : Production-ready extraction script

**Résultats** :
- ✅ Script `extract_bf6_meta_complete.py`
- ✅ Extraction 50 joueurs (vs 100 initial pour limiter durée)
- ✅ 2 étapes séquentielles :
  1. Leaderboard scraping → `data/bronze/bf6_leaderboard_*.ndjson`
  2. Weapons scraping → `data/bronze/bf6_weapons_*.ndjson`
- ✅ Taux succès : 100% (50/50 joueurs)
- ✅ Checkpointing : Sauvegarde incrémentale (reprise possible si crash)
- ✅ Logs détaillés : `data/logs/extraction.log`

### Phase 5.2 - Pipeline Automatisé ✅

**Date** : 30 octobre 2025

**Script** : `scripts/run_pipeline.sh`

**Étapes** :
1. Extraction (`extract_bf6_meta_complete.py`) — 4-5 min
2. Upload BigQuery (`load_to_bigquery_latest.py`) — 30s
3. Transformations DBT (`dbt run`) — 13s
4. Tests DBT (`dbt test`) — 18s
5. Validation (`query_bigquery.py`) — 5s

**Total** : ~6-8 min end-to-end

### Phase 6 - Automation Scripts ✅

**Date** : 31 octobre - 1 novembre 2025

**Livrables** :
- ✅ `run_pipeline.sh` : Script principal orchestration
- ✅ `crontab_setup.txt` : Configuration cron hebdomadaire
- ✅ Documentation : `scripts/README.md`

**Cron example** :
```bash
# Extraction chaque dimanche 2h UTC
0 2 * * 0 /path/to/battlefield_meta_aggregator/scripts/run_pipeline.sh
```

### Phase 7 - GitHub Actions CI/CD 🚀 (EN COURS)

**Date début** : 1 novembre 2025

**Statut** : Jour 1/5 (Service Account validé)

**Planning** :
- **Jour 1** ✅ : Vérification Service Account GCP
- **Jour 2** ⏳ : GitHub Secrets + Workflow creation
- **Jour 3** ⏳ : Test manuel + debugging
- **Jour 4** ⏳ : Monitoring + notifications
- **Jour 5** ⏳ : Documentation opérationnelle (`RUNBOOK.md`)

**Voir** : [`docs/PHASE_7_CHECKLIST.md`](PHASE_7_CHECKLIST.md)

---

## Schéma Complet des Données

### Bronze Layer (Raw)

**Naming convention** : `snapshot_utc` (TIMESTAMP avec timezone), `snapshot_date` (DATE partitionnée)

```sql
-- bronze_leaderboard
CREATE TABLE `bf6_meta.bronze_leaderboard` (
  player_id STRING NOT NULL,        -- MD5 hash du username (PK)
  username STRING NOT NULL,          -- Pseudo joueur
  platform STRING,                   -- PC, PS5, Xbox
  profile_url STRING,                -- URL Tracker.gg
  rank INT64,                        -- Position leaderboard (si disponible)
  snapshot_utc TIMESTAMP NOT NULL,   -- Horodatage extraction UTC
  snapshot_date DATE NOT NULL        -- Date extraction (partition key)
);

-- bronze_weapons
CREATE TABLE `bf6_meta.bronze_weapons` (
  player_id STRING NOT NULL,         -- FK → bronze_leaderboard
  weapon_name STRING NOT NULL,       -- Nom de l'arme (ex: "SG 553R")
  kills INT64 NOT NULL,              -- Nombre de kills avec cette arme
  weapon_rank INT64 NOT NULL,        -- Rang 1-3 pour ce joueur
  snapshot_utc TIMESTAMP NOT NULL,
  snapshot_date DATE NOT NULL
);
```

### Silver Layer (Cleaned & Joined)

```sql
-- silver_players : Déduplication + enrichissement
CREATE TABLE `bf6_meta.silver_players` AS
SELECT 
  player_id,
  username,
  platform,
  profile_url,
  snapshot_date,
  -- Calcul best weapon (arme avec le plus de kills)
  (SELECT weapon_name 
   FROM `bronze_weapons` bw 
   WHERE bw.player_id = bl.player_id 
   ORDER BY kills DESC 
   LIMIT 1) AS best_weapon,
  -- Total kills sur top 3 armes
  (SELECT SUM(kills) 
   FROM `bronze_weapons` bw 
   WHERE bw.player_id = bl.player_id) AS total_kills_top3
FROM `bronze_leaderboard` bl;

-- silver_weapons : Agrégation par arme
CREATE TABLE `bf6_meta.silver_weapons` AS
SELECT 
  weapon_name,
  COUNT(DISTINCT player_id) AS player_count,  -- Nb joueurs utilisant cette arme
  SUM(kills) AS total_kills,                  -- Kills totaux tous joueurs
  AVG(kills) AS avg_kills_per_player,
  MAX(kills) AS max_kills_single_player,
  snapshot_date
FROM `bronze_weapons`
GROUP BY weapon_name, snapshot_date;

-- silver_player_weapons : Jointure enrichie
CREATE TABLE `bf6_meta.silver_player_weapons` AS
SELECT 
  bl.player_id,
  bl.username,
  bl.platform,
  bw.weapon_name,
  bw.kills,
  bw.weapon_rank,
  bl.snapshot_date
FROM `bronze_leaderboard` bl
JOIN `bronze_weapons` bw USING (player_id, snapshot_date);
```

### Gold Layer (Analytical)

```sql
-- gold_top_weapons_global : Top 10 armes MVP
CREATE TABLE `bf6_meta.gold_top_weapons_global` AS
SELECT 
  weapon_name,
  total_kills,
  player_count,
  ROUND(avg_kills_per_player, 0) AS avg_kills_per_player,
  max_kills_single_player,
  ROUND(100.0 * player_count / (SELECT COUNT(DISTINCT player_id) FROM bronze_leaderboard), 1) AS usage_pct,
  COALESCE(wt.weapon_type, 'Unknown') AS weapon_type,  -- Enrichissement type arme
  snapshot_date
FROM `silver_weapons` sw
LEFT JOIN `weapon_types` wt USING (weapon_name)  -- Table de référence
ORDER BY total_kills DESC
LIMIT 10;

-- gold_player_performance : Classement joueurs
CREATE TABLE `bf6_meta.gold_player_performance` AS
SELECT 
  ROW_NUMBER() OVER (ORDER BY total_kills_top3 DESC) AS player_rank,
  player_id,
  username,
  platform,
  best_weapon,
  total_kills_top3,
  snapshot_date
FROM `silver_players`
ORDER BY total_kills_top3 DESC;

-- gold_weapon_diversity : Métriques méta
CREATE TABLE `bf6_meta.gold_weapon_diversity` AS
SELECT 
  COUNT(DISTINCT weapon_name) AS total_weapons,
  COUNT(DISTINCT CASE WHEN player_count >= 5 THEN weapon_name END) AS popular_weapons,  -- Utilisées par 5+ joueurs
  ROUND(AVG(player_count), 1) AS avg_players_per_weapon,
  MAX(player_count) AS max_players_single_weapon,
  snapshot_date
FROM `silver_weapons`;
```

---

## Configuration DBT

### profiles.yml (Connexion BigQuery)

**Path** : `~/.dbt/profiles.yml`

```yaml
battlefield_meta:
  target: prod
  outputs:
    prod:
      type: bigquery
      method: service-account
      project: battlefield-meta-aggregator
      dataset: bf6_meta
      keyfile: /path/to/battlefield_meta_aggregator/config/bigquery-key.json
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive
```

### dbt_project.yml

```yaml
name: 'battlefield_meta'
version: '1.0.0'
config-version: 2

profile: 'battlefield_meta'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

models:
  battlefield_meta:
    bronze:
      +materialized: view
      +schema: bronze
    silver:
      +materialized: table
      +schema: silver
    gold:
      +materialized: table
      +schema: gold
```

### Tests DBT (schema.yml)

**Exemple** : `dbt/models/gold/schema.yml`

```yaml
version: 2

models:
  - name: gold_top_weapons_global
    description: "Top 10 armes par kills totaux avec métriques d'usage"
    columns:
      - name: weapon_name
        description: "Nom de l'arme"
        tests:
          - not_null
          - unique
      - name: total_kills
        description: "Kills totaux tous joueurs confondus"
        tests:
          - not_null
      - name: usage_pct
        description: "% de joueurs utilisant cette arme"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100
```

---

## Déploiement Dashboard

### Configuration Streamlit Cloud

**Étapes** :
1. Connexion GitHub : https://share.streamlit.io
2. Repo : `paulfrettepro-collab/battlefield_meta_aggregator`
3. Branch : `main`
4. Main file : `streamlit_app.py`

**Secrets** :
```toml
# .streamlit/secrets.toml (Streamlit Cloud UI)
[gcp_service_account]
type = "service_account"
project_id = "battlefield-meta-aggregator"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "bigquery-admin-service-882@battlefield-meta-aggregator.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

**Auto-deploy** :
- Trigger : Commit sur `main` branch
- Délai : 2-3 min après push
- Cache : Invalidé automatiquement après 10 min

### Synchronisation dashboard/ ↔ root

**Problème** : Streamlit Cloud lit `streamlit_app.py` + `pages/` à la racine

**Solution** : Script sync (ou workflow GitHub Actions)

```bash
# Manuel
rm -rf pages/
cp -r dashboard/pages .
cat dashboard/app.py > streamlit_app.py
git add pages/ streamlit_app.py
git commit -m "chore: sync dashboard files"
git push

# Auto (à venir Phase 7.2) : .github/workflows/deploy_dashboard.yml
```

---

## Troubleshooting

### Erreur : Cloudflare Challenge Non Résolu

**Symptôme** : Extraction retourne 0 joueurs, timeout après 30s

**Cause** : User-Agent détecté comme bot, challenge trop long

**Solution** :
1. Augmenter timeout : `time.sleep(20)` au lieu de 15s
2. Ajouter headers custom :
   ```python
   options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
   ```
3. Retry avec librairie `tenacity` :
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def extract_player(url):
       # ... scraping logic
   ```

### Erreur : DBT Tests Failing (weapon_type)

**Symptôme** : `dbt test` retourne 2/44 FAIL sur `gold_top_weapons_global`

**Cause** : Colonne `weapon_type` manquante (LEFT JOIN sur table inexistante)

**Solution** :
```sql
-- Ajouter COALESCE pour gérer NULL
COALESCE(wt.weapon_type, 'Unknown') AS weapon_type

-- Ou créer seed weapon_types
-- dbt/seeds/weapon_types.csv
weapon_name,weapon_type
SG 553R,Assault Rifle
TR-7,Assault Rifle
M4A1,Assault Rifle
```

### Erreur : BigQuery Quota Exceeded

**Symptôme** : `403 Quota exceeded: Your table size quota has been exceeded`

**Cause** : Free tier 10 GB dépassé

**Solution** :
1. Vérifier taille dataset :
   ```sql
   SELECT 
     table_schema,
     SUM(size_bytes)/1024/1024/1024 AS size_gb
   FROM `bf6_meta.INFORMATION_SCHEMA.TABLE_STORAGE`
   GROUP BY table_schema;
   ```
2. Nettoyer anciennes partitions :
   ```sql
   DELETE FROM `bronze_leaderboard` WHERE snapshot_date < '2025-10-01';
   ```
3. Activer facturation (si nécessaire) : $5/TB après 1 TB gratuit

### Erreur : GitHub Actions - GCP Auth Failed

**Symptôme** : Job `setup` fail avec `Invalid credentials`

**Cause** : Secret `GCP_SERVICE_ACCOUNT_KEY` mal encodé ou expiré

**Solution** :
1. Régénérer clé service account :
   ```bash
   gcloud iam service-accounts keys create new-key.json \
     --iam-account=bigquery-admin-service-882@battlefield-meta-aggregator.iam.gserviceaccount.com
   ```
2. Encoder en base64 :
   ```bash
   cat new-key.json | base64 | pbcopy
   ```
3. Mettre à jour secret GitHub (Settings > Secrets > `GCP_SERVICE_ACCOUNT_KEY`)

---

**Document maintenu par** : Paul Fretté  
**Dernière mise à jour** : 2 novembre 2025  
**Version** : 1.0
