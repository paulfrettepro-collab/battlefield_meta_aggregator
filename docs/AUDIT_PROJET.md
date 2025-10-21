# 🔍 AUDIT COMPLET DU PROJET - 21 Octobre 2025

## 📊 État Actuel

### Taille Totale : ~320 MB
```
.venv/          314 MB  (dépendances Python - NORMAL)
archive/        1.5 MB  (anciens tests - À NETTOYER)
data/           1.4 MB  (données extraites)
extract/        176 KB  (Scrapy - OBSOLÈTE)
docs/           96 KB   (documentation)
scripts/        36 KB   (scripts actifs)
```

---

## 🗂️ Fichiers à la Racine (12 fichiers)

### ✅ À GARDER
| Fichier | Taille | Raison |
|---------|--------|--------|
| `readme.md` | 15 KB | ✅ Documentation principale |
| `requirements.txt` | 4 KB | ✅ Dépendances Python |
| `docker-compose.yml` | 1 KB | ✅ Configuration MinIO |
| `.env` | 8 KB | ✅ Variables d'environnement (local) |
| `.env.example` | 8 KB | ✅ Template (versionné) |
| `.gitignore` | 8 KB | ✅ Config Git |
| `cli_git_symboles_vs_code.md` | 24 KB | ✅ Guide de référence Git/CLI/Python/SQL |

### ❌ À SUPPRIMER OU DÉPLACER
| Fichier | Taille | Action | Raison |
|---------|--------|--------|--------|
| `STATUS_CURRENT.md` | 12 KB | ❌ Supprimer | Obsolète (18 oct, info dépassée) |
| `TODO.md` | 8 KB | ❌ Supprimer | Obsolète (18 oct) |
| `Prompt_engineering.md` | 8 KB | 🔄 Déplacer → `docs/` | Notes perso (utile mais mal placé) |
| `liste_defis_projet.md` | 4 KB | ❌ Supprimer | Obsolète |
| `.DS_Store` | 12 KB | ❌ Supprimer | Fichier macOS inutile |

---

## 📁 Dossiers

### ✅ Dossiers Actifs (À GARDER)

#### `scripts/` (36 KB)
```
extract_bf6_top_weapons.py      ✅ Script production (avec rank)
upload_to_minio.py              ✅ Upload MinIO
README.md                       ✅ Documentation
```

#### `data/` (1.4 MB)
```
data/
├── bronze/
│   ├── tracker_gg/top_weapons/
│   │   └── bf6_top_weapons_2025-10-20_200220.ndjson  ✅ Production (100 joueurs)
│   └── bf6_leaderboard_2025-10-18_174621.ndjson      ❌ Ancien test (à supprimer)
├── logs/                       ✅ Logs d'extraction
└── exploration/                ⚠️  Vérifier contenu
```

**Actions** :
- ✅ Garder `data/bronze/tracker_gg/top_weapons/bf6_top_weapons_2025-10-20_200220.ndjson`
- ❌ Supprimer `data/bronze/bf6_leaderboard_2025-10-18_174621.ndjson`
- 🔍 Vérifier `data/exploration/` (vieux fichiers HTML ?)

#### `docs/` (96 KB)
```
DOCKER_EXPLAINED.md             ✅ Guide Docker
JOINTURE_PROBLEM.md             ✅ Analyse jointure
CRAWLING_GUIDE.md               ⚠️  Obsolète ? (Scrapy)
EXTRACTION_STRATEGY.md          ⚠️  Obsolète ? (Scrapy)
MINIO_EXPLAINED.md              ⚠️  Doublon avec DOCKER_EXPLAINED ?
SOURCES_EXPLORATION.md          ⚠️  Obsolète ?
```

**Actions** :
- ✅ Garder `DOCKER_EXPLAINED.md`, `JOINTURE_PROBLEM.md`
- 🔍 Vérifier pertinence des autres (liés à Scrapy obsolète)

#### `.venv/` (314 MB)
✅ **NORMAL** - Environnement virtuel Python (dépendances)
- Déjà dans `.gitignore` ✅
- Ne pas versionner ✅

---

### ❌ Dossiers OBSOLÈTES (À NETTOYER)

