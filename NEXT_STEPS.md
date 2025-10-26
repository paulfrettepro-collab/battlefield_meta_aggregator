# 🚀 NEXT STEPS - Battlefield Meta Aggregator

**Dernière mise à jour :** 25 octobre 2025  
**Phase actuelle :** Phase 4 complète ✅  
**Prochaine phase :** Phase 5 - Analyses avancées

---

## 📋 Vue d'ensemble

Ce document détaille les **prochaines étapes** du projet après la complétion de la Phase 4 (Dashboard MVP).

---

## 🎯 Phase 5 : Analyses avancées (Priorité HAUTE)

**Objectif :** Enrichir le dashboard avec des analyses temporelles et comparatives

**Durée estimée :** 2-3 semaines

---

### 5.1 Page "Meta Trends" 📈

**Fichier à créer :** `dashboard/pages/3_📈_Meta_Trends.py`

**Fonctionnalités :**

1. **Évolution temporelle des armes**
   - Graphique ligne : kills par arme dans le temps
   - Sélecteur multi-armes (compare 2-5 armes)
   - Période : 7j / 30j / 90j / All time

2. **Détection de changements**
   - Algorithme de détection de rupture (changepoint)
   - Alertes visuelles sur les shifts de meta
   - Annotations sur événements (patches, updates)

3. **Ranking evolution**
   - Heatmap : Position rank par arme/semaine
   - Table : Movers (⬆️⬇️) depuis dernière semaine
   - Highlight : New entries dans top 10

**Requêtes BigQuery nécessaires :**

```sql
-- Créer vue historique
CREATE VIEW gold_weapons_history AS
SELECT 
    weapon_name,
    weapon_type,
    total_kills,
    extraction_date,
    ROW_NUMBER() OVER (
        PARTITION BY extraction_date 
        ORDER BY total_kills DESC
    ) AS daily_rank
FROM silver_weapons
ORDER BY extraction_date DESC, daily_rank;

-- Détecter movers
WITH rank_changes AS (
    SELECT 
        weapon_name,
        daily_rank AS current_rank,
        LAG(daily_rank) OVER (
            PARTITION BY weapon_name 
            ORDER BY extraction_date
        ) AS previous_rank
    FROM gold_weapons_history
    WHERE extraction_date IN (
        SELECT DISTINCT extraction_date 
        FROM gold_weapons_history 
        ORDER BY extraction_date DESC 
        LIMIT 2
    )
)
SELECT 
    weapon_name,
    current_rank,
    previous_rank,
    (previous_rank - current_rank) AS rank_change
FROM rank_changes
WHERE previous_rank IS NOT NULL
ORDER BY ABS(rank_change) DESC;
```

**Graphiques Plotly :**

1. **Line chart** : Multi-series temporel
2. **Heatmap** : Ranking matrix
3. **Bar chart** : Biggest movers
4. **Scatter** : Position vs change

**Priorité :** 🔴 HAUTE (feature la plus demandée)

---

### 5.2 Page "Player Deep Dive" 🔍

**Fichier à créer :** `dashboard/pages/4_🔍_Player_Deep_Dive.py`

**Fonctionnalités :**

1. **Sélecteur de joueur**
   - Dropdown des 100 joueurs
   - Recherche autocomplete
   - Favoris (localStorage)

2. **Profil complet**
   - Header card : Rank, kills, accuracy, headshot %
   - Progression dans le temps (si historique dispo)
   - Comparaison avec moyenne du top 100

3. **Arsenal détaillé**
   - Tableau : Toutes les armes du joueur
   - Tri par kills / accuracy / time played
   - Highlight : Top 3 weapons du joueur
   - Pie chart : Distribution kills par weapon type

4. **Comparaisons**
   - Radar chart : Stats player vs moyenne
   - Table : Rank sur chaque arme
   - Heatmap : Performance par type d'arme

**Requêtes BigQuery :**

