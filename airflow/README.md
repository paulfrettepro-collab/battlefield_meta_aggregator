# 🚀 Apache Airflow - BF6 Meta Aggregator

## 📋 Vue d'ensemble

Apache Airflow orchestre l'extraction hebdomadaire des données BF6 Meta.

**DAG principal** : `bf6_weekly_extraction`
- **Schedule** : Tous les dimanches à 2h UTC
- **Durée** : ~40 minutes
- **Tasks** : 6 étapes séquentielles

```
extract_leaderboard (35s)
      ↓
extract_weapons (35 min)
      ↓
load_to_bigquery (2 min)
      ↓
dbt_run_silver (3 min)
      ↓
dbt_run_gold (2 min)
      ↓
send_notification (5s)
```

---

## ⚙️ Installation Rapide (15 minutes)

### Option 1 : Installation Globale (Recommandé pour MVP)

```bash
# 1. Créer un venv dédié Airflow
cd /Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator
python3 -m venv airflow_venv
source airflow_venv/bin/activate

# 2. Installer Airflow 2.10.3
pip install "apache-airflow==2.10.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.12.txt"

# 3. Configurer AIRFLOW_HOME
export AIRFLOW_HOME=/Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator/airflow

# 4. Initialiser la base de données SQLite
airflow db migrate

# 5. Créer un utilisateur admin
airflow users create \
    --username admin \
    --firstname Paul \
    --lastname Frette \
    --role Admin \
    --email paul.frette@example.com \
    --password admin123

# 6. Lancer Airflow (mode standalone)
airflow standalone
```

**Interface web** : http://localhost:8080
- Username: `admin`
- Password: `admin123`

---

## 📂 Structure

```
airflow/
├── README.md                    # Ce fichier
├── dags/                        # DAGs Airflow
│   └── bf6_weekly_extraction.py # DAG principal (6 tasks)
├── logs/                        # Logs d'exécution (auto-créé)
├── airflow.db                   # Base SQLite (auto-créé)
├── airflow.cfg                  # Configuration (auto-créé)
└── webserver_config.py          # Config UI (auto-créé)
```

---

## 🎯 DAG: bf6_weekly_extraction

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| **Schedule** | `0 2 * * 0` (Dimanches 2h UTC) |
| **Start Date** | 27 octobre 2025 |
| **Retries** | 2 tentatives |
| **Retry Delay** | 5 minutes |
| **Catchup** | False (ne re-exécute pas le passé) |

### Tasks

#### 1. **extract_leaderboard**
- **Durée** : ~35 secondes
- **Script** : `scripts/extract_bf6_leaderboard.py`
- **Output** : `data/bronze/tracker_gg/leaderboard/bf6_leaderboard_YYYY-MM-DD_HHMMSS.ndjson`
- **Résultat** : 97 joueurs extraits

#### 2. **extract_weapons**
- **Durée** : ~35 minutes
- **Script** : `scripts/extract_bf6_top_weapons_final.py`
- **Output** : `data/bronze/tracker_gg/top_weapons/bf6_top_weapons_YYYY-MM-DD_HHMMSS.ndjson`
- **Résultat** : 288 armes (3 par joueur)

#### 3. **load_to_bigquery**
- **Durée** : ~2 minutes
- **Script** : `scripts/load_to_bigquery.py`
- **Output** : Tables BigQuery `bronze_leaderboard` et `bronze_top_weapons`

#### 4. **dbt_run_silver**
- **Durée** : ~3 minutes
- **Command** : `dbt run --select silver.*`
- **Output** : Tables `silver_players`, `silver_weapons`, `silver_player_weapons`

#### 5. **dbt_run_gold**
- **Durée** : ~2 minutes
- **Command** : `dbt run --select gold.*`
- **Output** : Tables `gold_top_weapons_global`, `gold_top_weapons_by_type`, `gold_player_rankings`

#### 6. **send_notification**
- **Durée** : ~5 secondes
- **Action** : Log de succès (TODO: Slack/Email)

---

## 🧪 Tester le DAG

### Mode Manuel (interface web)

1. Ouvrir http://localhost:8080
2. Aller dans **DAGs**
3. Trouver `bf6_weekly_extraction`
4. Cliquer sur **Trigger DAG** (play button)
5. Surveiller l'exécution dans **Graph View**

### Mode CLI

```bash
# Activer le venv Airflow
source airflow_venv/bin/activate
export AIRFLOW_HOME=/Users/paulfrette/Github_pro_folder/battlefield_meta_aggregator/airflow

# Lister les DAGs
airflow dags list

# Tester un DAG (dry-run)
airflow dags test bf6_weekly_extraction 2025-10-27

# Exécuter une task spécifique
airflow tasks test bf6_weekly_extraction extract_leaderboard 2025-10-27

# Voir les logs
airflow tasks logs bf6_weekly_extraction extract_leaderboard 2025-10-27
```

---

## 📊 Monitoring

### Logs

Logs disponibles dans :
- **UI Airflow** : http://localhost:8080 → DAG → Task → Logs
- **Fichiers** : `airflow/logs/dag_id=bf6_weekly_extraction/run_id=*/task_id=*/`

### Métriques

- **Success Rate** : Visible dans UI (Graph View)
- **Duration** : Temps d'exécution par task
- **Retries** : Nombre de tentatives

---

## ⚠️ Troubleshooting

### Erreur : "Dag not found"

```bash
# Vérifier que AIRFLOW_HOME pointe vers le bon dossier
echo $AIRFLOW_HOME

# Rescanner les DAGs
airflow dags list-import-errors
```

### Erreur : "ModuleNotFoundError"

Le DAG ajoute automatiquement le projet au `sys.path`. Si problème :

```python
# Vérifier dans airflow/dags/bf6_weekly_extraction.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
```

### Erreur : "Cloudflare blocking"

Le script `extract_bf6_top_weapons_final.py` attend 20s par joueur pour bypass Cloudflare. 
Durée normale : ~35 minutes pour 97 joueurs.

---

## 🔧 Configuration Avancée

### Changer le schedule

Éditer `airflow/dags/bf6_weekly_extraction.py` :

```python
# Actuel : Dimanches 2h UTC
schedule_interval='0 2 * * 0'

# Quotidien 3h UTC
schedule_interval='0 3 * * *'

# Toutes les 6h
schedule_interval='0 */6 * * *'
```

### Activer les notifications Slack

```python
# Dans send_notification()
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

slack_msg = SlackWebhookOperator(
    task_id='slack_notification',
    http_conn_id='slack_webhook',
    message='✅ BF6 extraction completed!',
    dag=dag
)
```

### Déployer sur Cloud (Production)

**Option 1** : Google Cloud Composer (Airflow managé)
**Option 2** : Docker Compose (self-hosted)
**Option 3** : Astronomer (SaaS)

Voir `docs/AIRFLOW_CLOUD_DEPLOY.md` (Phase 5+)

---

## 📚 Ressources

- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [DAG Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow CLI Reference](https://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html)

---

**Dernière mise à jour** : 27 octobre 2025 - Phase 5 MVP
