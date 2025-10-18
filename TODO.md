# 📋 TODO - Battlefield 6 Meta Aggregator

**Dernière mise à jour** : 18 octobre 2025

---

## 🔴 PRIORITÉ ABSOLUE

### ⚠️ #1 : Retester API Tracker.gg
**Deadline** : 19-20 octobre 2025 (24-48h après création clé)

**Actions** :
1. ⏳ Attendre activation clé API (55b66bdc-3610-482e-b94c-aa0b2dbc93f9)
2. ⏳ Exécuter : `python scripts/test_api.py`
3. ⏳ Si ✅ SUCCESS → Développer `extract/apis/tracker_client.py`
4. ⏳ Si ❌ FAIL → Documenter dans `docs/TRACKER_GG_EXPLORATION.md`
5. ⏳ Si ❌ FAIL → Continuer avec Selenium comme méthode principale

**Pourquoi prioritaire** :
- API = Plus rapide, stable, légal
- Selenium = Fonctionnel mais plus fragile (changements HTML)
- Décision architecturale importante pour la suite

---

## 🟡 PHASE 1 : MinIO Upload

### Task 1.1 : Installer Docker Desktop
**Durée estimée** : 15 minutes

- [ ] Télécharger Docker Desktop : https://www.docker.com/products/docker-desktop
- [ ] Installer et lancer Docker Desktop
- [ ] Vérifier : `docker --version`
- [ ] Vérifier : `docker compose version`

### Task 1.2 : Lancer MinIO
**Durée estimée** : 10 minutes

- [ ] Exécuter : `docker compose up -d minio`
- [ ] Vérifier conteneur : `docker ps | grep minio`
- [ ] Ouvrir UI MinIO : http://localhost:9001
- [ ] Login : minioadmin / minioadmin
- [ ] Créer bucket `bf6-bronze`

### Task 1.3 : Tester upload
**Durée estimée** : 5 minutes

- [ ] Exécuter : `python scripts/upload_to_minio.py`
- [ ] Vérifier dans MinIO UI : bucket `bf6-bronze`
- [ ] Vérifier fichier uploadé : `bf6_leaderboard_2025-10-18.ndjson`

---

## 🟢 PHASE 2 : BigQuery Setup

### Task 2.1 : Créer projet Google Cloud
**Durée estimée** : 15 minutes

- [ ] Aller sur : https://console.cloud.google.com
- [ ] Créer nouveau projet : `battlefield-meta-aggregator`
- [ ] Activer BigQuery API
- [ ] Noter PROJECT_ID

### Task 2.2 : Configuration authentification
**Durée estimée** : 15 minutes

- [ ] Créer Service Account
- [ ] Télécharger clé JSON
- [ ] Sauvegarder : `gcp_credentials.json` (gitignored)
- [ ] Ajouter à `.env` : `GOOGLE_APPLICATION_CREDENTIALS=./gcp_credentials.json`

### Task 2.3 : Créer dataset BigQuery
**Durée estimée** : 10 minutes

- [ ] Dans BigQuery, créer dataset : `bf6_meta`
- [ ] Région : `US` (gratuit)
- [ ] Créer table : `bronze_leaderboard`
- [ ] Schema : rank INT, username_hash STRING, kills INT, etc.

### Task 2.4 : Load NDJSON → BigQuery
**Durée estimée** : 20 minutes

- [ ] Créer script : `scripts/load_to_bigquery.py`
- [ ] Tester import : fichier NDJSON → BigQuery
- [ ] Vérifier données dans BigQuery UI
- [ ] Query test : `SELECT * FROM bf6_meta.bronze_leaderboard LIMIT 10`

---

## 🔵 PHASE 3 : DBT Transformations

### Task 3.1 : Installer DBT Core
**Durée estimée** : 10 minutes

- [ ] Exécuter : `pip install dbt-bigquery`
- [ ] Init projet : `dbt init` (dans dossier `/dbt`)
- [ ] Configurer `profiles.yml` avec BigQuery credentials
- [ ] Tester : `dbt debug`

### Task 3.2 : Modèles Silver
**Durée estimée** : 1 heure

