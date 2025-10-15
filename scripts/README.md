# 🛠️ Scripts - Utilitaires du projet

**Rôle** : Scripts d'automatisation et utilitaires pour le pipeline

## 📁 Contenu

Ce dossier contiendra les scripts suivants (à créer pendant Phase 0.5 et Phase 1) :

### Scripts prévus

```
scripts/
├── upload_to_minio.py          # Upload crawls → MinIO (Bronze layer)
├── test_minio.py               # Test connexion MinIO
├── load_bigquery.py            # Charger MinIO → BigQuery
├── test_all_sources.py         # Tester toutes les sources (APIs + Scrapy)
└── README.md                   # Ce fichier
```

## 🚀 Scripts à créer

### 1. `upload_to_minio.py` (Action 2)
**Objectif** : Uploader automatiquement les résultats crawlés vers MinIO

**Usage** :
```bash
python scripts/upload_to_minio.py
```

**Code complet** : Voir `NEXT_STEPS.md` (Action 2)

### 2. `test_all_sources.py` (Phase 1)
**Objectif** : Tester toutes les sources de données (APIs + Scrapy)

**Usage** :
```bash
python scripts/test_all_sources.py

# Output attendu :
# ✅ EA API: 150 weapons retrieved
# ✅ Tracker.gg API: 45 loadouts retrieved
# ✅ Reddit API: 20 posts retrieved
# ✅ PC Gamer (Scrapy): 10 guides crawled
```

### 3. `load_bigquery.py` (Phase 2)
**Objectif** : Charger les données MinIO vers BigQuery (avant DBT)

**Usage** :
```bash
python scripts/load_bigquery.py --source pcgamer --date 2025-10-15
```

## 📊 État actuel

- ⏳ Dossier créé, scripts à implémenter après Phase 0.5 (exploration)
- ⏳ `upload_to_minio.py` sera le premier script créé (Action 2)
- ⏳ Autres scripts dépendent des sources choisies lors de l'exploration

## 🔗 Liens

- **NEXT_STEPS.md** : Guide complet avec code des scripts
- **docs/SOURCES_EXPLORATION.md** : Exploration des sources avant implémentation