#### `archive/` (1.5 MB) ⚠️ **GROS MÉNAGE NÉCESSAIRE**
```
TOTAL : 33 fichiers (1.5 MB)

Contenu :
• 6 fichiers NDJSON de test (bf6_top_weapons_2025-10-18/19/20_*.ndjson)
• 4 fichiers HTML debug (debug_*.html) - 1.3 MB !
• Anciens scripts Python (extract_10_*.py, explore_trackergg.py)
• Anciens docs (NEXT_STEPS.md, PROJECT_OVERVIEW.md, STATUS.md)
• .gitignore vide
```

**Actions** :
- ❌ Supprimer TOUS les fichiers HTML debug (1.3 MB libérés)
- ❌ Supprimer fichiers NDJSON de test (< 10 joueurs)
- ❌ Supprimer anciens scripts (obsolètes)
- ⚠️  Garder 1-2 docs si historique intéressant (sinon supprimer)
- ❌ Supprimer `.gitignore` vide dans archive/

#### `extract/` (176 KB) - **SCRAPY OBSOLÈTE**
```
Projet Scrapy complet (non utilisé)
• spiders/pcgamer_spider.py     ❌ Obsolète
• spiders/wzstats_spider.py     ❌ Obsolète
• items.py, settings.py, etc.   ❌ Obsolète
```

**Actions** :
- ❌ **Supprimer TOUT le dossier `extract/`**
- Raison : On utilise Selenium, pas Scrapy

#### `airflow/` (4 KB)
```
dags/ (vide)
README.md (4 KB)
```

**Actions** :
- ⚠️  Garder pour Phase 5 (automation future)
- OU ❌ Supprimer si on utilise cron job simple

#### `dashboard/` (4 KB)
```
pages/ (vide)
README.md (4 KB)
```

**Actions** :
- ⚠️  Garder pour Phase 4 (Streamlit)
- Structure vide OK pour l'instant

#### `dbt/` (4 KB)
```
models/
  bronze/ (vide)
  silver/ (vide)
  gold/ (vide)
README.md (4 KB)
```

**Actions** :
- ⚠️  Garder pour Phase 3 (transformations DBT)
- Structure vide OK pour l'instant

---

## 🔍 Problèmes Identifiés

### 1. ❌ Multiples `.gitignore`
```
/Users/.../battlefield_meta_aggregator/.gitignore          ✅ Principal
/Users/.../battlefield_meta_aggregator/archive/.gitignore   ❌ Vide (à supprimer)
/Users/.../battlefield_meta_aggregator/.venv/.gitignore     ✅ Normal (dépendances)
```

### 2. ❌ Fichiers Obsolètes à la Racine
- `STATUS_CURRENT.md` (18 oct - dépassé)
- `TODO.md` (18 oct - dépassé)
- `liste_defis_projet.md` (incomplet)
- `.DS_Store` (fichier système macOS)

### 3. ❌ Archive Surchargée
- 1.3 MB de fichiers HTML debug inutiles
- 6 fichiers NDJSON de test obsolètes
- Scripts Python dupliqués/obsolètes

### 4. ❌ Dossier `extract/` Inutilisé
- Projet Scrapy complet (176 KB)
- Non utilisé (on utilise Selenium)

### 5. ⚠️  Docs Potentiellement Redondants
- `MINIO_EXPLAINED.md` vs `DOCKER_EXPLAINED.md`
- Docs liés à Scrapy (`CRAWLING_GUIDE.md`, `EXTRACTION_STRATEGY.md`)

---

## 📋 Plan de Nettoyage

### Phase 1 : Racine (5 fichiers à supprimer)
```bash
rm STATUS_CURRENT.md
rm TODO.md
rm liste_defis_projet.md
rm .DS_Store
mv Prompt_engineering.md docs/
```

### Phase 2 : Archive (33 fichiers → 0-2 fichiers)
```bash
# Supprimer TOUS les fichiers HTML debug (1.3 MB)
rm archive/debug_*.html

# Supprimer TOUS les fichiers NDJSON de test
rm archive/bf6_top_weapons_*.ndjson

# Supprimer anciens scripts
rm archive/extract_*.py
rm archive/explore_*.py

# Supprimer .gitignore vide
rm archive/.gitignore

# Optionnel : garder 1 doc historique
# Supprimer le reste
rm archive/NEXT_STEPS.md
rm archive/PROJECT_OVERVIEW.md
rm archive/STATUS.md
```

