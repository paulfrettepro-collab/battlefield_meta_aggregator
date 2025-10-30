"""
Upload des fichiers NDJSON vers MinIO (Data Lake Bronze)

Ce script upload les données extraites vers le bucket MinIO.
"""

from minio import Minio
from minio.error import S3Error
from pathlib import Path
from datetime import datetime
import os


def upload_to_minio(file_path, bucket_name="bronze"):
    """Upload un fichier vers MinIO"""
    
    print("\n" + "=" * 80)
    print("📤 UPLOAD VERS MINIO")
    print("=" * 80)
    
    # Configuration MinIO (depuis docker-compose.yml)
    minio_client = Minio(
        "localhost:9000",
        access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        secure=False
    )
    
    print(f"\n🌐 Connexion à MinIO...")
    print(f"   Endpoint: localhost:9000")
    print(f"   Bucket: {bucket_name}")
    
    try:
        # Créer le bucket s'il n'existe pas
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' créé")
        else:
            print(f"✅ Bucket '{bucket_name}' existe déjà")
        
        # Uploader le fichier
        file_path = Path(file_path)
        object_name = f"bf6/top_weapons/{file_path.name}"  # Correct path pour armes
        
        print(f"\n📤 Upload en cours...")
        print(f"   Source: {file_path}")
        print(f"   Destination: {bucket_name}/{object_name}")
        
        minio_client.fput_object(
            bucket_name,
            object_name,
            str(file_path),
            content_type="application/x-ndjson"
        )
        
        print(f"\n✅ Upload réussi !")
        print(f"   📂 Object: {object_name}")
        print(f"   📊 Taille: {file_path.stat().st_size:,} octets")
        
        # Interface web
        print(f"\n💡 Vérifier dans l'interface MinIO:")
        print(f"   🌐 http://localhost:9001")
        print(f"   👤 User: minioadmin")
        print(f"   🔑 Pass: minioadmin")
        
        return True
    
    except S3Error as e:
        print(f"\n❌ Erreur MinIO: {e}")
        print(f"\n💡 Vérifier que MinIO est lancé:")
        print(f"   docker-compose up -d minio")
        return False
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    # Fichier d'extraction des armes (100 joueurs)
    latest_file = Path("data/bronze/tracker_gg/top_weapons/bf6_top_weapons_2025-10-20_200220.ndjson")
    
    if not latest_file.exists():
        print(f"❌ Fichier introuvable: {latest_file}")
        exit(1)
    
    print("\n🎮" * 40)
    print("   BATTLEFIELD 6 - UPLOAD MINIO")
    print("🎮" * 40)
    
    print(f"\n📂 Fichier à uploader: {latest_file}")
    print(f"📅 Date: {datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = upload_to_minio(latest_file)
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if success:
        print("\n✅ SUCCESS ! Données dans MinIO")
        print("\n💡 PROCHAINE ÉTAPE: Configuration BigQuery")
    else:
        print("\n⚠️  Upload échoué - Voir logs ci-dessus")
    
    print("=" * 80 + "\n")