```sql
-- Profil joueur complet
CREATE OR REPLACE VIEW gold_player_profile AS
SELECT 
    p.player_handle,
    p.player_rank,
    p.player_total_kills,
    COUNT(DISTINCT w.weapon_name) AS weapons_count,
    AVG(w.accuracy) AS avg_accuracy,
    AVG(w.headshot_pct) AS avg_headshot,
    SUM(w.time_played) AS total_time_played,
    ARRAY_AGG(
        STRUCT(
            w.weapon_name, 
            w.weapon_kills, 
            w.accuracy,
            w.headshot_pct
        ) 
        ORDER BY w.weapon_kills DESC
    ) AS weapons_arsenal
FROM silver_players p
LEFT JOIN silver_player_weapons w 
    ON p.player_handle = w.player_handle
GROUP BY 
    p.player_handle, 
    p.player_rank, 
    p.player_total_kills;

-- Comparaison avec moyennes
WITH player_stats AS (
    SELECT * FROM gold_player_profile WHERE player_handle = @handle
),
top100_avg AS (
    SELECT 
        AVG(player_total_kills) AS avg_kills,
        AVG(avg_accuracy) AS avg_accuracy,
        AVG(avg_headshot) AS avg_headshot
    FROM gold_player_profile
)
SELECT 
    p.*,
    t.avg_kills AS top100_avg_kills,
    t.avg_accuracy AS top100_avg_accuracy,
    (p.player_total_kills - t.avg_kills) AS kills_diff,
    (p.avg_accuracy - t.avg_accuracy) AS accuracy_diff
FROM player_stats p
CROSS JOIN top100_avg t;
```

**Priorité :** 🟡 MOYENNE

---

### 5.3 Page "Weapon Comparisons" ⚔️

**Fichier à créer :** `dashboard/pages/5_⚔️_Weapon_Compare.py`

**Fonctionnalités :**

1. **Sélecteur multi-armes**
   - Dropdown avec recherche
   - Maximum 3-4 armes simultanément
   - Presets : "Top 3 ARs", "Top 3 SMGs", etc.

2. **Tableau comparatif**
   - Side-by-side stats
   - Highlight : Meilleur dans chaque catégorie
   - Delta % entre armes

3. **Radar chart**
   - 6 axes : Kills, Accuracy, Headshot %, Damage, Players, Popularity
   - Normalisation 0-100
   - Superposition des armes

4. **Bar charts détaillés**
   - Chart par stat (kills, accuracy, etc.)
   - Groupé par arme
   - Sortable

**Exemple de layout :**

```python
# Sélecteurs
col1, col2, col3 = st.columns(3)
with col1:
    weapon1 = st.selectbox("Arme 1", weapons_list)
with col2:
    weapon2 = st.selectbox("Arme 2", weapons_list)
with col3:
    weapon3 = st.selectbox("Arme 3", weapons_list)

# Tableau comparatif
comparison_df = create_comparison_table(weapon1, weapon2, weapon3)
st.dataframe(comparison_df, use_container_width=True)

# Radar chart
fig = create_radar_comparison(weapon1, weapon2, weapon3)
st.plotly_chart(fig)

# Détails par stat
tabs = st.tabs(["Kills", "Accuracy", "Headshot %", "Damage"])
with tabs[0]:
    st.plotly_chart(create_kills_comparison(...))
# etc.
```

**Priorité :** 🟢 BASSE (nice-to-have)

---

### 5.4 Filtres temporels globaux 📅

**Modification :** Ajouter dans `dashboard/utils/bigquery.py`

**Fonctionnalités :**

1. **Date range picker**
   - Sidebar : st.date_input avec range
   - Presets : Last 7 days, Last 30 days, All time
   - Sync sur toutes les pages

2. **Mise à jour des requêtes**
   - Ajouter clause WHERE `extraction_date BETWEEN @start AND @end`
   - Cache par période
   - Invalidation automatique

**Exemple implémentation :**

