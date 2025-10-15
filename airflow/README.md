# 🔀 Airflow - Orchestration

**Rôle** : Automatiser le pipeline ELT quotidien

## 🎯 Qu'est-ce que c'est ?

Apache Airflow orchestre toute la pipeline de données :
- Lance les crawls Scrapy tous les jours à 2h du matin
- Upload les données vers MinIO
- Déclenche les transformations DBT
- Envoie des alertes en cas d'erreur

## 📁 Structure

```
airflow/
├── dags/
│   └── battlefield_pipeline.py    # DAG principal
├── logs/                          # Logs d'exécution
└── plugins/                       # Plugins custom (optionnel)
```

## 🗓️ DAG Principal

**`battlefield_pipeline.py`** - Exécution quotidienne :

```
┌─────────────────┐
│  2h00 du matin  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Crawl   │ ← Scrapy (5 sources en parallèle)
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Upload  │ ← MinIO (Bronze layer)
    └────┬─────┘
         │
    ┌────▼─────┐
    │  DBT     │ ← Transformations (Bronze → Gold)
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Alertes │ ← Email si erreur
    └──────────┘
```

## 🚀 Démarrage

```bash
# Démarrer Airflow (avec Docker)
docker-compose up -d airflow

# Accéder à l'interface web
open http://localhost:8080

# Login par défaut
# Username : airflow
# Password : airflow
```

## 📊 Interface Web

Dans l'interface Airflow, tu peux :
- ✅ **Voir tous les DAGs** (pipelines)
- ✅ **Activer/Désactiver** un DAG
- ✅ **Lancer manuellement** un DAG
- ✅ **Voir l'historique** des exécutions
- ✅ **Consulter les logs** en cas d'erreur

## 🔧 Configuration

**Fréquence d'exécution** (dans `battlefield_pipeline.py`) :

```python
default_args = {
    'schedule_interval': '0 2 * * *',  # Tous les jours à 2h
    'retries': 3,                      # Réessayer 3 fois si erreur
    'retry_delay': timedelta(minutes=5),
}
```

## 🔗 Prochaines étapes

1. Créer le fichier `dags/battlefield_pipeline.py`
2. Définir les tâches (crawl, upload, DBT)
3. Tester en manuel
4. Activer l'exécution automatique
