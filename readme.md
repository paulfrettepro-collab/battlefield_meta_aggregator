# 🎮 Battlefield 6 Meta Aggregator# 🎮 Battlefield Meta Aggregator



> **Projet ELT complet** : Extraction automatisée du leaderboard Battlefield 6, analyse des performances et visualisation des métas.**💡Idées** 

Chaque jour, échantillonner 100 joueurs du leaderboard d'un site spécialisé, récupérer leur loadout par arme, anonymiser les pseudos, calculer les combinaisons d’accessoires les plus fréquentes et afficher un top 3 par arme dans une petite UI. Pipeline: Scrapy → MinIO (Bronze, NDJSON) → BigQuery → DBT (Silver/Gold) → Streamlit. Orchestration quotidienne via Airflow.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)

[![Scrapy](https://img.shields.io/badge/Scrapy-2.11-green.svg)](https://scrapy.org/)**Ce qu’il faut scraper précisément**

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)	1.	leaderboard players

champs: rank, username, platform, url_profil.

**Projet personnel d'ELT & Data Engineering — par Paul Fretté**cible: page classement par plateforme/mode.

indicateurs Scrapy: sélecteurs CSS/XPath pour les lignes du tableau + lien profil.

---	2.	player loadouts

champs: weapon, attachments [optic, barrel, magazine, underbarrel, stock…], timestamp, source_url.

## 🎯 Objectifcible: page profil joueur (onglet stats/loadout).

indicateurs Scrapy: sélecteurs CSS/XPath ciblant les blocs armes et leurs accessoires.

Chaque jour, échantillonner **100 joueurs** du leaderboard Battlefield 6 (tracker.gg), récupérer leurs statistiques, anonymiser les pseudos, et analyser les tendances de performance.bonus: si la page charge un JSON via XHR, viser directement l’endpoint JSON plutôt que le HTML (plus fiable).

**astuces sélecteurs (à adapter via DevTools)**

**Pipeline complet** : Selenium/API → MinIO (Bronze, NDJSON) → BigQuery → DBT (Silver/Gold) → Streamlit  – repère les blocs parent: data-testid, aria-label, classes stables.

**Orchestration** : Apache Airflow (exécution quotidienne automatisée)– exemple générique:

ligne joueur: div.player-row

---pseudo: div.username::text

lien profil: a.player-link::attr(href)

## ✅ Statut Actuelbloc arme: section.weapon-card

nom arme: h3.weapon-name::text

### Phase 0.5 - Extraction ✅ **COMPLÈTE**accessoire: li.attachment .name::text

- [x] Exploration Tracker.gg réussie

- [x] Tests API Tracker.gg (en attente activation clé)**Projet personnel d'ELT & Data Engineering — par Paul Fretté**

- [x] Script Selenium développé et testé

- [x] **100 joueurs extraits avec succès**---

- [x] Anonymisation SHA256 implémentée

- [x] Format NDJSON (BigQuery-ready)## 🧠 Problématique



**📂 Dernier fichier** : `data/bronze/bf6_leaderboard_2025-10-18_174621.ndjson`  **Comment aider les joueurs de Battlefield à améliorer leur performance grâce à l'analyse multi-source de données issues de la communauté (statistiques, loadouts, cartes, métas) ?**

**📊 Résultat** : 100 joueurs, 5,068,303 kills totaux, moyenne 50,683 kills/joueur

L'objectif est de construire un **pipeline ELT complet et automatisé** pour :

### ⚠️ PRIORITÉ #1 : Re-tester API Tracker.gg- ✅ **Extraire** des données de performance et de stratégie issues de plusieurs sources (sites communautaires, forums, guides)

- ✅ **Stocker** les données brutes dans MinIO (Data Lake Bronze)

La clé API est stockée dans `.env` mais retourne actuellement des erreurs 401.- ✅ **Charger** dans BigQuery pour analyse et transformation

- ✅ **Transformer** avec DBT Core (modèles Bronze → Silver → Gold)

**Actions** :- ✅ **Présenter** via une interface Streamlit interactive et en temps réel

1. Attendre 24-48h après création

2. Retester : `python scripts/test_api.py`**Mise à jour automatique** : Pipeline orchestré par Apache Airflow (runs quotidiens), 100% open source

3. Si l'API fonctionne → Migrer vers extraction API (plus rapide/stable)

4. Si l'API échoue → Continuer avec Selenium---



---## 🏗️ Architecture du Pipeline



## 🏗️ Architecture```

┌─────────────────────────────────────────────────────────────────┐

```│                     SOURCES DE DONNÉES                           │

┌─────────────────────────────────────────────────────────────┐│  • Tracker.gg (Leaderboard + Stats)                             │

│               TRACKER.GG (Source de données)                 ││  • API Tracker.gg (en attente activation)                        │

│  • Leaderboard BF6                                           │└─────────────────┬───────────────────────────────────────────────┘

│  • API (en attente) ou Selenium (actuel)                     │                  │

└─────────────────┬───────────────────────────────────────────┘                  │ Selenium/Scrapy (extraction quotidienne)

                  │                  ▼

                  ▼┌─────────────────────────────────────────────────────────────────┐

┌─────────────────────────────────────────────────────────────┐│              BRONZE LAYER - Data Lake (MinIO)                    │

│           BRONZE LAYER - Data Lake (MinIO)                   ││  • Stockage fichiers bruts NDJSON                                │

│  • NDJSON: bf6_leaderboard_YYYY-MM-DD.ndjson                 ││  • data/bronze/bf6_leaderboard_YYYY-MM-DD.ndjson                 │

│  • Anonymisation SHA256                                      ││  • Partition par date                                            │

└─────────────────┬───────────────────────────────────────────┘└─────────────────┬───────────────────────────────────────────────┘

                  │                  │

                  ▼                  │ Load to BigQuery

┌─────────────────────────────────────────────────────────────┐                  ▼

│         SILVER LAYER - BigQuery + DBT                        │┌─────────────────────────────────────────────────────────────────┐

│  • Nettoyage, typage, déduplication                          ││            SILVER LAYER - BigQuery + DBT                         │

│  • Calculs KPIs (K/D, trends)                                ││  • Nettoyage et typage des données                               │

└─────────────────┬───────────────────────────────────────────┘│  • Déduplication des joueurs                                     │

                  ││  • Calculs KPIs (K/D, trends, rankings)                          │

                  ▼└─────────────────┬───────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐                  │

│           GOLD LAYER - BigQuery (Tables finales)             │                  │ DBT transformations

│  • Métriques agrégées                                        │                  ▼

│  • Top performers, évolutions                                │┌─────────────────────────────────────────────────────────────────┐

└─────────────────┬───────────────────────────────────────────┘│              GOLD LAYER - BigQuery (Tables finales)              │

                  ││  • Métriques agrégées par jour/semaine/mois                      │

                  ▼│  • Top performers, évolutions, statistiques                      │

┌─────────────────────────────────────────────────────────────┐│  • Tables optimisées pour dashboard                              │

│              DASHBOARD - Streamlit                           │└─────────────────┬───────────────────────────────────────────────┘

│  • Visualisation interactive                                 │                  │

│  • Filtres, graphiques, trends                               │                  │ SQL queries

└─────────────────────────────────────────────────────────────┘                  ▼

                  ▲┌─────────────────────────────────────────────────────────────────┐

                  ││                 DASHBOARD - Streamlit                            │

┌─────────────────┴───────────────────────────────────────────┐│  • Visualisation interactive                                     │

│        ORCHESTRATION - Apache Airflow                        ││  • Filtres par date, top N, statistiques                         │

│  • Exécution quotidienne                                     ││  • Graphiques trends et comparaisons                             │

└─────────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────────────┘

```                  ▲

                  │

---┌─────────────────┴───────────────────────────────────────────────┐

│           ORCHESTRATION - Apache Airflow                         │

## 🚀 Démarrage Rapide│  • Exécution quotidienne automatique                             │

│  • DAG : Extract → Upload → Transform → Update                  │

### Prérequis└─────────────────────────────────────────────────────────────────┘

```bash```

# Python 3.12+

python --version---



# Packages requis## ⚙️ Stack Technique

pip install -r requirements.txt

| Composant          | Technologie                    | Rôle                                      |

# Docker (pour MinIO/Airflow - optionnel Phase 1)|--------------------|--------------------------------|-------------------------------------------|

docker --version| **Extraction**     | `Selenium` + `Scrapy`          | Scraping Tracker.gg leaderboard           |

```| **API Client**     | `requests` + `python-dotenv`   | Tests API Tracker.gg (en attente)         |

| **Storage Bronze** | `MinIO` (S3-compatible)        | Data Lake NDJSON (fichiers bruts)         |

### Extraction des données (READY ✅)| **Data Warehouse** | `Google BigQuery`              | Entrepôt cloud SQL, gratuit jusqu'à 1TB   |

| **Transformation** | `DBT Core`                     | Modèles SQL Bronze → Silver → Gold        |

```bash| **Visualisation**  | `Streamlit`                    | Dashboard interactif Python               |

# Méthode 1 : Selenium (ACTUEL - fonctionne)| **Orchestration**  | `Apache Airflow`               | Automatisation quotidienne (DAGs)         |

python scripts/extract_bf6_final.py| **Containerisation**| `Docker` + `docker-compose`   | MinIO, Airflow, environnement isolé       |

| **Versioning**     | `Git` + `GitHub`               | Code versionné, collaboration             |

# Méthode 2 : API Tracker.gg (À retester - PRIORITÉ)- **GPT-4** : Extraction structurée des articles HTML (loadouts, accessoires)

# 1. Vérifier .env contient TRACKER_GG_API_KEY- **Alternative gratuite** : Llama 3 / Mistral via Ollama (local)

# 2. Tester :- **Coût** : ~$15/mois pour 50 articles (ou gratuit avec Ollama)

python scripts/test_api.py---

```---



**📂 Résultat** : `data/bronze/bf6_leaderboard_YYYY-MM-DD.ndjson`## 🚀 Démarrage Rapide



---### Prérequis

```bash

## 📁 Structure du Projet# Python 3.12+

python --version

```

battlefield_meta_aggregator/# Packages requis

├── extract/                 # Scrapy configpip install -r requirements.txt

│   ├── spiders/            # Spiders Scrapy

│   └── settings.py         # Configuration# Docker (pour MinIO et Airflow - optionnel pour Phase 1)

├── scripts/                # Scripts productiondocker --version

│   ├── extract_bf6_final.py       # ✅ Selenium (prod)```

│   ├── test_api.py                # Test API

│   └── upload_to_minio.py         # Upload MinIO### Extraction des données (Production Ready ✅)

├── data/

│   ├── bronze/             # ✅ NDJSON extraits```bash

│   └── exploration/        # HTML pour analyse# Méthode 1 : Script Selenium (RECOMMANDÉ - fonctionne actuellement)

├── dbt/                    # Transformations (Phase 2)python scripts/extract_bf6_final.py

├── dashboard/              # Streamlit (Phase 4)

├── airflow/                # DAGs (Phase 5)# Méthode 2 : API Tracker.gg (À retester quand clé activée - PRIORITÉ)

├── docs/                   # Documentation# 1. Vérifier que .env contient TRACKER_GG_API_KEY=votre_clé

│   ├── STATUS_CURRENT.md          # Statut détaillé# 2. Tester la connexion :

│   ├── PREREQUISITES.md           # Guide setuppython scripts/test_api.py

│   └── TRACKER_GG_EXPLORATION.md  # Exploration

├── docker-compose.yml      # MinIO + Airflow# Si l'API fonctionne, implémenter l'extraction API

├── requirements.txt# (Plus rapide et stable que Selenium)

└── .env                    # API keys (gitignored)```

```

**� Résultat** : `data/bronze/bf6_leaderboard_YYYY-MM-DD.ndjson`

---

### Sources finales (après exploration)

## 📊 Exemple de Donnée

**Stratégie validée : Approche hybride**

```json

{| Priorité | Source | Méthode | Rôle | Données fournies |

  "extraction_date": "2025-10-18T17:46:21",|----------|--------|---------|------|------------------|

  "rank": 1,| 🔴 **CRITICAL** | **Tracker.gg** | Scraping/API | **Base de données** | Armes, stats, win rates, pick rates |

  "username_original": "Happy_3201",| 🔴 **HIGH** | **GameTools API** | API | **Enrichissement** | Accessoires, loadouts détaillés |

  "username_hash": "player_a7f3d891",| 🟢 **MEDIUM** | **Reddit API** | API officielle | **Méta communautaire** | Discussions, tendances, feedback joueurs |

  "stats": {| 🟡 **SUPPORT** | PC Gamer | Scrapy + LLM | **Guides enrichis** | Loadouts recommandés, analyses |

    "kills": 95150,| 🟡 **SUPPORT** | Skycoach | Scrapy + LLM | **Guides loadouts** | Configurations optimales |

    "score": 282| 🟡 **SUPPORT** | Gam3s.gg | Scrapy + LLM | **Tier lists** | Classements armes par patch |

  },

  "source_url": "https://tracker.gg/bf6/leaderboards",**Workflow de traitement** :

  "extraction_method": "selenium_headless"1. **Tracker.gg** → Données structurées (JSON/API) → BigQuery Bronze

}2. **GameTools** → API REST → Accessoires détaillés → BigQuery Bronze

```3. **Articles** → HTML brut → MinIO → LLM Processing → BigQuery Bronze

4. **DBT Silver** → Fusion intelligente (Tracker + GameTools + LLM)

---5. **DBT Gold** → Consensus multi-sources avec scoring



## 📋 Roadmap**Fréquence de crawling** : Quotidienne (via Airflow DAG), avec respect des `robots.txt` et rate limiting.



| Phase | Description | Statut | Durée |---

|-------|-------------|--------|-------|

| **0** | Setup & Config | ✅ 100% | Terminé |## 📊 Données Actuelles

| **0.5** | Extraction | ✅ 100% | Terminé |

| **1** | MinIO Upload | ⏳ 0% | 30 min |### Dernière extraction (18 oct 2025)

| **2** | BigQuery + DBT | ⏳ 0% | 1-2h |- **Fichier** : `data/bronze/bf6_leaderboard_2025-10-18_174621.ndjson`

| **3** | DBT Gold | ⏳ 0% | 2-3h |- **Joueurs** : 100 (Top leaderboard)

| **4** | Dashboard Streamlit | ⏳ 0% | 2h |- **Total Kills** : 5,068,303

| **5** | Airflow | ⏳ 0% | 1h |- **Moyenne** : 50,683 kills/joueur

- **Top 1** : Happy_3201 (95,150 kills)

### Prochaines étapes immédiates- **Format** : NDJSON (1 joueur par ligne, BigQuery-ready)

1. **⚠️ PRIORITÉ** : Retester API Tracker.gg (24-48h après création clé)

2. Installer Docker Desktop### Exemple de donnée

3. Lancer MinIO : `docker compose up -d minio`

4. Upload données : `python scripts/upload_to_minio.py````json

5. Setup BigQuery (Phase 2){

  "extraction_date": "2025-10-18T17:46:21",

---  "rank": 1,

  "username_original": "Happy_3201",

## ⚙️ Stack Technique  "username_hash": "player_a7f3d891",

  "stats": {

| Composant | Technologie | Rôle |    "kills": 95150,

|-----------|-------------|------|    "score": 282

| **Extraction** | Selenium + Scrapy | Scraping leaderboard |  },

| **API** | requests + python-dotenv | Tests API (priorité) |  "source_url": "https://tracker.gg/bf6/leaderboards",

| **Bronze** | MinIO (S3) | Data Lake NDJSON |  "extraction_method": "selenium_headless"

| **Warehouse** | Google BigQuery | SQL cloud gratuit 1TB |}

| **Transform** | DBT Core | Bronze → Silver → Gold |```

| **Viz** | Streamlit | Dashboard Python |

| **Orchestration** | Apache Airflow | Automatisation DAGs |---

| **Container** | Docker | MinIO + Airflow |

## 🌍 Source de Données

---

### Tracker.gg (Source principale)

## 📚 Documentation

**URL** : https://tracker.gg/bf6/leaderboards

| Document | Description |

|----------|-------------|**Méthodes d'extraction** :

| [`STATUS_CURRENT.md`](docs/STATUS_CURRENT.md) | État détaillé du projet |1. **🔑 API Tracker.gg** (PRIORITÉ - en attente activation)

| [`PREREQUISITES.md`](docs/PREREQUISITES.md) | Guide installation |   - Endpoint : `https://public-api.tracker.gg/v2/bf6/`

| [`TRACKER_GG_EXPLORATION.md`](docs/TRACKER_GG_EXPLORATION.md) | Exploration source |   - Authentification : Header `TRN-Api-Key`

   - Status : Clé API obtenue, activation en cours

---   - **⚠️ Action requise** : Retester dans 24-48h



## 🤝 Contribution2. **🤖 Selenium** (ACTIF - fonctionne)

   - Chrome headless + BeautifulSoup

Projet personnel de Paul Fretté. Suggestions bienvenues via Issues.   - Extraction table HTML

   - Anonymisation SHA256

---   - Script : `scripts/extract_bf6_final.py`



## 📄 License**Données extraites** :

- Rank (1-100)

MIT License - Voir LICENSE- Username (anonymisé)

- Kills

---- Score/Points

- Date d'extraction

**Dernière mise à jour** : 18 octobre 2025

---

## 📋 Roadmap Complète

### ✅ Phase 0 : Setup (100%)
- [x] Architecture définie
- [x] Repository Git configuré
- [x] Structure projet créée
- [x] Docker-compose MinIO configuré
- [x] Documentation complète

### ✅ Phase 0.5 : Extraction (100%)
- [x] Exploration Tracker.gg
- [x] Script Selenium développé
- [x] 100 joueurs extraits (NDJSON)
- [x] Anonymisation implémentée
- [ ] **⏳ Test API quand clé activée** (PRIORITÉ #1)

### ⏳ Phase 1 : MinIO Upload (0%)
**Durée estimée** : 30 minutes
- [ ] Installer Docker Desktop
- [ ] Lancer `docker compose up -d minio`
- [ ] Tester upload : `python scripts/upload_to_minio.py`
- [ ] Vérifier dans MinIO UI (localhost:9001)

### ⏳ Phase 2 : BigQuery (0%)
**Durée estimée** : 1-2 heures
- [ ] Créer projet Google Cloud
- [ ] Activer BigQuery API
- [ ] Créer dataset `bf6_meta`
- [ ] Créer table `bronze_leaderboard`
- [ ] Load NDJSON → BigQuery
- [ ] Vérifier données importées

### ⏳ Phase 3 : DBT Transformations (0%)
**Durée estimée** : 2-3 heures
- [ ] Installer DBT Core
- [ ] Configurer profiles.yml (BigQuery)
- [ ] Créer modèles Bronze → Silver
- [ ] Créer modèles Silver → Gold
- [ ] Tests qualité données
- [ ] Documentation DBT

### ⏳ Phase 4 : Dashboard Streamlit (0%)
**Durée estimée** : 2 heures
- [ ] Créer app Streamlit
- [ ] Connexion BigQuery
- [ ] Graphique Top 10 joueurs
- [ ] Évolution temporelle
- [ ] Filtres interactifs
- [ ] Déploiement (Streamlit Cloud)

### ⏳ Phase 5 : Airflow Orchestration (0%)
**Durée estimée** : 1 heure
- [ ] Configurer Airflow (docker-compose)
- [ ] Créer DAG extraction quotidienne
- [ ] Intégration Upload → Transform
- [ ] Tests exécution automatique
- [ ] Monitoring et alertes
   
4. Fusion intelligente (DBT Silver)
   └─> Base Tracker.gg + Enrichissement LLM
   
5. Tables Gold (BigQuery)
   └─> Loadouts complets avec consensus multi-sources
```

**Avantages approche hybride** :
- ✅ Base solide avec Tracker.gg (données fiables)
- ✅ Granularité maximale via LLM (extraction intelligente)
- ✅ Consensus multi-sources (croiser Tracker + Articles)
- ✅ Flexibilité (LLM s'adapte aux changements de HTML)

**Technologies prévues** :
- `Scrapy` : Crawler Tracker.gg + articles
- `LangChain` : Orchestration LLM
- `OpenAI API` (GPT-4) : Extraction structurée HTML → JSON
- `DBT` : Fusion et consensus des sources

**Livrables** :
```
/data/exploration/
├── test_api_ea.json           # Réponse API EA (si trouvée)
├── test_api_tracker.json      # Réponse Tracker.gg
├── test_api_reddit.json       # Posts Reddit extraits
├── findings_summary.md        # Résumé découvertes
└── final_sources.md           # 5 sources choisies avec plan
```

**📖 Guide complet** : `docs/SOURCES_EXPLORATION.md`

---

### 🔄 **Phase 1 : Extraction** (APRÈS Phase 0.5)
**Approche hybride : API Tracker.gg + Scraping enrichi par LLM**

**Architecture prévue** :
```
/extract/
├── apis/                      # Clients API
│   ├── tracker_client.py     # Tracker.gg (base de données)
│   ├── gametools_client.py   # GameTools API (accessoires)
│   └── reddit_client.py      # Reddit API (praw)
├── spiders/                   # Scrapy crawlers
│   ├── pcgamer_spider.py     ✅ Fait
│   ├── skycoach_spider.py    # Guides loadouts
│   └── gam3s_spider.py       # Tier lists
├── llm/                       # Extraction intelligente
│   ├── html_processor.py     # LangChain + GPT-4
│   └── schema_mapper.py      # HTML → JSON structuré
└── README.md
```

**Workflow d'extraction** :
1. **Tracker.gg** (Scraping/API) → Base de données armes/stats
2. **GameTools** (API) → Détails accessoires/loadouts
3. **Articles guides** (Scrapy) → HTML brut → MinIO
4. **LLM Processing** → HTML → JSON structuré (accessoires, recommandations)
5. **Upload MinIO** → Bronze layer (tout conservé)

**Temps estimé** : 
- Tracker.gg scraper : 3-4 heures
- GameTools API : 2-3 heures
- LLM extraction : 4-5 heures
- Scripts upload : 1-2 heures
- **Total** : ~10-14 heures

---

### 📊 **Schéma de données prévu (BigQuery)**

#### Bronze Layer (Raw data)
```sql
-- Table : bronze_tracker_weapons
CREATE TABLE bronze_tracker_weapons (
  weapon_name STRING,
  weapon_type STRING,
  damage INT64,
  fire_rate INT64,
  accuracy FLOAT64,
  win_rate FLOAT64,
  pick_rate FLOAT64,
  crawled_at TIMESTAMP,
  source STRING
);

-- Table : bronze_html_articles
CREATE TABLE bronze_html_articles (
  article_url STRING,
  html_content STRING,
  source_site STRING,
  crawled_at TIMESTAMP
);
```

#### Silver Layer (Cleaned & enriched)
```sql
-- Table : silver_weapons
CREATE TABLE silver_weapons (
  weapon_id STRING,
  weapon_name_normalized STRING,  -- PW7A2 = MP7
  weapon_category STRING,          -- AR, SMG, Sniper, etc.
  base_stats STRUCT<
    damage INT64,
    fire_rate INT64,
    accuracy FLOAT64,
    range INT64
  >,
  meta_score FLOAT64,              -- Score consensuel
  data_quality_score FLOAT64,      -- Fiabilité source
  last_updated TIMESTAMP
);

-- Table : silver_loadouts (extraction LLM)
CREATE TABLE silver_loadouts (
  loadout_id STRING,
  weapon_id STRING,
  attachments ARRAY<STRUCT<
    slot STRING,                   -- Optic, Barrel, Magazine, etc.
    item STRING,                   -- Red Dot, Extended Mag, etc.
    impact STRING                  -- +Accuracy, +Range, etc.
  >>,
  recommended_by ARRAY<STRING>,    -- Sources qui recommandent
  confidence_score FLOAT64,        -- Score LLM
  extracted_at TIMESTAMP
);
```

#### Gold Layer (KPIs & Analytics)
```sql
-- Table : gold_meta_consensus
CREATE TABLE gold_meta_consensus (
  weapon_name STRING,
  overall_rank INT64,
  meta_score FLOAT64,
  best_loadout STRUCT<
    attachments ARRAY<STRING>,
    sources ARRAY<STRING>,
    consensus_level STRING        -- High, Medium, Low
  >,
  win_rate_avg FLOAT64,
  pick_rate_avg FLOAT64,
  trend STRING,                   -- Rising, Stable, Falling
  last_patch_impact FLOAT64,
  updated_at TIMESTAMP
);
```

---

### 🤖 **Extraction intelligente par LLM**

**Processus d'extraction HTML → JSON structuré**

#### Étape 1 : Crawling HTML brut
```python
# Scrapy crawl articles guides
scrapy crawl pcgamer -o data/outputs/pcgamer_articles.json

# Output : HTML complet sauvegardé
{
  "url": "https://pcgamer.com/battlefield-loadout-guide",
  "html_content": "<html>...</html>",
  "crawled_at": "2025-10-16T10:30:00"
}
```

#### Étape 2 : Traitement LLM (GPT-4 / Claude)
```python
# LangChain + OpenAI API
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Prompt structuré
prompt = """
Analyse cet article HTML Battlefield et extrais les informations structurées.

HTML : {html_content}

Extrais au format JSON :
{
  "weapons": [
    {
      "name": "nom exact de l'arme",
      "category": "AR/SMG/Sniper/LMG",
      "recommended_loadout": {
        "optic": "...",
        "barrel": "...",
        "magazine": "...",
        "underbarrel": "...",
        "stock": "..."
      },
      "pros": ["avantage 1", "avantage 2"],
      "cons": ["inconvénient 1"],
      "best_for": "situation/style de jeu",
      "meta_tier": "S/A/B/C",
      "confidence": 0.0-1.0
    }
  ]
}

Règles :
- Extrais SEULEMENT les informations explicitement mentionnées
- Si un accessoire n'est pas mentionné, utilise null
- confidence = fiabilité de l'extraction (1.0 = très sûr)
"""

# Exécution
llm = ChatOpenAI(model="gpt-4")
response = llm.predict(prompt.format(html_content=html))
structured_data = json.loads(response)
```

#### Étape 3 : Validation et stockage
```python
# Validation schema Pydantic
from pydantic import BaseModel, Field

class WeaponLoadout(BaseModel):
    name: str
    category: str
    recommended_loadout: dict
    confidence: float = Field(ge=0.0, le=1.0)

# Stockage BigQuery
validated_data = WeaponLoadout(**structured_data)
upload_to_bigquery(validated_data, table="bronze_llm_extractions")
```

#### Avantages de l'approche LLM :
- ✅ **Flexibilité** : S'adapte aux changements de HTML
- ✅ **Granularité** : Capture nuances (pros/cons, contexte)
- ✅ **Multi-sources** : Unifie formats différents
- ✅ **Confidence scoring** : Mesure fiabilité extraction
- ✅ **NLP avancé** : Comprend recommandations implicites

**Coût estimé** :
- GPT-4 : ~$0.03 / 1K tokens
- Article moyen : ~10K tokens
- **Coût par article** : ~$0.30
- **50 articles/mois** : ~$15/mois

**Alternative gratuite** : Open-source LLM (Llama 3, Mistral) via Ollama

---

### ✅ **Phase 2 : Chargement BigQuery (Silver Layer)**
- Setup compte Google Cloud (gratuit, 300$ crédit)
- Créer dataset BigQuery `battlefield_meta`
- Service Account pour authentification
- Installer DBT (`pip install dbt-bigquery`)
- Configurer `dbt/profiles.yml`
- **Créer modèles Bronze** :
  - `bronze_tracker_weapons.sql` : Import Tracker.gg
  - `bronze_html_articles.sql` : Import HTML brut
  - `bronze_llm_extractions.sql` : Import résultats LLM
- **Modèles Silver** : Nettoyage et normalisation
  - Suppression doublons
  - Normalisation noms d'armes (PW7A2 → MP7)
  - **Fusion intelligente** : Tracker.gg (stats) + LLM (loadouts)
  - Calcul consensus multi-sources
  - Typage et validation

---

### ✅ **Phase 3 : Transformation DBT (Gold Layer)**
- Modèles DBT pour agrégations :
  - **Consensus méta** : Score pondéré par source et fraîcheur
  - **Top armes** par classe, carte, mode de jeu
  - **Loadouts recommandés** avec accessoires
  - **Évolution méta** dans le temps
- Tests automatiques DBT (données cohérentes)
- Documentation auto-générée des modèles
- DAG Airflow pour orchestration quotidienne

---

### ✅ **Phase 4 : Visualisation Streamlit**
- Dashboard interactif avec :
  - 📊 Graphiques top armes par patch
  - 🎯 Filtres : classe, carte, mode de jeu, date
  - 📈 Évolution méta dans le temps
  - 🔗 Liens vers sources originales
- Connexion BigQuery (lecture tables Gold)
- Déploiement Streamlit Cloud (gratuit)
- Rafraîchissement automatique quotidien

---

### 🔜 **Phase 5 : Production & Monitoring** (Optionnel)
- Alertes email si DAG échoue
- Métriques qualité données (freshness, completeness)
- Logs centralisés
- CI/CD GitHub Actions
- Documentation utilisateur finale

---

## 📊 Exemple de KPI produits (Gold Layer)

| Carte      | Classe top | Victoire % | Loadout recommandé              | Score Meta |
|------------|------------|------------|----------------------------------|------------|
| Manifest   | Médecin    | 62.4%      | M5A3 + Smoke + Defibrillator    | 4.5 / 5    |
| Orbital    | Ingénieur  | 58.1%      | PKP-BP + Drone Repair           | 4.2 / 5    |
| Hourglass  | Assaut     | 55.3%      | AC-42 + Frag Grenade            | 4.1 / 5    |

**Calcul du Score Meta** :
```sql
-- DBT Model : gold_weapon_consensus.sql
SELECT 
  weapon_name,
  AVG(normalized_score) * 
  AVG(source_credibility) * 
  AVG(freshness_weight) AS meta_score
FROM {{ ref('silver_weapons') }}
GROUP BY weapon_name
ORDER BY meta_score DESC
```

---

## 🔁 Pipeline Airflow - DAG quotidien

```python
# airflow/dags/battlefield_meta_pipeline.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'paul_frette',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='battlefield_meta_pipeline',
    default_args=default_args,
    description='Pipeline ELT quotidien Battlefield Meta',
    schedule='0 2 * * *',  # Tous les jours à 2h du matin
    start_date=datetime(2025, 10, 1),
    catchup=False,
) as dag:
    
    # Task 1 : Extraction avec Scrapy
    extract_pcgamer = BashOperator(
        task_id='extract_pcgamer',
        bash_command='scrapy crawl pcgamer -o /data/bronze/pcgamer_{{ ds }}.json'
    )
    
    extract_reddit = BashOperator(
        task_id='extract_reddit',
        bash_command='scrapy crawl reddit -o /data/bronze/reddit_{{ ds }}.json'
    )
    
    # Task 2 : Upload vers MinIO
    upload_to_minio = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_files_to_minio,
    )
    
    # Task 3 : Load dans BigQuery
    load_to_bigquery = BashOperator(
        task_id='load_to_bigquery',
        bash_command='python scripts/load_bigquery.py --date {{ ds }}'
    )
    
    # Task 4 : DBT Transformation
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd dbt && dbt run --models silver gold'
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd dbt && dbt test'
    )
    
    # Task 5 : Refresh Dashboard Streamlit (optionnel)
    refresh_dashboard = PythonOperator(
        task_id='refresh_dashboard',
        python_callable=trigger_streamlit_refresh,
    )
    
    # Définir les dépendances
    [extract_pcgamer, extract_reddit] >> upload_to_minio
    upload_to_minio >> load_to_bigquery
    load_to_bigquery >> dbt_run >> dbt_test
    dbt_test >> refresh_dashboard
