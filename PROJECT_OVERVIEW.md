# 📊 Structure du projet - Vue rapide

**Mise à jour : 15 octobre 2025**

## 🎯 Architecture moderne ELT

```
Scrapy/APIs → MinIO → BigQuery → DBT → Streamlit
   (Extract)  (Bronze)  (Silver)  (Gold) (Dashboard)
```

## 📁 Dossiers principaux

```
battlefield_meta_aggregator/
│
├── 📥 extract/                 ← EXTRACTION (Phase 1)
│   ├── apis/                  ← Clients API (après Phase 0.5)
│   └── spiders/               ← Scrapy crawlers
│       ├── pcgamer_spider.py  ✅
│       └── wzstats_spider.py  ✅
│
├── 🔄 dbt/                     ← TRANSFORMATION (Phase 2-3)
│   └── models/
│       ├── bronze/            ← Raw data
│       ├── silver/            ← Cleaned
│       └── gold/              ← KPIs
│
├── 🔀 airflow/                 ← ORCHESTRATION (Phase 3)
│   └── dags/                  ← DAGs quotidiens
│
├── 📊 dashboard/               ← VISUALISATION (Phase 4)
│   ├── app.py                 ← Streamlit app
│   └── pages/                 ← Multi-pages
│
├── 💾 data/                    ← DONNÉES LOCALES
│   ├── outputs/               ← Résultats crawls
│   ├── bronze/                ← Tests
│   └── exploration/           ← Findings Phase 0.5 ⭐
│
├── 🛠️ scripts/                 ← UTILITAIRES
│   └── (à créer après Phase 0.5)
│
└── 📚 docs/                    ← DOCUMENTATION
    ├── SOURCES_EXPLORATION.md ← Guide exploration ⭐
    ├── MINIO_EXPLAINED.md     ← Comprendre MinIO
    └── CRAWLING_GUIDE.md      ← Guide Scrapy
```

## 🚀 Fichiers clés

| Fichier | Rôle | Priorité |
|---------|------|----------|
| **NEXT_STEPS.md** | 🎯 Guide des prochaines étapes | 🔴 LIRE EN PREMIER |
| **docs/SOURCES_EXPLORATION.md** | 🔍 Méthodologie exploration | 🔴 Phase 0.5 actuelle |
| **readme.md** | 📖 Documentation complète | 🟢 Référence |
| **docker-compose.yml** | 🐳 MinIO + Airflow | 🟡 Setup infra |
| **requirements.txt** | 📦 Dépendances Python | 🟡 Installation |

## 📊 État actuel (15 oct 2025)

| Phase | Nom | État | Durée | Prochaine action |
|-------|-----|------|-------|------------------|
| 0 | Setup | ✅ FAIT | - | - |
| **0.5** | **Exploration** | 🔄 **EN COURS** | **2-3 jours** | **Lire docs/SOURCES_EXPLORATION.md** |
| 1 | Extraction | ⏳ À faire | 6-8h | Après 0.5 |
| 2 | BigQuery+DBT | ⏳ À faire | 1 semaine | Après 1 |
| 3 | Airflow | ⏳ À faire | 3-4 jours | Après 2 |
| 4 | Streamlit | ⏳ À faire | 2-3 jours | Après 3 |

## 🎯 Ta prochaine étape

### Phase 0.5 : Exploration des sources (⚠️ PRIORITÉ)

**Objectif** : Trouver des APIs (EA, Tracker.gg, Reddit) avant de coder

**Actions** :
1. 📖 Ouvrir `docs/SOURCES_EXPLORATION.md`
2. 🔍 Chercher "Battlefield API EA developer" sur Google
3. 🧪 Tester Tracker.gg avec DevTools (Network tab)
4. 🤖 Setup Reddit API (gratuit)
5. 📊 Remplir tableau comparatif
6. ✅ Choisir 5 sources finales

**Durée** : 2-3 jours d'exploration

**Livrable** : `data/exploration/findings_summary.md` avec décisions

## 📚 Documentation disponible

✅ **NEXT_STEPS.md** : Guide complet avec checklist  
✅ **docs/SOURCES_EXPLORATION.md** : Méthodologie exploration (550 lignes)  
✅ **docs/MINIO_EXPLAINED.md** : Comprendre MinIO simplement  
✅ **docs/CRAWLING_GUIDE.md** : Guide Scrapy avancé  
✅ **README.md** dans chaque dossier (extract/, dbt/, airflow/, etc.)

## 🧹 Nettoyage effectué

### Supprimé (obsolète)
- ❌ `backend/` (API FastAPI + SQL Server)
- ❌ `frontend/` (Next.js app)
- ❌ `tests/` (anciens tests)
- ❌ 8 fichiers docs obsolètes (SQL Server, ChromaDB, etc.)
- ❌ 3 scripts de test obsolètes

### Conservé (moderne)
- ✅ `extract/` (Scrapy + APIs futures)
- ✅ `dbt/` (Transformations SQL)
- ✅ `airflow/` (Orchestration)
- ✅ `dashboard/` (Streamlit)
- ✅ `data/` (Stockage local)
- ✅ 3 docs essentiels (SOURCES_EXPLORATION, MINIO_EXPLAINED, CRAWLING_GUIDE)

## 💡 Philosophie du projet

**APIs > Scraping** : Privilégier toujours les APIs officielles (plus rapide, stable, légal)

**ELT > ETL** : Charger d'abord (Load), transformer après dans BigQuery (Transform)

**Open Source** : 100% gratuit (BigQuery free tier, Streamlit Cloud, MinIO local)

**Simplicité** : 5 technologies (vs 12 avant) = -60% de complexité

---

**🚀 Commence par lire : `NEXT_STEPS.md` → Action 0.5**

Bon courage pour l'exploration ! 🔍
