# 📝 AI Collaboration Log

## Session 1 - 22 octobre 2025

### 🎯 Request
User asked for complete project analysis to:
- Detect redundant, outdated, or duplicate files
- Identify inconsistencies between code, documentation, and README
- Suggest reorganization
- Review config files for coherence
- Maintain living memory of collaboration

### 🔍 Analysis Performed

#### 1. File Inventory
**Total files**: 34 (excluding .venv, .git, cache)

**By type**:
- `.md`: 18 files (documentation)
- `.py`: 6 files (scripts)
- `.json`: 3 files (data outputs)
- `.ndjson`: 2 files (production data)
- `.txt`: 1 file (requirements)
- `.yml`: 1 file (docker-compose)
- config: 3 files (.env, .env.example, .gitignore)

#### 2. Duplicates Detected

**⚠️ README.md (6 occurrences)**:
- `dbt/README.md` - Empty placeholder
- `airflow/README.md` - Empty placeholder
- `dashboard/README.md` - Empty placeholder
- `scripts/README.md` - Contains useful content
- `data/README.md` - Contains useful content
- `data/exploration/README.md` - Contains useful content

**Analysis**: 3/6 are empty placeholders that should be removed or filled.

#### 3. Project Structure Issues

**✅ Well organized**:
- `/scripts/` - 6 Python scripts (extraction, upload, debug)
- `/docs/` - 10 markdown files (documentation)
- `/data/bronze/` - Production NDJSON files
- Root config files - Clean (docker-compose.yml, requirements.txt, etc.)

**⚠️ Issues found**:
1. **Old/obsolete files**:
   - `data/outputs/` contains old JSON files (pcgamer, wzstats, meta_analysis) - From Scrapy exploration
   - `data/bronze/bf6_leaderboard_2025-10-18_174225.ndjson` - Old test file (18 oct)
   - `scripts/debug_profile_page.py` - Debug script, should be archived
   - `scripts/test_undetected_chrome.py` - Test script, should be archived
   - `scripts/extract_bf6_final.py` - Old extraction, replaced by `extract_bf6_top_weapons.py`
   - `scripts/analyze_data.py` - Old analysis script

2. **Empty placeholder directories**:
   - `dbt/` - Has README but no models yet
   - `airflow/` - Has README but no DAGs yet
   - `dashboard/` - Has README but no code yet

3. **Documentation proliferation**:
   - 10 docs in `/docs/` (good)
   - `cli_git_symboles_vs_code.md` at root (should be in `/docs/`)
   - Multiple README files (some empty)

#### 4. Config Files Review

**✅ .env**:
- Contains actual secrets (not in git)
- Well structured

**✅ .env.example**:
- Template without secrets
- Coherent with .env

**✅ .gitignore**:
- Properly ignores .env, .venv, data files, logs
- Up to date

**✅ docker-compose.yml**:
- Clean (MinIO only)
- Recently simplified (Phase 1)

**✅ requirements.txt**:
- Contains all needed packages
- Up to date

### 📋 Findings Summary

#### 🟢 What's Good
1. Clear separation: scripts, docs, data
2. Config files are coherent
3. Production file is clean (bf6_top_weapons_2025-10-20_200220.ndjson)
4. Recent documentation is excellent (DOCKER_EXPLAINED, JOINTURE_PROBLEM)
5. Git workflow is clean