```

---

## 📁 Structure du projet

```
battlefield_meta_aggregator/
│
├── 📥 extract/                 # Extraction de données (Scrapy + APIs)
│   ├── apis/                  # Clients API (après Phase 0.5)
│   │   ├── ea_client.py       # API EA/DICE (si trouvée)
│   │   ├── tracker_client.py  # Tracker.gg API
│   │   └── reddit_client.py   # Reddit API (praw)
│   ├── spiders/               # Scrapy crawlers (complément)
│   │   ├── pcgamer_spider.py  ✅ Fait
│   │   └── wzstats_spider.py  ✅ Fait
│   ├── items.py
│   ├── settings.py
│   ├── scrapy.cfg
│   └── README.md
│
├── 🔄 dbt/                     # Transformations SQL (DBT Core)
│   ├── models/
│   │   ├── bronze/            # Raw data MinIO → BigQuery
│   │   ├── silver/            # Nettoyage & normalisation
│   │   └── gold/              # KPIs & métriques business
│   ├── dbt_project.yml
│   ├── profiles.yml           # Connexion BigQuery
│   └── README.md
│
├── 🔀 airflow/                 # Orchestration (Apache Airflow)
│   ├── dags/
│   │   └── battlefield_pipeline.py  # DAG quotidien
│   ├── logs/
│   └── README.md
│
├── 📊 dashboard/               # Visualisation (Streamlit)
│   ├── app.py                 # Application principale
│   ├── pages/                 # Pages multi-vues
│   └── README.md
│
├── 💾 data/                    # Données locales (dev)
│   ├── outputs/               # Résultats crawls Scrapy
│   ├── bronze/                # Tests locaux
│   ├── exploration/           # Findings Phase 0.5
│   └── README.md
│
├── 🛠️ scripts/                 # Utilitaires Python
│   ├── upload_to_minio.py     # Upload → MinIO (Bronze)
│   ├── load_bigquery.py       # MinIO → BigQuery
│   ├── test_all_sources.py    # Tester APIs + Scrapy
│   └── README.md
│
├── 📚 docs/                    # Documentation
│   ├── SOURCES_EXPLORATION.md # Guide exploration (Phase 0.5)
│   ├── MINIO_EXPLAINED.md     # Comprendre MinIO
│   └── CRAWLING_GUIDE.md      # Guide Scrapy
│
├── 🚀 NEXT_STEPS.md            # Guide des prochaines étapes
├── 📖 readme.md                # Ce fichier
├── � docker-compose.yml       # MinIO + Airflow
├── 📦 requirements.txt         # Dépendances Python
├── � .env.example             # Template variables d'env
└── 🚫 .gitignore
```

### 📌 Légende des dossiers

| Dossier | Rôle | Phase | État |
|---------|------|-------|------|
| `extract/` | Extraction données (APIs + Scrapy) | Phase 1 | 🔄 En cours |
| `dbt/` | Transformations SQL (Bronze→Gold) | Phase 2-3 | ⏳ À faire |
| `airflow/` | Orchestration quotidienne | Phase 3 | ⏳ À faire |
| `dashboard/` | Visualisation Streamlit | Phase 4 | ⏳ À faire |
| `data/` | Stockage local développement | Phase 0-1 | ✅ Créé |
| `scripts/` | Utilitaires & helpers | Phase 1-2 | ⏳ À créer |
| `docs/` | Documentation technique | Phase 0 | ✅ Fait |

---

## 🚀 Démarrage rapide

### 1. Prérequis

```bash
# Python 3.11+
python --version

