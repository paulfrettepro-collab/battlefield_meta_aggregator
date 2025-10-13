# 📁 Structure du Projet Battlefield Meta Aggregator

## Vue d'ensemble de l'arborescence

```
battlefield_meta_aggregator/
│
├── 📄 Configuration & Documentation Racine
│   ├── readme.md                    # Documentation principale du projet
│   ├── requirements.txt             # Dépendances Python
│   ├── docker-compose.yml           # Orchestration des services
│   ├── .gitignore                   # Fichiers exclus de Git
│   ├── .env.example                 # Template des variables d'environnement
│   ├── .env                         # Variables d'environnement (SECRET)
│   │
│   ├── DATA_LAKE_GUIDE.md          # Guide d'utilisation du Data Lake
│   ├── SQL_SERVER_SETUP.md         # Guide d'installation SQL Server
│   └── STACK_ANALYSIS.md           # Analyse de la stack technique
│
├── 📂 backend/                      # Code Python du backend
│   ├── __init__.py                  # Module principal backend
│   │
│   ├── scraper/                     # Module de scraping
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Orchestration du scraping (À CRÉER)
│   │   ├── scheduler.py             # Planification APScheduler (À CRÉER)
│   │   └── parsers/                 # Parsers spécifiques par site
│   │       ├── __init__.py
│   │       ├── base_parser.py       # Classe abstraite de base (À CRÉER)
│   │       ├── pcgamer_parser.py    # Parser PC Gamer (À CRÉER)
│   │       └── codmunity_parser.py  # Parser CODMunity (À CRÉER)
│   │
│   ├── db/                          # Base de données SQL Server
│   │   ├── __init__.py
│   │   ├── models.py                # Modèles SQLAlchemy (À CRÉER)
│   │   ├── connection.py            # Connexion DB (À CRÉER)
│   │   └── migrations/              # Alembic migrations (À INITIALISER)
│   │
│   ├── api/                         # API FastAPI
│   │   ├── __init__.py
│   │   ├── main.py                  # Point d'entrée FastAPI (À CRÉER)
│   │   ├── routes/                  # Routes par domaine (À CRÉER)
│   │   └── schemas.py               # Schémas Pydantic (À CRÉER)
│   │
│   └── utils/                       # Utilitaires
│       ├── __init__.py
│       ├── datalake.py              # ✅ Gestion Data Lake (MinIO/Azure)
│       ├── consensus.py             # Calcul du consensus (À CRÉER)
│       └── logger.py                # Configuration Loguru (À CRÉER)
│
├── 📂 frontend/                     # Application Next.js (À CRÉER)
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── public/
│
├── 📂 scripts/                      # Scripts utilitaires
│   ├── setup_database.py            # Création des tables SQL (À CRÉER)
│   ├── test_scraper.py              # Tests du scraper (À CRÉER)
│   └── test_datalake.py             # Tests du Data Lake (À CRÉER)
│
├── 📂 tests/                        # Tests unitaires
│   ├── test_parsers.py              # Tests des parsers (À CRÉER)
│   ├── test_consensus.py            # Tests du consensus (À CRÉER)
│   └── test_api.py                  # Tests API (À CRÉER)
│
└── 📂 docs/                         # Documentation supplémentaire
    ├── PROJECT_STRUCTURE.md         # Ce fichier
    ├── API_DOCUMENTATION.md         # Doc des endpoints (À CRÉER)
    └── DEPLOYMENT_GUIDE.md          # Guide de déploiement (À CRÉER)
```

## Description des dossiers

### 📁 `/backend/`
**Rôle** : Contient tout le code Python du backend (scraping, API, base de données).

