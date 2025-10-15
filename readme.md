# 🎮 Battlefield Meta Aggregator

**Projet personnel d'ELT & Data Engineering — par Paul Fretté**

---

## 🧠 Problématique

**Comment aider les joueurs de Battlefield à améliorer leur performance grâce à l'analyse multi-source de données issues de la communauté (statistiques, loadouts, cartes, métas) ?**

L'objectif est de construire un **pipeline ELT complet et automatisé** pour :
- ✅ **Extraire** des données de performance et de stratégie issues de plusieurs sources (sites communautaires, forums, guides)
- ✅ **Stocker** les données brutes dans MinIO (Data Lake Bronze)
- ✅ **Charger** dans BigQuery pour analyse et transformation
- ✅ **Transformer** avec DBT Core (modèles Bronze → Silver → Gold)
- ✅ **Présenter** via une interface Streamlit interactive et en temps réel

**Mise à jour automatique** : Pipeline orchestré par Apache Airflow (runs quotidiens), 100% open source

---

## 🏗️ Architecture du pipeline ELT

```
            +-------------------+
            |  Sites communaut. |
            |  PC Gamer, Reddit |
            |  Gam3s, Skycoach  |
            +--------+----------+
                     |
                     | Scrapy Crawlers
                     ▼
            +-------------------+
            |   Bronze Layer    |  ← MinIO (Raw HTML/JSON)
            |   (Data Lake)     |     Stockage fichiers bruts
            +--------+----------+
                     |
                     | Load vers BigQuery
                     ▼
            +-------------------+
            |   Silver Layer    |  ← BigQuery + DBT Core
            |  (Nettoyé, typé)  |     Transformation SQL
            +--------+----------+
                     |
                     | Modélisation DBT
                     ▼
            +-------------------+
            |    Gold Layer     |  ← BigQuery (Tables finales)
            | (KPI, Consensus)  |     Prêt pour dashboard
            +--------+----------+
                     |
                     | Requêtes SQL
                     ▼
            +-------------------+
            |  Dashboard UI     |  ← Streamlit
            |  (Visualisation)  |     Interface interactive
            +-------------------+
                     ▲
                     |
            +-------------------+
            | Apache Airflow    |  ← Orchestrateur
            | (Automatisation)  |     DAGs quotidiens
            +-------------------+
```

---

## ⚙️ Stack Technique (100% Open Source)

| Composant         | Technologie                    | Rôle                                                          |
|-------------------|--------------------------------|---------------------------------------------------------------|
| **Extraction**    | `Scrapy` + `Playwright`        | Crawler les sites Battlefield (PC Gamer, Reddit, forums)      |
| **Orchestration** | `Apache Airflow`               | Planification DAGs, relances auto, logs, monitoring           |
| **Storage Bronze**| `MinIO` (S3-compatible)        | Data Lake pour fichiers bruts (HTML, JSON, images)            |
| **Data Warehouse**| `Google BigQuery`              | Entrepôt de données cloud, SQL performant, gratuit jusqu'à 1TB|
| **Transformation**| `DBT Core`                     | Modèles SQL (Bronze → Silver → Gold), tests, documentation   |
| **Visualisation** | `Streamlit`                    | Dashboard interactif Python, filtres dynamiques, temps réel   |
| **IA (optionnel)**| `Langchain` + `OpenAI API`     | Génération insights, résumés stratégiques, recherche sémantique|
| **Containerisation**| `Docker` + `docker-compose`  | Environnement reproductible (Airflow, MinIO, DBT)            |
| **Versioning**    | `Git` + `GitHub`               | Code versionné, CI/CD GitHub Actions                          |
---

## 🌍 Sources de données Battlefield 6

Les données seront extraites quotidiennement des sources suivantes :

