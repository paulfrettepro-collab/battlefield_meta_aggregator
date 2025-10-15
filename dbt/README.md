# 🔄 DBT - Transformations SQL

**Rôle** : Transformer les données brutes en analyses exploitables

## 🎯 Qu'est-ce que c'est ?

DBT (Data Build Tool) transforme les données crawlées en modèles SQL prêts pour l'analyse.

**Architecture Bronze → Silver → Gold** :

```
Bronze (Raw)    →    Silver (Clean)    →    Gold (KPIs)
────────────         ──────────────         ────────────
HTML brut            Données nettoyées     Top armes
JSON crawlé          Données normalisées   Évolution méta
Doublons             Dates formatées       Statistiques
```

## 📁 Structure

```
dbt/
├── models/
│   ├── bronze/        # Données brutes de MinIO
│   ├── silver/        # Nettoyage et normalisation
│   └── gold/          # Agrégations et KPIs
├── dbt_project.yml    # Configuration DBT
└── profiles.yml       # Connexion BigQuery
```

## 🛠️ Modèles prévus

### Bronze Layer (copie brute)
- `bronze_pcgamer.sql` : Import direct MinIO → BigQuery
- `bronze_reddit.sql` : Import Reddit
- ...

### Silver Layer (nettoyage)
- `silver_weapons.sql` : Normalisation noms armes
- `silver_loadouts.sql` : Parsing des loadouts
- `silver_metadata.sql` : Métadonnées enrichies

### Gold Layer (KPIs)
- `gold_top_weapons.sql` : Top 10 armes par score
- `gold_meta_evolution.sql` : Évolution méta dans le temps
- `gold_source_stats.sql` : Statistiques par source

## 🚀 Utilisation

```bash
# Tester connexion BigQuery
dbt debug

# Compiler les modèles (sans exécuter)
dbt compile

# Exécuter tous les modèles
dbt run

# Exécuter un modèle spécifique
dbt run --select silver_weapons

# Tester les données
dbt test
```

## 📊 Exemple de modèle

**`models/gold/gold_top_weapons.sql`** :
```sql
SELECT 
  weapon,
  AVG(meta_score) as avg_score,
  COUNT(*) as mentions,
  MAX(crawled_at) as last_seen
FROM {{ ref('silver_weapons') }}
GROUP BY weapon
ORDER BY avg_score DESC
LIMIT 10
```

## 🔗 Workflow

1. **Scrapy** crawl → MinIO (Bronze)
2. **DBT Bronze** : MinIO → BigQuery (raw)
3. **DBT Silver** : Nettoyage et normalisation
4. **DBT Gold** : Agrégations et KPIs
5. **Streamlit** : Affichage des Gold tables
