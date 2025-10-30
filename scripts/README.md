# 🛠️ Scripts - Pipeline d'Extraction et Chargement# 🛠️ Scripts - Pipeline d'Extraction et Chargement



**Dernière mise à jour** : 29 octobre 2025  **Dernière mise à jour** : 24 octobre 2025  

**Rôle** : Scripts Python pour l'extraction, le stockage et le chargement des données**Rôle** : Scripts Python pour l'extraction, le stockage et le chargement des données



------



## 📁 Structure Actuelle (Post-Nettoyage)## 📁 Structure



``````

scripts/scripts/

├── README.md                          # Ce fichier├── README.md                          # Ce fichier

││

├── 🎯 SCRIPTS ACTIFS├── 🎯 EXTRACTION (Phase 2.5)

│   ├── extract_bf6_meta_complete.py   # ⭐ Extraction complète (leaderboard + armes)│   ├── extract_bf6_leaderboard.py         # Extraction top 100 joueurs

│   ├── load_to_bigquery_latest.py     # ⭐ Chargement BigQuery (bronze)│   └── extract_bf6_top_weapons_final.py   # Extraction top 3 armes par joueur

│   ├── query_bigquery.py              # 🔧 Requêtes BigQuery interactives│

│   └── test_bigquery_connection.py    # 🔧 Test connexion BigQuery├── 📤 CHARGEMENT (Phase 2)

││   ├── upload_to_minio.py                 # Upload NDJSON → MinIO

└── 📦 archive/                        # Scripts obsolètes archivés│   └── upload_to_bigquery_v2.py           # Upload MinIO → BigQuery

    ├── extract_bf6_leaderboard.py│

    ├── extract_bf6_top_weapons_final.py└── 🔧 UTILITAIRES

    ├── extract_bf6_top_weapons_parallel.py    ├── test_bigquery_connection.py        # Test connexion BigQuery

    ├── extract_bf6_top_weapons_robust.py    └── query_bigquery.py                  # Requêtes BigQuery interactives

    ├── upload_to_bigquery_v2.py```

    └── upload_to_minio.py

```---



---## 🎯 Scripts d'Extraction



## 🎯 Scripts Actifs### 1. `extract_bf6_leaderboard.py` ⭐

**Objectif** : Extraire le top 100 du leaderboard tracker.gg

### 1. `extract_bf6_meta_complete.py` ⭐ **PRODUCTION**

**Objectif** : Extraction complète du leaderboard + top 3 armes par joueur**Fonctionnalités** :

- ✅ Bypass Cloudflare avec `undetected-chromedriver`

**Fonctionnalités** :- ✅ Parsing HTML avec BeautifulSoup

- ✅ Extraction automatique du top 100 joueurs (tracker.gg)- ✅ Sauvegarde NDJSON avec timestamp

- ✅ Extraction top 3 armes pour chaque joueur- ✅ Logging détaillé + HTML debug

- ✅ Bypass Cloudflare avec `undetected-chromedriver`

- ✅ Retry automatique (3 tentatives par joueur)**Usage** :

- ✅ Logging détaillé + HTML debug```bash

- ✅ Sauvegarde NDJSON avec timestamp.venv/bin/python scripts/extract_bf6_leaderboard.py

```

**Usage** :

```bash**Output** :

python scripts/extract_bf6_meta_complete.py```

```data/bronze/tracker_gg/leaderboard/bf6_leaderboard_YYYY-MM-DD_HHMMSS.ndjson

```

**Dernière Extraction** : 29 octobre 2025, 21:23:58

- ✅ **50 joueurs** extraits avec succès**Performance** :

- ✅ **150 armes** au total (3 armes/joueur)- ⏱️ Durée : ~25 secondes

- ✅ **100% de taux de succès**- 🎯 Résultat : 97/100 joueurs (rangs 4-100)

- ⚠️ Rangs 1-3 non extraits (badges visuels)

**Output Files** :

```---

data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-29_212358.ndjson

data/bronze/tracker_gg/top_weapons/bf6_weapons_2025-10-29_212358.ndjson### 2. `extract_bf6_top_weapons_final.py` ⭐

```**Objectif** : Extraire le top 3 armes pour chaque joueur du leaderboard



**Armes Extraites** :**Fonctionnalités** :

- DRS-IAR, KORD 6P67, TR-7, KV9, M87A1- ✅ Lecture auto du dernier fichier leaderboard

- SCW-10, M4A1, SG 553R, KVM, M433- ✅ 8 métriques par arme (kills, accuracy, headshot%, damage, time_played)

- LWRC M6, RS86, CS95, MK20, ARMO- ✅ Retry automatique (2 tentatives)

