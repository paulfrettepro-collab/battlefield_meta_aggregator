#!/usr/bin/env python3
"""
Script de monitoring workflow GitHub Actions en temps réel
Vérifie le status du dernier workflow run et affiche les logs
"""

import requests
import sys
import time
from datetime import datetime

# Configuration
REPO = "paulfrettepro-collab/battlefield_meta_aggregator"
WORKFLOW_NAME = "Weekly BF6 Meta Extraction"

def get_latest_workflow_run():
    """Récupère le dernier workflow run"""
    url = f"https://api.github.com/repos/{REPO}/actions/runs"
    params = {"per_page": 1, "status": "in_progress,queued,completed"}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["total_count"] == 0:
            return None
            
        return data["workflow_runs"][0]
    except Exception as e:
        print(f"❌ Erreur API GitHub: {e}")
        return None


def format_duration(seconds):
    """Formate une durée en secondes"""
    if seconds < 60:
        return f"{seconds}s"
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}m {secs}s"


def monitor_workflow():
    """Monitore le workflow en temps réel"""
    print("=" * 70)
    print("🔍 MONITORING WORKFLOW GITHUB ACTIONS")
    print("=" * 70)
    print(f"📦 Repo: {REPO}")
    print(f"⚙️  Workflow: {WORKFLOW_NAME}")
    print()
    
    print("🔄 Récupération dernier workflow run...")
    run = get_latest_workflow_run()
    
    if not run:
        print("❌ Aucun workflow run trouvé")
        print("💡 Déclencher un workflow manuellement sur GitHub")
        return False
    
    # Informations générales
    run_number = run["run_number"]
    status = run["status"]
    conclusion = run.get("conclusion", "N/A")
    created_at = run["created_at"]
    
    # Calcul durée
    start_time = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
    if status == "completed":
        end_time = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
    else:
        end_time = datetime.now(start_time.tzinfo)
    
    duration = int((end_time - start_time).total_seconds())
    
    print(f"🎯 Workflow Run #{run_number}")
    print(f"📅 Démarré: {created_at}")
    print(f"⏱️  Durée: {format_duration(duration)}")
    print()
    
    # Status avec emoji
    status_emoji = {
        "queued": "⏳",
        "in_progress": "🔄",
        "completed": "✅" if conclusion == "success" else "❌"
    }
    
    print(f"{status_emoji.get(status, '❓')} Status: {status.upper()}")
    if conclusion != "N/A":
        print(f"   Conclusion: {conclusion.upper()}")
    print()
    
    # Jobs
    jobs_url = run["jobs_url"]
    try:
        jobs_response = requests.get(jobs_url)
        jobs_response.raise_for_status()
        jobs_data = jobs_response.json()
        
        print("📋 JOBS:")
        print("-" * 70)
        
        for i, job in enumerate(jobs_data["jobs"], 1):
            job_name = job["name"]
            job_status = job["status"]
            job_conclusion = job.get("conclusion", "N/A")
            
            # Emoji status job
            if job_status == "completed":
                emoji = "✅" if job_conclusion == "success" else "❌"
            elif job_status == "in_progress":
                emoji = "🔄"
            else:
                emoji = "⏳"
            
            # Durée job
            if job.get("started_at"):
                job_start = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                if job.get("completed_at"):
                    job_end = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                else:
                    job_end = datetime.now(job_start.tzinfo)
                job_duration = int((job_end - job_start).total_seconds())
                duration_str = f"({format_duration(job_duration)})"
            else:
                duration_str = ""
            
            print(f"{emoji} Job {i}: {job_name} {duration_str}")
            
            # Focus sur Job 2 (Extract) - le plus critique
            if "Extract" in job_name and job_status == "completed":
                if job_conclusion == "failure":
                    print(f"   ⚠️  ÉCHEC JOB EXTRACTION - Vérifier logs pour détails")
                    print(f"   📎 Logs: {job['html_url']}")
        
        print("-" * 70)
        print()
        
    except Exception as e:
        print(f"⚠️  Impossible de récupérer les jobs: {e}")
        print()
    
    # Recommandations selon status
    if status == "in_progress":
        print("⏳ Workflow en cours...")
        print("💡 Attendre la fin puis valider avec scripts:")
        print("   ./scripts/validate_extraction.sh <ndjson_file>")
        print("   python3 scripts/validate_bigquery.py")
        
    elif status == "completed":
        if conclusion == "success":
            print("✅ WORKFLOW RÉUSSI !")
            print()
            print("🎯 PROCHAINES ÉTAPES:")
            print("1. Télécharger artefacts depuis GitHub Actions")
            print("2. Valider extraction:")
            print("   ./scripts/validate_extraction.sh <ndjson_file>")
            print("3. Valider BigQuery:")
            print("   python3 scripts/validate_bigquery.py")
            print("4. Vérifier Dashboard Streamlit")
            
        else:
            print("❌ WORKFLOW ÉCHOUÉ")
            print()
            print("🔍 ACTIONS:")
            print("1. Consulter logs Job 2 (Extract) sur GitHub")
            print("2. Chercher erreur 'Cloudflare challenge non résolu'")
            print("3. Si Cloudflare: voir docs/TROUBLESHOOTING.md")
            print("4. Relancer workflow si erreur temporaire")
    
    print()
    print(f"🔗 Voir détails: {run['html_url']}")
    
    return conclusion == "success" if status == "completed" else None


if __name__ == "__main__":
    success = monitor_workflow()
    
    if success is True:
        sys.exit(0)
    elif success is False:
        sys.exit(1)
    else:
        sys.exit(2)  # En cours