| Nom du site | Type de contenu | Lien |
|--------------|----------------|------|
| CODMunity / Battlefinity | Classements d’armes, comparateurs de stats, méta actuelle. | [https://codmunity.gg/battlefield](https://codmunity.gg/battlefield) |
| BattlefieldMeta (WZStats) | Tier lists, armes les plus performantes, méta actuelle. | [https://wzstats.gg/battlefield-6/meta](https://wzstats.gg/battlefield-6/meta) |
| Skycoach.gg | Guides de loadouts et accessoires pour chaque arme. | [https://skycoach.gg/blog/battlefield-6/articles/top-loadouts](https://skycoach.gg/blog/battlefield-6/articles/top-loadouts) |
| Gam3s.gg | Tier lists, classement des meilleures armes, méta par patch. | [https://gam3s.gg/battlefield-6/guides/ultimate-battlefield-6-weapon-tier-list](https://gam3s.gg/battlefield-6/guides/ultimate-battlefield-6-weapon-tier-list) |
| PC Gamer | Analyses d’armes et loadouts détaillés, méta du moment. | [https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build](https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build) |
| GamesRadar | Conseils pour armes, accessoires, et classes à privilégier. | [https://www.gamesradar.com/games/battlefield/battlefield-6-weapons-guns](https://www.gamesradar.com/games/battlefield/battlefield-6-weapons-guns) |
| Beebom | Guides “best weapons & loadouts”, guides rapides par type d’arme. | [https://beebom.com/battlefield-6-best-weapons-guns-loadout-guide](https://beebom.com/battlefield-6-best-weapons-guns-loadout-guide) |
| EA Forums – Battlefield 6 Discussions | Discussions communautaires, retours joueurs, stats d’armes. | [https://forums.ea.com/discussions/battlefield-6-general-discussion-en](https://forums.ea.com/discussions/battlefield-6-general-discussion-en) |
| Epic Games Blog | Guides officiels (snipers, armes, mécaniques du jeu). | [https://store.epicgames.com/news/best-sniper-loadout-guide-battlefield-6](https://store.epicgames.com/news/best-sniper-loadout-guide-battlefield-6) |
| Reddit /r/Battlefield6 | Méta communautaire, retours directs des joueurs. | [https://www.reddit.com/r/Battlefield6/](https://www.reddit.com/r/Battlefield6/) |

| Reddit /r/Battlefield6 | Méta communautaire, retours directs des joueurs. | [https://www.reddit.com/r/Battlefield6/](https://www.reddit.com/r/Battlefield6/) |

**Fréquence de crawling** : Quotidienne (via Airflow DAG), avec respect des `robots.txt` et rate limiting.

---

## 🧩 Fonctionnalités du pipeline

### ✅ **Phase 1 : Extraction (Bronze Layer)**
- Scrapy spiders pour crawler automatiquement les 10 sources
- Support JavaScript avec Playwright pour sites dynamiques
- Sauvegarde fichiers bruts dans MinIO :
  - HTML des pages crawlées
  - JSON structuré (loadouts, stats)
  - Images (screenshots d'armes)
- Métadonnées : URL, date crawl, source, hash pour déduplication

### ✅ **Phase 2 : Chargement dans BigQuery (Silver Layer)**
- Upload automatique des JSON de MinIO vers BigQuery
- Tables partitionnées par date de crawl
- Schémas définis (armes, loadouts, classes, cartes)
- Nettoyage et typage avec DBT Core :
  - Suppression doublons
  - Normalisation noms d'armes (PW7A2 = MP7)
  - Conversion métadonnées (tier S → 1.0, A → 0.8)

### ✅ **Phase 3 : Transformation (Gold Layer)**
- Modèles DBT pour agrégations :
  - **Consensus méta** : Score pondéré par source et fraîcheur
  - **Top armes** par classe, carte, mode de jeu
  - **Loadouts recommandés** avec accessoires
  - **Taux de victoire** par stratégie
- Tests automatiques DBT (données cohérentes, pas de NULL)
- Documentation auto-générée des modèles

### ✅ **Phase 4 : Visualisation (Streamlit)**
- Dashboard interactif avec :
  - 📊 Graphiques top armes par patch
  - 🎯 Filtres : classe, carte, mode de jeu
  - 📈 Évolution méta dans le temps
  - 🔗 Liens vers sources originales
- Mise à jour automatique quotidienne (connecté à BigQuery)
- Déployable sur Streamlit Cloud (gratuit)

### 🔜 **Phase 5 : IA & Insights (Optionnel)**
- Langchain + OpenAI pour :
  - Résumés automatiques des stratégies gagnantes
  - Recommandations personnalisées par style de jeu
  - Recherche sémantique dans les forums
  - Génération de patch notes synthétiques

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

## 📁 Structure du projet (mise à jour)

```
battlefield_meta_aggregator/
│
├── airflow/                    ← Apache Airflow
│   ├── dags/
│   │   └── battlefield_pipeline.py
│   ├── plugins/
│   └── logs/
│
├── dbt/                        ← DBT Core (Transformations)
│   ├── models/
│   │   ├── bronze/             ← Raw data from MinIO
│   │   │   └── bronze_crawled_pages.sql
│   │   ├── silver/             ← Cleaned & typed data
│   │   │   ├── silver_weapons.sql
│   │   │   ├── silver_loadouts.sql
│   │   │   └── silver_classes.sql
│   │   └── gold/               ← Business metrics
│   │       ├── gold_weapon_consensus.sql
│   │       ├── gold_top_loadouts.sql
│   │       └── gold_win_rates.sql
│   ├── tests/
│   ├── macros/
│   ├── dbt_project.yml
│   └── profiles.yml            ← BigQuery connection
│
├── extract/                    ← Scrapy crawlers
│   ├── spiders/
│   │   ├── pcgamer_spider.py
│   │   ├── reddit_spider.py
│   │   ├── skycoach_spider.py
│   │   └── gam3s_spider.py
│   ├── items.py
│   ├── pipelines.py
│   ├── settings.py
│   └── scrapy.cfg
│
├── scripts/                    ← Utilitaires Python
│   ├── load_bigquery.py        ← Upload MinIO → BigQuery
│   ├── test_minio.py
│   └── test_bigquery.py
│
├── dashboard/                  ← Streamlit App
│   ├── app.py                  ← Application principale
│   ├── pages/
│   │   ├── 1_📊_Top_Weapons.py
│   │   ├── 2_🎯_Loadouts.py
│   │   └── 3_📈_Trends.py
│   └── requirements.txt
│
├── data/                       ← Données locales (dev)
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── docker-compose.yml          ← Airflow + MinIO + DBT
├── requirements.txt            ← Dépendances Python
├── .env                        ← Variables d'environnement
├── .gitignore
└── README.md
```

---

## 2. Architecture technique (vue d'ensemble)

### Stack principale (MVP - Phase 1-2)
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