# Docker & Docker Compose
docker --version
docker-compose --version
```

### 2. Installation

```bash
# Cloner le repo
git clone https://github.com/paulfrettepro-collab/battlefield_meta_aggregator.git
cd battlefield_meta_aggregator

# Créer environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Mac/Linux

# Installer dépendances
pip install -r requirements.txt

# Copier variables d'environnement
cp .env.example .env
# Éditer .env avec tes clés
```

### 3. Lancer MinIO (stockage Bronze)

```bash
# Démarrer MinIO
docker-compose up -d minio

# Accéder interface web
open http://localhost:9001
# Login : minioadmin / minioadmin
```

### 4. Explorer les sources (Phase 0.5 - EN COURS)

```bash
# Lire le guide d'exploration
open docs/SOURCES_EXPLORATION.md

# Créer dossier exploration
mkdir -p data/exploration

# Commencer recherche APIs
# 1. Chercher "Battlefield API EA developer"
# 2. Tester Tracker.gg (DevTools)
# 3. Setup Reddit API
```

### 5. Tester extraction (après Phase 0.5)

```bash
# Lancer un spider Scrapy
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json

# Upload vers MinIO
python scripts/upload_to_minio.py
```

---

## 📚 Documentation

| Document | Description | Phase |
|----------|-------------|-------|
| **`NEXT_STEPS.md`** | 🎯 Guide des prochaines actions | Phase 0.5-1 |
| **`docs/SOURCES_EXPLORATION.md`** | 🔍 Exploration méthodique des sources | Phase 0.5 |
| **`docs/MINIO_EXPLAINED.md`** | 🗄️ Comprendre MinIO simplement | Phase 0 |
| **`docs/CRAWLING_GUIDE.md`** | 🕷️ Guide Scrapy avancé | Phase 1 |
| **`extract/README.md`** | 📥 Documentation extraction | Phase 1 |
| **`dbt/README.md`** | 🔄 Architecture DBT | Phase 2-3 |
| **`airflow/README.md`** | 🔀 Orchestration Airflow | Phase 3 |
| **`dashboard/README.md`** | 📊 Dashboard Streamlit | Phase 4 |

**📖 Commence ici** : `NEXT_STEPS.md` → Action 0.5 (Exploration)

---

## 🔁 Pipeline Airflow - DAG quotidien (Preview Phase 3)
## 🚀 Roadmap simplifiée & Étapes

### 📋 Légende des statuts
- ✅ **Complet** : Terminé et testé
- 🔄 **En cours** : En développement
- ⏳ **À faire** : Prochaine étape
- 📝 **Planifié** : Phase ultérieure

---

## 📊 Récapitulatif Global

| Phase | Nom | Statut | Objectif |
|-------|-----|--------|----------|
| **Phase 0** | Initialisation | ✅ **Complet** | Structure + Git + MinIO |
| **Phase 1** | Extraction (Bronze) | 🔄 **50%** | Scrapy spiders fonctionnels |
| **Phase 2** | BigQuery + DBT | ⏳ **0%** | Setup DWH + Transformations |
| **Phase 3** | Airflow | ⏳ **0%** | Orchestration automatique |
| **Phase 4** | Streamlit | ⏳ **0%** | Dashboard interactif |
| **Phase 5** | Production | 📝 **Planifié** | Déploiement cloud |

---

## Phase 0 : Initialisation ✅

### ✅ 0.1 Structure du projet
- [x] Repository Git configuré
- [x] Branches (sandbox, main)
- [x] Structure dossiers (extract/, dbt/, airflow/, dashboard/)
- [x] .gitignore + README.md

### ✅ 0.2 MinIO (Data Lake)
- [x] Docker-compose avec MinIO
- [x] Scripts Python pour upload/download
- [x] Bucket `battlefield-bronze` créé

### ✅ 0.3 Premier test crawler
- [x] Spider PC Gamer fonctionnel
- [x] Extraction loadout PW7A2 réussie
- [x] Sauvegarde JSON locale

---

## Phase 1 : Extraction (Bronze Layer) 🔄

### 🔄 1.1 Scrapy Spiders complets
- [x] `pcgamer_spider.py` : Extrait loadouts et guides
- [ ] `reddit_spider.py` : Posts /r/Battlefield6
- [ ] `skycoach_spider.py` : Guides loadouts
- [ ] `gam3s_spider.py` : Tier lists
- [ ] `beebom_spider.py` : Best weapons guides

**Commande** : `scrapy crawl pcgamer -o data/bronze/pcgamer_2025-10-15.json`

### ⏳ 1.2 Pipeline MinIO
- [ ] Script `upload_to_minio.py` : Upload automatique JSON → MinIO
- [ ] Organisation par date : `/bronze/pcgamer/2025/10/15/data.json`
- [ ] Métadonnées : source, date, hash
- [ ] Tests unitaires

**Fichiers à créer** : 
- `scripts/upload_to_minio.py`
- `tests/test_minio_upload.py`

### ⏳ 1.3 Items Scrapy structurés
- [ ] Définir `WeaponItem` (nom, type, stats, tier)
- [ ] Définir `LoadoutItem` (arme, accessoires, classe)
- [ ] Définir `MetaSnapshotItem` (source, date, patch)
- [ ] Validation des données (required fields)

**Fichier** : `extract/items.py`

---

## Phase 2 : BigQuery + DBT ⏳

### ⏳ 2.1 Setup BigQuery
- [ ] Créer projet Google Cloud (gratuit jusqu'à 1TB/mois)
- [ ] Créer dataset `battlefield_meta`
- [ ] Configurer authentification (service account JSON)
- [ ] Tester connexion Python

**Commandes** :
```bash
# Créer service account
gcloud iam service-accounts create battlefield-etl

