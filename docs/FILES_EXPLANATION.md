# 📚 Guide d'Explication des Fichiers du Projet

## 🎯 Vue d'ensemble

Ce document explique en détail le rôle de **chaque fichier créé** depuis le début du projet Battlefield Meta Aggregator.

---

## 📄 Fichiers de Configuration Racine

### **readme.md**
- **Rôle** : Documentation principale et centrale du projet
- **Contenu** :
  - Présentation du projet et contexte métier
  - Spécifications techniques complètes
  - Architecture Bronze/Silver/Gold + Data Lake
  - Stack technique (MVP et Production)
  - Roadmap par phases
  - Guide de contribution Git (sandbox/staging/main)
- **Utilisation** : Point d'entrée pour comprendre le projet entier
- **Statut** : ✅ Créé et complet (198 lignes)

---

### **requirements.txt**
- **Rôle** : Liste exhaustive des dépendances Python du projet
- **Contenu** : 40+ packages organisés par catégories :
  - **Core API** : `fastapi`, `uvicorn` (serveur ASGI)
  - **Scraping** : `requests`, `beautifulsoup4`, `selenium`, `webdriver-manager`
  - **Database** : `sqlalchemy`, `alembic`, `pyodbc` (SQL Server)
  - **Scheduling** : `apscheduler` (automatisation hebdomadaire)
  - **Error Handling** : `tenacity` (retry avec backoff exponentiel)
  - **Logging** : `loguru` (logs structurés)
  - **Data Lake** : `azure-storage-blob`, `minio`, `boto3`
  - **Cache** : `redis`
  - **Monitoring** : `sentry-sdk`
- **Utilisation** : `pip install -r requirements.txt` pour installer toutes les dépendances
- **Statut** : ✅ Créé et complet

---

### **docker-compose.yml**
- **Rôle** : Orchestration multi-services pour environnement de développement
- **Services définis** (5 au total) :
  1. **sqlserver** : SQL Server 2022 (port 1433)
     - Image : `mcr.microsoft.com/mssql/server:2022-latest`
     - Variables : `ACCEPT_EULA=Y`, `MSSQL_SA_PASSWORD`
     - Volume : `sqlserver_data` pour persistance
  2. **redis** : Redis 7 (port 6379)
     - Cache pour consensus (TTL 1h)
     - Volume : `redis_data`
  3. **minio** : MinIO (ports 9000 API, 9001 Console)
     - Data Lake pour développement
     - Credentials : `minioadmin/minioadmin`
     - Volume : `minio_data`
  4. **backend** : FastAPI (port 8000)
     - Build depuis `./backend/Dockerfile` (à créer)
     - Dépend de sqlserver, redis, minio
  5. **frontend** : Next.js (port 3000)
     - Build depuis `./frontend/Dockerfile` (à créer)
     - Dépend de backend
- **Utilisation** : `docker-compose up -d` pour démarrer tous les services
- **Statut** : ✅ Créé et complet

---

### **.gitignore**
- **Rôle** : Exclure les fichiers sensibles et générés de Git
- **Patterns inclus** :
  - Système : `.DS_Store`, `Thumbs.db`
  - Python : `__pycache__/`, `*.pyc`, `.venv/`, `venv/`
  - Node.js : `node_modules/`, `.next/`
  - Sécurité : `.env`, `.env.local`
  - Docker : `docker-compose.override.yml`
  - IDE : `.vscode/`, `.idea/`, `*.swp`
  - Data Lake : `data/raw/` (commenté, à activer si besoin)
- **Utilisation** : Automatique par Git pour ignorer les fichiers listés
- **Statut** : ✅ Créé et testé

---