- [ ] Créer : `dbt/models/silver/silver_leaderboard.sql`
- [ ] Nettoyage : déduplication, typage
- [ ] Calculs : K/D ratio, ranks, percentiles
- [ ] Tests DBT : not_null, unique

### Task 3.3 : Modèles Gold
**Durée estimée** : 1 heure

- [ ] Créer : `dbt/models/gold/gold_top_players.sql`
- [ ] Agrégations : Top 10, Top 50, Top 100
- [ ] Trends : évolution quotidienne
- [ ] Documentation : `dbt docs generate`

---

## 🟣 PHASE 4 : Dashboard Streamlit

### Task 4.1 : Créer app Streamlit
**Durée estimée** : 1 heure

- [ ] Créer : `dashboard/app.py`
- [ ] Connexion BigQuery
- [ ] Page 1 : Top 10 players
- [ ] Graphique : Plotly bar chart

### Task 4.2 : Features avancées
**Durée estimée** : 1 heure

- [ ] Filtres : Date range, Top N
- [ ] Graphique : Évolution kills dans le temps
- [ ] Stats globales : Total kills, average K/D
- [ ] Styling : Thème gaming

### Task 4.3 : Déploiement
**Durée estimée** : 30 minutes

- [ ] Push code GitHub
- [ ] Connecter Streamlit Cloud
- [ ] Configurer secrets (BigQuery creds)
- [ ] Tester URL publique

---

## 🟤 PHASE 5 : Airflow Orchestration

### Task 5.1 : Setup Airflow
**Durée estimée** : 30 minutes

- [ ] Mise à jour `docker-compose.yml` (Airflow)
- [ ] Lancer : `docker compose up -d airflow`
- [ ] Accéder UI : http://localhost:8080
- [ ] Configurer connexions (MinIO, BigQuery)

### Task 5.2 : Créer DAG
**Durée estimée** : 30 minutes

- [ ] Créer : `airflow/dags/bf6_daily_pipeline.py`
- [ ] Tasks : Extract → Upload → Load → DBT → Notify
- [ ] Schedule : Quotidien 2h du matin
- [ ] Tests : Déclencher manuellement

---

## 📝 BACKLOG (Idées futures)

### Améliorations extraction
- [ ] Extraire loadouts par joueur (profiles individuels)
- [ ] Extraire stats par arme
- [ ] Extraire performances par carte/mode

### Analyses avancées
- [ ] Prédiction trends (ML)
- [ ] Corrélations armes/performances
- [ ] Clustering joueurs (styles de jeu)

### Features dashboard
- [ ] Comparaison joueurs
- [ ] Heatmaps performances
- [ ] Recommandations personnalisées

---

## ✅ TERMINÉ

### Phase 0 : Setup
- [x] Repository GitHub initialisé
- [x] Structure projet créée
- [x] Documentation rédigée
- [x] Docker-compose MinIO configuré

### Phase 0.5 : Extraction
- [x] Exploration Tracker.gg
- [x] Script Selenium développé
- [x] 100 joueurs extraits
- [x] Format NDJSON validé
- [x] Anonymisation implémentée
- [x] Clé API obtenue (en attente activation)

---

## 🎯 Objectif Hebdomadaire

**Semaine 1 (18-25 oct)** : Phases 1-2 complètes
- Extraction quotidienne automatique
- Données dans BigQuery
- Premières requêtes SQL

**Semaine 2 (25 oct - 1 nov)** : Phases 3-4 complètes
- DBT transformations opérationnelles
- Dashboard Streamlit déployé
- Visualisations interactives

**Semaine 3 (1-8 nov)** : Phase 5 + Polish
- Airflow automatisation complète
- Documentation utilisateur
- Présentation projet

---

## 📊 Progression Globale

```
Phase 0   : ████████████████████ 100%
Phase 0.5 : ████████████████████ 100%
Phase 1   : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 2   : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3   : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4   : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5   : ░░░░░░░░░░░░░░░░░░░░   0%

GLOBAL    : ████░░░░░░░░░░░░░░░░  20%
```

---

**Prochaine action** : Retester API Tracker.gg (19-20 oct 2025) 🔴