# Télécharger clé JSON
gcloud iam service-accounts keys create key.json \
  --iam-account=battlefield-etl@PROJECT_ID.iam.gserviceaccount.com
```

### ⏳ 2.2 Load MinIO → BigQuery
- [ ] Script Python `load_bigquery.py`
- [ ] Lire JSON depuis MinIO
- [ ] Upload vers BigQuery (tables partitionnées par date)
- [ ] Gestion erreurs et retry

**Tables BigQuery créées** :
- `bronze_crawled_pages` (raw JSON)
- `bronze_weapons` (armes extraites)
- `bronze_loadouts` (loadouts extraits)

### ⏳ 2.3 DBT Core Setup
- [ ] Installer DBT : `pip install dbt-bigquery`
- [ ] Initialiser projet : `dbt init battlefield_dbt`
- [ ] Configurer `profiles.yml` avec BigQuery
- [ ] Tester connexion : `dbt debug`

**Fichiers** :
- `dbt/dbt_project.yml`
- `dbt/profiles.yml`

### ⏳ 2.4 Modèles DBT (Silver Layer)
- [ ] `silver_weapons.sql` : Nettoyage + typage armes
- [ ] `silver_loadouts.sql` : Déduplicate + normalize
- [ ] `silver_classes.sql` : Agrégation par classe
- [ ] Tests DBT : unicité, not null, références

**Exemple modèle** :
```sql
-- dbt/models/silver/silver_weapons.sql
{{ config(materialized='table') }}

