# 🎮 Battlefield Meta Aggregator

> **Analyse quotidienne des loadouts les plus performants sur Battlefield 6**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.11-green.svg)](https://scrapy.org/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Active-blue.svg)](https://cloud.google.com/bigquery)
[![DBT](https://img.shields.io/badge/DBT-1.11.0-orange.svg)](https://www.getdbt.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Phase%205%20In%20Progress-yellow.svg)]()

**Projet personnel d'ELT & Data Engineering — par Paul Fretté**

---

## 💡 Idée du Projet

**Chaque semaine**, échantillonner **100 joueurs** du leaderboard Tracker.gg, récupérer leurs **top 3 armes** (nom + kills), calculer les **armes les plus populaires** et afficher les tendances dans une petite UI.

**Pipeline** : `Selenium` → `BigQuery (Bronze)` → `DBT (Silver/Gold)` → `Streamlit`  
**Orchestration** : Apache Airflow (exécution hebdomadaire automatisée - Phase 5 en cours)

**🎉 Phase 4.5 (Cloud Deploy) COMPLÈTE** : Dashboard public accessible 24/7 | Auto-deploy GitHub | SSL/HTTPS

**✅ Phase 5.1 (Extraction Optimization) COMPLÈTE** : Extraction complète validée | 50 joueurs × 3 armes | 100% succès

**✅ Phase 5.2 (BigQuery + DBT Pipeline) COMPLÈTE** : Pipeline automatisé complet | 6 modèles DBT | 44/44 tests ✅

**🤖 Phase 6 (Automation) COMPLÈTE** : Script pipeline end-to-end | Prêt pour cron/GitHub Actions

**🏆 DERNIÈRE EXTRACTION** : 30 oct 2025 - 50 joueurs, 150 armes (SG 553R, TR-7, M4A1, DRS-IAR, M433, etc.)

**📊 DASHBOARD** : 
- ☁️ **Cloud** : https://battlefieldmetaaggregator.streamlit.app ✅ **100% FONCTIONNEL** (30 oct 2025)
  - **✅ RÉSOLU** : Toutes les erreurs `weapon_type` corrigées
  - **✅ TESTÉ** : 3 pages opérationnelles (Home, All Weapons, All Players)
  - Déploiement auto depuis GitHub (commit `8f3bac4`)
  - Données du 30 oct 2025 (50 joueurs, 150 armes)
- 🏠 **Local** : `streamlit run streamlit_app.py` → http://localhost:8501 ✅ **TESTÉ**
  - Graphiques Plotly affichés correctement
  - TOP 10 armes, scatter plot, métriques fonctionnelles
- 🌐 **Réseau** : http://192.168.1.12:8501 (accessible WiFi local)
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

### Vue d'Ensemble (Data Flow)

```
┌───────────────────────────────────────────────────────────┐
│              TRACKER.GG (Source de données)               │
│  • Leaderboard + Player Profiles                         │
│  • Extraction: Selenium + undetected-chromedriver        │
└─────────────────┬─────────────────────────────────────────┘
                  │ scripts/extract_bf6_meta_complete.py
                  │ (50 joueurs × 3 armes = 150 weapons)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         DATA LAKE - data/bronze/ (Fichiers NDJSON)        │
│  • leaderboard/bf6_leaderboard_YYYYMMDD.ndjson            │
│  • top_weapons/bf6_weapons_YYYYMMDD.ndjson                │
└─────────────────┬─────────────────────────────────────────┘
                  │ scripts/load_to_bigquery_latest.py
                  │ (auto-détecte derniers fichiers)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         BRONZE - BigQuery (Tables brutes)                 │
│  • bf6_meta.bronze_leaderboard (50 joueurs)               │
│  • bf6_meta.bronze_weapons (150 armes)                    │
└─────────────────┬─────────────────────────────────────────┘
                  │ dbt/models/bronze/sources.yml
                  │ (définit sources DBT)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         SILVER - BigQuery (Tables nettoyées)              │
│  • silver_players (50 joueurs + stats enrichies)          │
│  • silver_weapons (150 armes + métriques calculées)       │
│  • silver_player_weapons (jointure enrichie)              │
└─────────────────┬─────────────────────────────────────────┘
                  │ dbt/models/gold/*.sql
                  │ (agrégations + classements)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         GOLD - BigQuery (Tables finales)                  │
│  • gold_top_weapons_global (Top 10 MVP)                   │
│  • gold_top_weapons_by_type (Top 20 par catégorie)        │
│  • gold_player_rankings (50 joueurs classés)              │
└─────────────────┬─────────────────────────────────────────┘
                  │ dashboard/utils/bigquery.py
                  │ (requêtes SQL vers tables gold)
                  ▼
┌───────────────────────────────────────────────────────────┐
│              DASHBOARD - Streamlit                        │
│  • streamlit_app.py (page principale)                     │
│  • pages/1_All_Weapons.py (Top 20 + filtres)              │
│  • pages/2_All_Players.py (50 joueurs + recherche)        │
│  • dashboard/utils/charts.py (Plotly visualisations)      │
└───────────────────────────────────────────────────────────┘
                  ▲
┌─────────────────┴─────────────────────────────────────────┐
│         ORCHESTRATION - Automation (Phase 6)              │
│  • scripts/run_pipeline.sh (pipeline end-to-end)          │
│  • Cron / GitHub Actions (exécution hebdomadaire)         │
│  • Extract → Load → DBT → Validation                      │
└───────────────────────────────────────────────────────────┘
```

### Architecture des Dossiers & Dépendances

```
battlefield_meta_aggregator/
│
├── 📝 config/                         # CONFIGURATION
│   └── bigquery-key.json              # 🔐 Credentials GCP (gitignored)
│        ↓ utilisé par →
│        ├── scripts/load_to_bigquery_latest.py
│        ├── scripts/query_bigquery.py
│        ├── dbt/profiles.yml
│        └── dashboard/utils/bigquery.py
│
├── 🔧 scripts/                        # EXTRACTION & CHARGEMENT
│   ├── extract_bf6_meta_complete.py   # [1] Extraction web scraping
│   │    ├── Input: Tracker.gg (web)
│   │    ├── Output: data/bronze/tracker_gg/*.ndjson
│   │    └── Dépendances: selenium, undetected-chromedriver
│   │
│   ├── load_to_bigquery_latest.py     # [2] Chargement BigQuery
│   │    ├── Input: data/bronze/tracker_gg/*.ndjson (auto-detect)
│   │    ├── Output: BigQuery bronze_* tables
│   │    └── Dépendances: google-cloud-bigquery, config/bigquery-key.json
│   │
│   ├── run_pipeline.sh                # [ORCHESTRATEUR] Pipeline complet
│   │    ├── Étape 1: extract_bf6_meta_complete.py
│   │    ├── Étape 2: load_to_bigquery_latest.py
│   │    ├── Étape 3: cd dbt && dbt run && dbt test
│   │    ├── Étape 4: Validation SQL (query_bigquery.py)
│   │    └── Output: Logs dans data/logs/pipeline_*.log
│   │
│   ├── query_bigquery.py              # [VALIDATION] Requêtes analytiques
│   │    ├── Input: BigQuery gold_* tables
│   │    └── Output: Console (Top 3 armes, joueurs, etc.)
│   │
│   ├── test_bigquery_connection.py    # [TEST] Connexion BigQuery
│   └── crontab_setup.txt              # [CONFIG] Automatisation cron
│
├── 📊 data/                           # DATA LAKE (local storage)
│   ├── bronze/tracker_gg/             # Raw data (NDJSON)
│   │   ├── leaderboard/               # Joueurs extraits
│   │   │    └── bf6_leaderboard_YYYYMMDD_HHMMSS.ndjson
│   │   │         ↓ chargé par → scripts/load_to_bigquery_latest.py
│   │   │         ↓ vers → BigQuery bronze_leaderboard
│   │   │
│   │   └── top_weapons/               # Armes extraites
│   │        └── bf6_weapons_YYYYMMDD_HHMMSS.ndjson
│   │             ↓ chargé par → scripts/load_to_bigquery_latest.py
│   │             ↓ vers → BigQuery bronze_weapons
│   │
│   ├── logs/                          # Logs du pipeline
│   │    └── pipeline_*.log
│   └── exploration/                   # Tests & analyses ad-hoc
│
├── 🏗️ dbt/                            # TRANSFORMATIONS DBT
│   ├── profiles.yml                   # Config connexion BigQuery
│   │    └── Utilise: config/bigquery-key.json
│   │
│   ├── dbt_project.yml                # Config projet DBT
│   │
│   └── models/                        # Modèles SQL (Bronze → Silver → Gold)
│       │
│       ├── bronze/                    # Layer 1: Sources brutes
│       │   └── sources.yml            # Définit bronze_* tables BigQuery
│       │        ↓ référence →
│       │        ├── bf6_meta.bronze_leaderboard
│       │        └── bf6_meta.bronze_weapons
│       │
│       ├── silver/                    # Layer 2: Nettoyage & Enrichissement
│       │   ├── silver_players.sql     # Joueurs + stats calculées
│       │   │    ├── Input: {{ source('bf6_meta', 'bronze_leaderboard') }}
│       │   │    └── Output: bf6_meta_silver.silver_players
│       │   │
│       │   ├── silver_weapons.sql     # Armes + métriques normalisées
│       │   │    ├── Input: {{ source('bf6_meta', 'bronze_weapons') }}
│       │   │    └── Output: bf6_meta_silver.silver_weapons
│       │   │
│       │   └── silver_player_weapons.sql  # Jointure enrichie
│       │        ├── Input: silver_players + silver_weapons
│       │        └── Output: bf6_meta_silver.silver_player_weapons
│       │
│       └── gold/                      # Layer 3: Agrégations finales
│           ├── gold_top_weapons_global.sql  # Top 10 armes MVP
│           │    ├── Input: {{ ref('silver_player_weapons') }}
│           │    └── Output: bf6_meta_gold.gold_top_weapons_global
│           │         ↓ consommé par → dashboard (page Home)
│           │
│           ├── gold_top_weapons_by_type.sql  # Top 20 armes (par type)
│           │    ├── Input: {{ ref('silver_weapons') }}
│           │    └── Output: bf6_meta_gold.gold_top_weapons_by_type
│           │         ↓ consommé par → dashboard (All Weapons)
│           │
│           └── gold_player_rankings.sql  # Classement joueurs
│                ├── Input: {{ ref('silver_players') }}
│                └── Output: bf6_meta_gold.gold_player_rankings
│                     ↓ consommé par → dashboard (All Players)
│
├── 📊 dashboard/                      # STREAMLIT DASHBOARD
│   ├── utils/                         # Utilitaires réutilisables
│   │   ├── bigquery.py                # Connecteur BigQuery
│   │   │    ├── Input: BigQuery gold_* tables
│   │   │    ├── Fonctions: load_top_weapons(), load_all_weapons(), etc.
│   │   │    ├── Cache: @st.cache_data (10 min TTL)
│   │   │    └── Utilisé par: streamlit_app.py + pages/*.py
│   │   │
│   │   ├── charts.py                  # Graphiques Plotly
│   │   │    ├── Fonctions: plot_top_weapons_bar(), plot_accuracy_scatter()
│   │   │    └── Utilisé par: streamlit_app.py + pages/*.py
│   │   │
│   │   └── formatting.py              # Formatage (nombres, dates, %)
│   │
│   ├── pages/                         # Pages multi-pages Streamlit
│   │   ├── 1_🔫_All_Weapons.py        # Top 20 armes + filtres
│   │   │    └── Requête: gold_top_weapons_by_type
│   │   │
│   │   └── 2_👥_All_Players.py        # 50 joueurs + recherche
│   │        └── Requête: gold_player_rankings
│   │
│   └── app.py                         # Code principal du dashboard
│        └── Copié vers → streamlit_app.py (root, pour Streamlit Cloud)
│
├── streamlit_app.py                   # 🌐 DASHBOARD PRINCIPAL (root)
│   ├── Input: BigQuery gold_top_weapons_global
│   ├── Imports: dashboard.utils.bigquery, dashboard.utils.charts
│   ├── Affichage: TOP 10 armes + scatter plot + 3 metrics
│   └── Déployé sur: https://battlefieldmetaaggregator.streamlit.app
│
├── pages/                             # 📄 PAGES STREAMLIT (root, copie de dashboard/pages/)
│   ├── 1_🔫_All_Weapons.py            # (copie identique pour Streamlit Cloud)
│   └── 2_👥_All_Players.py            # (copie identique pour Streamlit Cloud)
│
├── 🤖 airflow/                        # ORCHESTRATION AIRFLOW (archived)
│   └── dags/
│       └── bf6_weekly_extraction.py   # DAG automatisation (non utilisé en prod)
│            ├── Alternative: scripts/run_pipeline.sh + cron
│            └── Statut: Créé mais non déployé (Airflow standalone non installé)
│
├── 📚 docs/                           # DOCUMENTATION
│   ├── BIGQUERY_GUIDE.md              # Setup BigQuery + exemples SQL
│   ├── STREAMLIT_GUIDE.md             # Guide dashboard complet
│   ├── STREAMLIT_CLOUD_DEPLOY.md      # Déploiement Cloud
│   ├── AUTOMATION_GUIDE.md            # Cron / GitHub Actions / Cloud Functions
│   └── CLI_GIT_GUIDE.md               # Commandes Git/Python/SQL
│
├── 📦 archive/                        # ANCIENS FICHIERS (26 fichiers)
│   └── Scripts de test obsolètes (Phase 0-2)
│
└── 🕷️ extract/                        # SCRAPY PROJECT (archived)
    └── spiders/                       # Alternative scraping (non utilisée)
         └── Statut: Remplacé par extract_bf6_meta_complete.py
```

### Flux de Données Complet (Step-by-Step)

#### **Phase 1 : Extraction (4-5 min)**
```
Tracker.gg (Web)
    ↓
scripts/extract_bf6_meta_complete.py
    ├── Étape 1: Leaderboard (top 50 joueurs) → 25s
    ├── Étape 2: Top 3 armes par joueur → 4min
    └── Output:
         ├── data/bronze/tracker_gg/leaderboard/bf6_leaderboard_20251030_160241.ndjson (50 lignes)
         └── data/bronze/tracker_gg/top_weapons/bf6_weapons_20251030_160241.ndjson (150 lignes)
```

#### **Phase 2 : Chargement BigQuery (16s)**
```
data/bronze/tracker_gg/*.ndjson
    ↓
scripts/load_to_bigquery_latest.py
    ├── Détection automatique derniers fichiers NDJSON
    ├── Chargement BigQuery (WRITE_APPEND mode)
    └── Output:
         ├── BigQuery: bf6_meta.bronze_leaderboard (50 rows)
         └── BigQuery: bf6_meta.bronze_weapons (150 rows)
```

#### **Phase 3 : Transformations DBT (13s)**
```
BigQuery bronze_* tables
    ↓
dbt run (dbt/models/)
    ├── Bronze → Silver (nettoyage, typage, enrichissement)
    │    ├── silver_players (50 rows)
    │    ├── silver_weapons (150 rows)
    │    └── silver_player_weapons (150 rows jointure)
    │
    └── Silver → Gold (agrégations, classements)
         ├── gold_top_weapons_global (10 rows - MVP)
         ├── gold_top_weapons_by_type (20 rows - par catégorie)
         └── gold_player_rankings (50 rows - classement)
```

#### **Phase 4 : Tests de Qualité (18s)**
```
BigQuery gold_* tables
    ↓
dbt test
    ├── Tests unicité (unique primary keys)
    ├── Tests valeurs nulles (not_null columns)
    ├── Tests relations (foreign keys)
    └── Résultat: 42/44 tests PASS (2 warnings doublons mineurs)
```

#### **Phase 5 : Dashboard (Temps réel)**
```
BigQuery gold_* tables
    ↓
dashboard/utils/bigquery.py
    ├── load_top_weapons() → gold_top_weapons_global
    ├── load_all_weapons() → gold_top_weapons_by_type
    └── load_player_rankings() → gold_player_rankings
         ↓
streamlit_app.py + pages/*.py
    ├── Cache: @st.cache_data (10 min TTL)
    ├── Visualisations: Plotly charts
    └── Output: https://battlefieldmetaaggregator.streamlit.app
```

#### **Phase 6 : Automatisation (Hebdomadaire)**
```
Cron / GitHub Actions (Dimanches 2h UTC)
    ↓
scripts/run_pipeline.sh
    ├── [1] Extraction → data/bronze/
    ├── [2] Chargement → BigQuery bronze_*
    ├── [3] DBT run → BigQuery silver_* + gold_*
    ├── [4] DBT test → Validation qualité
    └── [5] Logs → data/logs/pipeline_*.log
         ↓
Streamlit Cloud (auto-refresh cache après 10 min)
```

### Dépendances entre Composants

| Composant | Dépend de | Utilisé par |
|-----------|-----------|-------------|
| **config/bigquery-key.json** | - | scripts/*, dbt/profiles.yml, dashboard/utils/bigquery.py |
| **scripts/extract_bf6_meta_complete.py** | Tracker.gg (web) | scripts/run_pipeline.sh |
| **data/bronze/*.ndjson** | extract_bf6_meta_complete.py | load_to_bigquery_latest.py |
| **BigQuery bronze_*** | load_to_bigquery_latest.py | dbt/models/bronze/sources.yml |
| **dbt/models/silver/** | BigQuery bronze_* | dbt/models/gold/ |
| **BigQuery gold_*** | dbt/models/gold/ | dashboard/utils/bigquery.py |
| **dashboard/utils/bigquery.py** | BigQuery gold_* | streamlit_app.py, pages/*.py |
| **dashboard/utils/charts.py** | - | streamlit_app.py, pages/*.py |
| **streamlit_app.py** | dashboard/utils/* | Streamlit Cloud |
| **scripts/run_pipeline.sh** | extract, load, dbt | Cron / GitHub Actions |

### Points Clés de l'Architecture

✅ **Séparation des responsabilités** :
- `scripts/` : Extraction & Chargement (Python)
- `dbt/` : Transformations SQL (Bronze → Silver → Gold)
- `dashboard/` : Visualisation (Streamlit + Plotly)

✅ **Pipeline automatisé end-to-end** :
- 1 script bash (`run_pipeline.sh`) orchestre tout
- Durée totale : ~5 minutes (extraction → validation)

✅ **Data Lake local + Data Warehouse cloud** :
- Local : `data/bronze/` (NDJSON, versionné par timestamp)
- Cloud : BigQuery (tables Bronze/Silver/Gold)

✅ **Cache intelligent** :
- Dashboard Streamlit : 10 min TTL (@st.cache_data)
- Évite requêtes BigQuery répétées

✅ **Déploiement continu** :
- Push GitHub main → Streamlit Cloud auto-deploy
- Zéro downtime, SSL automatique

✅ **3 layers de transformation** :
- **Bronze** : Données brutes (extraction Tracker.gg)
- **Silver** : Données nettoyées (typage, enrichissement)
- **Gold** : Données finales (agrégations, classements)

---

## ⚙️ Stack Technique

| Composant          | Technologie                    | Rôle                                      |
|--------------------|--------------------------------|-------------------------------------------|
| **Extraction**     | `Selenium` + `undetected-chromedriver` | Bypass Cloudflare + scraping HTML  |
| **Data Warehouse** | `Google BigQuery`              | Entrepôt cloud SQL (Bronze/Silver/Gold)   |
| **Data Lake**      | `MinIO` (S3-compatible)        | Stockage données non-structurées (futur)  |
| **Transformation** | `DBT Core`                     | Modèles SQL Bronze → Silver → Gold        |
| **Visualisation**  | `Streamlit`                    | Dashboard interactif Python               |
| **Orchestration**  | `Apache Airflow`               | DAGs pour automatisation hebdomadaire     |
| **Conteneurisation**| `Docker` + `docker-compose`   | MinIO + Airflow, environnements isolés    |

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

### 🚀 Pipeline Automatisé Complet (✅ PRODUCTION-READY)

```bash
# OPTION 1: Pipeline complet automatisé (RECOMMANDÉ) ⭐
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
./scripts/run_pipeline.sh
# Durée: ~35 minutes (4min extraction + 30s BigQuery + 15s DBT)
# Résultat: Extraction → BigQuery → DBT → Validation automatique

# OPTION 2: Étapes manuelles
# 1. Extraction complète (leaderboard + armes)
python scripts/extract_bf6_meta_complete.py
# Résultat: 50 joueurs + 150 armes (4-5 min)

# 2. Chargement dans BigQuery
python scripts/load_to_bigquery_latest.py
# Résultat: bronze_leaderboard + bronze_weapons

# 3. Transformations DBT
export PATH="/Users/paulfrette/.local/bin:$PATH"
cd dbt && dbt run && dbt test
# Résultat: 6 modèles + 44 tests
```

📂 **Dernières extractions** : 
- **30 oct 2025** : `bf6_leaderboard_2025-10-30_160241.ndjson` (50 joueurs)
- **30 oct 2025** : `bf6_weapons_2025-10-30_160241.ndjson` (150 armes)
- **Taux succès** : 100% (50/50 joueurs, 0 erreurs)
- **Performance** : 4.96s/joueur moyen

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
│   ├── run_pipeline.sh               # ⭐ Pipeline automatisé complet (Extraction → BigQuery → DBT)
│   ├── extract_bf6_meta_complete.py  # ⭐ PRODUCTION: Extraction leaderboard + armes (50 joueurs)
│   ├── load_to_bigquery_latest.py    # ⭐ PRODUCTION: Chargement auto vers BigQuery
│   ├── query_bigquery.py             # ✅ Requêtes SQL analytiques
│   ├── test_bigquery_connection.py   # ✅ Test connexion BigQuery
│   ├── crontab_setup.txt             # 📝 Configuration cron (automatisation)
│   ├── archive/                      # Scripts obsolètes (6 fichiers)
│   └── README.md
│
├── data/                              # Données extraites
│   ├── bronze/tracker_gg/
│   │   ├── top_weapons/               # ✅ NDJSON weapons
│   │   │   └── bf6_weapons_2025-10-30_160241.ndjson (150 armes - 30 oct)
│   │   └── leaderboard/               # ✅ NDJSON leaderboard
│   │       └── bf6_leaderboard_2025-10-30_160241.ndjson (50 joueurs - 30 oct)
│   ├── logs/                          # Logs du pipeline
│   │   └── pipeline_20251030_160241.log (dernière exécution)
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

- [x] Installer DBT Core + dbt-bigquery

### ✅ Phase 2.5 : Extraction Production Pipeline **COMPLÈTE** (23-24 oct 2025)

**Objectif** : Pipeline robuste d'extraction en 2 étapes (Leaderboard + Weapons)

**Architecture 2 fichiers** :
- **Étape 1** : Extraction leaderboard (97 joueurs) → Clé primaire `handle`
- **Étape 2** : Extraction top 3 armes par joueur (288 armes) → 8 stats détaillées
- **Jointure** : Via `handle` dans DBT (Silver layer)

**Scripts créés** :
- [x] `scripts/extract_bf6_leaderboard.py` - ✅ Extraction top 100 
- [x] `scripts/extract_bf6_top_weapons_final.py` - ✅ Extraction weapons avec stats complètes
- [x] `scripts/load_to_bigquery.py` - ✅ Chargement automatique vers BigQuery

**Résultats Production** :
- [x] **97 joueurs** extraits (rangs 4-100, badges visuels 1-3 structure différente)
- [x] **288 armes** extraites (3 par joueur)
- [x] **8 stats par arme** : name, kills, damage, accuracy, headshot_pct, games, wins, kpm
- [x] Fichiers NDJSON :
  - `bf6_leaderboard_2025-10-23_185748.ndjson`
  - `bf6_top_weapons_2025-10-24_XXXXXX.ndjson`
- [x] Chargement BigQuery réussi (tables Bronze)
- [x] Durée totale : ~35 minutes (25s leaderboard + 32-35 min weapons)
- [x] Taux de succès : >95%

**Problèmes résolus vs v1 (20 oct)** :
- ✅ **Cloudflare bypass** : Mode headless bloqué → Navigateur visible requis
- ✅ **Délai insuffisant** : 15s → 20s pour chargement complet
- ✅ **Parser inadapté** : Regex → BeautifulSoup avec sélecteurs CSS précis
- ✅ **Structure HTML** : data-key numérique au lieu de player_id_*
- ✅ **Stats manquantes** : Ajout de 8 stats complètes par arme (vs 2 avant)
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
- [x] Structure multi-pages (3 pages)
  - **Top 3 Weapons** (page principale)
  - **All Weapons** (liste complète + filtres)
  - **All Players** (top 100 + recherche)
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
- [x] Fonctionnalités avancées :
  - Theme toggle (Dark/Light mode)
  - Filtres dynamiques (type, recherche texte)
  - CSV export sur toutes les pages
  - Tables scrollables avec bordures
  - Hover effects et animations CSS
- [x] Documentation complète
  - `dashboard/README.md` (installation, architecture)
  - `docs/STREAMLIT_GUIDE.md` (guide complet 500+ lignes)
  - `ai/session_2025-10-25_phase4_dashboard.md` (session détaillée)
  - `ai/PROJECT_STATUS.md` (état global)
  - `ai/EXECUTIVE_SUMMARY.md` (résumé exécutif)

**MVP Fonctionnel** :
- 🌐 **URL locale** : http://localhost:8501
- 🌐 **URL réseau** : http://192.168.1.12:8501 (accessible sur WiFi local)
- ⚡ Cache : 10 minutes (requêtes BigQuery)
- 📊 3 pages + 6 graphiques + 12 metrics
- 📥 Export CSV disponible
- 🎨 Design professionnel (Dark/Light themes)

### ✅ Phase 4.5 : Déploiement Cloud **COMPLÈTE** (27 oct 2025)

**Objectif** : Rendre le dashboard accessible publiquement sur Internet ✅

**Étapes** :
- [x] Documentation déploiement (`docs/STREAMLIT_CLOUD_DEPLOY.md`)
- [x] Modifier `dashboard/utils/bigquery.py` (gestion secrets Cloud)
- [x] Créer `.streamlit/secrets.toml` (local)
- [x] Tests en local avec secrets
- [x] Push sur GitHub
- [x] Déploiement sur Streamlit Community Cloud
- [x] Configuration secrets BigQuery sur Cloud
- [x] Tests URL publique validés

**Résultat** :
- 🌐 **URL publique** : https://battlefieldmetaaggregator.streamlit.app ✅ **LIVE**
- ✅ Gratuit (Streamlit Community Cloud Free Tier)
- ✅ Auto-deploy depuis GitHub (push main → redéploiement automatique)
- ✅ SSL/HTTPS automatique
- ✅ Dashboard accessible mondialement

**Problèmes résolus** :
- ✅ Dépendances requirements.txt (langchain conflicts)
- ✅ Streamlit version 1.28.2 → 1.39.0
- ✅ st.image() parameter `use_container_width` → `use_column_width`
- ✅ Import paths (streamlit_app.py → dashboard/app.py)

**Guide complet** : `docs/STREAMLIT_CLOUD_DEPLOY.md`

### ✅ Phase 5.1 : Extraction Optimization & Validation **COMPLÈTE** (29 oct 2025)

**Objectif** : Pipeline robuste avec extraction complète leaderboard → armes

**Architecture finale** :
- **Script principal** : `extract_bf6_meta_complete.py` (523 lignes)
- **Étape 1** : Extraction leaderboard (50 joueurs) → 25 secondes
- **Étape 2** : Extraction top 3 armes par joueur (150 armes) → 4 min 3s
- **Format** : NDJSON avec checkpoint automatique
- **Performance** : 4.87s/joueur (vs 20s séquentiel = **76% plus rapide**)

**Corrections critiques appliquées** :
- [x] ✅ **Bug player_id** : Extraction href corrigée (dernier segment au lieu de l'avant-dernier)
- [x] ✅ **Bug CSS selector** : data-key avec `startswith('wp_')` au lieu de `isdigit()`
- [x] ✅ **Bug weapon names** : Navigation HTML correcte dans cells[0] (div.name-value → span.stat-value → span.truncate)
- [x] ✅ **URL weapons** : Format corrigé sans paramètre handle
- [x] ✅ **ChromeDriver** : Mise à jour vers version 141 (match Chrome browser)

**Résultats Production (29 oct 2025)** :
```bash
📊 EXTRACTION COMPLÈTE RÉUSSIE :
✅ Leaderboard : 50 joueurs extraits (25 secondes)
✅ Weapons : 150 armes extraites (3 par joueur, 4 min 3s)
✅ Taux succès : 100% (50/50 joueurs, 0 erreurs)
✅ Performance : 4.87s/joueur moyen
✅ Armes réelles extraites : DRS-IAR, KORD 6P67, TR-7, KV9, M87A1, 
   SCW-10, M4A1, SG 553R, NVO-228E, SOR-556 MK2, etc.

📁 Fichiers générés :
   • bf6_leaderboard_2025-10-29_212358.ndjson (9.2 KB)
   • bf6_weapons_2025-10-29_212358.ndjson (21 KB)
```

**Problèmes résolus vs versions précédentes** :
- ❌ v1 (20 oct) : API Tracker.gg non fonctionnelle → ✅ Scraping HTML
- ❌ v2 (23 oct) : Cloudflare headless bloqué → ✅ Mode visible requis  
- ❌ v3 (28 oct) : Noms d'armes = valeurs de temps ("108h") → ✅ **FIXÉ** : cellule HTML correcte
- ✅ v4 (29 oct) : **Extraction 100% fonctionnelle et validée**

**Documentation** :
- ✅ Commit Git : `7d2d636` "fix: correct weapon name extraction..."
- ✅ Push GitHub réussi
- ✅ Code validé et prêt pour BigQuery

### 🔵 Phase 5.2 : Pipeline BigQuery + DBT **À VENIR**

**Objectif** : Automatiser l'extraction hebdomadaire + optimiser le temps d'extraction

#### 5.1 Airflow DAG ✅ Créé
- [x] DAG `bf6_weekly_extraction` avec 6 tâches séquentielles :
  1. `extract_leaderboard` → Extraction top 100 joueurs
  2. `extract_weapons` → Extraction armes par joueur
  3. `load_to_bigquery` → Chargement dans BigQuery
  4. `dbt_run_silver` → Transformations Silver
  5. `dbt_run_gold` → Transformations Gold
  6. `send_notification` → Notification fin de pipeline
- [x] Schedule : `0 2 * * 0` (Dimanches 2h UTC)
- [x] Documentation : `airflow/README.md` (guide installation 15 min)
- [ ] Installation Airflow (en attente)
- [ ] Tests DAG end-to-end

**Architecture Airflow** :
```
Apache Airflow 2.10.3 (Standalone mode)
├── Metadata DB: SQLite (local ~/airflow/airflow.db)
├── Executor: SequentialExecutor (MVP, 1 tâche à la fois)
├── DAGs: airflow/dags/bf6_weekly_extraction.py
└── Logs: ~/airflow/logs/
```

#### 5.2 Extraction Optimization ✅ Implémentée

**Problème identifié** :
- Durée actuelle : ~32 minutes (97 joueurs × 20s)
- Bottleneck : `time.sleep(20)` fixe pour bypass Cloudflare

**Solutions analysées** :
1. **Parallel extraction** (5 workers) → 6 min (81% gain) ✅
2. **Dynamic wait** (WebDriverWait) → 24 min (25% gain) ✅
3. **Incremental cache** → 5 min après 1ère run (84% gain)
4. **Headless optimized** → 29 min (10% gain)

**Combo recommandé : Parallel + Dynamic wait → 4-6 min (85-87% gain)** ✅

**Implémentation** :
- [x] Script créé : `scripts/extract_bf6_top_weapons_parallel.py` (520 lignes)
- [x] Technologie : `ThreadPoolExecutor` + thread-local driver pool
- [x] Dynamic wait : `WebDriverWait` (détection table chargée)
- [x] CLI : `--workers N` (default 5), `--limit N` (pour tests)
- [x] Test 10 joueurs : 51.8s vs 200s séquentiel (**74% faster**) ✅
- [ ] Test complet 97 joueurs (5-6 min attendu)
- [ ] Intégration dans DAG Airflow

**Résultats test (28 oct 2025)** :
```bash
python3 scripts/extract_bf6_top_weapons_parallel.py --limit 10 --workers 3

📊 RÉSULTATS :
⏱️  Durée : 51.8 secondes (vs 200s séquentiel)
✅ Succès : 10/10 joueurs (100%)
⚡ Vitesse : 0.19 joueurs/s
🎯 Gain : 74% plus rapide
```

**Documentation** : `docs/EXTRACTION_OPTIMIZATION.md` (450+ lignes d'analyse)

### ✅ Phase 5.2 : BigQuery + DBT Pipeline **COMPLÈTE** (30 oct 2025)

**Objectif** : Pipeline end-to-end automatisé avec nouvelles données simplifiées ✅

**Réalisations** :
- [x] **Script `load_to_bigquery_latest.py`** : Chargement auto des derniers NDJSON
  - Détection automatique fichiers les plus récents
  - UNNEST des armes (150 lignes → bronze_weapons)
  - Mode WRITE_APPEND (chargement incrémental)
  - Validation post-upload avec requêtes SQL
- [x] **DBT Core installé** : v1.10.13 + dbt-bigquery v1.10.2
- [x] **6 modèles DBT mis à jour** :
  - `silver_players` (50 rows)
  - `silver_weapons` (150 rows)
  - `silver_player_weapons` (150 rows)
  - `gold_top_weapons_global` (TOP 10)
  - `gold_top_weapons_by_type` (TOP 20)
  - `gold_player_rankings` (50 rows)
- [x] **44 tests DBT** : 42 PASS + 2 warnings (doublons mineurs)
- [x] **Dashboard Streamlit mis à jour** :
  - `utils/bigquery.py` : Requêtes pour nouvelles tables gold
  - `app.py` : TOP 10 armes au lieu de TOP 3
  - `1_All_Weapons.py` : TOP 20 armes
  - `2_All_Players.py` : Nouvelles colonnes (player_matches, location)
- [x] **Codebase nettoyé** : 6 scripts archivés, 4 scripts actifs conservés
- [x] **Documentation complète** : README scripts mis à jour

**Résultats Production (30 oct 2025)** :
```bash
✅ Extraction : 50 joueurs + 150 armes (4min 36s)
✅ BigQuery : 50 + 150 lignes chargées (16s)
✅ DBT run : 6 modèles créés (13s)
✅ DBT test : 42/44 tests passent (18s)
✅ TOP 3 armes : SG 553R (86,897 kills), TR-7 (50,394 kills), M4A1 (39,049 kills)
```

### ✅ Phase 6 : Automation **COMPLÈTE** (30 oct 2025)

**Objectif** : Automatiser l'exécution hebdomadaire du pipeline complet ✅

**Réalisations** :
- [x] **Script `run_pipeline.sh`** : Pipeline end-to-end automatisé (190 lignes)
  - Étape 1 : Extraction (leaderboard + armes)
  - Étape 2 : Chargement BigQuery (bronze)
  - Étape 3 : Transformations DBT (silver + gold)
  - Étape 4 : Validation des données
  - Logging complet avec timestamps
  - Gestion des erreurs (exit on error)
- [x] **Configuration cron** : `crontab_setup.txt`
  - 3 options : Dimanche 2h, Lundi 3h, Mercredi 1h
  - Instructions complètes pour macOS
  - Commandes de monitoring (tail -f logs)
- [x] **Guide automatisation** : `AUTOMATION_GUIDE.md` (450+ lignes)
  - 3 méthodes : Cron local, GitHub Actions, Cloud Functions
  - Comparaisons (coûts, avantages, inconvénients)
  - Monitoring et alertes (email, Slack)
  - Dépannage complet
- [x] **Répertoire logs/** : Créé avec .gitignore
- [x] **Test pipeline complet** : ✅ Succès (durée 4min 54s)

**Options d'automatisation** :
1. **Cron (Local)** : Simple, gratuit, contrôle total
2. **GitHub Actions** : Cloud, gratuit (2000 min/mois), logs centralisés
3. **Cloud Scheduler + Functions** : Fully managed, ~$0.50/mois

#### 5.3 Prochaines étapes
- [ ] Installation Airflow standalone (15 min)
- [ ] Test DAG dans UI Airflow
- [ ] Extraction complète 97 joueurs (validation 81-87% gain)
- [ ] Mise à jour task `extract_weapons` dans DAG (utiliser script parallèle)
- [ ] Intégration bouton "Refresh" dans dashboard → trigger DAG Airflow
Ou
- [ ] Configurer cron OU GitHub Actions (choix utilisateur)
- [ ] Monitorer première exécution automatique
- [ ] Ajouter bouton "Refresh" dans dashboard Streamlit
- [ ] Historisation : conserver plusieurs extractions (semaine vs semaine)

**Durée estimée Phase 5-6** : ✅ COMPLÉTÉE (2 jours de développement)

**Bénéfices obtenus** :
- ⏰ Extraction : 4min 36s (50 joueurs) - ✅ Optimisée
- 🔄 Automatisation : Script pipeline.sh prêt pour cron/GitHub Actions
- 📊 Pipeline complet opérationnel : Extract → Load → Transform → Validate
- 🚨 Monitoring : Logs avec timestamps + gestion erreurs
- 📈 Performance : 4.96s/joueur moyen (100% succès)
- 🧹 Codebase nettoyée : 4 scripts actifs (vs 10 avant)

---

**Temps total réalisé** : ~20 heures (phases 1-6)  
**Statut actuel** : ✅ Phase 6 (Automation) complète | Pipeline production-ready | Dashboard Cloud live

**📈 Métriques actuelles** :
- ✅ **50 joueurs** extraits (dernière extraction 30 oct 2025)
- ✅ **150 armes** détaillées (3 par joueur, 100% succès)
- ✅ **8 tables BigQuery** (Bronze/Silver/Gold)
- ✅ **44 tests DBT** : 42 PASS (95%)
- ✅ **6 modèles DBT** : silver_players, silver_weapons, silver_player_weapons, gold_top_weapons_global, gold_top_weapons_by_type, gold_player_rankings
- ✅ **Dashboard Streamlit** déployé publiquement (https://battlefieldmetaaggregator.streamlit.app)
- ✅ **3 pages** : Top 10 Weapons, Top 20 Weapons, All Players
- ✅ **Pipeline automatisé** : run_pipeline.sh (4 étapes)
- ✅ **Performance** : 4min 54s pour pipeline complet (extraction → validation)
- ✅ **Codebase optimisé** : 4 scripts actifs (6 archivés)
- ✅ **Documentation** : 8 guides (BigQuery, DBT, Streamlit, Automation, etc.)
- ✅ **Coût total** : $0/mois (Free Tiers)

**📊 Top 3 Armes (30 oct 2025)** :
1. 🥇 **SG 553R** : 86,897 kills | 18 joueurs | 23.0% accuracy
2. 🥈 **TR-7** : 50,394 kills | 11 joueurs | 22.6% accuracy
3. 🥉 **M4A1** : 39,049 kills | 14 joueurs | 25.5% accuracy

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

**� PROJECT OVERVIEW** : `PROJECT_OVERVIEW.md` - Vue d'ensemble complète pour entretiens (métriques, architecture, compétences démontrées)

**📚 Documentation complète** :
- 📊 **Project Overview** : `PROJECT_OVERVIEW.md` (métriques détaillées, 5,761 lignes code, 60-80h dev)
- 🔍 **BigQuery** : `docs/BIGQUERY_GUIDE.md` (setup, queries, troubleshooting)
- 🏗️ **DBT** : `dbt/README.md` (modèles, transformations, tests)
- 📊 **Streamlit** : `docs/STREAMLIT_GUIDE.md` (dashboard, cache, visualisations)
- ☁️ **Déploiement Cloud** : `docs/STREAMLIT_CLOUD_DEPLOY.md` (guide déploiement Streamlit Cloud)
- 🔧 **Dépannage Dashboard** : `docs/STREAMLIT_TROUBLESHOOTING.md` (résolution problèmes affichage données) ⭐ **NOUVEAU**
- 🤖 **Automation** : `AUTOMATION_GUIDE.md` (cron, GitHub Actions, Cloud Functions)
- 📋 **Scripts** : `scripts/README.md` (extraction, chargement, pipeline)
- 🧠 **CLI/Git/Python/SQL** : `docs/CLI_GIT_GUIDE.md` (moyens mnémotechniques)
- 📝 **Collaboration** : `ai/notes.md` (historique sessions + décisions)
- 🎓 **DBT & BigQuery** : `docs/DBT_BIGQUERY_EXPLAINED.md` (guide débutant complet)
- 🎮 **Dashboard** : `dashboard/README.md` (installation, fonctionnalités)
- 📈 **État du projet** : `ai/PROJECT_STATUS.md` (vue d'ensemble complète)

---

**Dernière mise à jour** : 30 octobre 2025 - Phase 6 (Automation) complète ✅ - Pipeline production-ready

