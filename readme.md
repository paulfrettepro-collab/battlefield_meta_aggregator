# Battlefield Meta Aggregator

## 1. Idée métier

Ce projet vise à construire un site web public qui agrège les données de plusieurs sites communautaires Battlefield 6 afin de répondre à une question simple :
> « Quelle est la méta actuelle ? »
> (armes les plus performantes, classes dominantes, classes avec armes dominantes meilleurs accessoires par armes, mode de jeu le plus joué.)

L'objectif est de collecter, normaliser et combiner les informations provenant de plusieurs sources fiables, puis de calculer un consensus global basé sur ces données.
Automatiser ce flux de données permettrait de fournir des mises à jour rapides et précises de la méta, aidant ainsi les joueurs à optimiser leurs choix d'équipement et de stratégie en temps réel.
Intérroger les sites web hebdomadairement pour capturer les changements de méta après chaque patch et vérifier si il y a de l'ajout de contenu pertinent (découverte d'une nouvelle meta par un joueur qui partage son expérience par exemple)

---
## 1.1 idée de site web qui récupère de la données sur battelfied 6 :
## 🌍 Sources Battlefield 6 – Guides, Méta & Loadouts

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

## 2. Architecture technique (vue d'ensemble)

### Stack principale (MVP - Phase 1-2)
- **Python** → scraping (Requests, BeautifulSoup, Selenium)
- **FastAPI** → création d'une API REST légère avec autodoc Swagger
- **SQL Server** → stockage structuré selon la logique bronze/silver/gold
- **SQLAlchemy / Alembic** → gestion ORM et migrations de base de données
- **APScheduler** → automatisation et planification du scraping hebdomadaire
- **Tenacity** → gestion des erreurs et retry automatique pour le scraping
- **Loguru** → logging structuré et traçabilité des opérations
- **Docker & docker-compose** → environnement portable et reproductible
- **Next.js / React** → front-end moderne, SEO-friendly, connecté à l'API FastAPI
- **GitHub Copilot + VS Code** → écriture assistée et automatisée du code

### Stack additionnelle (Production - Phase 3-4)
- **Redis** → cache des résultats de consensus (amélioration performances)
- **Azure Blob Storage / MinIO** → Data Lake pour données non structurées (HTML brut, images, vidéos)
- **Sentry** → monitoring des erreurs et alertes en temps réel
- **Discord/Slack Webhook** → notifications si scraping échoue
- **GitHub Actions / Airflow** → orchestration avancée des pipelines (optionnel)

### Structure des dossiers
```
battlefield-meta/
│
├── backend/
│   ├── main.py              # Entrée FastAPI
│   ├── scraper/
│   │   ├── sources.py       # URLs à scraper
│   │   ├── scraper.py       # Logique de scraping avec retry
│   │   ├── parser.py        # Extraction et nettoyage
│   │   ├── consensus.py     # Calcul du consensus
│   │   └── scheduler.py     # APScheduler pour automatisation
│   ├── db/
│   │   ├── models.py        # Modèles SQLAlchemy
│   │   └── schema.sql       # Schéma initial
│   ├── utils/
│   │   ├── normalization.py # Normalisation des données
│   │   ├── logger.py        # Configuration Loguru
│   │   └── cache.py         # Gestion cache Redis (optionnel)
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   │   └── index.tsx        # Page principale
│   ├── components/
│   └── package.json
│
├── docker-compose.yml
├── .env
└── README.md
```

## 3. Étapes du pipeline data