SELECT 
  UPPER(weapon_name) AS weapon_name,
  weapon_type,
  CAST(fire_rate AS INT64) AS fire_rate,
  CASE tier
    WHEN 'S' THEN 1.0
    WHEN 'A' THEN 0.8
    WHEN 'B' THEN 0.6
    ELSE 0.5
  END AS tier_score,
  source,
  crawled_date
FROM {{ ref('bronze_weapons') }}
WHERE weapon_name IS NOT NULL
```

### ⏳ 2.5 Modèles DBT (Gold Layer)
- [ ] `gold_weapon_consensus.sql` : Score méta pondéré
- [ ] `gold_top_loadouts.sql` : Top 10 loadouts par carte
- [ ] `gold_win_rates.sql` : Taux victoire par stratégie
- [ ] Documentation auto : `dbt docs generate`

**Commandes** :
```bash
dbt run --models silver      # Exécute modèles Silver
dbt run --models gold        # Exécute modèles Gold
dbt test                     # Lance tests
dbt docs serve               # Documentation interactive
```

---

## Phase 3 : Airflow (Orchestration) ⏳

### ⏳ 3.1 Setup Airflow
- [ ] Docker-compose avec Airflow (LocalExecutor)
- [ ] Configuration : `airflow.cfg`
- [ ] Connexions : MinIO, BigQuery
- [ ] Interface Web : http://localhost:8080

**Fichier** : `docker-compose.yml` (mise à jour)

### ⏳ 3.2 DAG Pipeline complet
- [ ] Créer DAG `battlefield_meta_pipeline`
- [ ] Tasks : Extract → Upload → Load → DBT → Refresh
- [ ] Schedule : Quotidien à 2h du matin
- [ ] Retry : 3 tentatives, backoff exponentiel
- [ ] Alertes : Email si échec

**Fichier** : `airflow/dags/battlefield_pipeline.py`

### ⏳ 3.3 Monitoring & Logs
- [ ] Dashboard Airflow (succès/échecs)
- [ ] Logs structurés par task
- [ ] Métriques : temps exécution, données crawlées
- [ ] Alertes Slack/Discord (optionnel)

---

## Phase 4 : Streamlit Dashboard ⏳

### ⏳ 4.1 App Streamlit
- [ ] Page principale : Top armes
- [ ] Filtres : Classe, Carte, Mode de jeu
- [ ] Graphiques : Plotly/Altair
- [ ] Connexion BigQuery (lecture Gold tables)

**Fichier** : `dashboard/app.py`

**Exemple code** :
```python
import streamlit as st
from google.cloud import bigquery

