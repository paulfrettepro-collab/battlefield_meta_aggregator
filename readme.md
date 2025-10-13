# Battlefield Meta Aggregator

## 1. Idée métier

Ce projet vise à construire un site web public qui agrège les données de plusieurs sites communautaires Battlefield afin de répondre à une question simple à chaque mise à jour du jeu :
> « Quelle est la méta actuelle ? »
> (armes les plus performantes, classes dominantes, meilleurs accessoires, etc.)

L'objectif est de collecter, normaliser et combiner les informations provenant de plusieurs sources fiables, puis de calculer un consensus global basé sur ces données.

---

## 2. Architecture technique (vue d'ensemble)

### Stack principale
- Python → scraping (Requests, BeautifulSoup, Selenium)
- FastAPI → création d'une API REST légère
- PostgreSQL → stockage structuré selon la logique bronze/silver/gold
- SQLAlchemy / Alembic → gestion ORM et migrations
- Docker & docker-compose → environnement portable et reproductible
- Next.js / React → front-end simple, connecté à l'API FastAPI
- GitHub Copilot + VS Code → écriture assistée et automatisée du code

### Structure des dossiers
```
battlefield-meta/
│
├── backend/
│   ├── main.py              # Entrée FastAPI
│   ├── scraper/
│   │   ├── sources.py       # URLs à scraper
│   │   ├── scraper.py       # Logique de scraping
│   │   ├── parser.py        # Extraction et nettoyage
│   │   └── consensus.py     # Calcul du consensus
│   ├── db/
│   │   ├── models.py        # Modèles SQLAlchemy
│   │   └── schema.sql       # Schéma initial
│   ├── utils/
│   │   └── normalization.py
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

### Bronze — Ingestion
- Scraping des pages publiques (Requests, BeautifulSoup)
- Sauvegarde des pages HTML ou JSON bruts dans PostgreSQL

### Silver — Transformation
- Extraction des entités principales : armes, classes, accessoires
- Nettoyage et harmonisation des noms et unités
- Structuration dans des tables extracted_items

### Gold — Synthèse
- Calcul d'un score normalisé pour chaque entité
- Pondération par crédibilité et fraîcheur des sources
- Calcul du consensus final (classement + justification)
- Stockage dans la table consensus

---

## 4. Modèle de données (simplifié)

| Table | Description |
|-------|-------------|
| sources | Liste des sites à scraper et leur stratégie |
| raw_pages | Données brutes (HTML/JSON) |
| extracted_items | Données extraites et nettoyées |
| consensus | Résultat agrégé et classé |

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

L'API interroge la couche gold dans PostgreSQL.

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

## 9. Sécurité & éthique

- Respect strict des robots.txt
- Pas de contournement d'authentification
- Attribution des sources avec lien direct
- Fréquence de scraping limitée pour éviter la surcharge
- Mise à disposition d'un contact pour demande de retrait

## 10. Roadmap

| Phase | Description | Livrables |
|-------|-------------|-----------|
| 0 | Initialisation projet | Repo GitHub + Docker OK |
| 1 | MVP (1 source) | Scraping, parsing, stockage |
| 2 | Multi-sources | Consensus pondéré |
| 3 | Front-end | Classements & filtres |
| 4 | Optimisation | Alertes, historiques, monétisation |

## 11. Pitch technique (30 sec)

Ce projet agrège automatiquement les données de plusieurs sites Battlefield pour identifier la méta actuelle.
Il repose sur un pipeline Python + PostgreSQL, orchestré via Docker et exposé par une API FastAPI.
Les résultats agrégés sont publiés sur un site Next.js léger, garantissant performance, transparence et respect des règles d'éthique du scraping.
