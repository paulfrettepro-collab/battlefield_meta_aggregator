"""
Test de connexion à BigQuery
Vérifie que les credentials et le projet sont correctement configurés
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_bigquery_connection():
    """Test la connexion à BigQuery"""
    
    print("=" * 80)
    print("🔍 TEST CONNEXION BIGQUERY")
    print("=" * 80)
    print()
    
    # 1. Vérifier que les variables d'environnement existent
    print("📋 Étape 1: Vérification des variables d'environnement")
    print("-" * 80)
    
    gcp_project_id = os.getenv('GCP_PROJECT_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not gcp_project_id:
        print("❌ GCP_PROJECT_ID non trouvé dans .env")
        print("   Ajoute: GCP_PROJECT_ID=ton-project-id")
        return False
    else:
        print(f"✅ GCP_PROJECT_ID trouvé: {gcp_project_id}")
    
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS non trouvé dans .env")
        print("   Ajoute: GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json")
        return False
    else:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS trouvé: {credentials_path}")
    
    print()
    
    # 2. Vérifier que le fichier de credentials existe
    print("📋 Étape 2: Vérification du fichier credentials")
    print("-" * 80)
    
    credentials_file = Path(credentials_path)
    if not credentials_file.exists():
        print(f"❌ Fichier non trouvé: {credentials_path}")
        print("   Place ton fichier bigquery-key.json dans config/")
        return False
    else:
        print(f"✅ Fichier trouvé: {credentials_path}")
        print(f"   Taille: {credentials_file.stat().st_size} octets")
    
    print()
    
    # 3. Vérifier que google-cloud-bigquery est installé
    print("📋 Étape 3: Vérification de google-cloud-bigquery")
    print("-" * 80)
    
    try:
        from google.cloud import bigquery
        print("✅ google-cloud-bigquery est installé")
    except ImportError:
        print("❌ google-cloud-bigquery n'est pas installé")
        print("   Lance: pip install google-cloud-bigquery")
        return False
    
    print()
    
    # 4. Tester la connexion
    print("📋 Étape 4: Test de connexion à BigQuery")
    print("-" * 80)
    
    try:
        # Créer le client BigQuery
        client = bigquery.Client(project=gcp_project_id)
        
        print(f"✅ Client BigQuery créé")
        print(f"   Project: {client.project}")
        print(f"   Location: {client.location or 'default (US)'}")
        
        # Lister les datasets (sera vide au début)
        print("\n📊 Datasets existants:")
        datasets = list(client.list_datasets())
        
        if datasets:
            for dataset in datasets:
                print(f"  • {dataset.dataset_id}")
        else:
            print("  (Aucun dataset - c'est normal pour un nouveau projet)")
        
        print()
        print("=" * 80)
        print("✅ CONNEXION BIGQUERY RÉUSSIE !")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print()
        print("Causes possibles:")
        print("  • Le fichier JSON de credentials est invalide")
        print("  • Le projet n'existe pas ou l'ID est incorrect")
        print("  • BigQuery API n'est pas activée")
        print("  • Le compte de service n'a pas les bonnes permissions")
        return False

if __name__ == "__main__":
    success = test_bigquery_connection()
    exit(0 if success else 1)
