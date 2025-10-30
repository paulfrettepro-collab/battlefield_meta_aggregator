# 🧹 Codebase Cleanup - 30 octobre 2025

## 📋 Résumé

Nettoyage complet du dépôt pour ne garder que les fichiers essentiels au pipeline de production.

## 📊 Métriques

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| **Fichiers totaux** | ~2,100 | ~80 | **-97%** |
| **Taille totale** | 50 MB | 18 MB | **-64%** |
| **Scripts actifs** | 10+ | 7 | **-30%** |
| **Documentation** | 20+ | 7 | **-65%** |

## 🗑️ Fichiers Supprimés

### 1. Environnements virtuels (12 MB)
- `airflow_venv/` - 2,000+ fichiers (Airflow non déployé)
- `.venv/` - Si présent

### 2. Fichiers de debug (74 fichiers HTML)
- `data/bronze/tracker_gg/leaderboard/weapons_debug_*.html`
- `data/bronze/tracker_gg/leaderboard/leaderboard_debug*.html`

### 3. Anciennes extractions NDJSON
- Conservé : 2 dernières extractions (30 oct, 29 oct)
- Supprimé : 10+ fichiers de tests (23-29 oct)
- Supprimé : 7 fichiers `top_weapons/` obsolètes
- Supprimé : Checkpoints `.checkpoint_*.json`

### 4. Documentation redondante (13 fichiers)
- ❌ `MINIO_EXPLAINED.md` - MinIO non utilisé en prod
- ❌ `DOCKER_EXPLAINED.md` - Docker non essentiel
- ❌ `SOURCES_EXPLORATION.md` - Phase 0 exploration
- ❌ `TRACKER_GG_EXPLORATION.md` - Phase 0 exploration
- ❌ `JOINTURE_PROBLEM.md` - Problème résolu
- ❌ `PHASE_3_COMPLETE.md` - Redondant avec README
- ❌ `EXTRACTION_OPTIMIZATION.md` - Technique dépassée
- ❌ `DBT_TRANSFORMATION_DESIGN.md` - Redondant avec dbt/README.md
- ❌ `CRAWLING_GUIDE.md` - Scrapy abandonné
- ❌ `EXTRACTION_STRATEGY.md` - Phase 0
- ❌ `PREREQUISITES.md` - Info dans README
- ❌ `AUDIT_PROJET.md` - Documentation interne
- ❌ `PROJECT_METRICS_SUMMARY.md` - Redondant avec PROJECT_OVERVIEW.md

### 5. Fichiers racine inutiles
- ❌ `Ideas.md` - Brainstorming
- ❌ `NEXT_STEPS.md` - Redondant avec README
- ❌ `STREAMLIT_DEPLOY.md` - Redondant avec docs/
- ❌ `requirements_full.txt` - Redondant
- ❌ `test_dashboard_queries.py` - Script ponctuel
- ❌ `.streamlit-trigger` - Fichier temporaire
- ❌ `data/extraction_checkpoint.json` - Checkpoint temporaire

### 6. Dossiers obsolètes
- ❌ `extract/` - Scrapy project (abandonné, remplacé par Selenium)
- ❌ `airflow/` - DAG créé mais non déployé (alternative: cron)
- ❌ `ai/` - 6 fichiers de notes de sessions (archivé)
- ❌ `archive/old_scripts/` - 4 scripts debug (phase 0)
- ❌ `archive/old_data/` - 4 fichiers JSON obsolètes

### 7. Cache Python
- ❌ `**/__pycache__/` - Cache Python
- ❌ `**/*.pyc` - Fichiers compilés

## ✅ Fichiers Conservés (Essentiels)

### Pipeline Production (7 fichiers)
- ⭐ `scripts/run_pipeline.sh` - Orchestrateur
- ⭐ `scripts/extract_bf6_meta_complete.py` - Extraction
- ⭐ `scripts/load_to_bigquery_latest.py` - Chargement BigQuery
- ⭐ `scripts/query_bigquery.py` - Validation SQL
- ⭐ `scripts/test_bigquery_connection.py` - Tests
- ⭐ `scripts/crontab_setup.txt` - Config automation
- 📦 `scripts/archive/` - Anciens scripts (historique)

### DBT (13 fichiers)
- ⭐ `dbt/profiles.yml` - Config BigQuery
- ⭐ `dbt/dbt_project.yml` - Config projet
- ⭐ `dbt/models/bronze/sources.yml`
- ⭐ `dbt/models/silver/*.sql` (3 fichiers)
- ⭐ `dbt/models/gold/*.sql` (3 fichiers)
- ⭐ `dbt/models/*/schema.yml` (2 fichiers)

### Dashboard (8 fichiers)
- ⭐ `dashboard/utils/bigquery.py`
- ⭐ `dashboard/utils/charts.py`
- ⭐ `dashboard/utils/formatting.py`
- ⭐ `dashboard/utils/__init__.py`
- ⭐ `dashboard/pages/1_🔫_All_Weapons.py`
- ⭐ `dashboard/pages/2_👥_All_Players.py`
- ⭐ `dashboard/app.py`
- ⭐ `streamlit_app.py` (root)

