# Guide BigQuery - Battlefield Meta Aggregator

## 🎯 Objectif

Charger les données BF6 top weapons de MinIO vers BigQuery pour faire des analyses SQL.

## 📋 Prérequis

1. ✅ Compte Google Cloud créé
2. ✅ Projet Google Cloud créé (ex: `battlefield-meta-aggregator`)
3. ✅ BigQuery API activée
4. ✅ Compte de service créé avec role "BigQuery Admin"
5. ✅ Clé JSON téléchargée et placée dans `config/bigquery-key.json`

## 🔧 Configuration

### 1. Installer les dépendances

```bash
pip install google-cloud-bigquery google-cloud-storage db-dtypes
```

Ou mettre à jour tout le projet:

```bash
pip install -r requirements.txt
```

### 2. Configurer .env

Ajoute ces lignes dans `.env`:

```bash
# Google Cloud / BigQuery
GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json
GCP_PROJECT_ID=battlefield-meta-aggregator  # Remplace par ton project ID
```

### 3. Vérifier la connexion

```bash
python scripts/test_bigquery_connection.py
```

Tu devrais voir:
```
✅ CONNEXION BIGQUERY RÉUSSIE !
```

## 🚀 Chargement des données

### Script automatique

Le script `load_to_bigquery.py` fait tout automatiquement:

1. Crée le dataset `bf6_meta` s'il n'existe pas
2. Télécharge le fichier le plus récent depuis MinIO
3. Charge les données dans la table `top_weapons`

```bash
python scripts/load_to_bigquery.py
```

### Ce qui est créé

**Dataset**: `bf6_meta`
- Location: US (ou EU selon config)
- Description: Battlefield 6 meta data - weapons statistics

**Table**: `top_weapons`
- Schema:
  - `player_id` (STRING) - ID unique du joueur
  - `handle` (STRING) - Nom du joueur
  - `rank` (INTEGER) - Rang dans le leaderboard
  - `top_weapons` (RECORD, REPEATED) - Liste des 3 meilleures armes
    - `name` (STRING) - Nom de l'arme
    - `kills` (INTEGER) - Nombre de kills
    - `kpm` (FLOAT) - Kills par minute
    - `accuracy` (FLOAT) - Précision
  - `status` (STRING) - Statut de l'extraction
  - `extraction_date` (TIMESTAMP) - Date d'extraction

## 📊 Requêtes SQL

### 1. Voir les 10 premiers joueurs

```sql
SELECT 
  rank,
  handle,
  player_id,
  status
FROM `battlefield-meta-aggregator.bf6_meta.top_weapons`
ORDER BY rank
LIMIT 10;
```

### 2. Top 10 armes les plus utilisées

```sql
SELECT 
  weapon.name,
  COUNT(*) as nb_players,
  AVG(weapon.kills) as avg_kills,
  AVG(weapon.kpm) as avg_kpm
FROM `battlefield-meta-aggregator.bf6_meta.top_weapons`,
  UNNEST(top_weapons) as weapon
GROUP BY weapon.name
ORDER BY nb_players DESC
LIMIT 10;
```

### 3. Joueurs avec une arme spécifique

```sql
SELECT 
  handle,
  rank,
  weapon.name,
  weapon.kills,
  weapon.kpm
FROM `battlefield-meta-aggregator.bf6_meta.top_weapons`,
  UNNEST(top_weapons) as weapon
WHERE weapon.name = 'AK-24'
ORDER BY weapon.kills DESC;
```

### 4. Statistiques par arme

```sql
WITH weapon_stats AS (
  SELECT 
    weapon.name,
    weapon.kills,
    weapon.kpm,
    weapon.accuracy
  FROM `battlefield-meta-aggregator.bf6_meta.top_weapons`,
    UNNEST(top_weapons) as weapon
)
SELECT 
  name,
  COUNT(*) as occurrences,
  MIN(kills) as min_kills,
  MAX(kills) as max_kills,
  AVG(kills) as avg_kills,
  AVG(kpm) as avg_kpm,
  AVG(accuracy) as avg_accuracy
FROM weapon_stats
GROUP BY name
ORDER BY occurrences DESC;
```

## 🔄 Pipeline complet

### MinIO → BigQuery

```bash
# 1. Extraction des données (Phase 0.5)
python scripts/extract_bf6_top_weapons.py

# 2. Upload vers MinIO (Phase 1)
python scripts/upload_to_minio.py

# 3. Chargement vers BigQuery (Phase 2)
python scripts/load_to_bigquery.py
```

### Mettre à jour les données

Par défaut, `load_to_bigquery.py` **remplace** la table (WRITE_TRUNCATE).

Pour **ajouter** des données (historique):

```python
# Modifier dans load_to_bigquery.py
loader.load_to_bigquery(tmp_path, write_disposition="WRITE_APPEND")
```

## 💰 Coûts BigQuery

### Gratuit

- **10 GB** de stockage / mois
- **1 TB** de requêtes / mois

### Notre projet

- Stockage: ~0.02 KB par joueur × 100 = **2 KB** (négligeable)
- Requêtes: Très faible volume (< 1 GB / mois)

**Résultat**: **100% gratuit** pour ce projet ! 🎉

## 🔍 Interface Web

Console BigQuery: https://console.cloud.google.com/bigquery

1. Sélectionne ton projet
2. Navigue: `bf6_meta` > `top_weapons`
3. Clique "Query" pour écrire du SQL
4. Clique "Run" pour exécuter

## 🐛 Troubleshooting

### Erreur: "Project not found"

→ Vérifie que `GCP_PROJECT_ID` dans `.env` correspond à ton project ID

### Erreur: "Permission denied"

→ Vérifie que le compte de service a le role "BigQuery Admin"

### Erreur: "API not enabled"

→ Active BigQuery API: https://console.cloud.google.com/apis/library/bigquery.googleapis.com

### Erreur: "Invalid credentials"

→ Vérifie que `config/bigquery-key.json` existe et est valide

## 📚 Ressources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)

## 🎯 Prochaines étapes

1. ✅ Phase 0.5: Extraction (fait)
2. ✅ Phase 1: MinIO (fait)
3. 🔄 Phase 2: BigQuery (en cours)
4. 🟡 Phase 3: DBT (transformation)
5. 🟡 Phase 4: Streamlit (dashboard)
