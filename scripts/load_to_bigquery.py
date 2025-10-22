"""
Chargement des données BF6 Top Weapons de MinIO vers BigQuery
Phase 2 du pipeline
"""

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import bigquery
from minio import Minio

# Charger les variables d'environnement
load_dotenv()

class BigQueryLoader:
    """Charge les données de MinIO vers BigQuery"""
    
    def __init__(self):
        """Initialise les clients MinIO et BigQuery"""
        
        # Configuration MinIO
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=False
        )
        
        # Configuration BigQuery
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.dataset_id = 'bf6_meta'  # Nom du dataset
        self.table_id = 'top_weapons'  # Nom de la table
        
        self.bq_client = bigquery.Client(project=self.project_id)
        
        print(f"✅ Clients initialisés")
        print(f"   MinIO: {os.getenv('MINIO_ENDPOINT')}")
        print(f"   BigQuery: {self.project_id}")
    
    def create_dataset_if_not_exists(self):
        """Crée le dataset BigQuery s'il n'existe pas"""
        
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.bq_client.get_dataset(dataset_ref)
            print(f"✅ Dataset existe déjà: {dataset_ref}")
        except Exception:
            # Dataset n'existe pas, on le crée
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # ou "EU" selon ta préférence
            dataset.description = "Battlefield 6 meta data - weapons statistics"
            
            dataset = self.bq_client.create_dataset(dataset, timeout=30)
            print(f"✅ Dataset créé: {dataset_ref}")
    
    def create_table_schema(self):
        """Définit le schéma de la table BigQuery"""
        
        schema = [
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("board", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("snapshot_utc", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("handle", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("top_weapons", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("kills", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("accuracy_pct", "FLOAT", mode="NULLABLE"),
            ]),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        ]
        
        return schema
    
    def download_from_minio(self, bucket_name: str, object_name: str, local_path: str):
        """Télécharge un fichier depuis MinIO"""
        
        try:
            self.minio_client.fget_object(bucket_name, object_name, local_path)
            print(f"✅ Fichier téléchargé depuis MinIO: {object_name}")
            return True
        except Exception as e:
            print(f"❌ Erreur téléchargement MinIO: {e}")
            return False
    
    def load_to_bigquery(self, ndjson_file: str, write_disposition="WRITE_TRUNCATE"):
        """
        Charge un fichier NDJSON vers BigQuery
        
        Args:
            ndjson_file: Chemin vers le fichier NDJSON
            write_disposition: 
                - WRITE_TRUNCATE: Remplace la table (défaut)
                - WRITE_APPEND: Ajoute à la table existante
        """
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        # Configuration du job de chargement
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema=self.create_table_schema(),
            write_disposition=write_disposition,
            autodetect=False,  # On utilise notre schéma explicite
        )
        
        print(f"\n📤 Chargement vers BigQuery...")
        print(f"   Table: {table_ref}")
        print(f"   Mode: {write_disposition}")
        
        with open(ndjson_file, 'rb') as f:
            load_job = self.bq_client.load_table_from_file(
                f, 
                table_ref, 
                job_config=job_config
            )
        
        # Attendre la fin du job
        load_job.result()
        
        # Statistiques
        destination_table = self.bq_client.get_table(table_ref)
        print(f"✅ Chargement terminé !")
        print(f"   Lignes chargées: {destination_table.num_rows}")
        print(f"   Taille: {destination_table.num_bytes / 1024:.2f} KB")
        
        return True
    
    def run(self, bucket_name="bronze", object_name=None):
        """
        Pipeline complet: MinIO → BigQuery
        
        Args:
            bucket_name: Nom du bucket MinIO
            object_name: Nom du fichier dans MinIO (None = prend le plus récent)
        """
        
        print("=" * 80)
        print("🚀 CHARGEMENT MINIO → BIGQUERY")
        print("=" * 80)
        print()
        
        # Étape 1: Créer le dataset
        print("📋 Étape 1: Création du dataset")
        print("-" * 80)
        self.create_dataset_if_not_exists()
        print()
        
        # Étape 2: Trouver le fichier dans MinIO
        print("📋 Étape 2: Récupération du fichier depuis MinIO")
        print("-" * 80)
        
        if object_name is None:
            # Lister les objets et prendre le plus récent
            objects = self.minio_client.list_objects(bucket_name, prefix="bf6/top_weapons/")
            objects_list = list(objects)
            
            if not objects_list:
                print("❌ Aucun fichier trouvé dans MinIO")
                return False
            
            # Trier par date et prendre le plus récent
            latest = sorted(objects_list, key=lambda x: x.last_modified, reverse=True)[0]
            object_name = latest.object_name
            
            print(f"✅ Fichier le plus récent trouvé: {object_name}")
            print(f"   Date: {latest.last_modified}")
            print(f"   Taille: {latest.size / 1024:.2f} KB")
        
        # Étape 3: Télécharger depuis MinIO
        print()
        print("📋 Étape 3: Téléchargement depuis MinIO")
        print("-" * 80)
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.ndjson', delete=False) as tmp:
            tmp_path = tmp.name
        
        if not self.download_from_minio(bucket_name, object_name, tmp_path):
            return False
        
        # Étape 4: Charger vers BigQuery
        print()
        print("📋 Étape 4: Chargement vers BigQuery")
        print("-" * 80)
        
        success = self.load_to_bigquery(tmp_path)
        
        # Nettoyage
        os.unlink(tmp_path)
        
        if success:
            print()
            print("=" * 80)
            print("✅ PIPELINE TERMINÉ AVEC SUCCÈS !")
            print("=" * 80)
            print()
            print(f"🔍 Tu peux maintenant requêter les données:")
            print(f"   https://console.cloud.google.com/bigquery?project={self.project_id}")
            print()
            print("Exemple de requête SQL:")
            print(f"   SELECT * FROM `{self.project_id}.{self.dataset_id}.{self.table_id}` LIMIT 10")
        
        return success


def main():
    """Fonction principale"""
    
    try:
        loader = BigQueryLoader()
        loader.run()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
