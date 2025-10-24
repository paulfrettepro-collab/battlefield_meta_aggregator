# 🛠️ Scripts - Pipeline d'Extraction et Chargement

**Dernière mise à jour** : 24 octobre 2025  
**Rôle** : Scripts Python pour l'extraction, le stockage et le chargement des données

---

## 📁 Structure

```
scripts/
├── README.md                          # Ce fichier
│
├── 🎯 EXTRACTION (Phase 2.5)
│   ├── extract_bf6_leaderboard.py         # Extraction top 100 joueurs
│   └── extract_bf6_top_weapons_final.py   # Extraction top 3 armes par joueur
│
├── 📤 CHARGEMENT (Phase 2)
│   ├── upload_to_minio.py                 # Upload NDJSON → MinIO
│   └── upload_to_bigquery_v2.py           # Upload MinIO → BigQuery
│
└── 🔧 UTILITAIRES
    ├── test_bigquery_connection.py        # Test connexion BigQuery
    └── query_bigquery.py                  # Requêtes BigQuery interactives
```

---

## 🎯 Scripts d'Extraction

### 1. `extract_bf6_leaderboard.py` ⭐
**Objectif** : Extraire le top 100 du leaderboard tracker.gg

**Fonctionnalités** :
- ✅ Bypass Cloudflare avec `undetected-chromedriver`
- ✅ Parsing HTML avec BeautifulSoup
- ✅ Sauvegarde NDJSON avec timestamp
- ✅ Logging détaillé + HTML debug

**Usage** :
```bash
.venv/bin/python scripts/extract_bf6_leaderboard.py
```

**Output** :
```
data/bronze/tracker_gg/leaderboard/bf6_leaderboard_YYYY-MM-DD_HHMMSS.ndjson
```

**Performance** :
- ⏱️ Durée : ~25 secondes
- 🎯 Résultat : 97/100 joueurs (rangs 4-100)
- ⚠️ Rangs 1-3 non extraits (badges visuels)

---

### 2. `extract_bf6_top_weapons_final.py` ⭐
**Objectif** : Extraire le top 3 armes pour chaque joueur du leaderboard

**Fonctionnalités** :
- ✅ Lecture auto du dernier fichier leaderboard
- ✅ 8 métriques par arme (kills, accuracy, headshot%, damage, time_played)
- ✅ Retry automatique (2 tentatives)
- ✅ Sauvegarde HTML debug en cas d'échec
- ✅ Progression temps réel

**Usage** :
```bash
.venv/bin/python scripts/extract_bf6_top_weapons_final.py

# Prompt interactif:
# ⚠️  Cela va ouvrir 97 pages Chrome
# ⏱️  Temps estimé: ~40 minutes
# ▶️  Continuer ? (o/n): o
```

**Output** :
```
data/bronze/tracker_gg/top_weapons/bf6_top_weapons_YYYY-MM-DD_HHMMSS.ndjson
```

**Performance** :
- ⏱️ Durée : ~40 minutes (97 joueurs × 25s)
- 🎯 Objectif : >90% de succès
- 📊 Dernière extraction : 288 armes (97 joueurs)

---

## 📤 Scripts de Chargement

### 3. `upload_to_minio.py`
**Objectif** : Uploader les fichiers NDJSON vers MinIO (Bronze layer)

**Fonctionnalités** :
- ✅ Upload automatique depuis `data/bronze/`
- ✅ Structure de buckets organisée
- ✅ Métadonnées enrichies

**Usage** :
```bash
.venv/bin/python scripts/upload_to_minio.py
```

**Structure MinIO** :
```
bronze/
├── bf6/
│   ├── leaderboard/
│   │   └── bf6_leaderboard_2025-10-24_213134.ndjson
│   └── top_weapons/
│       └── bf6_top_weapons_2025-10-24_223302.ndjson
```

---

### 4. `upload_to_bigquery_v2.py` ⭐
**Objectif** : Charger les données NDJSON vers BigQuery (tables Bronze)

**Fonctionnalités** :
- ✅ UNNEST automatique des armes (ARRAY → rows)
- ✅ Schéma explicite pour chaque table
- ✅ Mode WRITE_TRUNCATE (remplacement complet)
- ✅ Validation post-upload avec preview

**Usage** :
```bash
.venv/bin/python scripts/upload_to_bigquery_v2.py
```

**Tables créées** :
- `bf6_meta.bf6_leaderboard_raw` (97 rows)
- `bf6_meta.bf6_top_weapons_raw` (288 rows)