- MINIMI, PM7, PKP, M84U, SG99R- ✅ Sauvegarde HTML debug en cas d'échec

- ✅ Progression temps réel

**Performance** :

- ⏱️ Durée totale : ~30 minutes**Usage** :

- 📊 Données : 50 joueurs × 3 armes = 150 lignes```bash

- 🎯 Taux de réussite : 100%.venv/bin/python scripts/extract_bf6_top_weapons_final.py



---# Prompt interactif:

# ⚠️  Cela va ouvrir 97 pages Chrome

### 2. `load_to_bigquery_latest.py` ⭐ **PRODUCTION**# ⏱️  Temps estimé: ~40 minutes

**Objectif** : Charger automatiquement les dernières données NDJSON vers BigQuery# ▶️  Continuer ? (o/n): o

```

**Fonctionnalités** :

- ✅ Détection automatique des fichiers les plus récents**Output** :

- ✅ UNNEST des armes (ARRAY → rows individuelles)```

- ✅ Schéma explicite (bronze_leaderboard, bronze_weapons)data/bronze/tracker_gg/top_weapons/bf6_top_weapons_YYYY-MM-DD_HHMMSS.ndjson

- ✅ Mode WRITE_APPEND (chargement incrémental)```

- ✅ Validation post-upload avec requêtes SQL

**Performance** :

**Usage** :- ⏱️ Durée : ~40 minutes (97 joueurs × 25s)

```bash- 🎯 Objectif : >90% de succès

python scripts/load_to_bigquery_latest.py- 📊 Dernière extraction : 288 armes (97 joueurs)

```

---

**Tables créées** :

- `bf6_meta.bronze_leaderboard` (50 rows - 29 oct)## 📤 Scripts de Chargement

- `bf6_meta.bronze_weapons` (150 rows - 29 oct)

### 3. `upload_to_minio.py`

**Schéma Bronze Leaderboard** :**Objectif** : Uploader les fichiers NDJSON vers MinIO (Bronze layer)

| Colonne | Type | Description |

|---------|------|-------------|**Fonctionnalités** :

| `handle` | STRING | Pseudo du joueur |- ✅ Upload automatique depuis `data/bronze/`

| `player_id` | STRING | ID unique tracker.gg |- ✅ Structure de buckets organisée

| `rank` | INTEGER | Rang (1-100) |- ✅ Métadonnées enrichies

| `kills` | INTEGER | Total kills |

| `location` | STRING | Localisation |**Usage** :

| `matches_played` | INTEGER | Nombre de parties |```bash

| `extraction_date` | TIMESTAMP | Date d'extraction |.venv/bin/python scripts/upload_to_minio.py

```

**Schéma Bronze Weapons** :

| Colonne | Type | Description |**Structure MinIO** :

|---------|------|-------------|```

| `player_handle` | STRING | Pseudo du joueur |bronze/

| `player_id` | STRING | ID unique |├── bf6/

| `player_rank` | INTEGER | Rang joueur |│   ├── leaderboard/

| `player_kills` | INTEGER | Total kills joueur |│   │   └── bf6_leaderboard_2025-10-24_213134.ndjson

| `weapon_name` | STRING | Nom de l'arme |│   └── top_weapons/

| `weapon_rank` | INTEGER | Rang arme (1-3) |│       └── bf6_top_weapons_2025-10-24_223302.ndjson

| `weapon_kills` | INTEGER | Kills avec arme |```

| `weapon_accuracy` | FLOAT | Précision (0-100) |

| `extraction_date` | TIMESTAMP | Date d'extraction |---



**Dernière exécution (29 oct)** :### 4. `upload_to_bigquery_v2.py` ⭐

```**Objectif** : Charger les données NDJSON vers BigQuery (tables Bronze)

✅ bronze_leaderboard: 50 lignes chargées

✅ bronze_weapons: 150 lignes chargées**Fonctionnalités** :

- ✅ UNNEST automatique des armes (ARRAY → rows)

🏆 Top 5 armes (29 oct):- ✅ Schéma explicite pour chaque table

  1. SG 553R: 1,620 kills (3 joueurs)- ✅ Mode WRITE_TRUNCATE (remplacement complet)

  2. TR-7: 1,523 kills (3 joueurs)- ✅ Validation post-upload avec preview

  3. M4A1: 1,469 kills (3 joueurs)

  4. DRS-IAR: 1,431 kills (3 joueurs)**Usage** :

  5. M433: 1,370 kills (3 joueurs)```bash

```.venv/bin/python scripts/upload_to_bigquery_v2.py

```

---

**Tables créées** :

### 3. `query_bigquery.py` 🔧 **UTILITAIRE**- `bf6_meta.bf6_leaderboard_raw` (97 rows)

