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

## 10. Roadmap

| Phase | Description | Livrables | Stack ajoutée |
|-------|-------------|-----------|---------------|
| 0 | Initialisation projet | Repo GitHub + Docker + .gitignore + .env ✅ | Git, Docker, SQL Server |
| 1 | MVP (1 source) | Scraping + parsing + stockage bronze/silver/gold + Data Lake | Python, BeautifulSoup, SQL Server, SQLAlchemy, MinIO |
| 2 | Multi-sources | Scraping 10 sources + consensus pondéré + retry + Data Lake | Tenacity, APScheduler, Loguru |
| 3 | Front-end + Data Lake | API FastAPI + Next.js + classements & filtres + accès Data Lake | FastAPI, Next.js, Swagger |
| 4 | Production | Cache Redis + monitoring Sentry + alertes Discord + Azure Blob | Redis, Sentry, Webhooks, Azure Blob Storage |
| 5 | AI & Analytics | Analyse images/vidéos Data Lake + ML prédictions méta | Azure AI Vision, scikit-learn, TensorFlow |

## 11. Pitch technique (30 sec)

Ce projet agrège automatiquement les données de plusieurs sites Battlefield pour identifier la méta actuelle.
Il repose sur un pipeline Python + SQL Server, orchestré via Docker et exposé par une API FastAPI.
Les résultats agrégés sont publiés sur un site Next.js léger, garantissant performance, transparence et respect des règles d'éthique du scraping.
