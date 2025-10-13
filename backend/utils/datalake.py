"""
Module de gestion du Data Lake
Stockage et récupération de fichiers bruts non structurés
Supporte MinIO (local) et Azure Blob Storage (production)
"""

from minio import Minio
from minio.error import S3Error
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO, List
from loguru import logger
import os
import hashlib


class DataLakeManager:
    """
    Gestionnaire unifié pour le Data Lake
    Supporte MinIO (dev) et Azure Blob (prod)
    """
    
    def __init__(self, use_azure: bool = False):
        """
        Initialise le gestionnaire de Data Lake
        
        Args:
            use_azure: True pour Azure Blob, False pour MinIO
        """
        self.use_azure = use_azure
        
        if use_azure:
            self._init_azure()
        else:
            self._init_minio()
    
    def _init_minio(self):
        """Initialise MinIO client"""
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
        secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        self.minio_client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        self.bucket_name = os.getenv("MINIO_BUCKET", "battlefield-data-lake")
        
        # Créer le bucket s'il n'existe pas
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)
            logger.info(f"✅ Bucket MinIO créé : {self.bucket_name}")
        
        logger.info(f"✅ MinIO initialisé : {endpoint}")
    
    def _init_azure(self):
        """Initialise Azure Blob Storage client"""
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING non défini")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "battlefield-data-lake")
        
        # Créer le conteneur s'il n'existe pas
        try:
            self.blob_service_client.create_container(self.container_name)
            logger.info(f"✅ Conteneur Azure créé : {self.container_name}")
        except Exception:
            pass  # Le conteneur existe déjà
        
        logger.info(f"✅ Azure Blob Storage initialisé")
    
    def _generate_path(self, source: str, content_type: str, filename: str) -> str:
        """
        Génère un chemin organisé dans le Data Lake
        Format: {source}/{content_type}/{year}/{month}/{day}/{filename}
        
        Args:
            source: Nom de la source (ex: "pcgamer")
            content_type: Type de contenu ("html", "json", "image", "video")
            filename: Nom du fichier
            
        Returns:
            Chemin complet dans le Data Lake
            
        Example:
            >>> _generate_path("pcgamer", "html", "weapon-guide.html")
            "pcgamer/html/2025/10/13/weapon-guide.html"
        """
        now = datetime.now()
        return f"{source}/{content_type}/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
    
    def upload_file(
        self,
        source: str,
        content_type: str,
        filename: str,
        data: bytes,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload un fichier dans le Data Lake
        
        Args:
            source: Nom de la source
            content_type: Type de contenu ("html", "json", "image", "video")
            filename: Nom du fichier
            data: Contenu binaire du fichier
            metadata: Métadonnées optionnelles
            
        Returns:
            Chemin du fichier dans le Data Lake
            
        Example:
            >>> manager = DataLakeManager()
            >>> path = manager.upload_file(
            ...     "pcgamer",
            ...     "html",
            ...     "weapon-guide.html",
            ...     b"<html>...</html>",
            ...     {"url": "https://pcgamer.com/...", "size": 1024}
            ... )
        """
        path = self._generate_path(source, content_type, filename)
        
        # Calculer le hash du contenu
        content_hash = hashlib.sha256(data).hexdigest()
        
        # Ajouter métadonnées de base
        if metadata is None:
            metadata = {}
        metadata.update({
            "content_hash": content_hash,
            "size": len(data),
            "uploaded_at": datetime.now().isoformat(),
            "source": source,
            "content_type": content_type
        })
        
        try:
            if self.use_azure:
                self._upload_azure(path, data, metadata)
            else:
                self._upload_minio(path, data, metadata)
            
            logger.success(f"✅ Fichier uploadé : {path} ({len(data)} bytes)")
            return path
            
        except Exception as e:
            logger.error(f"❌ Erreur upload {path} : {e}")
            raise
    
    def _upload_minio(self, path: str, data: bytes, metadata: dict):
        """Upload vers MinIO"""
        from io import BytesIO
        
        # MinIO attend des métadonnées en string
        minio_metadata = {k: str(v) for k, v in metadata.items()}
        
        self.minio_client.put_object(
            self.bucket_name,
            path,
            BytesIO(data),
            len(data),
            metadata=minio_metadata
        )
    
    def _upload_azure(self, path: str, data: bytes, metadata: dict):
        """Upload vers Azure Blob Storage"""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=path
        )
        blob_client.upload_blob(data, overwrite=True, metadata=metadata)
    
    def download_file(self, path: str) -> bytes:
        """
        Télécharge un fichier depuis le Data Lake
        
        Args:
            path: Chemin du fichier dans le Data Lake
            
        Returns:
            Contenu binaire du fichier
        """
        try:
            if self.use_azure:
                return self._download_azure(path)
            else:
                return self._download_minio(path)
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement {path} : {e}")
            raise
    
    def _download_minio(self, path: str) -> bytes:
        """Télécharge depuis MinIO"""
        response = self.minio_client.get_object(self.bucket_name, path)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    
    def _download_azure(self, path: str) -> bytes:
        """Télécharge depuis Azure Blob Storage"""
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=path
        )
        return blob_client.download_blob().readall()
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        Liste les fichiers dans le Data Lake
        
        Args:
            prefix: Préfixe pour filtrer (ex: "pcgamer/html/")
            
        Returns:
            Liste des chemins de fichiers
        """
        try:
            if self.use_azure:
                return self._list_azure(prefix)
            else:
                return self._list_minio(prefix)
        except Exception as e:
            logger.error(f"❌ Erreur listage {prefix} : {e}")
            raise
    
    def _list_minio(self, prefix: str) -> List[str]:
        """Liste fichiers MinIO"""
        objects = self.minio_client.list_objects(
            self.bucket_name,
            prefix=prefix,
            recursive=True
        )
        return [obj.object_name for obj in objects]
    
    def _list_azure(self, prefix: str) -> List[str]:
        """Liste fichiers Azure Blob"""
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]
    
    def delete_old_files(self, days: int = 180):
        """
        Supprime les fichiers plus anciens que X jours
        
        Args:
            days: Nombre de jours de rétention
        """
        logger.info(f"🗑️ Nettoyage des fichiers > {days} jours...")
        # TODO: Implémenter la logique de suppression
        # basée sur la date dans le chemin ou les métadonnées