**Objectif** : Exécuter des requêtes SQL interactives sur BigQuery- `bf6_meta.bf6_top_weapons_raw` (288 rows)



**Usage** :**Dernière exécution** :

```bash```

python scripts/query_bigquery.py🏆 Top 3 armes:

```  1. M4A1 (Carbines): 95,881 kills (35 players)

  2. SG 553R (Carbines): 66,392 kills (23 players)

**Exemples de requêtes** :  3. M433 (Assault Rifles): 53,780 kills (24 players)

```sql```

-- Compter les joueurs

SELECT COUNT(*) FROM bf6_meta.bronze_leaderboard;---



-- Top 10 armes globales## 🔧 Scripts Utilitaires

SELECT 

  weapon_name, ### 5. `test_bigquery_connection.py`

  SUM(weapon_kills) as total_kills,**Objectif** : Tester la connexion BigQuery et afficher les datasets

  COUNT(DISTINCT player_handle) as nb_players

FROM bf6_meta.bronze_weapons**Usage** :

GROUP BY weapon_name```bash

ORDER BY total_kills DESC.venv/bin/python scripts/test_bigquery_connection.py

LIMIT 10;```



-- Dernière extraction**Vérifie** :

SELECT MAX(extraction_date) FROM bf6_meta.bronze_leaderboard;- ✅ Variables d'environnement (.env)

```- ✅ Fichier credentials JSON

- ✅ Connexion au projet GCP

---- ✅ Liste des datasets disponibles



### 4. `test_bigquery_connection.py` 🔧 **UTILITAIRE**---

**Objectif** : Tester la connexion BigQuery et lister les datasets

### 6. `query_bigquery.py`

**Usage** :**Objectif** : Exécuter des requêtes SQL interactives sur BigQuery

```bash

python scripts/test_bigquery_connection.py**Usage** :

``````bash

.venv/bin/python scripts/query_bigquery.py

**Vérifie** :```

- ✅ Variables d'environnement (.env)

- ✅ Fichier credentials JSON**Exemples de requêtes** :

- ✅ Connexion au projet GCP```sql

- ✅ Liste des datasets disponibles-- Compter les joueurs

SELECT COUNT(*) FROM bf6_meta.bf6_leaderboard_raw;

---

-- Top 5 armes

## 🔄 Workflow Complet - Pipeline ProductionSELECT weapon_name, SUM(kills) as total_kills

FROM bf6_meta.bf6_top_weapons_raw

### Pipeline Automatisé (Hebdomadaire)GROUP BY weapon_name

ORDER BY total_kills DESC

```bashLIMIT 5;

# 1️⃣ Extraction des données (~30 min)```

python scripts/extract_bf6_meta_complete.py

---

# 2️⃣ Chargement vers BigQuery (Bronze Layer) (~10s)

python scripts/load_to_bigquery_latest.py## 🔄 Workflow Complet



# 3️⃣ Transformations DBT (Silver + Gold) (~15s)### Pipeline Extraction → BigQuery

export PATH="/Users/paulfrette/.local/bin:$PATH"

cd dbt/```bash

dbt run          # Crée 6 modèles (2 silver, 3 gold, 1 silver_player_weapons)# 1️⃣ Extraction des données (~40 min total)

dbt test         # 44 tests de qualité.venv/bin/python scripts/extract_bf6_leaderboard.py        # ~25s

.venv/bin/python scripts/extract_bf6_top_weapons_final.py  # ~40min

# 4️⃣ Dashboard Streamlit (temps réel)

cd ../dashboard/# 2️⃣ Upload vers MinIO (optionnel, pour archivage)

streamlit run app.py.venv/bin/python scripts/upload_to_minio.py

```

# 3️⃣ Chargement vers BigQuery (tables Raw)

