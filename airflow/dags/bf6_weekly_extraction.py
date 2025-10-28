"""
BF6 Weekly Extraction DAG

Orchestrates the weekly extraction, transformation, and loading of Battlefield 6 meta data.

Schedule: Every Sunday at 2:00 AM UTC
Duration: ~40 minutes total
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Default arguments
default_args = {
    'owner': 'paul_frette',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 10, 27),
}

# DAG definition
dag = DAG(
    'bf6_weekly_extraction',
    default_args=default_args,
    description='Weekly BF6 meta data extraction and transformation',
    schedule_interval='0 2 * * 0',  # Every Sunday at 2AM UTC
    catchup=False,
    tags=['bf6', 'extraction', 'weekly'],
)

# Task 1: Extract Leaderboard
def extract_leaderboard():
    """Extract top 100 players from Tracker.gg leaderboard"""
    import subprocess
    result = subprocess.run(
        [f"{PROJECT_ROOT}/scripts/extract_bf6_leaderboard.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Leaderboard extraction failed: {result.stderr}")
    print(result.stdout)

extract_leaderboard_task = PythonOperator(
    task_id='extract_leaderboard',
    python_callable=extract_leaderboard,
    dag=dag,
)

# Task 2: Extract Top Weapons
def extract_weapons():
    """Extract top 3 weapons for each player"""
    import subprocess
    result = subprocess.run(
        [f"{PROJECT_ROOT}/scripts/extract_bf6_top_weapons_final.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Weapons extraction failed: {result.stderr}")
    print(result.stdout)

extract_weapons_task = PythonOperator(
    task_id='extract_weapons',
    python_callable=extract_weapons,
    dag=dag,
)

# Task 3: Load to BigQuery
def load_bigquery():
    """Upload NDJSON files to BigQuery"""
    import subprocess
    result = subprocess.run(
        [f"{PROJECT_ROOT}/scripts/load_to_bigquery.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"BigQuery load failed: {result.stderr}")
    print(result.stdout)

load_bigquery_task = PythonOperator(
    task_id='load_to_bigquery',
    python_callable=load_bigquery,
    dag=dag,
)

# Task 4: DBT Run Silver Models
dbt_silver_task = BashOperator(
    task_id='dbt_run_silver',
    bash_command=f'cd {PROJECT_ROOT}/dbt && dbt run --select silver.*',
    dag=dag,
)

# Task 5: DBT Run Gold Models  
dbt_gold_task = BashOperator(
    task_id='dbt_run_gold',
    bash_command=f'cd {PROJECT_ROOT}/dbt && dbt run --select gold.*',
    dag=dag,
)

# Task 6: Send Notification
def send_notification(**context):
    """Send success notification"""
    print("✅ BF6 Weekly Extraction completed successfully!")
    print(f"Execution date: {context['execution_date']}")
    print(f"Duration: {context['task_instance'].duration}")
    # TODO: Add Slack/Email notification

notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
extract_leaderboard_task >> extract_weapons_task >> load_bigquery_task >> dbt_silver_task >> dbt_gold_task >> notification_task