#### `/backend/scraper/`
- **orchestrator.py** : Coordonne l'exécution des scrapers, gère l'ordre, les erreurs
- **scheduler.py** : Configure APScheduler pour automatiser les scrapes (tous les dimanches 2h)
- **parsers/** : Un fichier Python par site web à scraper (PC Gamer, CODMunity, etc.)

#### `/backend/db/`
- **models.py** : Définit les tables SQLAlchemy (sources, raw_pages, datalake_files, extracted_items, consensus)
- **connection.py** : Gère la connexion à SQL Server avec pyodbc
- **migrations/** : Historique des modifications de schéma avec Alembic

#### `/backend/api/`
- **main.py** : Application FastAPI principale avec CORS, middleware
- **routes/** : Endpoints par domaine (weapons, classes, vehicles)
- **schemas.py** : Modèles Pydantic pour validation des requêtes/réponses

#### `/backend/utils/`
- **datalake.py** : ✅ Module de gestion du Data Lake (MinIO dev, Azure Blob prod)
- **consensus.py** : Algorithme de calcul du consensus pondéré
- **logger.py** : Configuration centralisée de Loguru

### 📁 `/frontend/`
Application Next.js pour visualiser les données de consensus.

### 📁 `/scripts/`
Scripts Python standalone pour setup, tests, maintenance.

### 📁 `/tests/`
Tests unitaires avec pytest pour valider chaque composant.

### 📁 `/docs/`
Documentation technique supplémentaire (API, déploiement, etc.).

## Fichiers de configuration racine

| Fichier | Description | Statut |
|---------|-------------|--------|
| **readme.md** | Documentation principale avec specs, roadmap, étapes détaillées | ✅ Créé |
| **requirements.txt** | 40+ dépendances Python (FastAPI, SQLAlchemy, BeautifulSoup, etc.) | ✅ Créé |
| **docker-compose.yml** | 5 services (SQL Server, Redis, MinIO, Backend, Frontend) | ✅ Créé |
| **.gitignore** | Exclusions Git (Python cache, Node modules, .env) | ✅ Créé |
| **.env.example** | Template des variables (DATABASE_URL, API_KEY, etc.) | ✅ Créé |
| **.env** | Variables d'environnement réelles (SECRET, non committé) | ✅ Créé |
| **DATA_LAKE_GUIDE.md** | Guide complet du Data Lake avec exemples Python | ✅ Créé |
| **SQL_SERVER_SETUP.md** | Installation SQL Server, ODBC driver, schéma DB | ✅ Créé |
| **STACK_ANALYSIS.md** | Validation de la stack technique vs besoins métier | ✅ Créé |

## Prochaines étapes de développement

1. **Phase 1 - Setup Infrastructure** (En cours)
   - ✅ Structure de dossiers créée
   - ⏳ Créer `backend/db/models.py` avec les tables SQLAlchemy
   - ⏳ Créer `backend/db/connection.py` pour connexion SQL Server
   - ⏳ Initialiser Alembic pour les migrations

2. **Phase 2 - Premier Scraper**
   - ⏳ Créer `backend/scraper/parsers/base_parser.py` (classe abstraite)
   - ⏳ Implémenter `backend/scraper/parsers/pcgamer_parser.py`
   - ⏳ Créer `scripts/test_scraper.py` pour tester

3. **Phase 3 - Pipeline Bronze/Silver/Gold**
   - ⏳ Intégrer Data Lake dans le scraper (HTML → MinIO)
   - ⏳ Parser HTML → Extraction données structurées
   - ⏳ Calcul du consensus avec `backend/utils/consensus.py`

4. **Phase 4 - API FastAPI**
   - ⏳ Créer `backend/api/main.py` avec endpoints
   - ⏳ Créer `backend/api/schemas.py` (Pydantic models)
   - ⏳ Documenter avec Swagger/OpenAPI

5. **Phase 5 - Frontend Next.js**
   - ⏳ Initialiser projet Next.js
   - ⏳ Créer composants de visualisation
   - ⏳ Intégrer avec API backend

## Commandes utiles

```bash
# Structure actuelle du projet
tree -L 3 -I '__pycache__|*.pyc|node_modules'

# Démarrer les services Docker
docker-compose up -d

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer les tests
pytest tests/ -v

# Lancer l'API FastAPI (après création)
cd backend/api && uvicorn main:app --reload

# Lancer le frontend (après création)
cd frontend && npm run dev
```

---

**Dernière mise à jour** : 13 octobre 2025  
**Version du projet** : 0.1.0 (Setup initial)
