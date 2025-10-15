# 💾 Data - Stockage local

**Rôle** : Stocker les données locales de développement

## 🎯 Qu'est-ce que c'est ?

Dossier pour les données locales (non versionnées sur GitHub) :
- Résultats de crawls Scrapy
- Données brutes pour tests
- Stockage MinIO local

## 📁 Structure

```
data/
├── outputs/        # Résultats crawls Scrapy (*.json)
├── bronze/         # Données brutes locales (tests)
└── minio/          # Stockage MinIO (si utilisé localement)
```

## ⚠️ Fichiers ignorés

Ces dossiers sont dans `.gitignore` :
- `data/outputs/` → Résultats temporaires
- `data/minio/` → Volumes Docker MinIO
- Tous les `*.json` → Données crawlées

**Pourquoi ?**
- Éviter de polluer GitHub avec des données
- Les données sont dans MinIO/BigQuery (sources de vérité)
- Fichiers régénérables à tout moment

## 🗑️ Nettoyage

```bash
# Supprimer tous les outputs locaux
rm -rf data/outputs/*

# Supprimer les données MinIO locales
rm -rf data/minio/*
```

## 🔗 Sources de données

### En développement
- **Local** : `data/outputs/*.json` (tests)

### En production
- **Bronze** : MinIO (`battlefield-bronze/`)
- **Silver/Gold** : BigQuery (`battlefield_meta.silver_*`, `battlefield_meta.gold_*`)

## 📊 Exemple de fichier

**`data/outputs/pcgamer_results.json`** :
```json
[
  {
    "weapon": "PW7A2",
    "attachments": "Single-Port Brake, Hollow Point",
    "meta_score": 4.5,
    "source": "PC Gamer",
    "crawled_at": "2025-10-15T14:30:00"
  }
]
```

## 🚀 Workflow

```
1. Crawl Scrapy → data/outputs/pcgamer_results.json
2. Upload MinIO → minio://battlefield-bronze/pcgamer/2025/10/15/data.json
3. DBT charge → BigQuery bronze_pcgamer
4. Transformations → Silver → Gold
5. Streamlit affiche → Dashboard
```

**Note** : Les fichiers dans `data/outputs/` sont temporaires et nettoyés régulièrement.
