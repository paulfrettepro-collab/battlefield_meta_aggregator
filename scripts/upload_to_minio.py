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
        object_name = f"bf6/leaderboard/{file_path.name}"
        
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
    # Trouver le dernier fichier créé
    bronze_dir = Path("data/bronze")
    ndjson_files = sorted(bronze_dir.glob("bf6_leaderboard_*.ndjson"), reverse=True)
    
    if not ndjson_files:
        print("❌ Aucun fichier NDJSON trouvé dans data/bronze/")
        exit(1)
    
    latest_file = ndjson_files[0]
    
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