### Phase 3 : Dossier `extract/` (Scrapy obsolète)
```bash
rm -rf extract/
```

### Phase 4 : Data (nettoyage léger)
```bash
# Supprimer ancien leaderboard
rm data/bronze/bf6_leaderboard_2025-10-18_174621.ndjson

# Vérifier data/exploration/ (anciens HTML ?)
ls -lh data/exploration/
# Si fichiers HTML debug : supprimer
```

### Phase 5 : Docs (vérification)
```bash
# Vérifier pertinence des docs liés à Scrapy
# Si obsolètes, supprimer :
# - CRAWLING_GUIDE.md
# - EXTRACTION_STRATEGY.md
# - SOURCES_EXPLORATION.md

# Vérifier doublon MINIO_EXPLAINED.md
# Fusionner avec DOCKER_EXPLAINED.md si nécessaire
```

---

## 🎯 Résultat Attendu

### Avant Nettoyage
```
Total : ~320 MB
Fichiers racine : 12
archive/ : 33 fichiers (1.5 MB)
extract/ : 176 KB (obsolète)
```

### Après Nettoyage
```
Total : ~318 MB (gain ~2 MB)
Fichiers racine : 7 (propres)
archive/ : 0-2 fichiers (< 50 KB)
extract/ : SUPPRIMÉ ✅
```

### Structure Finale Idéale
```
battlefield_meta_aggregator/
├── .env                           ✅ Variables (local)
├── .env.example                   ✅ Template (versionné)
├── .gitignore                     ✅ Config Git
├── .venv/                         ✅ Dépendances Python
├── docker-compose.yml             ✅ MinIO
├── readme.md                      ✅ Documentation principale
├── requirements.txt               ✅ Dépendances
├── cli_git_symboles_vs_code.md    ✅ Guide référence
│
├── scripts/                       ✅ Scripts actifs
│   ├── extract_bf6_top_weapons.py
│   ├── upload_to_minio.py
│   └── README.md
│
├── data/                          ✅ Données
│   ├── bronze/tracker_gg/top_weapons/
│   │   └── bf6_top_weapons_2025-10-20_200220.ndjson
│   └── logs/
│
├── docs/                          ✅ Documentation
│   ├── DOCKER_EXPLAINED.md
│   ├── JOINTURE_PROBLEM.md
│   ├── AUDIT_PROJET.md            🆕 Ce fichier
│   └── Prompt_engineering.md      🔄 Déplacé
│
├── dbt/                           ⚠️  Phase 3 (vide OK)
├── dashboard/                     ⚠️  Phase 4 (vide OK)
└── airflow/                       ⚠️  Phase 5 (vide OK)
```

---

## ✅ Validation

### Fichiers à Versionner (Git)
- ✅ Scripts production (`scripts/`)
- ✅ Documentation (`readme.md`, `docs/`)
- ✅ Configuration (`docker-compose.yml`, `.env.example`, `.gitignore`)
- ✅ Guide référence (`cli_git_symboles_vs_code.md`)
- ✅ Fichier production (`bf6_top_weapons_2025-10-20_200220.ndjson`)

### Fichiers à NE PAS Versionner
- ❌ `.env` (secrets - déjà dans .gitignore)
- ❌ `.venv/` (dépendances - déjà dans .gitignore)
- ❌ `data/logs/` (logs - déjà dans .gitignore)
- ❌ `.DS_Store` (système - à supprimer)

---

## 🚀 Exécution du Nettoyage

**Commandes à exécuter** :
```bash
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator

# Phase 1 : Racine
rm STATUS_CURRENT.md TODO.md liste_defis_projet.md .DS_Store
mv Prompt_engineering.md docs/

# Phase 2 : Archive (ATTENTION : vérifier avant)
rm archive/debug_*.html
rm archive/bf6_top_weapons_*.ndjson
rm archive/extract_*.py archive/explore_*.py
rm archive/.gitignore
rm archive/*.md

# Phase 3 : Scrapy obsolète
rm -rf extract/

# Phase 4 : Data
rm data/bronze/bf6_leaderboard_2025-10-18_174621.ndjson

# Commit
git add -A
git commit -m "chore: nettoyage complet projet"
git push origin main
```

**Gain estimé** : ~2 MB + structure claire et cohérente ✅