# ============================================
# Fonctions utilitaires
# ============================================

def save_html_to_datalake(
    source: str,
    url: str,
    html_content: str,
    manager: DataLakeManager
) -> str:
    """
    Sauvegarde une page HTML dans le Data Lake
    
    Args:
        source: Nom de la source
        url: URL de la page
        html_content: Contenu HTML
        manager: Instance de DataLakeManager
        
    Returns:
        Chemin du fichier dans le Data Lake
    """
    # Générer un nom de fichier basé sur l'URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    filename = f"{parsed.netloc}_{parsed.path.replace('/', '_')}.html"
    
    return manager.upload_file(
        source=source,
        content_type="html",
        filename=filename,
        data=html_content.encode('utf-8'),
        metadata={
            "url": url,
            "content_length": len(html_content)
        }
    )


def save_json_to_datalake(
    source: str,
    data: dict,
    filename: str,
    manager: DataLakeManager
) -> str:
    """
    Sauvegarde des données JSON dans le Data Lake
    
    Args:
        source: Nom de la source
        data: Données à sauvegarder
        filename: Nom du fichier
        manager: Instance de DataLakeManager
        
    Returns:
        Chemin du fichier dans le Data Lake
    """
    import json
    
    json_bytes = json.dumps(data, indent=2).encode('utf-8')
    
    return manager.upload_file(
        source=source,
        content_type="json",
        filename=filename,
        data=json_bytes,
        metadata={
            "records_count": len(data) if isinstance(data, list) else 1
        }
    )


# ============================================
# Tests
# ============================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test avec MinIO
    manager = DataLakeManager(use_azure=False)
    
    # Upload un fichier de test
    test_data = b"<html><body>Test HTML</body></html>"
    path = manager.upload_file(
        source="test",
        content_type="html",
        filename="test.html",
        data=test_data
    )
    
    print(f"✅ Fichier uploadé : {path}")
    
    # Télécharger le fichier
    downloaded = manager.download_file(path)
    assert downloaded == test_data
    print("✅ Téléchargement vérifié")
    
    # Lister les fichiers
    files = manager.list_files(prefix="test/")
    print(f"✅ Fichiers trouvés : {files}")