**Durée totale** : ~30-35 minutes (dont 30 min d'extraction).venv/bin/python scripts/upload_to_bigquery_v2.py



---# 4️⃣ Transformations DBT (Silver → Gold)

cd dbt/

## 📦 Scripts Archivésdbt run --models silver_players silver_weapons

dbt run --models gold_top_weapons_global

Les scripts suivants ont été déplacés vers `archive/` car ils sont obsolètes :dbt test



1. **`extract_bf6_leaderboard.py`** - Remplacé par `extract_bf6_meta_complete.py`# 5️⃣ Dashboard Streamlit

2. **`extract_bf6_top_weapons_final.py`** - Remplacé par `extract_bf6_meta_complete.py`cd dashboard/

3. **`extract_bf6_top_weapons_parallel.py`** - Version expérimentalestreamlit run app.py

4. **`extract_bf6_top_weapons_robust.py`** - Version de test```

5. **`upload_to_bigquery_v2.py`** - Remplacé par `load_to_bigquery_latest.py`

6. **`upload_to_minio.py`** - MinIO non utilisé dans le pipeline actuel---



**Raison de l'archivage** :## 📊 Données Extraites

- Scripts obsolètes remplacés par des versions améliorées

- Simplification de la codebase (4 scripts actifs vs 10 précédemment)### Leaderboard (par joueur)

- Focus sur les scripts de production| Colonne | Type | Description |

|---------|------|-------------|

---| `handle` | STRING | Pseudo du joueur |

| `player_id` | STRING | ID unique tracker.gg |

## 🛠️ Dépendances| `rank` | INTEGER | Rang (4-100) |

| `kills` | INTEGER | Total kills |

```txt| `extraction_date` | TIMESTAMP | Date d'extraction |

# Extraction| `url_source` | STRING | URL source |

undetected-chromedriver==3.5.5  # Bypass Cloudflare

beautifulsoup4==4.12.3          # Parsing HTML### Top Weapons (par arme × joueur)

selenium==4.16.0                # Automation navigateur| Colonne | Type | Description |

|---------|------|-------------|

# Stockage| `handle` | STRING | Pseudo du joueur |

google-cloud-bigquery==3.38.0   # Client BigQuery| `player_id` | STRING | ID unique |

python-dotenv==1.0.0            # Variables d'environnement| `weapon_name` | STRING | Nom de l'arme |

| `weapon_type` | STRING | Catégorie (SMG, AR, LMG...) |

# Utilitaires| `weapon_rank` | INTEGER | Rang arme pour ce joueur (1-3) |

pandas==2.1.4                   # Manipulation de données| `kills` | INTEGER | Kills avec cette arme |

```| `time_played` | STRING | Temps joué |

| `damage` | INTEGER | Dégâts totaux |

**Installation** :| `accuracy` | STRING | Précision (%) |

```bash| `headshot_pct` | STRING | Taux headshot (%) |

pip install -r requirements.txt

```---



---## 🛠️ Dépendances



## 📊 Historique des Extractions Récentes```txt

undetected-chromedriver==3.5.5  # Bypass Cloudflare

| Date | Joueurs | Armes | Taux Succès | Fichiers |beautifulsoup4==4.12.3          # Parsing HTML

|------|---------|-------|-------------|----------|selenium==4.16.0                # Automation navigateur

| 2025-10-29 21:23 | 50 | 150 | 100% | ✅ Complet |minio==7.2.0                    # Client MinIO

| 2025-10-24 22:33 | 97 | 288 | 98% | ✅ Complet |google-cloud-bigquery==3.14.0   # Client BigQuery

| 2025-10-20 20:02 | 100 | 26 | 26% | ⚠️ Échec partiel |python-dotenv==1.0.0            # Variables d'environnement

```

**Tendance** : Amélioration continue du taux de succès grâce à l'optimisation du script d'extraction

**Installation** :

---```bash

.venv/bin/pip install -r requirements.txt

## 🔗 Documentation Associée```



- **`docs/EXTRACTION_STRATEGY.md`** - Stratégie d'extraction détaillée---

- **`docs/CRAWLING_GUIDE.md`** - Guide web scraping

- **`dbt/README.md`** - Documentation des transformations DBT## 🔗 Documentation Associée

- **`dashboard/README.md`** - Guide du dashboard Streamlit

- **`docs/BIGQUERY_GUIDE.md`** - Guide BigQuery complet

---- **`docs/MINIO_EXPLAINED.md`** - Configuration MinIO

- **`docs/DBT_TRANSFORMATION_DESIGN.md`** - Design des transformations

**Dernière extraction** : 29 octobre 2025, 21:23:58  - **`ai/notes.md`** - Historique des développements

**Prochaine maintenance** : Automatisation hebdomadaire (Étape 6)

---

---

## 📈 Historique des Extractions

## 🎯 Prochaines Étapes

| Date | Leaderboard | Weapons | Statut |

- [ ] Automatisation hebdomadaire (Cloud Scheduler + Cloud Functions)|------|-------------|---------|--------|

- [ ] Monitoring et alertes (Stackdriver)| 2025-10-24 21:31 | 97 joueurs | 288 armes | ✅ Succès |

- [ ] Expansion : top 100 joueurs (actuellement top 50)| 2025-10-20 20:02 | 100 joueurs | 26 armes | ⚠️ Échec (74%) |

- [ ] Historisation : conservation de plusieurs extractions

---

**Dernière extraction** : 24 octobre 2025, 22:33  
**Prochaine étape** : Phase 3 - Transformations DBT