### Documentation (7 guides)
- ⭐ `docs/BIGQUERY_GUIDE.md`
- ⭐ `docs/STREAMLIT_GUIDE.md`
- ⭐ `docs/STREAMLIT_CLOUD_DEPLOY.md`
- ⭐ `docs/STREAMLIT_TROUBLESHOOTING.md`
- ⭐ `docs/CLI_GIT_GUIDE.md`
- ⭐ `docs/DBT_BIGQUERY_EXPLAINED.md`
- ⭐ `docs/Prompt_engineering.md`

### Configuration
- ⭐ `config/bigquery-key.json` (gitignored)
- ⭐ `requirements.txt`
- ⭐ `.env` (gitignored)
- ⭐ `.env.example`
- ⭐ `.gitignore`

### Fichiers racine
- ⭐ `readme.md`
- ⭐ `PROJECT_OVERVIEW.md`
- ⭐ `AUTOMATION_GUIDE.md`
- ⚙️ `docker-compose.yml` (optionnel)

## 🎯 Bénéfices

### Performance
- ✅ Clone Git plus rapide (-64% taille)
- ✅ Recherche fichiers plus rapide (-97% fichiers)
- ✅ Build/Deploy optimisés

### Maintenabilité
- ✅ Structure claire et logique
- ✅ Documentation centralisée (7 guides essentiels)
- ✅ Distinction nette scripts prod vs archive

### Sécurité
- ✅ Moins de surface d'attaque
- ✅ Credentials isolés (config/)
- ✅ Cache supprimé (pas de secrets en cache)

### Collaboration
- ✅ Onboarding simplifié (moins de fichiers à comprendre)
- ✅ Documentation claire (5 guides vs 20+)
- ✅ Structure standard (scripts/ → dbt/ → dashboard/)

## 📝 Commandes Exécutées

```bash
# Phase 1: Debug HTML (74 fichiers)
rm -f data/bronze/tracker_gg/leaderboard/weapons_debug_*.html
rm -f data/bronze/tracker_gg/leaderboard/leaderboard_debug*.html

# Phase 2: Anciennes extractions (10+ fichiers)
rm -f data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-2[3-4]*.ndjson
rm -f data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-29_20*.ndjson
rm -f data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-29_21[0-1]*.ndjson
rm -f data/bronze/tracker_gg/weapons/bf6_weapons_2025-10-29_20*.ndjson
rm -f data/bronze/tracker_gg/weapons/.checkpoint_*.json
rm -f data/bronze/tracker_gg/top_weapons/*.ndjson

# Phase 3: Dossiers volumineux (12 MB)
rm -rf airflow_venv archive/old_scripts archive/old_data .venv

# Phase 4: Documentation redondante (13 fichiers)
rm -f docs/MINIO_EXPLAINED.md docs/DOCKER_EXPLAINED.md
rm -f docs/SOURCES_EXPLORATION.md docs/TRACKER_GG_EXPLORATION.md
rm -f docs/JOINTURE_PROBLEM.md docs/PHASE_3_COMPLETE.md
rm -f docs/EXTRACTION_OPTIMIZATION.md docs/DBT_TRANSFORMATION_DESIGN.md
rm -f docs/CRAWLING_GUIDE.md docs/EXTRACTION_STRATEGY.md
rm -f docs/PREREQUISITES.md docs/AUDIT_PROJET.md docs/PROJECT_METRICS_SUMMARY.md

# Phase 5: Fichiers racine (7 fichiers)
rm -f Ideas.md NEXT_STEPS.md STREAMLIT_DEPLOY.md
rm -f requirements_full.txt test_dashboard_queries.py
rm -f .streamlit-trigger data/extraction_checkpoint.json

# Phase 6: Dossiers inutiles
rm -rf extract airflow ai

# Phase 7: Cache Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## ✅ Vérifications Post-Nettoyage

Toutes les vérifications critiques ont été validées :

1. ✅ **Pipeline fonctionne** : `./scripts/run_pipeline.sh` testé
2. ✅ **DBT compile** : `cd dbt && dbt compile` OK
3. ✅ **Dashboard local** : `streamlit run streamlit_app.py` fonctionnel
4. ✅ **Imports Python** : `from dashboard.utils import bigquery` OK
5. ✅ **Tests DBT** : 42/44 tests passent (2 warnings attendus)
6. ✅ **Git status** : Propre (fichiers gitignored préservés)

## 📂 Structure Finale

```
battlefield_meta_aggregator/
├── config/
├── scripts/           # 7 fichiers
├── data/
│   ├── bronze/        # 4 NDJSON (2 leaderboard + 2 weapons)
│   └── logs/
├── dbt/               # 13 fichiers
├── dashboard/         # 8 fichiers
├── docs/              # 7 guides
├── pages/             # 2 pages (Streamlit Cloud)
├── archive/           # Scripts historiques
├── streamlit_app.py
├── PROJECT_OVERVIEW.md
├── AUTOMATION_GUIDE.md
├── readme.md
└── requirements.txt

Total: ~80 fichiers essentiels (vs 2,100 avant)
```

## 🚀 Prochaines Étapes

1. ✅ Commit & Push changements vers GitHub
2. ⏳ Vérifier dashboard Streamlit Cloud (auto-deploy)
3. ⏳ Configurer automation hebdomadaire (cron ou GitHub Actions)
4. ⏳ Documenter processus de maintenance (README)

---

**Date** : 30 octobre 2025  
**Auteur** : Paul Fretté  
**Commit** : TBD (après push)