**Dernière exécution** :
```
🏆 Top 3 armes:
  1. M4A1 (Carbines): 95,881 kills (35 players)
  2. SG 553R (Carbines): 66,392 kills (23 players)
  3. M433 (Assault Rifles): 53,780 kills (24 players)
```

---

## 🔧 Scripts Utilitaires

### 5. `test_bigquery_connection.py`
**Objectif** : Tester la connexion BigQuery et afficher les datasets

**Usage** :
```bash
.venv/bin/python scripts/test_bigquery_connection.py
```

**Vérifie** :
- ✅ Variables d'environnement (.env)
- ✅ Fichier credentials JSON
- ✅ Connexion au projet GCP
- ✅ Liste des datasets disponibles

---

### 6. `query_bigquery.py`
**Objectif** : Exécuter des requêtes SQL interactives sur BigQuery

**Usage** :
```bash
.venv/bin/python scripts/query_bigquery.py
```

**Exemples de requêtes** :
```sql
-- Compter les joueurs
SELECT COUNT(*) FROM bf6_meta.bf6_leaderboard_raw;

-- Top 5 armes
SELECT weapon_name, SUM(kills) as total_kills
FROM bf6_meta.bf6_top_weapons_raw
GROUP BY weapon_name
ORDER BY total_kills DESC
LIMIT 5;
```

---

## 🔄 Workflow Complet

### Pipeline Extraction → BigQuery

```bash
# 1️⃣ Extraction des données (~40 min total)
.venv/bin/python scripts/extract_bf6_leaderboard.py        # ~25s
.venv/bin/python scripts/extract_bf6_top_weapons_final.py  # ~40min

# 2️⃣ Upload vers MinIO (optionnel, pour archivage)
.venv/bin/python scripts/upload_to_minio.py

# 3️⃣ Chargement vers BigQuery (tables Raw)
.venv/bin/python scripts/upload_to_bigquery_v2.py

# 4️⃣ Transformations DBT (Silver → Gold)
cd dbt/
dbt run --models silver_players silver_weapons
dbt run --models gold_top_weapons_global
dbt test

# 5️⃣ Dashboard Streamlit
cd dashboard/
streamlit run app.py
```

---

## 📊 Données Extraites

### Leaderboard (par joueur)
| Colonne | Type | Description |
|---------|------|-------------|
| `handle` | STRING | Pseudo du joueur |
| `player_id` | STRING | ID unique tracker.gg |
| `rank` | INTEGER | Rang (4-100) |
| `kills` | INTEGER | Total kills |
| `extraction_date` | TIMESTAMP | Date d'extraction |
| `url_source` | STRING | URL source |

### Top Weapons (par arme × joueur)
| Colonne | Type | Description |
|---------|------|-------------|
| `handle` | STRING | Pseudo du joueur |
| `player_id` | STRING | ID unique |
| `weapon_name` | STRING | Nom de l'arme |
| `weapon_type` | STRING | Catégorie (SMG, AR, LMG...) |
| `weapon_rank` | INTEGER | Rang arme pour ce joueur (1-3) |
| `kills` | INTEGER | Kills avec cette arme |
| `time_played` | STRING | Temps joué |
| `damage` | INTEGER | Dégâts totaux |
| `accuracy` | STRING | Précision (%) |
| `headshot_pct` | STRING | Taux headshot (%) |

---

## 🛠️ Dépendances

```txt
undetected-chromedriver==3.5.5  # Bypass Cloudflare
beautifulsoup4==4.12.3          # Parsing HTML
selenium==4.16.0                # Automation navigateur
minio==7.2.0                    # Client MinIO
google-cloud-bigquery==3.14.0   # Client BigQuery
python-dotenv==1.0.0            # Variables d'environnement
```

**Installation** :
```bash
.venv/bin/pip install -r requirements.txt
```

---

## 🔗 Documentation Associée

- **`docs/BIGQUERY_GUIDE.md`** - Guide BigQuery complet
- **`docs/MINIO_EXPLAINED.md`** - Configuration MinIO
- **`docs/DBT_TRANSFORMATION_DESIGN.md`** - Design des transformations
- **`ai/notes.md`** - Historique des développements

---

## 📈 Historique des Extractions

| Date | Leaderboard | Weapons | Statut |
|------|-------------|---------|--------|
| 2025-10-24 21:31 | 97 joueurs | 288 armes | ✅ Succès |
| 2025-10-20 20:02 | 100 joueurs | 26 armes | ⚠️ Échec (74%) |

---

**Dernière extraction** : 24 octobre 2025, 22:33  
**Prochaine étape** : Phase 3 - Transformations DBT
