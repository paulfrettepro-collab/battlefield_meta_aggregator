# 🎮 Battlefield Meta Aggregator

> **Analyse quotidienne des loadouts les plus performants sur Battlefield 6**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.11-green.svg)](https://scrapy.org/)
[![Status](https://img.shields.io/badge/Status-Phase%200.5-yellow.svg)]()

**Projet personnel d'ELT & Data Engineering — par Paul Fretté**

---

## 💡 Idée du Projet

**Chaque jour**, échantillonner **100 joueurs** du leaderboard Tracker.gg, récupérer leur **loadout par arme**, anonymiser les pseudos, calculer les **combinaisons d'accessoires les plus fréquentes** et afficher un **top 3 par arme** dans une petite UI.

**Pipeline** : `Scrapy` → `MinIO (Bronze, NDJSON)` → `BigQuery` → `DBT (Silver/Gold)` → `Streamlit`  
**Orchestration** : Apache Airflow (exécution quotidienne automatisée)

---

## 🎯 Ce Qu'on Scrape

### 1️⃣ **Leaderboard Players**
- **Champs** : `rank`, `username`, `platform`, `url_profil`
- **Cible** : Page classement par plateforme/mode
- **Méthode** : Sélecteurs CSS/XPath pour lignes de tableau + lien profil

### 2️⃣ **Player Loadouts**
- **Champs** : `weapon`, `attachments` (optic, barrel, magazine, underbarrel, stock…), `timestamp`, `source_url`
- **Cible** : Page profil joueur (onglet stats/loadout)
- **Méthode** : Sélecteurs CSS/XPath ciblant blocs armes et accessoires
- **Bonus** : Si la page charge un JSON via XHR → viser directement l'endpoint JSON (plus fiable)

### 🔍 Astuces Sélecteurs (à adapter via DevTools)

\`\`\`python
# Repère les blocs parent: data-testid, aria-label, classes stables

# Exemple générique :
ligne_joueur = "div.player-row"
pseudo = "div.username::text"
lien_profil = "a.player-link::attr(href)"

bloc_arme = "section.weapon-card"
nom_arme = "h3.weapon-name::text"
accessoire = "li.attachment .name::text"
\`\`\`

---

## ✅ Statut Actuel

### Phase 0.5 - Extraction ✅ **COMPLÈTE**
- [x] Exploration Tracker.gg réussie
- [x] **100 joueurs extraits avec Selenium** (\`bf6_leaderboard_2025-10-18_174621.ndjson\`)
- [x] Anonymisation SHA256 implémentée
- [x] Format NDJSON (BigQuery-ready)
- [x] Projet réorganisé et documenté

📊 **Résultat** : 100 joueurs, 5,068,303 kills totaux, moyenne 50,683 kills/joueur

### �� PRIORITÉ #1 : Re-tester API Tracker.gg
- **Clé API** : Stockée dans \`.env\` (retourne 401 pour le moment)
- **Actions** :
  1. Attendre 24-48h après création (oct 19-20, 2025)
  2. Retester : \`python scripts/test_api.py\`
  3. Si API fonctionne → Migrer vers extraction API (plus rapide/stable)
  4. Si API échoue → Continuer avec Selenium

---

## 🏗️ Architecture du Pipeline

\`\`\`
┌───────────────────────────────────────────────────────────┐
│              TRACKER.GG (Source de données)               │
│  • Leaderboard + Player Profiles                         │
│  • API (en test) ou Selenium (actuel)                    │
└─────────────────┬─────────────────────────────────────────┘
                  │ Scrapy/Selenium (quotidien)
                  ▼
┌───────────────────────────────────────────────────────────┐
│         BRONZE - Data Lake (MinIO S3-compatible)          │
│  • Fichiers NDJSON bruts                                  │
│  • bf6_leaderboard_YYYY-MM-DD.ndjson                      │
│  • bf6_loadouts_YYYY-MM-DD.ndjson                         │
└─────────────────┬─────────────────────────────────────────┘
                  │ Load to BigQuery
                  ▼
┌───────────────────────────────────────────────────────────┐
│            SILVER - BigQuery + DBT                        │
│  • Nettoyage, typage, déduplication                       │
│  • Calculs KPIs (fréquence accessoires, combos)           │
└─────────────────┬─────────────────────────────────────────┘
                  │ DBT transformations
                  ▼
┌───────────────────────────────────────────────────────────┐
│              GOLD - BigQuery (Tables finales)             │
│  • top_3_attachments_by_weapon                            │
│  • weapon_usage_trends                                    │
│  • player_performance_evolution                           │
└─────────────────┬─────────────────────────────────────────┘
                  │ SQL queries
                  ▼
┌───────────────────────────────────────────────────────────┐
│                 DASHBOARD - Streamlit                     │
│  • Affichage Top 3 loadouts par arme                      │
│  • Filtres : Date, Arme, Plateforme                       │
│  • Graphiques tendances                                   │
└───────────────────────────────────────────────────────────┘
                  ▲
┌─────────────────┴─────────────────────────────────────────┐
│         ORCHESTRATION - Apache Airflow                    │
│  • DAG quotidien : Extract → Upload → Transform → Update  │
└───────────────────────────────────────────────────────────┘
\`\`\`

---

## ⚙️ Stack Technique

| Composant          | Technologie                    | Rôle                                      |
|--------------------|--------------------------------|-------------------------------------------|
| **Extraction**     | \`Selenium\` + \`Scrapy\`          | Scraping leaderboard + profils joueurs    |
| **API Client**     | \`requests\` + \`python-dotenv\`   | Tests API Tracker.gg (en attente)         |
| **Storage Bronze** | \`MinIO\` (S3-compatible)        | Data Lake NDJSON (fichiers bruts)         |
| **Data Warehouse** | \`Google BigQuery\`              | Entrepôt cloud SQL (gratuit jusqu'à 1TB)  |
| **Transformation** | \`DBT Core\`                     | Modèles SQL Bronze → Silver → Gold        |
| **Visualisation**  | \`Streamlit\`                    | Dashboard interactif Python               |
| **Orchestration**  | \`Apache Airflow\`               | Automatisation quotidienne (DAGs)         |
| **Conteneurisation**| \`Docker\` + \`docker-compose\`   | MinIO, Airflow, environnement isolé       |

---

## 🚀 Démarrage Rapide

### Prérequis

\`\`\`bash
# Python 3.12+
python --version

# Packages requis
pip install -r requirements.txt

# Docker (pour MinIO/Airflow)
docker --version
\`\`\`

### Extraction des données (✅ READY)

\`\`\`bash
# Méthode 1 : Selenium (ACTUEL - fonctionne)
python scripts/extract_bf6_final.py

# Méthode 2 : API Tracker.gg (À retester - PRIORITÉ)
# 1. Vérifier .env contient TRACKER_GG_API_KEY
# 2. Tester :
python scripts/test_api.py
\`\`\`

📂 **Résultat** : \`data/bronze/bf6_leaderboard_YYYY-MM-DD_HHMMSS.ndjson\`

---

## 📁 Structure du Projet

\`\`\`
battlefield_meta_aggregator/
├── README.md                          # Ce fichier
├── TODO.md                            # Roadmap détaillé phases 1-5
├── STATUS_CURRENT.md                  # État actuel du projet
├── requirements.txt                   # Dépendances Python
├── docker-compose.yml                 # MinIO + Airflow containers
│
├── scripts/                           # Scripts d'extraction et upload
│   ├── extract_bf6_final.py          # ✅ Selenium extraction (production)
│   ├── test_api.py                   # 🔴 Test API Tracker.gg (PRIORITÉ)
│   ├── upload_to_minio.py            # Upload NDJSON → MinIO
│   └── analyze_data.py               # Analyse données extraites
│
├── extract/                           # Scrapy project
│   ├── spiders/
│   │   ├── pcgamer_spider.py         # Spider articles PC Gamer
│   │   └── wzstats_spider.py         # Spider stats Warzone
│   ├── items.py                      # Scrapy items
│   └── settings.py                   # Scrapy config
│
├── data/                             # Données extraites
│   ├── bronze/                       # ✅ NDJSON bruts (100 joueurs)
│   │   └── bf6_leaderboard_*.ndjson
│   ├── outputs/                      # Résultats d'analyse
│   └── exploration/                  # Tests et explorations
│
├── dbt/                              # DBT transformations (à venir)
│   └── models/
│       ├── bronze/                   # Raw data
│       ├── silver/                   # Cleaned data
│       └── gold/                     # Aggregated metrics
│
├── dashboard/                        # Streamlit UI (à venir)
│   └── pages/
│
├── airflow/                          # Airflow DAGs (à venir)
│   └── dags/
│
└── archive/                          # Fichiers obsolètes
\`\`\`

---

## 📋 Roadmap

### ✅ Phase 0.5 : Extraction (COMPLÈTE)
- [x] Exploration Tracker.gg
- [x] Test API + Selenium
- [x] Extraction 100 joueurs
- [x] Anonymisation SHA256
- [x] Format NDJSON

### 🟡 Phase 1 : MinIO Upload (NEXT - 30 min)
- [ ] Installer Docker Desktop
- [ ] \`docker compose up -d minio\`
- [ ] Exécuter \`upload_to_minio.py\`
- [ ] Valider fichiers dans MinIO UI

### 🔵 Phase 2 : BigQuery Setup (1-2h)
- [ ] Créer projet Google Cloud
- [ ] Activer BigQuery API
- [ ] Créer dataset \`bf6_meta\`
- [ ] Charger NDJSON → table \`bronze_leaderboard\`

### 🔵 Phase 3 : DBT Transformations (2-3h)
- [ ] Installer DBT Core
- [ ] Créer modèles Bronze → Silver → Gold
- [ ] Calculer fréquence accessoires par arme
- [ ] Créer table \`top_3_attachments_by_weapon\`

### 🔵 Phase 4 : Streamlit Dashboard (2-3h)
- [ ] Interface affichage Top 3 par arme
- [ ] Filtres (Date, Arme, Plateforme)
- [ ] Graphiques tendances

### 🔵 Phase 5 : Airflow Orchestration (3-4h)
- [ ] Créer DAG quotidien
- [ ] Tasks : Extract → Upload → Transform → Update
- [ ] Monitoring et alertes

---

## 🔧 Configuration

### Variables d'environnement (\`.env\`)

\`\`\`bash
# API Tracker.gg
TRACKER_GG_API_KEY=55b66bdc-3610-482e-b94c-aa0b2dbc93f9

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# BigQuery (à venir)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BQ_PROJECT_ID=battlefield-meta-aggregator
BQ_DATASET=bf6_meta
\`\`\`

---

## 📊 Format des Données

### Leaderboard (NDJSON)
\`\`\`json
{
  "extraction_date": "2025-10-18T17:46:21",
  "rank": 1,
  "username_original": "Happy_3201",
  "username_hash": "player_b97fd6bc",
  "stats": {
    "kills": 95150,
    "score": 282
  },
  "source_url": "https://tracker.gg/bf6/leaderboards",
  "extraction_method": "selenium_html"
}
\`\`\`

### Loadouts (NDJSON - à venir)
\`\`\`json
{
  "extraction_date": "2025-10-19T10:00:00",
  "username_hash": "player_b97fd6bc",
  "weapon": "AK-24",
  "attachments": {
    "optic": "Holographic Sight",
    "barrel": "Extended Barrel",
    "magazine": "Extended Mag",
    "underbarrel": "Vertical Grip",
    "stock": "Close Combat Stock"
  },
  "source_url": "https://tracker.gg/bf6/profile/...",
  "extraction_method": "selenium_html"
}
\`\`\`

---

## 🚨 Troubleshooting

### API retourne 401 Unauthorized
→ **Solution** : Attendre 24-48h après création de la clé (oct 19-20, 2025)  
→ **Test** : \`python scripts/test_api.py\`

### Docker command not found
→ **Solution** : Installer [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Selenium: ChromeDriver incompatible
→ **Solution** : \`pip install --upgrade selenium webdriver-manager\`

---

## 🎓 Ressources

- [Tracker.gg API Docs](https://tracker.gg/developers/docs)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [DBT Core Docs](https://docs.getdbt.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Airflow Docs](https://airflow.apache.org/docs/)

---

## 📝 Licence

MIT License - Projet personnel d'apprentissage

---

**🔴 NEXT STEP** : Retester API Tracker.gg le 19-20 octobre 2025 → \`python scripts/test_api.py\`