```python
# dashboard/app.py (sidebar)
with st.sidebar:
    st.subheader("📅 Time Period")
    
    date_range = st.date_input(
        "Select period",
        value=(
            datetime.now() - timedelta(days=7),
            datetime.now()
        ),
        key="global_date_range"
    )
    
    # Presets
    preset = st.radio(
        "Quick select",
        ["Last 7 days", "Last 30 days", "All time"],
        horizontal=True
    )
    
    if preset == "Last 7 days":
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    # etc.

# Passer aux fonctions BigQuery
df = load_top_weapons(
    start_date=start_date,
    end_date=end_date
)
```

**Priorité :** 🟡 MOYENNE (dépend de l'historique disponible)

---

## 🔄 Phase 5 : Automatisation & Refresh (Priorité HAUTE)

**Objectif :** Automatiser l'extraction et le rafraîchissement des données

**Durée estimée :** 1-2 jours (8-16h)

**2 Scénarios à implémenter :**

---

### 5.1 Scénario 1 : Refresh Manuel (Bouton Dashboard) 🔄

**Use case :** Utilisateur clique sur "Refresh Data" dans le dashboard Streamlit

**Architecture :**
```
Dashboard Streamlit → Bouton "Refresh" → Trigger extraction
                          ↓
    Cloud Function/Cloud Run Job (Python script)
                          ↓
    Extract Tracker.gg → Upload BigQuery → DBT Run
                          ↓
    Invalidate Streamlit Cache → Dashboard mis à jour
```

**Implémentation détaillée :**

#### Étape 1 : Créer Cloud Function GCP

**Fichier :** `cloud_functions/trigger_extraction/main.py`

```python
import functions_framework
import subprocess
import logging
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO)

@functions_framework.http
def trigger_extraction(request):
    """
    HTTP Cloud Function to trigger data extraction pipeline.
    
    Triggered by: Streamlit dashboard button click
    Returns: JSON status
    """
    
    try:
        # 1. Run extraction scripts
        logging.info("Starting leaderboard extraction...")
        result1 = subprocess.run(
            ['python', 'scripts/extract_bf6_leaderboard.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )
        
        if result1.returncode != 0:
            raise Exception(f"Leaderboard extraction failed: {result1.stderr}")
        
        logging.info("Starting weapons extraction...")
        result2 = subprocess.run(
            ['python', 'scripts/extract_bf6_top_weapons_final.py'],
            capture_output=True,
            text=True,
            timeout=2400  # 40 min timeout
        )
        
        if result2.returncode != 0:
            raise Exception(f"Weapons extraction failed: {result2.stderr}")
        
        # 2. Run DBT transformations
        logging.info("Running DBT transformations...")
        result3 = subprocess.run(
            ['dbt', 'run', '--project-dir', 'dbt'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result3.returncode != 0:
            raise Exception(f"DBT run failed: {result3.stderr}")
        
        # 3. Run DBT tests
        logging.info("Running DBT tests...")
        result4 = subprocess.run(
            ['dbt', 'test', '--project-dir', 'dbt'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # 4. Get extraction stats
        client = bigquery.Client()
        query = """
            SELECT 
                COUNT(*) as total_players,
                MAX(extraction_date) as last_extraction
            FROM `battlefield-meta-aggregator.bf6_meta.bf6_leaderboard_raw`
        """
        stats = client.query(query).to_dataframe().iloc[0]
        
        return {
            'status': 'success',
            'message': 'Data extraction completed successfully',
            'stats': {
                'total_players': int(stats['total_players']),
                'last_extraction': stats['last_extraction'].isoformat()
            }
        }, 200
        
    except Exception as e:
        logging.error(f"Extraction failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }, 500
```

**Fichier :** `cloud_functions/trigger_extraction/requirements.txt`
```
functions-framework==3.*
google-cloud-bigquery==3.14.0
selenium==4.15.0
undetected-chromedriver==3.5.4
beautifulsoup4==4.12.2
dbt-core==1.8.1
dbt-bigquery==1.8.2
```

**Deploy :**
```bash
gcloud functions deploy trigger-extraction \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --timeout 3600 \
    --memory 2GB \
    --region us-central1 \
    --entry-point trigger_extraction
```

---

#### Étape 2 : Ajouter bouton Refresh dans Streamlit

**Modifier :** `dashboard/app.py`

```python
import streamlit as st
import requests

# Dans la sidebar
with st.sidebar:
    st.divider()
    st.subheader("🔄 Data Management")
    
    if st.button("🔄 Refresh Latest Data", type="primary"):
        with st.spinner("⏳ Extracting latest data (35-40 min)..."):
            try:
                # Appel à la Cloud Function
                response = requests.post(
                    "https://us-central1-battlefield-meta-aggregator.cloudfunctions.net/trigger-extraction",
                    timeout=3600  # 1h timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Clear cache
                    st.cache_data.clear()
                    
                    st.success(f"""
                    ✅ Data refreshed successfully!
                    
                    **Stats:**
                    - Total players: {result['stats']['total_players']}
                    - Last extraction: {result['stats']['last_extraction']}
                    """)
                    
                    # Rerun app to show new data
                    st.rerun()
                else:
                    st.error(f"❌ Extraction failed: {response.json()['message']}")
                    
            except requests.exceptions.Timeout:
                st.warning("⏱️ Extraction is taking longer than expected. Check back in a few minutes.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.caption("⚠️ Extraction takes ~35-40 minutes")
```

---

### 5.2 Scénario 2 : Refresh Automatique Hebdomadaire (Dimanches) 📅

**Use case :** Extraction automatique tous les dimanches à 2h UTC (routine)

**Architecture :**
```
Cloud Scheduler (cron) → Trigger Cloud Function
                              ↓
              Python extraction script
                              ↓
        Extract Tracker.gg (97 joueurs + weapons)
                              ↓
              Upload to BigQuery (Bronze)
                              ↓
                  DBT Run (Silver + Gold)
                              ↓
            Notification (Email/Slack)
                              ↓
        Streamlit cache auto-invalide (TTL)
```

**Implémentation détaillée :**

#### Étape 1 : Créer Cloud Scheduler Job

```bash
# Créer le job cron
gcloud scheduler jobs create http weekly-bf6-extraction \
    --schedule="0 2 * * 0" \
    --uri="https://us-central1-battlefield-meta-aggregator.cloudfunctions.net/trigger-extraction" \
    --http-method=POST \
    --time-zone="UTC" \
    --location=us-central1 \
    --description="Weekly BF6 data extraction (Sundays 2am UTC)"
```

---

#### Étape 2 : Ajouter Notifications

**Modifier :** `cloud_functions/trigger_extraction/main.py`

```python
# Ajouter en haut
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

def send_notification(stats, status='success'):
    """Send email notification via SendGrid"""
    
    if status == 'success':
        subject = "✅ BF6 Weekly Extraction - Success"
        content = f"""
        <h2>Battlefield Meta Extraction Completed</h2>
        
        <p><strong>Status:</strong> ✅ Success</p>
        
        <h3>Statistics:</h3>
        <ul>
            <li><strong>Total Players:</strong> {stats['total_players']}</li>
            <li><strong>Last Extraction:</strong> {stats['last_extraction']}</li>
            <li><strong>Duration:</strong> ~35-40 minutes</li>
        </ul>
        
        <p>Dashboard: <a href="https://bf6-meta.streamlit.app">bf6-meta.streamlit.app</a></p>
        """
    else:
        subject = "❌ BF6 Weekly Extraction - Failed"
        content = f"""
        <h2>Battlefield Meta Extraction Failed</h2>
        
        <p><strong>Status:</strong> ❌ Error</p>
        <p><strong>Error:</strong> {stats.get('error', 'Unknown error')}</p>
        
        <p>Check logs: <a href="https://console.cloud.google.com/functions">Cloud Functions Console</a></p>
        """
    
    message = Mail(
        from_email='noreply@bf6meta.com',
        to_emails='your_email@example.com',
        subject=subject,
        html_content=content
    )
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logging.info(f"Email sent: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

# Dans trigger_extraction(), ajouter à la fin :
        send_notification(stats, status='success')
        return {...}
        
# Dans except, ajouter :
    except Exception as e:
        send_notification({'error': str(e)}, status='error')
        return {...}
```

---

#### Étape 3 : Monitoring et Alertes

**Créer alertes dans GCP Monitoring :**

```bash
# Alert si Cloud Function échoue
gcloud alpha monitoring policies create \
    --notification-channels=EMAIL_CHANNEL_ID \
    --display-name="BF6 Extraction Failure Alert" \
    --condition-display-name="Function Error Rate > 10%" \
    --condition-threshold-value=0.1 \
    --condition-threshold-duration=60s
```

---

### 5.3 Comparaison des 2 Scénarios

| Critère | Scénario 1 (Manuel) | Scénario 2 (Auto) |
|---------|---------------------|-------------------|
| **Fréquence** | À la demande | Hebdomadaire (fixe) |
| **Trigger** | Bouton dashboard | Cloud Scheduler (cron) |
| **Contrôle** | Utilisateur décide | Automatique |
| **Coût/mois** | Variable ($0-10) | Fixe ($2) |
| **Latence** | Immédiate | Max 7 jours |
| **Use case** | Événement spécial (patch) | Routine standard |
| **Notification** | Dans dashboard | Email/Slack |
| **Timeout** | 1h (user wait) | 1h (background) |

**Recommandation :** **Implémenter les DEUX** 🎯
- Scénario 2 (auto) pour routine hebdomadaire
- Scénario 1 (manuel) pour patchs/événements urgents

---

### 5.4 Coûts Estimés (GCP)

**Scénario 1 (Manuel - à la demande) :**
- Cloud Functions : $0.40/invocation
- BigQuery : $0 (Free Tier 1TB/mois)
- Usage estimé : 4x/mois = **$1.60/mois**

**Scénario 2 (Auto - hebdomadaire) :**
- Cloud Scheduler : $0.10/job/mois
- Cloud Functions : $0.40/invocation × 4 = $1.60
- BigQuery : $0 (Free Tier)
- SendGrid : $0 (Free 100 emails/jour)
- **Total : $1.70/mois**

**Scénario 1 + 2 combinés :** **~$3-5/mois**

---

### 5.5 Tasks Checklist

- [ ] **Setup GCP Cloud Functions**
  - [ ] Créer fonction `trigger-extraction`
  - [ ] Déployer avec timeout 1h + 2GB RAM
  - [ ] Tester manuellement
  
- [ ] **Scénario 1 : Bouton Refresh**
  - [ ] Modifier `dashboard/app.py` (bouton sidebar)
  - [ ] Gérer états de chargement (spinner)
  - [ ] Clear cache après refresh
  - [ ] Tester end-to-end
  
- [ ] **Scénario 2 : Cron Hebdomadaire**
  - [ ] Créer Cloud Scheduler job (dimanches 2h UTC)
  - [ ] Configurer SendGrid (email notifications)
  - [ ] Ajouter fonction `send_notification()`
  - [ ] Tester trigger manuel
  
- [ ] **Monitoring**
  - [ ] Configurer alertes GCP (error rate > 10%)
  - [ ] Dashboard Cloud Monitoring
  - [ ] Logs structurés (Cloud Logging)
  
- [ ] **Documentation**
  - [ ] Créer `docs/AUTOMATION_GUIDE.md`
  - [ ] Diagrammes d'architecture
  - [ ] Troubleshooting guide
  
- [ ] **Tests**
  - [ ] Test extraction complète (97 joueurs)
  - [ ] Test notifications (success + error)
  - [ ] Test invalidation cache Streamlit
  - [ ] Load testing (10 refreshes simultanés)

**Durée estimée :** 1-2 jours (8-16h)

**Prérequis :** Phase 4.5 complète (dashboard déployé sur Streamlit Cloud)

---

## 🔄 Phase 6 : Airflow Orchestration (Optionnel - Future)

**Note :** Phase 5 remplace Airflow pour ce projet (plus simple avec Cloud Functions)

**Airflow peut être ajouté plus tard si besoin de :**
- Orchestration complexe multi-étapes
- Dépendances entre tasks
- Retry logic avancé
- UI de monitoring riche

### 6.1 Airflow DAG - Alternative (si besoin futur)

**Fichier :** `airflow/dags/daily_bf6_extraction.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'bf6-meta',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 25),
    'email_on_failure': True,
    'email': ['your_email@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bf6_daily_extraction',
    default_args=default_args,
    description='Extract BF6 leaderboard data daily',
    schedule_interval='0 6 * * *',  # 6h UTC daily
    catchup=False
)

# Task 1: Extract data
extract_task = BashOperator(
    task_id='extract_leaderboard',
    bash_command='cd /path/to/project && .venv/bin/python scripts/extract_bf6_leaderboard.py',
    dag=dag
)

# Task 2: Validate data
def validate_extraction(**context):
    from google.cloud import bigquery
    client = bigquery.Client()
    
    query = """
        SELECT COUNT(*) AS row_count
        FROM bf6_meta.bf6_leaderboard_raw
        WHERE DATE(extraction_date) = CURRENT_DATE()
    """
    result = client.query(query).to_dataframe()
    
    if result['row_count'].iloc[0] < 90:  # Au moins 90 joueurs
        raise ValueError(f"Only {result['row_count'].iloc[0]} players extracted!")
    
    print(f"✅ Validation OK: {result['row_count'].iloc[0]} players")

validate_task = PythonOperator(
    task_id='validate_extraction',
    python_callable=validate_extraction,
    dag=dag
)

# Task 3: Run DBT
dbt_run_task = BashOperator(
    task_id='dbt_transform',
    bash_command='cd /path/to/project/dbt && dbt run && dbt test',
    dag=dag
)

# Task 4: Send notification
def send_notification(**context):
    # Utiliser SendGrid, Slack, etc.
    print("✅ Daily extraction completed successfully!")

notify_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag
)

# Define dependencies
extract_task >> validate_task >> dbt_run_task >> notify_task
```

**Setup Airflow :**

```bash
# 1. Installer Airflow
pip install apache-airflow

# 2. Initialiser DB
airflow db init

# 3. Créer user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# 4. Démarrer webserver
airflow webserver -p 8080

# 5. Démarrer scheduler
airflow scheduler
```

**Priorité :** 🟡 MOYENNE (après Phase 5)

---

### 6.2 Alertes et notifications 🔔

**Fichier :** `scripts/meta_alerts.py`

**Fonctionnalités :**

1. **Nouveau #1 weapon**
   - Détecte si top weapon a changé
   - Envoie email/Slack
   - Log dans BigQuery

2. **Changements significatifs**
   - Seuil : +/- 3 ranks ou +10% kills
   - Liste des movers
   - Résumé quotidien

3. **Data freshness**
   - Alerte si extraction_date > 48h
   - Vérifier daily à 12h UTC

**Exemple implémentation :**

```python
import smtplib
from email.mime.text import MIMEText
from google.cloud import bigquery

def check_top_weapon_change():
    """Vérifie si le top weapon a changé"""
    client = bigquery.Client()
    
    query = """
        WITH ranked_weapons AS (
            SELECT 
                weapon_name,
                extraction_date,
                ROW_NUMBER() OVER (
                    PARTITION BY extraction_date 
                    ORDER BY total_kills DESC
                ) AS rank
            FROM gold_weapons_history
            WHERE extraction_date IN (
                SELECT DISTINCT extraction_date 
                FROM gold_weapons_history 
                ORDER BY extraction_date DESC 
                LIMIT 2
            )
        )
        SELECT 
            TODAY.weapon_name AS current_top,
            YESTERDAY.weapon_name AS previous_top
        FROM ranked_weapons TODAY
        LEFT JOIN ranked_weapons YESTERDAY
            ON TODAY.rank = YESTERDAY.rank
        WHERE TODAY.rank = 1 
            AND YESTERDAY.rank = 1
            AND TODAY.extraction_date > YESTERDAY.extraction_date
    """
    
    result = client.query(query).to_dataframe()
    
    if not result.empty:
        current = result['current_top'].iloc[0]
        previous = result['previous_top'].iloc[0]
        
        if current != previous:
            send_alert(
                f"🚨 NEW #1 WEAPON: {current} (was {previous})"
            )
            return True
    
    return False

def send_alert(message):
    """Envoie une alerte par email"""
    msg = MIMEText(message)
    msg['Subject'] = 'BF6 Meta Alert'
    msg['From'] = 'alerts@bf6meta.com'
    msg['To'] = 'your_email@example.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)

if __name__ == "__main__":
    if check_top_weapon_change():
        print("✅ Alert sent: Top weapon changed!")
    else:
        print("ℹ️ No change in top weapon")
```

**Priorité :** 🟢 BASSE (nice-to-have)

---

## ☁️ Phase 7 : Déploiement Cloud (Priorité BASSE)

**Objectif :** Rendre le dashboard accessible publiquement

**Durée estimée :** 3-5 jours

---

### 7.1 Streamlit Community Cloud

**Avantages :**
- ✅ Gratuit pour apps publiques
- ✅ Auto-deploy depuis GitHub
- ✅ URL publique (https://bf6meta.streamlit.app)
- ✅ SSL inclus

**Setup :**

1. **Push sur GitHub**
   ```bash
   git add .
   git commit -m "feat: Dashboard MVP ready for deploy"
   git push origin main
   ```

2. **Créer app sur Streamlit Cloud**
   - Aller sur https://streamlit.io/cloud
   - Connect GitHub repo
   - Sélectionner `dashboard/app.py`
   - Ajouter secrets (BigQuery key en base64)

3. **Configurer secrets**
   ```toml
   # .streamlit/secrets.toml (sur Streamlit Cloud)
   [gcp_service_account]
   type = "service_account"
   project_id = "battlefield-meta-aggregator"
   private_key_id = "..."
   private_key = "..."
   client_email = "..."
   # etc.
   ```

4. **Update code pour secrets**
   ```python
   # dashboard/utils/bigquery.py
   import streamlit as st
   from google.oauth2 import service_account
   
   def get_bigquery_client():
       if st.secrets.get("gcp_service_account"):
           # Production (Streamlit Cloud)
           credentials = service_account.Credentials.from_service_account_info(
               st.secrets["gcp_service_account"]
           )
           return bigquery.Client(credentials=credentials)
       else:
           # Local dev
           credentials_path = Path(__file__).parent.parent.parent / "config" / "bigquery-key.json"
           return bigquery.Client.from_service_account_json(str(credentials_path))
   ```

**Priorité :** 🟢 BASSE (après Phase 5-6)

---

### 7.2 GCP Cloud Run (Alternative)

**Avantages :**
- ✅ Plus de contrôle
- ✅ Custom domain possible
- ✅ Authentication intégrée GCP
- ❌ Coût : ~$5-10/mois

**Setup :**

1. **Créer Dockerfile**
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY dashboard/ dashboard/
   COPY config/ config/
   
   EXPOSE 8080
   CMD streamlit run dashboard/app.py --server.port=8080
   ```

2. **Build et push**
   ```bash
   gcloud builds submit --tag gcr.io/battlefield-meta-aggregator/dashboard
   ```

3. **Deploy sur Cloud Run**
   ```bash
   gcloud run deploy bf6-dashboard \
       --image gcr.io/battlefield-meta-aggregator/dashboard \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated
   ```

**Priorité :** 🟢 BASSE (si besoin auth/custom domain)

---

## 🧪 Tests et CI/CD (Priorité BASSE)

### GitHub Actions workflow

**Fichier :** `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run DBT tests
      run: |
        cd dbt
        dbt test
    
    - name: Lint code
      run: |
        pip install flake8
        flake8 scripts/ dashboard/
    
    - name: Type check
      run: |
        pip install mypy
        mypy scripts/
```

**Priorité :** 🟢 BASSE (nice-to-have)

---

## 📊 Roadmap visuelle

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Phase 4 : Dashboard MVP (COMPLÈTE)                   │
│    - 3 pages interactives                               │
│    - Theme Dark/Light                                   │
│    - Export CSV                                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 🔴 Phase 5 : Analyses avancées (PRIORITÉ HAUTE)         │
│    📈 Meta Trends (évolution temporelle)        2 sem   │
│    🔍 Player Deep Dive (profil détaillé)        1 sem   │
│    ⚔️ Weapon Comparisons (side-by-side)        1 sem   │
│    📅 Filtres temporels                         3 jours │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 🟡 Phase 6 : Automatisation (PRIORITÉ MOYENNE)          │
│    🔄 Airflow DAG (extraction daily)            3 jours │
│    🔔 Alertes (nouveau #1, staleness)           2 jours │
│    📊 Monitoring (data quality)                 2 jours │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 🟢 Phase 7 : Déploiement (PRIORITÉ BASSE)               │
│    ☁️ Streamlit Cloud / Cloud Run               2 jours │
│    🔐 Authentication (optionnel)                 1 jour  │
│    🧪 CI/CD GitHub Actions                      2 jours │
└─────────────────────────────────────────────────────────┘
```

**Durée totale estimée :** 6-8 semaines

---

## ✅ Quick wins (court terme)

Ces tâches peuvent être faites rapidement (< 1 jour) :

1. **Fix warnings Streamlit**
   - Remplacer `use_container_width` par `width='stretch'`
   - Impact : Enlever les warnings de dépréciation

2. **Ajouter favicon et meta tags**
   ```python
   st.set_page_config(
       page_icon="🎮",
       page_title="BF6 Meta Dashboard",
       menu_items={
           'About': "Battlefield 6 Meta Analysis Dashboard"
       }
   )
   ```

3. **Améliorer README.md**
   - Ajouter screenshots
   - Badge "Built with Streamlit"
   - Instructions d'installation plus détaillées

4. **Créer CHANGELOG.md**
   - Documenter toutes les versions
   - Suivre semantic versioning

5. **Ajouter Google Analytics** (optionnel)
   - Tracker usage du dashboard
   - Comprendre pages populaires

---

## 💡 Idées futures (brainstorming)

### Machine Learning
- Prédiction du prochain #1 weapon
- Clustering de joueurs par style
- Anomaly detection (cheaters?)

### Intégrations
- Discord bot (commande `/top-weapon`)
- Twitter bot (daily top 3)
- Twitch overlay (live stats)

### Fonctionnalités avancées
- User accounts (save favorites)
- Custom alerts (notify sur arme spécifique)
- Mobile app (React Native)
- API REST publique

### Analyses supplémentaires
- Map-specific meta
- Mode-specific (TDM vs Conquest)
- Platform comparison (PC vs Console)

---

## 📝 Checklist prochaine session

Avant de commencer Phase 5, vérifier :

- [ ] Dashboard fonctionne (http://localhost:8501)
- [ ] DBT tests passent (47/47)
- [ ] Données récentes dans BigQuery (< 48h)
- [ ] Documentation à jour
- [ ] Git commit de Phase 4
- [ ] Environnement Python propre (`.venv`)

---

## 📞 Questions à se poser

Avant Phase 5 :

1. **Historique de données :** Avons-nous assez d'extractions pour trends?
   - Besoin : Au moins 7-14 jours de data
   - Action : Extraire daily pendant 2 semaines

2. **Priorités utilisateurs :** Quelle feature est la plus demandée?
   - Sondage : Meta trends vs Player profiles vs Weapon compare
   - Décision : Prioriser en conséquence

3. **Performance :** Le dashboard scale-t-il avec plus de data?
   - Test : Simuler 1 mois de données
   - Optimisation : Partitioning BigQuery si nécessaire

---

**🎯 Prochaine action recommandée :**

Commencer par **Meta Trends page** (Phase 5.1) car c'est la feature la plus impactante et nécessite de l'historique que nous pouvons commencer à accumuler dès maintenant.

---

*Document créé par : GitHub Copilot*  
*Date : 25 octobre 2025*  
*Version : 1.0*