### Data Lake — Stockage brut (données non structurées)
- **Stockage** des fichiers bruts dans Azure Blob Storage / MinIO
  - HTML complet des pages scrapées
  - Images (screenshots d'armes, patchnotes)
  - Vidéos (tutoriels YouTube, streamers)
  - Fichiers JSON brut (réponses API)
  - Logs de scraping détaillés
- **Organisation** par source et date : `/{source}/{year}/{month}/{day}/{filename}`
- **Métadonnées** : contenu_hash, taille, URL origine, date scraping
- **Rétention** : 6 mois pour analyse historique et ML futur

### Bronze — Ingestion (Automatisée hebdomadairement)
- **Scraping** des pages publiques via APScheduler (tous les lundis à 2h)
- **Retry automatique** avec Tenacity (3 tentatives, backoff exponentiel)
- **Logging structuré** de chaque opération (succès/échecs)
- **Sauvegarde Data Lake** : fichiers bruts (HTML, JSON) dans Azure Blob / MinIO
- **Sauvegarde SQL Server** : métadonnées dans table `raw_pages` (référence vers Data Lake)
- **Alertes** Discord/Slack si échec après 3 tentatives

### Silver — Transformation
- **Extraction** des entités principales depuis Data Lake : armes, classes, accessoires
- **Nettoyage** et harmonisation des noms et unités
- **Validation** des données (détection anomalies)
- **Structuration** dans des tables `extracted_items` (SQL Server)
- **Enrichissement** : possibilité d'analyser images/vidéos du Data Lake avec AI (Phase 4)

### Gold — Synthèse
- **Calcul** d'un score normalisé pour chaque entité (échelle 0-1)
- **Pondération** par crédibilité et fraîcheur des sources
- **Calcul du consensus** final (classement + justification)
- **Stockage** dans la table `consensus` (SQL Server)
- **Mise en cache Redis** (TTL 1h) pour performances API
- **Export Data Lake** : résultats JSON pour analyses futures

---

## 4. Modèle de données (simplifié)

| Couche | Stockage | Tables/Conteneurs | Description |
|--------|----------|-------------------|-------------|
| **Data Lake** | Azure Blob / MinIO | `raw-html/`, `raw-json/`, `images/`, `videos/` | Fichiers bruts non structurés |
| **Bronze** | SQL Server | `sources`, `raw_pages`, `datalake_files` | Métadonnées + références Data Lake |
| **Silver** | SQL Server | `extracted_items` | Données extraites et nettoyées |
| **Gold** | SQL Server | `consensus` | Résultat agrégé et classé |

### Exemple de structure
```sql
CREATE TABLE extracted_items (
  id SERIAL PRIMARY KEY,
  source_id INT,
  scraped_at TIMESTAMP,
  game_patch VARCHAR(50),
  entity_type VARCHAR(50),
  entity_name VARCHAR(100),
  metric_name VARCHAR(100),
  metric_value FLOAT,
  evidence_url TEXT
);
```

## 5. Méthode de consensus (MVP)

1. Standardiser les métriques sur une échelle 0–1 (ex. taux de victoire, précision, pick rate)
2. Pondérer selon :
   - Crédibilité de la source
   - Fraîcheur de la donnée
3. Calculer le score final moyen par entité
4. Classer et afficher les 10 meilleures armes

## 6. API REST (FastAPI)

### Endpoints principaux
- GET /weapons/top
- GET /weapons/{weapon_name}
- GET /classes/top
- GET /attachments/top

L'API interroge la couche gold dans SQL Server.

## 7. Front-end (Next.js)

Affiche les classements et rationales de consensus :
- Page principale : top 10 par patch
- Filtres : arme, classe, accessoire
- Lien vers les sources originales (evidence_url)

## 8. Déploiement et exécution

### Pré-requis
- Docker & docker-compose installés
- Clé API (facultative si tu utilises des sources ouvertes)

### Lancement
```bash
git clone https://github.com/paulfrette/battlefield-meta.git
cd battlefield-meta
docker-compose up --build
```

Puis ouvrir :
- API : http://localhost:8000/docs
- Web app : http://localhost:3000
- MinIO Console (Data Lake) : http://localhost:9001

## 9. Sécurité & éthique

- **Attribution claire des sources** avec lien direct vers l'article original
- **Fréquence de scraping limitée** (délai minimum 2-5 sec entre requêtes)
- **User-Agent identifiable** avec email de contact
- **Gestion des erreurs gracieuse** (retry avec backoff exponentiel)
- **Monitoring et alertes** pour détecter les échecs de scraping
- **Mise à disposition d'un contact** pour demande de retrait (contact email dans .env)

## 10. Roadmap & Étapes Détaillées

### 📋 Légende des statuts
- ✅ **Validé et complet** : Étape terminée et testée
- 🔄 **En cours** : En cours de développement
- ⏳ **À faire** : Non démarré, prochaine étape
- 📝 **Planifié** : Planifié pour une phase ultérieure

---

## Phase 0 : Initialisation & Configuration ✅

### ✅ 0.1 Configuration Git & GitHub
- [x] Initialisation du repository Git local
- [x] Connexion au repository GitHub distant (`paulfrettepro-collab/battlefield_meta_aggregator`)
- [x] Configuration des branches (sandbox, staging, main)
- [x] Premier commit et push

**Commandes exécutées** :
```bash
git init
git remote add origin https://github.com/paulfrettepro-collab/battlefield_meta_aggregator.git
git branch -M sandbox
git add .
git commit -m "Initial commit"
git push -u origin sandbox
```

### ✅ 0.2 Fichiers de configuration
- [x] `.gitignore` créé avec patterns Python/Node.js/Docker
- [x] `.env.example` créé avec template de variables
- [x] `.env` créé avec valeurs réelles (non committé)
- [x] `requirements.txt` créé avec 40+ dépendances Python
- [x] `docker-compose.yml` créé avec 5 services (SQL Server, Redis, MinIO, Backend, Frontend)

### ✅ 0.3 Documentation
- [x] `readme.md` créé avec spécifications complètes (ce fichier)
- [x] `docs/DATA_LAKE_GUIDE.md` créé - Guide du Data Lake
- [x] `docs/SQL_SERVER_SETUP.md` créé - Setup SQL Server
- [x] `docs/STACK_ANALYSIS.md` créé - Analyse technique
- [x] `docs/PROJECT_STRUCTURE.md` créé - Arborescence détaillée
- [x] `docs/FILES_EXPLANATION.md` créé - Explication de chaque fichier

### ✅ 0.4 Structure du projet
- [x] Dossiers créés : `/backend`, `/frontend`, `/scripts`, `/tests`, `/docs`
- [x] Modules Python initialisés avec `__init__.py`
- [x] Module Data Lake créé : `backend/utils/datalake.py` (150+ lignes, complet)

**Structure actuelle** :
```
battlefield_meta_aggregator/
├── backend/
│   ├── api/ (__init__.py)
│   ├── db/ (__init__.py)
│   ├── scraper/ (__init__.py)
│   │   └── parsers/ (__init__.py)
│   └── utils/ (__init__.py, datalake.py ✅)
├── docs/ (5 fichiers de documentation ✅)
├── frontend/ (vide, à remplir Phase 4)
├── scripts/ (vide, à remplir Phase 2-3)
├── tests/ (vide, à remplir Phase 2-4)
├── .env ✅
├── .env.example ✅
├── .gitignore ✅
├── docker-compose.yml ✅
├── readme.md ✅
└── requirements.txt ✅
```

---

## Phase 1 : Infrastructure Base de Données 🔄

### ⏳ 1.1 Installation SQL Server
- [ ] Installer ODBC Driver 18 pour SQL Server (macOS/Linux/Windows)
- [ ] Tester connexion avec `pyodbc`
- [ ] Configurer SQL Server dans Docker (`docker-compose up -d sqlserver`)

**Documentation** : Suivre `docs/SQL_SERVER_SETUP.md`

**Commandes** :
```bash
# macOS (Homebrew)
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 mssql-tools18

# Vérifier installation
odbcinst -j

# Démarrer SQL Server
docker-compose up -d sqlserver
```

### ⏳ 1.2 Création des modèles SQLAlchemy
- [ ] Créer `backend/db/models.py` avec les tables :
  - `sources` : Sites web scrappés (nom, URL, crédibilité)
  - `raw_pages` : Métadonnées des pages HTML scrappées
  - `datalake_files` : Index des fichiers dans le Data Lake
  - `extracted_items` : Données structurées extraites (armes, classes, stats)
  - `consensus` : Résultats finaux agrégés
- [ ] Créer `backend/db/connection.py` pour gérer la connexion SQL Server

**Fichier à créer** : `backend/db/models.py` (~200 lignes)

### ⏳ 1.3 Migrations Alembic
- [ ] Initialiser Alembic : `alembic init backend/db/migrations`
- [ ] Configurer `alembic.ini` avec la connexion SQL Server
- [ ] Créer la première migration : `alembic revision --autogenerate -m "Initial schema"`
- [ ] Appliquer la migration : `alembic upgrade head`

**Documentation** : Section "Alembic Migrations" dans `docs/SQL_SERVER_SETUP.md`

### ⏳ 1.4 Scripts de setup
- [ ] Créer `scripts/setup_database.py` pour initialiser les tables
- [ ] Créer `scripts/test_connection.py` pour tester la connexion SQL Server
- [ ] Créer `scripts/test_datalake.py` pour tester upload/download MinIO

**Validation** : Exécuter les scripts de test sans erreur

---

## Phase 2 : Premier Scraper (MVP avec 1 source) ⏳

### ⏳ 2.1 Classe de base pour les parsers
- [ ] Créer `backend/scraper/parsers/base_parser.py`
  - Classe abstraite `BaseParser` avec méthodes :
    - `fetch_page()` : Télécharge une page HTML
    - `parse()` : Méthode abstraite à implémenter par chaque parser
    - `extract_weapons()` : Extraction des armes
    - `extract_stats()` : Extraction des statistiques
    - `save_to_bronze()` : Sauvegarde dans Data Lake + SQL Server

**Fichier à créer** : `backend/scraper/parsers/base_parser.py` (~150 lignes)

### ⏳ 2.2 Premier parser concret (PC Gamer)
- [ ] Créer `backend/scraper/parsers/pcgamer_parser.py`
  - Classe `PCGamerParser` héritant de `BaseParser`
  - Inspection manuelle de https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build
  - Extraction avec BeautifulSoup (sélecteurs CSS)
  - Test d'extraction sur une page réelle

**Fichier à créer** : `backend/scraper/parsers/pcgamer_parser.py` (~100 lignes)

### ⏳ 2.3 Orchestration du scraping
- [ ] Créer `backend/scraper/orchestrator.py`
  - Fonction `scrape_all_sources()` qui appelle chaque parser
  - Gestion des erreurs avec `tenacity` (3 tentatives, backoff exponentiel)
  - Logging avec `loguru`
  - Sauvegarde HTML dans Data Lake + métadonnées dans SQL Server

**Fichier à créer** : `backend/scraper/orchestrator.py` (~120 lignes)

### ⏳ 2.4 Tests du scraper
- [ ] Créer `scripts/test_scraper.py` pour tester manuellement
- [ ] Créer `tests/test_parsers.py` avec pytest
  - Test d'extraction sur HTML mock
  - Test de sauvegarde dans Data Lake
  - Test de sauvegarde des métadonnées SQL Server

**Validation** : Scraper capable d'extraire des données de PC Gamer et les sauvegarder

---

## Phase 3 : Pipeline Complet Bronze → Silver → Gold ⏳

### ⏳ 3.1 Normalisation des données (Silver layer)
- [ ] Créer `backend/utils/normalization.py`
  - Fonction `normalize_tier()` : S-tier → 1.0, A-tier → 0.8, etc.
  - Fonction `normalize_percentage()` : 95% win rate → 0.95
  - Fonction `normalize_rank()` : Rank #1 → 1.0, #10 → 0.1
  - Fonction `normalize_all()` : Applique toutes les normalisations

**Fichier à créer** : `backend/utils/normalization.py` (~80 lignes)

### ⏳ 3.2 Calcul du consensus (Gold layer)
- [ ] Créer `backend/utils/consensus.py`
  - Fonction `calculate_weighted_score()` :
    - Score = Σ(score_normalisé × crédibilité_source × fraicheur_données) / Σ(crédibilité × fraicheur)
  - Fonction `generate_consensus()` : Calcule le consensus pour toutes les armes
  - Sauvegarde dans la table `consensus`

**Fichier à créer** : `backend/utils/consensus.py` (~100 lignes)

### ⏳ 3.3 Tests du pipeline
- [ ] Créer `tests/test_consensus.py`
  - Test de normalisation avec données fictives
  - Test de calcul du consensus avec 3 sources simulées
  - Test de cohérence (score entre 0 et 1)

**Validation** : Pipeline complet fonctionnel de scraping → normalisation → consensus

---

## Phase 4 : API FastAPI & Frontend Next.js 📝

### 📝 4.1 API FastAPI
- [ ] Créer `backend/api/main.py` avec FastAPI
  - Endpoints GET `/weapons/top` (top 10 armes)
  - Endpoint GET `/weapons/{weapon_name}` (détails arme)
  - Endpoint GET `/classes/top` (top classes)
  - Documentation Swagger automatique
- [ ] Créer `backend/api/schemas.py` avec modèles Pydantic
- [ ] Créer `backend/Dockerfile` pour conteneuriser l'API
- [ ] Tester avec `uvicorn backend.api.main:app --reload`

**Validation** : API accessible sur http://localhost:8000/docs

### 📝 4.2 Frontend Next.js
- [ ] Initialiser projet Next.js : `npx create-next-app@latest frontend`
- [ ] Créer composants :
  - `WeaponCard.tsx` : Affichage d'une arme avec stats
  - `TopWeaponsList.tsx` : Liste des top armes
  - `FilterBar.tsx` : Filtres (arme, classe, patch)
- [ ] Intégrer l'API backend avec `fetch()` ou `axios`
- [ ] Créer `frontend/Dockerfile`

**Validation** : Frontend accessible sur http://localhost:3000

---

## Phase 5 : Production & Monitoring 📝

### 📝 5.1 Cache Redis
- [ ] Configurer Redis dans `docker-compose.yml` (déjà fait ✅)
- [ ] Créer `backend/utils/cache.py` pour gérer le cache
- [ ] Cacher les résultats de consensus (TTL 1 heure)

### 📝 5.2 Monitoring & Alertes
- [ ] Configurer Sentry pour monitoring erreurs
- [ ] Créer webhook Discord/Slack pour alertes scraping
- [ ] Dashboard de monitoring des scrapers

### 📝 5.3 Migration Azure Blob Storage (Data Lake production)
- [ ] Configurer Azure Blob Storage (compte + container)
- [ ] Mettre à jour `backend/utils/datalake.py` pour basculer sur Azure (déjà supporté ✅)
- [ ] Migrer les données de MinIO vers Azure

**Validation** : Monitoring actif + Data Lake en production sur Azure

---

## Phase 6 : AI & Analytics 📝

### 📝 6.1 Analyse d'images/vidéos
- [ ] Utiliser Azure AI Vision pour extraire du texte des images de loadouts
- [ ] Parser les vidéos YouTube pour détecter les armes utilisées
- [ ] Enrichir la base de données avec ces données visuelles

### 📝 6.2 Prédictions ML
- [ ] Modèle de prédiction de la méta future (scikit-learn)
- [ ] Analyse de tendances temporelles
- [ ] Recommandations personnalisées de loadouts

---

## 📊 Récapitulatif Global

| Phase | Nom | Statut | Fichiers créés | Fichiers restants |
|-------|-----|--------|----------------|-------------------|
| **Phase 0** | Initialisation | ✅ **Complet** | 17/17 | 0 |
| **Phase 1** | Infrastructure DB | 🔄 **0% (0/8)** | 0/8 | 8 |
| **Phase 2** | Premier Scraper | ⏳ **0% (0/7)** | 0/7 | 7 |
| **Phase 3** | Pipeline Complet | ⏳ **0% (0/5)** | 0/5 | 5 |
| **Phase 4** | API + Frontend | 📝 **0% (0/10)** | 0/10 | 10 |
| **Phase 5** | Production | 📝 **0% (0/5)** | 0/5 | 5 |
| **Phase 6** | AI & Analytics | 📝 **Planifié** | 0/? | ? |
| **TOTAL** | | **36% (17/47)** | **17/47** | **30** |

---

## 🚀 Prochaine Étape Recommandée

**Phase 1.1** : Installation SQL Server et test de connexion
- Suivre le guide `docs/SQL_SERVER_SETUP.md`
- Installer ODBC Driver 18
- Démarrer SQL Server avec `docker-compose up -d sqlserver`
- Tester avec `scripts/test_connection.py` (à créer)

## 11. Pitch technique (30 sec)

Ce projet agrège automatiquement les données de plusieurs sites Battlefield pour identifier la méta actuelle.
Il repose sur un pipeline Python + SQL Server, orchestré via Docker et exposé par une API FastAPI.
Les résultats agrégés sont publiés sur un site Next.js léger, garantissant performance, transparence et respect des règles d'éthique du scraping.