st.title("🎮 Battlefield Meta Dashboard")

# Connexion BigQuery
client = bigquery.Client()

# Query Gold layer
query = """
  SELECT weapon_name, meta_score, recommended_loadout
  FROM `battlefield_meta.gold_weapon_consensus`
  ORDER BY meta_score DESC
  LIMIT 10
"""

df = client.query(query).to_dataframe()
st.dataframe(df)
```

### ⏳ 4.2 Pages multi-vues
- [ ] Page 1 : 📊 Top Weapons (graphiques)
- [ ] Page 2 : 🎯 Loadouts recommandés
- [ ] Page 3 : 📈 Évolution méta (timeline)
- [ ] Page 4 : 🗺️ Performances par carte

### ⏳ 4.3 Déploiement Streamlit Cloud
- [ ] Push code sur GitHub
- [ ] Connecter Streamlit Cloud
- [ ] Configurer secrets (BigQuery credentials)
- [ ] URL publique : `battlefield-meta.streamlit.app`

---

## Phase 5 : Production & IA 📝

### 📝 5.1 CI/CD
- [ ] GitHub Actions : tests automatiques
- [ ] Deploy automatique Streamlit
- [ ] DBT CI : tests sur PR

### 📝 5.2 IA & Insights
- [ ] Langchain + OpenAI : Résumés stratégiques
- [ ] Recherche sémantique forums
- [ ] Recommandations personnalisées

### 📝 5.3 Monitoring avancé
- [ ] Great Expectations : tests qualité données
- [ ] Sentry : monitoring erreurs
- [ ] Grafana : métriques pipeline

---

## 🛠️ Commandes rapides

### Lancer le pipeline complet (local)
```bash
# 1. Démarrer MinIO + Airflow
docker-compose up -d

