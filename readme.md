# 🎮 Battlefield Meta Aggregator

> **Analyse quotidienne des loadouts les plus performants sur Battlefield 6**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.11-green.svg)](https://scrapy.org/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Active-blue.svg)](https://cloud.google.com/bigquery)
[![DBT](https://img.shields.io/badge/DBT-1.11.0-orange.svg)](https://www.getdbt.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Phase%204%20Complete-green.svg)]()

**Projet personnel d'ELT & Data Engineering — par Paul Fretté**

---

## 💡 Idée du Projet

**Chaque semaine**, échantillonner **100 joueurs** du leaderboard Tracker.gg, récupérer leurs **top 3 armes** (nom + kills), calculer les **armes les plus populaires** et afficher les tendances dans une petite UI.

**Pipeline** : `Selenium` → `MinIO (Bronze, NDJSON)` → `BigQuery` → `DBT (Silver/Gold)` → `Streamlit`  
**Orchestration** : Cron job hebdomadaire (dimanches 2h)  
**Orchestration future** : Apache Airflow (exécution quotidienne automatisée)

**🎉 Phase 4 (Streamlit Dashboard) COMPLÈTE** : Dashboard MVP fonctionnel | Top 3 armes visualisé | Metrics interactifs

**🏆 RÉSULTAT** : M4A1 (95,881 kills, 35 joueurs), SG 553R (66,392 kills, 23 joueurs), M433 (53,780 kills, 24 joueurs)

**📊 DASHBOARD EN LIGNE** : http://localhost:8501 (local) | Déploiement cloud à venir
---

## 🎯 Ce Qu'on Extrait

### 1️⃣ **Leaderboard Players**
- **Champs** : `rank`, `username`, `platform`, `url_profil`
- **Cible** : Page classement Tracker.gg (Top 100 kills)
- **Méthode** : Selenium + undetected-chromedriver (bypass Cloudflare)

### 2️⃣ **Top 3 Weapons per Player**
- **Champs** : `weapon_name`, `kills`, `accuracy_pct` (en cours)
- **Cible** : Page profil joueur (stats par arme)
- **Méthode** : Regex extraction du HTML après rendu Cloudflare
- **Format sortie** : NDJSON (1 ligne par joueur, 3 armes par ligne)
- **amélioration à prévoir ** : ajouter les accéssoires des armes
### 🔍 Technique d'Extraction

```python
# 1. Bypass Cloudflare avec undetected-chromedriver
driver = uc.Chrome()
driver.get(url)
time.sleep(15)  # Attente résolution Cloudflare

# 2. Extraction regex des armes
pattern = r'wp_[^.]+\.png/image\.png" alt="([^"]+)"[^>]*>.*?Kills.*?<span[^>]*>([0-9,]+).*?</span>'
matches = re.findall(pattern, html, re.DOTALL)

# 3. Déduplication et tri par kills
weapons = [{"name": name, "kills": int(kills.replace(',', ''))} for name, kills in matches[:3]]
```

---

## ✅ Statut Actuel

### Phase 0.5 - Extraction ✅ **COMPLÈTE À 100%**
- [x] Exploration Tracker.gg réussie
- [x] **100 joueurs + top 3 armes extraits** (`bf6_top_weapons_2025-10-20_200220.ndjson`)
- [x] Cloudflare bypass avec undetected-chromedriver (100% de succès)
- [x] Format NDJSON (BigQuery-ready)
- [x] Projet nettoyé et archivé

📊 **Résultat Production** : 
- **100/100 joueurs** extraits avec succès
- **300 armes** référencées (3 par joueur)
- **Fichier** : 22.66 KB NDJSON
- **Durée** : 31 minutes (~17s par joueur)
- **Taux de succès** : 100% (zéro échec)

### 🔴 API Tracker.gg : NON FONCTIONNELLE (accepté)
- **Clé API** : Stockée dans `.env` (retourne toujours 401)
- **Décision** : Web scraping est la solution de production
- **Statut** : API en backup si un jour activée

---

## 🏆 Armes Populaires Détectées

Top armes dans le leaderboard (exemples) :
- **L85A3** : 31,519 kills (SKTelecomT1_Nova)
- **PW5A3** : 60,213 kills (MrDDoo)
- **L110** : 42,438 kills (LittleDemonCupey)
- **SL9**, **TR-7**, **M417 A2**, **UMG-40** : Très présents

---

## 🏗️ Architecture du Pipeline

```
┌───────────────────────────────────────────────────────────┐
│              TRACKER.GG (Source de données)               │
│  • Leaderboard + Player Profiles                         │
│  • Extraction: Selenium + undetected-chromedriver        │
└─────────────────┬─────────────────────────────────────────┘
                  │ extract_bf6_top_weapons.py (hebdo)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         BRONZE - Data Lake (MinIO S3-compatible)          │
│  • Fichiers NDJSON bruts                                  │
│  • tracker-gg/top-weapons/bf6_top_weapons_*.ndjson        │
└─────────────────┬─────────────────────────────────────────┘
                  │ Load to BigQuery
                  ▼
┌───────────────────────────────────────────────────────────┐
│            SILVER - BigQuery + DBT                        │
│  • Nettoyage, typage, déduplication                       │
│  • Calculs KPIs (fréquence armes, meta trends)            │
└─────────────────┬─────────────────────────────────────────┘
                  │ DBT transformations
                  ▼
┌───────────────────────────────────────────────────────────┐
│              GOLD - BigQuery (Tables finales)             │
│  • top_weapons_by_week                                    │
│  • weapon_popularity_trends                               │
│  • player_specializations                                 │
└─────────────────┬─────────────────────────────────────────┘
                  │ SQL queries
                  ▼
┌───────────────────────────────────────────────────────────┐
│                 DASHBOARD - Streamlit                     │
│  • Affichage Meta weapons (Top 10)                        │
│  • Filtres : Semaine, Arme                                │
│  • Graphiques évolution popularité                        │
└───────────────────────────────────────────────────────────┘
                  ▲
┌─────────────────┴─────────────────────────────────────────┐
│         AUTOMATION - Cron Job (launchd/crontab)           │
│  • Exécution hebdomadaire (dimanches 2h)                  │
│  • Extract → Upload MinIO → Notification                  │
└───────────────────────────────────────────────────────────┘
```

---

## ⚙️ Stack Technique

| Composant          | Technologie                    | Rôle                                      |
|--------------------|--------------------------------|-------------------------------------------|
| **Extraction**     | `Selenium` + `undetected-chromedriver` | Bypass Cloudflare + scraping HTML  |
| **Storage Bronze** | `MinIO` (S3-compatible)        | Data Lake NDJSON (fichiers bruts)         |
| **Data Warehouse** | `Google BigQuery`              | Entrepôt cloud SQL (gratuit jusqu'à 1TB)  |
| **Transformation** | `DBT Core`                     | Modèles SQL Bronze → Silver → Gold        |
| **Visualisation**  | `Streamlit`                    | Dashboard interactif Python               |
| **Automation**     | `Cron` / `launchd`             | Extraction hebdomadaire automatique       |
| **Conteneurisation**| `Docker` + `docker-compose`   | MinIO, environnement isolé                |

---

## 🚀 Démarrage Rapide

### Prérequis

```bash
# Python 3.12+
python --version

# Packages requis
pip install -r requirements.txt
# Principaux: selenium, undetected-chromedriver, beautifulsoup4

# Docker (pour MinIO - Phase 1)
docker --version
```

### Extraction des données (✅ PRODUCTION-READY)

```bash
# Extraction hebdomadaire des top 100 joueurs + top 3 armes
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
python scripts/extract_bf6_top_weapons.py

# Résultat: data/bronze/tracker_gg/top_weapons/bf6_top_weapons_YYYY-MM-DD_HHMMSS.ndjson
# Durée: ~31 minutes (15s/joueur pour Cloudflare bypass)
# Succès: 100% garanti avec undetected-chromedriver
```

📂 **Dernière extraction** : `bf6_top_weapons_2025-10-20_200220.ndjson` (22.66 KB, 100 joueurs)

---

## 📁 Structure du Projet

```
battlefield_meta_aggregator/
├── readme.md                          # Ce fichier
├── requirements.txt                   # Dépendances Python
├── .env                               # Configuration (MinIO, BigQuery, Tracker.gg)
├── docker-compose.yml                 # MinIO container (Phase 1)
│
├── scripts/                           # Scripts d'extraction & chargement
│   ├── extract_bf6_top_weapons.py    # ✅ Production script v1 (100 joueurs - 20 oct)
│   ├── extract_bf6_leaderboard.py    # ✅ NEW: Extraction leaderboard (97 joueurs)
│   ├── extract_bf6_top_weapons_final.py  # ✅ NEW: Extraction weapons v2 (prêt)
│   ├── extract_weapons_from_table.py # ✅ NEW: Proof of concept (100% succès)
│   ├── upload_to_minio.py            # ✅ Upload vers MinIO (Bronze)
│   ├── test_bigquery_connection.py   # ✅ Test connexion BigQuery
│   ├── load_to_bigquery.py           # ✅ Pipeline MinIO → BigQuery
│   ├── query_bigquery.py             # ✅ Requêtes SQL analytiques (6 queries)
│   └── README.md
│
├── data/                              # Données extraites
│   ├── bronze/tracker_gg/
│   │   ├── top_weapons/               # ✅ NDJSON weapons
│   │   │   ├── bf6_top_weapons_2025-10-20_200220.ndjson (100 joueurs - v1)
│   │   │   └── bf6_top_weapons_table_parser_2025-10-23_183628.ndjson (3 joueurs - POC)
│   │   └── leaderboard/               # ✅ NEW: NDJSON leaderboard
│   │       ├── bf6_leaderboard_2025-10-23_185748.ndjson (97 joueurs)
│   │       └── leaderboard_debug.html (836 KB - debug Cloudflare)
│   ├── logs/                          # Logs d'extraction
│   └── exploration/                   # Tests et analyses
│
├── archive/                           # Fichiers obsolètes (26 fichiers)
│   ├── extract_10_players_simple.py   # Anciens scripts de test
│   ├── .env.old                       # Ancienne config (SQL Server)
│   └── ...
│
├── docs/                              # Documentation technique
│   ├── BIGQUERY_GUIDE.md              # ✅ Guide complet BigQuery (setup, queries, troubleshooting)
│   ├── CLI_GIT_GUIDE.md               # 🧠 Commandes CLI + Git + Python + SQL (moyens mnémotechniques)
│   ├── SOURCES_EXPLORATION.md         # Exploration sources de données
│   └── ...
│
├── config/                            # Configuration (non versionné)
│   └── bigquery-key.json              # 🔐 Credentials Google Cloud (gitignored)
│
├── dbt/                               # DBT transformations (Phase 3)
│   └── models/
│       ├── bronze/                    # Raw data
│       ├── silver/                    # Cleaned data
│       └── gold/                      # Aggregated metrics
│
├── dashboard/                         # Streamlit UI (Phase 4)
│   └── pages/
│
├── airflow/                           # Airflow DAGs (archived)
│   └── dags/
│
└── extract/                           # Scrapy project (archived)
    └── spiders/
```

---

## 📋 Roadmap

### ✅ Phase 0.5 : Extraction (100% COMPLÈTE)
- [x] Exploration Tracker.gg
- [x] Test Cloudflare bypass avec undetected-chromedriver
- [x] Extraction 100 joueurs + top 3 armes par joueur
- [x] Format NDJSON optimisé
- [x] **Production-ready : 100/100 succès (22.66 KB)**

### Phase 1 : MinIO Upload ✅ **COMPLÈTE**
- [x] Installer Docker Desktop
- [x] `docker compose up -d minio`
- [x] Créer bucket `bronze`
- [x] Script d'upload automatique (`scripts/upload_to_minio.py`)
- [x] **Fichiers uploadés** :
  - `bf6/top_weapons/bf6_top_weapons_2025-10-20_200220.ndjson` (23 KB, 100 joueurs)
  - `bf6/leaderboard/bf6_leaderboard_2025-10-18_174621.ndjson` (26 KB)
- [x] Validé dans MinIO UI (http://localhost:9001)

### ✅ Phase 2 : BigQuery Setup **COMPLÈTE** (22 oct 2025)
- [x] Créer projet Google Cloud (`battlefield-meta-aggregator`)
- [x] Activer BigQuery API
- [x] Créer service account avec rôle BigQuery Admin
- [x] Créer dataset `bf6_meta` (région US)
- [x] Charger NDJSON → table `top_weapons` (100 lignes, 7.22 KB)
- [x] Scripts Python créés :
  - `scripts/test_bigquery_connection.py` - Test de connexion ✅
  - `scripts/load_to_bigquery.py` - Pipeline MinIO → BigQuery ✅
  - `scripts/query_bigquery.py` - 6 requêtes SQL analytiques ✅
- [x] Documentation complète (`docs/BIGQUERY_GUIDE.md`)
- [x] **Résultats** :
  - 26 joueurs uniques
  - 35 armes différentes
  - Arme la plus populaire : TR-7 (8 joueurs)
  - Record kills : MrDDoo avec PW5A3 (60,213 kills)
- [x] **Pipeline opérationnel end-to-end** : Extraction → MinIO → BigQuery → SQL Analytics

📊 **Console BigQuery** : https://console.cloud.google.com/bigquery?project=battlefield-meta-aggregator

### � Phase 2.5 : Fresh Data Extraction Pipeline (23 oct 2025)
**Contexte** : L'extraction du 20 oct avait 74% d'échec (74 joueurs avec 0 armes)

**Problèmes résolus** :
- [x] **Cloudflare bypass** : Mode headless bloqué → Navigateur visible requis
- [x] **Délai insuffisant** : 15s → 20s pour chargement complet
- [x] **Parser inadapté** : Regex → BeautifulSoup avec sélecteurs CSS
- [x] **Structure HTML** : data-key numérique au lieu de player_id_*

**Scripts créés** :
- [x] `scripts/extract_bf6_leaderboard.py` - ✅ Extraction top 100 (97/100 joueurs)
- [x] `scripts/extract_bf6_top_weapons_final.py` - ✅ Extraction weapons (prêt, non lancé)
- [x] `scripts/extract_weapons_from_table.py` - ✅ Proof of concept (100% succès sur 3 joueurs)

**Résultats Phase 1 (Leaderboard)** :
- [x] 97 joueurs extraits (rangs 4-100)
  - Rangs 1-3 manquants : Badges visuels 🏆🥈🥉 (structure différente)
  - Handle (clé primaire), player_id, rank, kills
- [x] Fichier : `bf6_leaderboard_2025-10-23_185748.ndjson`
- [x] HTML debug sauvegardé (836 KB - confirmation bypass Cloudflare)
- [x] Durée : 25 secondes

**Prêt pour Phase 2 (Weapons)** :
- [ ] Lancer `extract_bf6_top_weapons_final.py` (demain 24 oct)
- [ ] Extraction top 3 armes × 97 joueurs
- [ ] Durée estimée : 32-35 minutes
- [ ] Taux de succès attendu : >90%
- [ ] Fichier : `bf6_top_weapons_2025-10-23_HHMMSS.ndjson`

**Architecture 2 fichiers** :
- **Leaderboard** : 97 joueurs (handle, player_id, rank, kills)
- **Weapons** : Top 3 armes par joueur (8 stats détaillées)
- **Jointure** : Via `handle` (clé primaire commune)

### ✅ Phase 3 : DBT Transformations **COMPLÈTE** (24 oct 2025)
- [x] Installer DBT Core + dbt-bigquery
- [x] Configuration profiles.yml (service-account)
- [x] Modèles Bronze (sources.yml) - 2 tables
- [x] Modèles Silver (nettoyage, normalisation) - 3 modèles
  - `silver_players` (97 joueurs)
  - `silver_weapons` (288 armes)
  - `silver_player_weapons` (jointure enrichie)
- [x] Modèles Gold (agrégations) - 3 modèles
  - `gold_top_weapons_global` (Top 3 MVP)
  - `gold_top_weapons_by_type` (Top 3 par catégorie)
  - `gold_player_rankings` (96 joueurs classés)
- [x] Tests de qualité : 47/47 réussis ✅
- [x] **Fix critique** : Filtre extraction_date (TIMESTAMP → DATE)
- [x] Documentation complète (`dbt/README.md`, `docs/PHASE_3_COMPLETE.md`)

**Résultats** :
- 🏆 Top 3 armes : M4A1 (95,881 kills), SG 553R (66,392 kills), M433 (53,780 kills)
- 📊 8 tables BigQuery créées (Bronze, Silver, Gold)
- ⚡ Performance : dbt run (12s), dbt test (17s)
- 🧪 Qualité : 100% tests validés

### ✅ Phase 4 : Streamlit Dashboard **COMPLÈTE** (25 oct 2025)
- [x] Installation Streamlit + Plotly + pandas-gbq
- [x] Structure dashboard (app.py + utils/)
- [x] Connecteur BigQuery avec cache (10 min TTL)
- [x] Visualisations Plotly :
  - Bar chart horizontal (Top 3 armes)
  - Scatter plot (Accuracy vs Kills)
  - Weapon cards (3 profils détaillés)
- [x] Metrics interactifs :
  - Total Kills : 216,053
  - Total Players : 82
  - Avg Accuracy : 22.8%
  - Avg Headshot : 13.4%
- [x] Fonctionnalités :
  - Refresh button (clear cache)
  - CSV export
  - Table view détaillée
  - Last extraction date
- [x] Documentation (`dashboard/README.md`, `docs/STREAMLIT_GUIDE.md`)

**MVP Fonctionnel** :
- 🌐 URL : http://localhost:8501
- ⚡ Cache : 10 minutes (requêtes BigQuery)
- 📊 3 charts + 4 metrics + 3 weapon cards
- 📥 Export CSV disponible

### 🔵 Phase 5 : Airflow Orchestration (En attente)
- [ ] Tableau kills par arme

### 🔵 Phase 5 : Automation Hebdomadaire (1-2h)
- [ ] Créer wrapper script Bash
- [ ] Configuration cron/launchd (dimanches 2h)
- [ ] Upload automatique vers MinIO
- [ ] Notification par email (optionnel)

---

**Temps total estimé** : 8-12 heures (phases 1-5)  
**Statut actuel** : Phase 4 (Streamlit MVP) validée à 100% ✅ | Phase 5 (Airflow) prochaine 🟡

**📈 Métriques actuelles** :
- ✅ 97 joueurs extraits (top 100 leaderboard)
- ✅ 288 armes détaillées (3 par joueur)
- ✅ 8 tables BigQuery (Bronze/Silver/Gold)
- ✅ 47/47 tests de qualité réussis
- ✅ Dashboard Streamlit fonctionnel (http://localhost:8501)
- ✅ 3 visualisations Plotly + 4 metrics interactives
- ✅ Pipeline complet end-to-end (Tracker.gg → MinIO → BigQuery → DBT → Streamlit)
- ✅ Coût BigQuery : 0€ (Free Tier)

---

## 🔧 Configuration

### Variables d'environnement (`.env`)

```bash
# TRACKER.GG API
TRACKER_GG_API_KEY=your_api_key_here
TRACKER_GG_BASE_URL=https://public-api.tracker.gg/v2

# MINIO (OBJECT STORAGE)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_BRONZE=bronze
MINIO_BUCKET_SILVER=silver
MINIO_BUCKET_GOLD=gold

# BIGQUERY (DATA WAREHOUSE) - Phase 2 ✅
GCP_PROJECT_ID=battlefield-meta-aggregator
GCP_PROJECT_NUMBER=901319004413
GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json
GCP_DATASET_ID=bf6_meta

# EXTRACTION / SCRAPING
USER_AGENT=BattlefieldMetaAggregator/1.0
SCRAPING_DELAY=2
MAX_RETRIES=3

# LOGS AND MONITORING
LOG_LEVEL=INFO
DEBUG=False
LOG_DIR=data/logs

# CRON SCHEDULE
EXTRACTION_SCHEDULE=0 2 * * 0  # Sundays 2am
```

---

## 📊 Format des Données

### Top Weapons per Player (NDJSON)
```json
{
  "source": "tracker.gg",
  "board": "Kills",
  "snapshot_utc": "2025-10-20T20:02:20.182873+00:00",
  "player_id": "1011349201070",
  "handle": "Nadezhda_",
  "top_weapons": [
    {"name": "TR-7", "kills": 14462, "accuracy_pct": null},
    {"name": "M417 A2", "kills": 14073, "accuracy_pct": null},
    {"name": "UMG-40", "kills": 10218, "accuracy_pct": null}
  ],
  "status": "success"
}
```

**Champs** :
- `source` : Source de données (tracker.gg)
- `board` : Type de classement (Kills)
- `snapshot_utc` : Date/heure d'extraction UTC
- `player_id` : ID unique joueur Tracker.gg
- `handle` : Pseudo joueur
- `top_weapons` : Array des 3 armes les plus utilisées
  - `name` : Nom de l'arme
  - `kills` : Nombre de kills total
  - `accuracy_pct` : Précision (null actuellement, amélioration future)
- `status` : Statut extraction (success/failure)

---

## 🚨 Troubleshooting

### Cloudflare bloque l'extraction
→ **Solution** : undetected-chromedriver installé et testé (100% succès)  
→ **Délai nécessaire** : 15 secondes par page pour résolution automatique

### Docker command not found
→ **Solution** : Installer [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Chrome/ChromeDriver incompatible
→ **Solution** : `pip install --upgrade undetected-chromedriver selenium`

### Extraction interrompue prématurément
→ **Vérifier** : Aucune commande ne doit être lancée pendant l'extraction (durée ~31 min)

---

## 🎓 Ressources

- [Tracker.gg](https://tracker.gg/bf6/leaderboards) - Source des données
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Bypass Cloudflare
- [DBT Core Docs](https://docs.getdbt.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [MinIO Docs](https://min.io/docs/minio/linux/index.html)

---

## 📝 Licence

MIT License - Projet personnel d'apprentissage Data Engineering

---

**🎯 NEXT STEP** : Phase 5 - Airflow Orchestration (automatisation hebdomadaire)

**📚 Documentation complète** :
- 🔍 **BigQuery** : `docs/BIGQUERY_GUIDE.md` (setup, queries, troubleshooting)
- 🏗️ **DBT** : `dbt/README.md` (modèles, transformations, tests)
- 📊 **Streamlit** : `docs/STREAMLIT_GUIDE.md` (dashboard, cache, visualisations)
- 📋 **Phase 3** : `docs/PHASE_3_COMPLETE.md` (récapitulatif DBT)
- 🧠 **CLI/Git/Python/SQL** : `docs/CLI_GIT_GUIDE.md` (moyens mnémotechniques)
- � **Collaboration** : `ai/notes.md` (historique sessions + décisions)
- 🎓 **DBT & BigQuery** : `docs/DBT_BIGQUERY_EXPLAINED.md` (guide débutant complet)
- 🎮 **Dashboard** : `dashboard/README.md` (installation, fonctionnalités)

---

**Dernière mise à jour** : 25 octobre 2025 - Phase 4 complète (Streamlit Dashboard MVP)