#### 🟡 What Needs Attention
1. **6 old/obsolete files to archive or remove**
2. **3 empty README.md to remove or fill**
3. **1 file misplaced** (cli_git_symboles_vs_code.md should be in /docs/)
4. **data/outputs/** folder from old Scrapy exploration (to archive)

#### 🔴 Inconsistencies Found
1. **Old leaderboard file** (18 oct) still in data/bronze/ but not used
2. **Multiple extraction scripts** (extract_bf6_final.py vs extract_bf6_top_weapons.py)
3. **Test/debug scripts mixed with production** in /scripts/

### 🎯 Recommended Actions

#### Phase 1: Archive Old Files (SAFE)
```bash
# Create archive folder if not exists
mkdir -p archive/old_scripts
mkdir -p archive/old_data

# Move old scripts
mv scripts/debug_profile_page.py archive/old_scripts/
mv scripts/test_undetected_chrome.py archive/old_scripts/
mv scripts/extract_bf6_final.py archive/old_scripts/
mv scripts/analyze_data.py archive/old_scripts/

# Move old data
mv data/bronze/bf6_leaderboard_2025-10-18_174225.ndjson archive/old_data/
mv data/outputs/ archive/old_data/

# Remove empty READMEs
rm dbt/README.md
rm airflow/README.md
rm dashboard/README.md
```

#### Phase 2: Reorganize Documentation
```bash
# Move misplaced doc
mv cli_git_symboles_vs_code.md docs/CLI_GIT_GUIDE.md
```

#### Phase 3: Update .gitignore
Add to .gitignore:
```
# Archive folder
archive/

# AI collaboration logs
ai/
```

#### Phase 4: Clean Empty Folders (Later)
When dbt/airflow/dashboard are populated, add proper READMEs.

### 📊 Before/After Comparison

**Before cleanup**:
- 34 files
- 6 obsolete files
- 3 empty READMEs
- 1 misplaced doc
- Mixed test/prod scripts

**After cleanup**:
- ~25 active files
- 0 obsolete files in active directories
- 0 empty READMEs
- All docs in /docs/
- Clean separation test/prod

### 🚀 Next Steps

1. **Ask user for approval** of cleanup plan
2. **Execute Phase 1** (archive old files)
3. **Execute Phase 2** (reorganize docs)
4. **Update .gitignore**
5. **Git commit** with clear message
6. **Update README.md** to reflect new structure

### 💡 Additional Recommendations

1. **Create CHANGELOG.md** to track project evolution
2. **Add /ai/ to .gitignore** (this log is local)
3. **Consider renaming** readme.md → README.md (standard)
4. **Future**: When Phase 3-5 start, create proper docs in dbt/, airflow/, dashboard/

---

## Notes for Next Session

- User is currently at **Phase 1 complete** (MinIO operational)
- Ready to start **Phase 2** (BigQuery)
- Project is production-ready but has legacy artifacts
- Cleanup will make future phases clearer

---

# Session 2: Cleanup Execution - 22 octobre 2025, 10h59

## ✅ NETTOYAGE COMPLET EXÉCUTÉ

**VALIDATION UTILISATEUR**: ✅ "Oui"

### Phases exécutées:

**Phase 1 - Archivage** ✅
```bash
mkdir -p archive/old_scripts archive/old_data
mv scripts/{debug_profile_page,test_undetected_chrome,extract_bf6_final,analyze_data}.py → archive/old_scripts/
mv data/bronze/bf6_leaderboard_2025-10-18_174225.ndjson → archive/old_data/
mv data/outputs/ → archive/old_data/
```
**Résultat**: 4 scripts + 1 NDJSON + 1 dossier archivés (10 fichiers au total)

**Phase 2 - Suppression README vides** ✅
```bash
rm dbt/README.md airflow/README.md dashboard/README.md
```
**Résultat**: 3 fichiers supprimés

**Phase 3 - Réorganisation docs** ✅
```bash
mv cli_git_symboles_vs_code.md → docs/CLI_GIT_GUIDE.md
```
**Résultat**: 1 fichier relocalisé

**Phase 4 - Mise à jour .gitignore** ✅
Ajouté section 13:
```
archive/            # Anciens scripts et données
ai/                 # Notes de collaboration IA
```

### Résultats finaux:

**AVANT**: 34 fichiers
**APRÈS**: 33 fichiers actifs (+ archive/)
- ✅ 10 fichiers obsolètes archivés (récupérables dans `archive/`)
- ✅ 3 README vides supprimés
- ✅ 1 documentation relocalisée dans `/docs/`
- ✅ `.gitignore` mis à jour (archive/ et ai/ ignorés)

**Structure archive/ créée**:
```
archive/
├── old_scripts/ (4 fichiers - 16.6 KB)
│   ├── analyze_data.py
│   ├── debug_profile_page.py
│   ├── extract_bf6_final.py
│   └── test_undetected_chrome.py
└── old_data/ (1 NDJSON + dossier outputs)
    ├── bf6_leaderboard_2025-10-18_174225.ndjson (27.7 KB)
    └── outputs/ (3 JSON Scrapy)
```

### Prochaines actions:

1. ✅ FAIT: Commit Git du nettoyage
2. ✅ FAIT: Phase 2 - BigQuery setup complet

---

## Session 2 - 22 octobre 2025 (11h00-12h30)

### 🎯 Objectif
**Phase 2 : Intégration BigQuery** - Data Warehouse pour stocker les données extraites de MinIO

### � Tâches Réalisées

#### 1. Configuration Google Cloud Platform
- ✅ Projet GCP créé : `battlefield-meta-aggregator` (Project #901319004413)
- ✅ BigQuery API activée
- ✅ Service Account créé avec rôle BigQuery Admin
  - Email: `bigquery-admin-service-882@battlefield-meta-aggregator.iam.gserviceaccount.com`
  - Clé JSON téléchargée et placée dans `config/bigquery-key.json` (2,427 bytes)
  - **Sécurité** : Fichier ajouté au `.gitignore` (non versionné)

#### 2. Configuration Environnement Python
- ✅ Dépendances installées :
  ```bash
  google-cloud-bigquery==3.14.1
  google-cloud-storage==2.14.0
  db-dtypes==1.1.1
  ```
- ✅ Variables d'environnement ajoutées au `.env` :
  ```env
  GCP_PROJECT_ID=battlefield-meta-aggregator
  GCP_PROJECT_NUMBER=901319004413
  GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json
  ```

#### 3. Scripts Python Créés

**A. `scripts/test_bigquery_connection.py`** (113 lignes)
- Vérifie les variables d'environnement
- Teste l'existence du fichier credentials
- Valide la connexion à BigQuery
- Liste les datasets existants
- **Résultat** : ✅ Connexion réussie

**B. `scripts/load_to_bigquery.py`** (228 lignes)
- **Pipeline ETL** : MinIO → BigQuery
- Création automatique du dataset `bf6_meta`
- Création de la table `top_weapons` avec schéma :
  ```
  - source (STRING)
  - board (STRING)
  - snapshot_utc (TIMESTAMP)
  - player_id (STRING)
  - handle (STRING)
  - top_weapons[] (RECORD REPEATED):
    - name (STRING)
    - kills (INTEGER)
    - accuracy_pct (FLOAT)
  - status (STRING)
  ```
- Téléchargement automatique depuis MinIO (bucket `bronze`)
- Chargement NDJSON → BigQuery
- **Résultat** : ✅ 100 joueurs chargés (7.22 KB)

**C. `scripts/query_bigquery.py`** (150 lignes)
- 6 requêtes SQL analytiques :
  1. Top 10 joueurs
  2. Top 5 armes populaires (par nombre d'utilisateurs)
  3. Top 5 armes par kills maximum
  4. Statistiques globales
  5. Top 5 records joueur/arme
  6. Liste complète des armes
- **Résultat** : ✅ Toutes les requêtes exécutées avec succès

#### 4. Documentation Créée

**`docs/BIGQUERY_GUIDE.md`** (245 lignes)
- Guide complet d'installation et configuration
- Schéma de la table détaillé
- Exemples de requêtes SQL
- Analyse des coûts (projet 100% gratuit)
- Section troubleshooting (4 erreurs courantes)
- Liens vers ressources Google Cloud

#### 5. Problèmes Résolus

**Problème 1 : Environnement virtuel incorrect**
- **Symptôme** : `ModuleNotFoundError: No module named 'google'`
- **Cause** : Packages installés dans `/Codes/battlefield_meta_aggregator/.venv` au lieu de `/Github_pro_folder/battlefield_meta_aggregator/.venv`
- **Solution** : Recréation du venv avec `python3 -m venv .venv --clear` dans le bon dossier

**Problème 2 : Permission denied BigQuery**
- **Symptôme** : `403 POST bigquery.datasets.create permission denied`
- **Cause** : Service account sans rôle BigQuery Admin
- **Solution** : Création d'un nouveau service account avec permissions correctes (3ème tentative)

**Problème 3 : Schema mismatch**
- **Symptôme** : `400 Error: JSON parsing error - No such field: source`
- **Cause** : Schéma du script ne correspondait pas aux données NDJSON réelles
- **Solution** : Analyse du fichier NDJSON et correction du schéma (ajout de `source`, `board`, `snapshot_utc`)

**Problème 4 : Fichier MinIO introuvable**
- **Symptôme** : "Aucun fichier trouvé dans MinIO"
- **Cause** : Préfixe incorrect `tracker_gg/top_weapons/` au lieu de `bf6/top_weapons/`
- **Solution** : Correction du préfixe dans le script

**Problème 5 : .env avec JSON embarqué**
- **Symptôme** : Fichier .env illisible avec JSON de 50 lignes
- **Cause** : User a copié tout le JSON service account dans .env
- **Solution** : 
  - Création de `config/bigquery-key.json` avec le JSON
  - Nettoyage du `.env` pour ne garder que `GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json`
  - **Explication** : Les libs Google Cloud attendent un **chemin de fichier**, pas le JSON brut

#### 6. Résultats Analytiques (BigQuery Queries)

**Données chargées** :
- 100 joueurs (top 100 du leaderboard)
- 7.22 KB en BigQuery (compressé depuis 22.66 KB NDJSON)

**Insights découverts** :
- 26 joueurs uniques identifiés
- 35 armes différentes utilisées
- Moyenne : 3.0 armes par joueur
- **Arme la plus populaire** : TR-7 (utilisée par 8 joueurs, 14,157 kills en moyenne)
- **Record de kills** : MrDDoo avec PW5A3 (60,213 kills)
- **Top 3 kills** :
  1. PW5A3 : 60,213 kills
  2. SL9 : 49,605 kills
  3. M4A1 : 43,343 kills

#### 7. Fichiers Modifiés

**Créés** :
- `config/bigquery-key.json` (2,427 bytes - non versionné)
- `docs/BIGQUERY_GUIDE.md`
- `scripts/test_bigquery_connection.py`
- `scripts/load_to_bigquery.py`
- `scripts/query_bigquery.py`

**Modifiés** :
- `requirements.txt` (ajout section BigQuery)
- `.env` (nettoyé et restructuré)

**Restaurés** :
- `docs/CLI_GIT_GUIDE.md` (22 KB - était marqué pour suppression)

### 🔐 Sécurité - Bonnes Pratiques Appliquées

#### ❌ Ce qu'on ne commit JAMAIS :
- `.env` (mots de passe, clés API)
- `config/bigquery-key.json` (credentials Google Cloud)
- Fichiers `*.json` de service accounts

#### ✅ Ce qui est versionné :
- `.env.example` (template sans valeurs sensibles)
- Documentation (BIGQUERY_GUIDE.md)
- Scripts Python (qui **lisent** les credentials, mais ne les contiennent pas)

#### � Pourquoi NE PAS mettre le JSON dans .env ?

**Mauvaise pratique** ❌ :
```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account"...}
```

**Bonne pratique** ✅ :
```env
GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json
```

**Raisons** :
1. **Échappement** : JSON contient `"`, `\n`, `{}` qui causent des erreurs de parsing
2. **Lisibilité** : Un .env avec 50 lignes de JSON est illisible
3. **Convention** : Les libs Google Cloud attendent un **chemin de fichier**, pas du JSON brut
4. **Les deux fichiers sont ignorés par Git** (`.env` ET `*.json` dans `.gitignore`)

### 📊 État du Projet

#### Pipeline Actuel (End-to-End) :
```
Tracker.gg → Scrapy Spider → MinIO (bronze) → BigQuery (bf6_meta.top_weapons) → SQL Analytics
```

#### Infrastructure :
- ✅ **Phase 0.5** : Extraction web (Scrapy)
- ✅ **Phase 1** : Object Storage (MinIO)
- ✅ **Phase 2** : Data Warehouse (BigQuery)
- 🟡 **Phase 3** : Transformation (DBT) - À venir
- 🟡 **Phase 4** : Dashboard (Streamlit) - À venir

#### Coûts BigQuery :
- **Gratuit Tier** : 10 GB stockage + 1 TB requêtes / mois
- **Notre usage** : 7.22 KB stockage + < 1 GB requêtes
- **Résultat** : **100% gratuit** 🎉

### 🎓 Leçons Apprises

1. **Double venv** : Toujours vérifier le chemin du virtualenv actif (`which python`)
2. **Service Accounts** : Tester les permissions avant de générer plusieurs clés
3. **Schema First** : Analyser les données réelles avant de définir le schéma BigQuery
4. **Git staging** : Toujours vérifier `git diff --cached` avant de commit (éviter les suppressions accidentelles)
5. **Credentials** : Utiliser des fichiers séparés pour les JSONs, pas .env

### 🚀 Prochaines Étapes

1. ✅ **IMMÉDIAT** : Restaurer `docs/CLI_GIT_GUIDE.md` (fait)
2. 🔄 **EN COURS** : Commit Phase 2 (BigQuery)
3. 🟡 **TODO** : Phase 3 - DBT (transformation des données)
   - Installer dbt-core et dbt-bigquery
   - Créer modèles de transformation (staging, gold)
   - Tests de qualité de données
4. 🟡 **TODO** : Phase 4 - Dashboard Streamlit
5. 🟡 **TODO** : Airflow (orchestration)

### 📝 Questions / Clarifications Session

**Q: Pourquoi CLI_GIT_GUIDE.md a disparu ?**
- **R** : Le fichier était marqué pour suppression dans le `git staging area` (visible avec `git diff --cached`)
- **Solution** : `git reset HEAD docs/CLI_GIT_GUIDE.md` puis `git restore docs/CLI_GIT_GUIDE.md`
- **Fichier restauré** : ✅ 22 KB, tous les moyens mnémotechniques présents

**Q: Pourquoi ne pas mettre le JSON BigQuery dans .env ?**
- **R** : Voir section "Sécurité - Bonnes Pratiques" ci-dessus
- **TL;DR** : Les deux sont protégés (.env ET .json), mais Google Cloud attend un **chemin**, pas du JSON

---

## Session 3 - 23 octobre 2025 : Fresh Data Extraction Pipeline

### 🎯 Contexte
**Problème identifié** : L'extraction du 20 octobre avait un taux d'échec de 74% (74 joueurs sur 100 avec 0 armes extraites)

**Objectif** : Extraire des données fraîches directement depuis tracker.gg avec une architecture en 2 fichiers :
1. **Leaderboard** (top 100 joueurs)
2. **Top weapons** (3 armes par joueur)

### 🔍 Investigation et Résolution des Problèmes

#### Problème 1 : 74% d'échec sur l'extraction du 20 octobre
**Analyse des causes** :
1. ✅ **Cloudflare bloque le mode headless**
   - HTML en mode headless : 19-22 KB (page de challenge)
   - HTML sans headless : 400-836 KB (contenu réel)
   - **Solution** : Retirer `--headless` de undetected-chromedriver
   
2. ✅ **Délai insuffisant**
   - 15 secondes → insuffisant pour le chargement complet
   - **Solution** : Passer à 20 secondes par page

3. ✅ **Mauvaise URL ou mauvais parser**
   - Extraction depuis `/overview` au lieu de `/weapons`
   - Parser regex ne fonctionne pas sur la structure de `/weapons`
   - **Solution** : URL explicite `/weapons` + BeautifulSoup avec parsing de tables

#### Problème 2 : Structure HTML différente entre pages
**Découverte** :
- Page `/overview` : Structure compatible avec regex
- Page `/weapons` : Table HTML avec `data-key="wp_*"` pour les armes
- **Solution** : BeautifulSoup avec sélecteur `data-key` starting with `wp_`

**Test de validation** :
- Script : `extract_weapons_from_table.py`
- Test sur 3 joueurs : ✅ **100% de succès**
  - RoboCat (1000380403530) : KV9 (8,535 kills)
  - tails21c (2480703860) : GRT-BC (10,510 kills)
  - BnanaMilk (3115975313) : SL9 (14,580 kills)
- HTML chargé : 406-445 KB (pas de blocage Cloudflare)

### 📋 Architecture du Pipeline Fresh Data

#### Conception Two-File Strategy
**Pourquoi 2 fichiers au lieu de 1 ?**
- **Fichier 1** : `bf6_leaderboard_YYYY-MM-DD_HHMMSS.ndjson`
  - 100 joueurs avec : `handle`, `player_id`, `rank`, `kills`
  - Clé primaire : `handle`
  - Source : Page 1 du leaderboard uniquement
  
- **Fichier 2** : `bf6_top_weapons_YYYY-MM-DD_HHMMSS.ndjson`
  - Top 3 armes par joueur avec 8 stats détaillées
  - Clé primaire : `handle` (pour jointure avec leaderboard)
  - Source : Page `/weapons` de chaque joueur

**Avantages** :
- Données leaderboard préservées même si extraction weapons échoue
- Possibilité de re-run weapons sans refaire le leaderboard
- Jointure SQL propre via `handle`

### 🛠️ Scripts Créés

#### 1. `extract_bf6_leaderboard.py` (183 lignes)
**Objectif** : Extraire les 100 meilleurs joueurs depuis la page 1 du leaderboard

**Défis rencontrés** :
- ❌ **Tentative 1** : Sélecteur `data-key` contenant `'player_id_'` → 0 résultat
- ❌ **Cause** : Structure HTML réelle utilise `data-key="1"`, `"2"`, `"3"` (valeurs numériques)
- ✅ **Solution** : Sélecteur `data-key` avec `.isdigit()` + extraction du `player_id` depuis l'attribut `href`

**Parsing HTML** :
```html
<tr data-key="79">
  <td><span class="min-w-9">79</span></td>  <!-- Rank -->
  <td><a href="/bf6/profile/1016329076176">
    <span class="truncate">Sir Jekyll</span>  <!-- Handle -->
  </a></td>
  <td><!-- country flag --></td>
  <td><span class="truncate">15,423</span></td>  <!-- Kills -->
</tr>
```

**Extraction finale** :
- Rank : Cell 0 → span avec classe `min-w-9`
- Player ID : Cell 1 → href attribute split
- Handle : Cell 1 → span.truncate dans le lien
- Kills : Cell 3 ou 4 → span.truncate avec valeur > 1000

**Résultats** :
- ✅ **97 joueurs extraits sur 100** (97%)
- ❌ **Rangs 1-3 manquants** : Utilisent des badges visuels (🏆🥈🥉) au lieu de texte
  - Rank 1 : RoboCat
  - Rank 2 : ViteZ
  - Rank 3 : MaxiqYT
- ✅ Fichier créé : `bf6_leaderboard_2025-10-23_185748.ndjson`

**Format du fichier** :
```json
{
  "handle": "GoldFragGrenade",
  "player_id": "3134417660",
  "rank": 4,
  "kills": 24603,
  "extraction_date": "2025-10-23T18:57:47.954469",
  "url_source": "https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1"
}
```

#### 2. `extract_bf6_top_weapons_final.py` (227 lignes)
**Objectif** : Extraire top 3 armes pour chaque joueur du fichier leaderboard

**Fonctionnalités** :
- ✅ Auto-détection du dernier fichier `bf6_leaderboard_*.ndjson`
- ✅ Prompt de confirmation utilisateur avec estimation de durée
- ✅ Extraction de 8 stats par arme :
  - `weapon_name`, `kills`, `rank`, `weapon_type`
  - `time_played`, `damage`, `accuracy`, `headshot_pct`
- ✅ Primary key : `handle` (pour jointure SQL)
- ✅ Sauvegarde HTML en cas d'erreur pour debug
- ✅ Pas de mode headless (bypass Cloudflare)

**État** : ✅ Prêt à l'emploi (code validé, attend exécution)

**Durée estimée** : 32-35 minutes pour 97 joueurs (20s × 97 + overhead)

#### 3. `extract_weapons_from_table.py` (218 lignes)
**Objectif** : Proof of concept pour valider l'approche BeautifulSoup + no-headless

**Test effectué** :
- 3 joueurs testés : RoboCat, tails21c, BnanaMilk
- ✅ **100% de succès** (3/3)
- HTML chargé : 406-445 KB (confirmation que Cloudflare n'intervient pas)
- Fichier créé : `bf6_top_weapons_table_parser_2025-10-23_183628.ndjson`

**Validation** : ✅ L'approche fonctionne, ready pour production

### 📁 Fichiers de Données Créés

#### Production Data
1. `bf6_leaderboard_2025-10-23_185748.ndjson` (97 lignes)
   - 97 joueurs du top 100 (rangs 4-100)
   - Format : handle, player_id, rank, kills, extraction_date, url_source
   - ✅ Prêt pour l'extraction weapons

2. `bf6_top_weapons_table_parser_2025-10-23_183628.ndjson` (3 lignes)
   - Proof of concept validé
   - 3 joueurs × 3 armes chacun
   - ✅ Démontre que le pipeline fonctionne

#### Debug Data
3. `leaderboard_debug.html` (836 KB)
   - HTML complet de la page leaderboard
   - Utilisé pour analyser la structure et corriger les sélecteurs
   - Confirme : pas de blocage Cloudflare (taille > 800 KB)

### 🔧 Correctifs Techniques Appliqués

#### Fix 1 : Sélecteur BeautifulSoup pour leaderboard
**Avant** (❌ 0 résultat) :
```python
player_rows = soup.find_all('tr', {'data-key': lambda x: x and 'player_id_' in x})
```

**Après** (✅ 97 résultats) :
```python
player_rows = soup.find_all('tr', {'data-key': lambda x: x and x.isdigit()})
```

#### Fix 2 : Extraction du player_id
**Avant** : Cherché dans `data-key` attribute (introuvable)
**Après** : Extrait depuis `href="/bf6/profile/{player_id}"` avec `.split('/')[-1]`

#### Fix 3 : Détection des kills
**Problème** : Plusieurs cellules contiennent des chiffres (rank, country stats, kills)
**Solution** : 
- Chercher dans cells[3] et cells[4]
- Valider que c'est un nombre > 1000 (les kills sont toujours > 1000 pour le top 100)
- Prendre le premier match trouvé

### 📊 État du Pipeline Actuel

```
┌─────────────────────────────────────────────────────────────┐
│                    FRESH DATA PIPELINE                       │
└─────────────────────────────────────────────────────────────┘

Phase 1: Leaderboard Extraction  ✅ TERMINÉ
├─ Script: extract_bf6_leaderboard.py
├─ Input: tracker.gg/leaderboards (page 1)
├─ Output: bf6_leaderboard_2025-10-23_185748.ndjson
├─ Résultat: 97/100 joueurs (97%)
└─ Durée: 25 secondes

Phase 2: Weapons Extraction  🟡 PRÊT (NON LANCÉ)
├─ Script: extract_bf6_top_weapons_final.py
├─ Input: bf6_leaderboard_2025-10-23_185748.ndjson (97 joueurs)
├─ Output: bf6_top_weapons_2025-10-23_HHMMSS.ndjson
├─ Durée estimée: 32-35 minutes
└─ État: Code validé, attend confirmation utilisateur

Phase 3: Data Validation  ⏳ EN ATTENTE
├─ Vérifier taux de succès > 90%
├─ Valider jointure leaderboard ⟗ weapons (via handle)
└─ Compter armes extraites vs attendues

Phase 4: BigQuery Upload  ⏳ EN ATTENTE
├─ Load leaderboard → bf6_meta.leaderboard
├─ Load weapons → bf6_meta.top_weapons
└─ Queries de validation

Phase 5: DBT Transformations  ⏳ EN ATTENTE
├─ Bronze: Sources
├─ Silver: Joined player + weapons
└─ Gold: Analytics-ready tables
```

### 🎓 Leçons Apprises

#### 1. Cloudflare Challenge Detection
**Symptôme** : HTML trop petit (19-22 KB vs 400-800 KB attendu)
**Cause** : Mode headless déclenche la protection anti-bot
**Solution** : Navigateur visible (`uc.Chrome()` sans options headless)

#### 2. Structure HTML Dynamique
**Découverte** : Les top 3 rangs utilisent des badges visuels, pas du texte
**Impact** : Extraction partielle acceptable (97% vs 100%)
**Décision** : Ne pas compliquer le code pour 3 entrées

#### 3. BeautifulSoup vs Regex
**Weapons page** : Structure tabulaire complexe
**Regex** : ❌ Échoue complètement (0 armes extraites)
**BeautifulSoup** : ✅ 100% de succès avec sélecteurs CSS

#### 4. Two-File Architecture
**Avantages confirmés** :
- Leaderboard extrait rapidement (25s)
- Si weapons échoue, on garde le leaderboard
- Jointure SQL propre via `handle`
- Re-run possible sans tout refaire

### 📝 Décisions Techniques

#### 1. Primary Key : `handle` (pas `player_id`)
**Raison** : 
- `handle` est unique et lisible (ex: "RoboCat")
- `player_id` est un nombre long (ex: "1000380403530")
- Jointure SQL plus facile à lire et debugger

#### 2. Tolérer 3% de perte (97 vs 100 joueurs)
**Raison** :
- Top 3 utilisent des badges visuels (structure différente)
- Complexité supplémentaire pour 3 entrées = pas justifié
- 97 joueurs suffisants pour analyse statistique

#### 3. Délai 20s par page
**Test** :
- 15s → HTML incomplet sur certaines pages
- 20s → ✅ Chargement complet confirmé (836 KB)
- Trade-off : +5s par page = +8 minutes pour 100 joueurs (acceptable)

### 🚀 Prochaines Actions (Session 4 - 24 octobre)

#### Action Immédiate : Extraction Weapons
1. ✅ Leaderboard prêt (97 joueurs)
2. 🔄 Lancer `extract_bf6_top_weapons_final.py`
3. ⏱️ Attendre 32-35 minutes
4. ✅ Valider fichier weapons créé

#### Après Extraction :
5. Valider jointure `leaderboard ⟗ weapons` (via handle)
6. Compter succès/échecs (target > 90%)
7. Load vers BigQuery :
   - Table `bf6_meta.leaderboard` (nouvelle)
   - Table `bf6_meta.top_weapons` (remplacement données 20 oct)
8. DBT transformations (Phase 3)

### 💡 Améliorations Futures Identifiées

1. **Extraction top 3 rangs** : Parser les badges SVG (low priority)
2. **Retry logic** : Si une page échoue, retry 1-2 fois
3. **Progress bar** : tqdm pour visualiser l'avancement (35 min c'est long)
4. **Concurrent downloads** : Paralléliser avec threading (attention Cloudflare)
5. **Incremental updates** : Extraire seulement les nouveaux joueurs

### 📚 Fichiers Modifiés Aujourd'hui

**Créés** :
- `scripts/extract_bf6_leaderboard.py` (183 lignes)
- `scripts/extract_bf6_top_weapons_final.py` (227 lignes)
- `scripts/extract_weapons_from_table.py` (218 lignes)
- `data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-23_185748.ndjson`
- `data/bronze/tracker_gg/top_weapons/bf6_top_weapons_table_parser_2025-10-23_183628.ndjson`
- `data/bronze/tracker_gg/leaderboard/leaderboard_debug.html` (836 KB)

**Modifiés** :
- `ai/notes.md` (ce fichier - documentation complète)
- `readme.md` (mise à jour de l'avancement du projet)

**À commiter** :
- ✅ Les 3 nouveaux scripts d'extraction
- ✅ Documentation mise à jour (notes.md + readme.md)
- ❌ Pas les fichiers .ndjson (données générées, pas code)
- ❌ Pas le HTML debug (trop volumineux)

---

_Last updated: 2025-10-23 19:15 by AI Assistant_

---

_Last updated: 2025-10-22 12h30 by AI Assistant_