# 2. Crawler une source
scrapy crawl pcgamer -o data/bronze/pcgamer_$(date +%Y-%m-%d).json

# 3. Upload vers MinIO
python scripts/upload_to_minio.py

# 4. Load dans BigQuery
python scripts/load_bigquery.py --date $(date +%Y-%m-%d)

# 5. Transformations DBT
cd dbt && dbt run && dbt test

# 6. Lancer dashboard
cd dashboard && streamlit run app.py
```

### Airflow (production)
```bash
# Déclencher manuellement le DAG
airflow dags trigger battlefield_meta_pipeline

# Voir les logs
airflow tasks logs battlefield_meta_pipeline extract_pcgamer 2025-10-15
```

---

## 💡 Différences clés avec l'ancienne stack

| Aspect | Ancienne Stack | Nouvelle Stack | Avantage |
|--------|---------------|----------------|----------|
| **Orchestration** | APScheduler (Python) | Apache Airflow | ✅ Interface Web, retry, monitoring, DAGs |
| **Data Warehouse** | SQL Server | BigQuery | ✅ Gratuit 1TB/mois, SQL performant, cloud |
| **Transformation** | Python scripts | DBT Core | ✅ SQL modulaire, tests, documentation auto |
| **Visualisation** | Next.js/React | Streamlit | ✅ 100% Python, rapide, déploiement gratuit |
| **Vector DB** | ChromaDB/Qdrant | (Phase 5 optionnel) | ✅ Simplifié, focus sur l'essentiel |
| **Complexité** | Élevée (6 services) | Moyenne (3 services) | ✅ Maintenance facile, stack éprouvée |

---

## 📝 Prochaine étape recommandée

**Phase 1.2** : Implémenter upload automatique MinIO
- Créer `scripts/upload_to_minio.py`
- Tester avec données PC Gamer déjà crawlées
- Vérifier organisation par date dans MinIO

**Commande** :
```bash
python scripts/upload_to_minio.py --source pcgamer --date 2025-10-15
```

**Objectif** : Avoir un pipeline Bronze complet (Scrapy → MinIO) avant d'attaquer BigQuery.

---

## Stack principale (MVP - Phase 1-2)
---

## 📚 Ressources & Documentation

- **Scrapy** : https://docs.scrapy.org
- **Apache Airflow** : https://airflow.apache.org/docs
- **DBT Core** : https://docs.getdbt.com
- **BigQuery** : https://cloud.google.com/bigquery/docs
- **Streamlit** : https://docs.streamlit.io
- **MinIO** : https://min.io/docs

---

## 📄 Licence

MIT License - Paul Fretté © 2025

---

## 🎯 Pitch technique (30 sec)

**Battlefield Meta Aggregator** est un pipeline ELT automatisé qui :
1. **Crawle quotidiennement** 10 sources Battlefield avec Scrapy
2. **Stocke les données brutes** dans MinIO (Data Lake Bronze)
3. **Transforme dans BigQuery** avec DBT Core (modèles Silver/Gold)
4. **Orchestre avec Airflow** (DAGs quotidiens, retry, monitoring)
5. **Affiche dans Streamlit** (dashboard interactif temps réel)

**100% Open Source**, reproductible avec Docker, déployable gratuitement sur cloud.

**Objectif** : Aider les joueurs Battlefield à optimiser leur performance grâce à l'analyse data-driven de la méta communautaire.