### **.env.example**
- **Rôle** : Template des variables d'environnement pour les développeurs
- **Variables documentées** :
  - `DATABASE_URL` : Connexion SQL Server (`mssql+pyodbc://...`)
  - `MSSQL_SA_PASSWORD` : Mot de passe admin SQL Server
  - `ACCEPT_EULA` : Acceptation licence SQL Server
  - `API_PORT` : Port FastAPI (8000)
  - `FRONTEND_PORT` : Port Next.js (3000)
  - `REDIS_URL` : URL Redis pour cache
  - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` : Data Lake dev
  - `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_BLOB_CONTAINER` : Data Lake prod
  - `SENTRY_DSN` : Monitoring erreurs
- **Utilisation** : Copier en `.env` et remplir les valeurs réelles
- **Statut** : ✅ Créé avec toutes les variables nécessaires

---

### **.env**
- **Rôle** : Fichier contenant les valeurs réelles des variables d'environnement
- **Sécurité** : 
  - **JAMAIS committé** dans Git (protégé par `.gitignore`)
  - Contient les secrets (mots de passe, API keys, tokens)
- **Utilisation** : Chargé automatiquement par les applications (FastAPI, Docker)
- **Statut** : ✅ Créé (contenu secret)

---

## 📂 Documentation (dossier `/docs/`)

### **docs/DATA_LAKE_GUIDE.md**
- **Rôle** : Guide complet d'utilisation du Data Lake
- **Contenu** :
  - Explication Data Lake vs Database
  - Architecture (MinIO dev, Azure Blob prod)
  - Organisation des fichiers : `{source}/{type}/{year}/{month}/{day}/{filename}`
  - Exemples Python d'utilisation du module `backend/utils/datalake.py`
  - Guide de configuration MinIO et Azure Blob Storage
  - Analyse des coûts (<$0.50/mois pour ce projet)
  - Cas d'usage futurs (AI/ML, ré-parsing, analyse d'images/vidéos)
- **Utilisation** : Référence pour tout développeur travaillant avec le Data Lake
- **Statut** : ✅ Créé et complet (150+ lignes)

---

### **docs/SQL_SERVER_SETUP.md**
- **Rôle** : Guide d'installation et configuration SQL Server
- **Contenu** :
  - Installation du driver ODBC 18 (macOS/Linux/Windows)
  - Configuration Docker SQL Server
  - Test de connexion Python avec pyodbc
  - Schéma complet des tables (T-SQL) :
    - `sources` : Sites web scrappés
    - `raw_pages` : Métadonnées des pages HTML
    - `datalake_files` : Index des fichiers dans le Data Lake
    - `extracted_items` : Données structurées extraites (Silver)
    - `consensus` : Résultats finaux agrégés (Gold)
  - Configuration Alembic pour migrations
  - Installation Azure Data Studio (GUI)
  - Sécurité et hardening
  - Troubleshooting des erreurs courantes
- **Utilisation** : Suivre étape par étape pour setup SQL Server
- **Statut** : ✅ Créé et complet (200+ lignes)

---

### **docs/STACK_ANALYSIS.md**
- **Rôle** : Validation de la stack technique vs besoins métier
- **Contenu** :
  - Analyse besoin métier : scraper 10+ sites communautaires Battlefield
  - Validation de chaque technologie choisie :
    - **FastAPI** : Performance, auto-doc Swagger
    - **SQL Server** : Robustesse, transactions ACID
    - **BeautifulSoup/Selenium** : Scraping HTML statique/dynamique
    - **APScheduler** : Automatisation hebdomadaire
    - **Tenacity** : Gestion des erreurs réseau
    - **MinIO/Azure Blob** : Data Lake scalable
    - **Redis** : Cache pour performances
    - **Sentry** : Monitoring production
  - Améliorations apportées (APScheduler, Tenacity, Loguru, Redis, Sentry)
  - Roadmap par phases (4 phases : MVP, Multi-sources, Production, Scale)
  - Estimation des coûts ($17-30/mois en production)
  - Commandes pour démarrer Phase 1
- **Utilisation** : Comprendre pourquoi chaque techno a été choisie
- **Statut** : ✅ Créé et complet

---

### **docs/PROJECT_STRUCTURE.md**
- **Rôle** : Arborescence détaillée du projet avec descriptions
- **Contenu** :
  - Vue d'ensemble ASCII de la structure complète
  - Description de chaque dossier et son rôle
  - Statut de chaque fichier (✅ créé, ⏳ à créer)
  - Prochaines étapes de développement par phase
  - Commandes utiles (docker-compose, pytest, uvicorn, npm)
- **Utilisation** : Référence pour naviguer dans le projet
- **Statut** : ✅ Créé dans cette session

---

### **docs/FILES_EXPLANATION.md**
- **Rôle** : Ce fichier ! Explication détaillée de chaque fichier du projet
- **Contenu** : Description complète, rôle, utilisation, statut de chaque fichier
- **Utilisation** : Onboarding des nouveaux développeurs
- **Statut** : ✅ Créé dans cette session

---

## 🐍 Backend Python (dossier `/backend/`)

### **backend/__init__.py**
- **Rôle** : Déclare `backend/` comme un module Python importable
- **Contenu** : Docstring + version `__version__ = "0.1.0"`
- **Utilisation** : Permet d'importer avec `from backend import ...`
- **Statut** : ✅ Créé

---

### **backend/utils/datalake.py**
- **Rôle** : Module de gestion centralisée du Data Lake (MinIO dev + Azure Blob prod)
- **Contenu** :
  - **Classe `DataLakeManager`** :
    - Méthode `upload_file()` : Upload un fichier dans le Data Lake
    - Méthode `download_file()` : Télécharge un fichier depuis le Data Lake
    - Méthode `list_files()` : Liste les fichiers d'un dossier
    - Méthode `delete_old_files()` : Supprime les fichiers de plus de X jours
  - **Fonctions helpers** :
    - `save_html_to_datalake()` : Sauvegarde une page HTML scrappée
    - `save_json_to_datalake()` : Sauvegarde des métadonnées JSON
    - `_generate_path()` : Génère un chemin organisé `{source}/{type}/{year}/{month}/{day}/{filename}`
  - Support automatique MinIO (dev) ou Azure Blob (prod) selon variables d'env
  - Calcul de hash de contenu pour déduplication
  - Logging avec Loguru
- **Utilisation** :
  ```python
  from backend.utils.datalake import DataLakeManager
  dl = DataLakeManager()
  dl.upload_file("html_content", "pcgamer/html/2025/10/13/weapons.html")
  ```
- **Statut** : ✅ Créé et complet (150+ lignes)

---

### **backend/utils/__init__.py**
- **Rôle** : Déclare `backend/utils/` comme module Python
- **Contenu** : Docstring explicative
- **Utilisation** : Permet imports de `backend.utils.datalake`, `backend.utils.consensus`, etc.
- **Statut** : ✅ Créé

---

### **backend/scraper/__init__.py**
- **Rôle** : Déclare le module de scraping
- **Contenu** : Docstring
- **Utilisation** : Permet imports des scrapers et parsers
- **Statut** : ✅ Créé

---

### **backend/scraper/parsers/__init__.py**
- **Rôle** : Déclare le sous-module des parsers spécifiques par site
- **Contenu** : Docstring
- **Utilisation** : Permet imports de `backend.scraper.parsers.pcgamer_parser`
- **Statut** : ✅ Créé

---

### **backend/db/__init__.py**
- **Rôle** : Déclare le module de gestion de base de données
- **Contenu** : Docstring
- **Utilisation** : Permet imports de `backend.db.models`, `backend.db.connection`
- **Statut** : ✅ Créé

---

### **backend/api/__init__.py**
- **Rôle** : Déclare le module API FastAPI
- **Contenu** : Docstring
- **Utilisation** : Permet imports de `backend.api.main`, `backend.api.routes`
- **Statut** : ✅ Créé

---

## 📂 Dossiers créés (vides pour l'instant)

### **/frontend/**
- **Rôle** : Contiendra l'application Next.js React
- **À créer** : `package.json`, `next.config.js`, `src/app/`, `src/components/`
- **Statut** : ⏳ Dossier créé, contenu à ajouter en Phase 5

---

### **/scripts/**
- **Rôle** : Scripts Python standalone pour maintenance et tests
- **À créer** :
  - `setup_database.py` : Crée les tables SQL Server
  - `test_scraper.py` : Teste un scraper individuellement
  - `test_datalake.py` : Teste upload/download Data Lake
- **Statut** : ⏳ Dossier créé, scripts à ajouter en Phase 2-3

---

### **/tests/**
- **Rôle** : Tests unitaires avec pytest
- **À créer** :
  - `test_parsers.py` : Tests des parsers BeautifulSoup
  - `test_consensus.py` : Tests de l'algorithme de consensus
  - `test_api.py` : Tests des endpoints FastAPI
- **Statut** : ⏳ Dossier créé, tests à ajouter en Phase 2-4

---

## 🔄 Fichiers à créer (prochaines étapes)

### Phase 1 - Infrastructure
- [ ] `backend/db/models.py` : Modèles SQLAlchemy (tables sources, raw_pages, extracted_items, consensus, datalake_files)
- [ ] `backend/db/connection.py` : Connexion SQL Server avec pyodbc
- [ ] `backend/db/migrations/` : Initialiser Alembic
- [ ] `backend/utils/logger.py` : Configuration Loguru centralisée
- [ ] `scripts/setup_database.py` : Script pour créer les tables

### Phase 2 - Premier Scraper
- [ ] `backend/scraper/parsers/base_parser.py` : Classe abstraite pour tous les parsers
- [ ] `backend/scraper/parsers/pcgamer_parser.py` : Parser PC Gamer (premier site)
- [ ] `backend/scraper/orchestrator.py` : Orchestration du scraping (Bronze layer)
- [ ] `scripts/test_scraper.py` : Tests du scraper

### Phase 3 - Consensus
- [ ] `backend/utils/consensus.py` : Algorithme de consensus pondéré (Gold layer)
- [ ] `tests/test_consensus.py` : Tests unitaires consensus

### Phase 4 - API
- [ ] `backend/api/main.py` : Application FastAPI avec endpoints
- [ ] `backend/api/schemas.py` : Schémas Pydantic (requêtes/réponses)
- [ ] `backend/api/routes/weapons.py` : Routes pour les armes
- [ ] `backend/Dockerfile` : Image Docker pour le backend
- [ ] `tests/test_api.py` : Tests API

### Phase 5 - Frontend
- [ ] `frontend/package.json` : Dépendances Next.js
- [ ] `frontend/next.config.js` : Configuration Next.js
- [ ] `frontend/src/app/page.tsx` : Page d'accueil
- [ ] `frontend/src/components/WeaponCard.tsx` : Composant carte arme
- [ ] `frontend/Dockerfile` : Image Docker frontend

---

## 📊 Récapitulatif des Statuts

| Catégorie | Fichiers créés ✅ | Fichiers à créer ⏳ |
|-----------|-------------------|---------------------|
| **Configuration racine** | 6/6 (readme, requirements, docker-compose, .gitignore, .env.example, .env) | 0 |
| **Documentation** | 4/4 (DATA_LAKE_GUIDE, SQL_SERVER_SETUP, STACK_ANALYSIS, PROJECT_STRUCTURE, FILES_EXPLANATION) | 2 (API_DOCUMENTATION, DEPLOYMENT_GUIDE) |
| **Backend structure** | 6/6 (__init__.py pour tous les modules) | 0 |
| **Backend code** | 1/15 (datalake.py) | 14 (models, parsers, orchestrator, consensus, API, etc.) |
| **Frontend** | 0/10 | 10 (Next.js complet) |
| **Scripts** | 0/3 | 3 (setup_database, test_scraper, test_datalake) |
| **Tests** | 0/3 | 3 (test_parsers, test_consensus, test_api) |
| **TOTAL** | **17/47** | **30/47** |

---

## 🎯 Conclusion

### Ce qui est fait ✅
1. **Infrastructure de configuration** : Tous les fichiers de config (docker-compose, requirements, .env)
2. **Documentation complète** : 4 guides détaillés (README, Data Lake, SQL Server, Stack Analysis)
3. **Structure du projet** : Tous les dossiers et modules Python initialisés
4. **Premier module fonctionnel** : `datalake.py` prêt à l'emploi
5. **Git configuré** : Repository connecté à GitHub, .gitignore testé

### Ce qui reste à faire ⏳
1. **Phase 1** : Base de données (models, connection, migrations)
2. **Phase 2** : Premier scraper fonctionnel (parser PC Gamer)
3. **Phase 3** : Pipeline complet Bronze → Silver → Gold
4. **Phase 4** : API FastAPI avec endpoints
5. **Phase 5** : Frontend Next.js

### Prochaine action recommandée
Commencer par créer `backend/db/models.py` avec les modèles SQLAlchemy pour définir le schéma de la base de données.

---

**Date de création** : 13 octobre 2025  
**Auteur** : GitHub Copilot + Paul Frette  
**Version** : 1.0
