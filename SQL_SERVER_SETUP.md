# 🗄️ Configuration SQL Server pour Battlefield Meta Aggregator

## 📋 Pourquoi SQL Server ?

- ✅ **Enterprise-grade** : Robuste et fiable pour données critiques
- ✅ **Performances** : Excellentes performances pour requêtes analytiques
- ✅ **Intégration Azure** : Facile à déployer sur Azure SQL Database
- ✅ **Outils puissants** : SSMS, Azure Data Studio pour administration
- ✅ **Compatibilité** : Fonctionne bien avec SQLAlchemy/Python

---

## 🚀 Installation du driver ODBC

### macOS
```bash
# Installer Homebrew si nécessaire
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Ajouter le repo Microsoft
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release

# Installer le driver ODBC 18
brew update
brew install msodbcsql18 mssql-tools18

# Vérifier l'installation
odbcinst -q -d -n "ODBC Driver 18 for SQL Server"
```

### Linux (Ubuntu/Debian)
```bash
# Ajouter la clé Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -

# Ajouter le repository
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | \
  sudo tee /etc/apt/sources.list.d/mssql-release.list

# Mettre à jour et installer
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18

# Ajouter au PATH
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc

# Vérifier l'installation
odbcinst -q -d -n "ODBC Driver 18 for SQL Server"
```

### Windows
```powershell
# Télécharger depuis :
# https://go.microsoft.com/fwlink/?linkid=2249004

# Ou installer via winget
winget install Microsoft.ODBC.18
```

---

## 🐳 Lancer SQL Server avec Docker

### 1. Démarrer le conteneur
```bash
# Depuis la racine du projet
docker-compose up -d sqlserver

# Vérifier que le conteneur est démarré
docker-compose ps

# Voir les logs
docker-compose logs sqlserver
```

### 2. Se connecter à SQL Server
```bash
# Via sqlcmd (ligne de commande)
docker exec -it battlefield_sqlserver /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong!Passw0rd'

# Tester la connexion
1> SELECT @@VERSION;
2> GO
```

### 3. Créer la base de données
```sql
-- Dans sqlcmd
CREATE DATABASE battlefield_meta;
GO

USE battlefield_meta;
GO

-- Vérifier
SELECT name FROM sys.databases WHERE name = 'battlefield_meta';
GO
```

---

## 🔧 Configuration Python

### 1. Installer les dépendances
```bash
# Activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Installer les packages
pip install sqlalchemy pyodbc pymssql alembic
```

### 2. Tester la connexion
```python
# test_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

load_dotenv()

# Méthode 1 : Via URL string
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=True)

# Méthode 2 : Via paramètres séparés
connection_url = URL.create(
    "mssql+pyodbc",
    username=os.getenv("DB_USER", "sa"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 1433)),
    database=os.getenv("DB_NAME", "battlefield_meta"),
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "TrustServerCertificate": "yes"
    }
)
engine = create_engine(connection_url, echo=True)

# Tester
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        print("✅ Connexion réussie !")
        print(result.fetchone()[0])
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
```

```bash
# Exécuter le test
python test_connection.py
```

---

## 📊 Schéma de base de données

### Structure Bronze/Silver/Gold

```sql
-- ============================================
-- BRONZE LAYER - Données brutes
-- ============================================

CREATE TABLE sources (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    url NVARCHAR(500) NOT NULL,
    credibility FLOAT DEFAULT 0.5,
    is_active BIT DEFAULT 1,
    last_scraped DATETIME2,
    created_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE raw_pages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    source_id INT FOREIGN KEY REFERENCES sources(id),
    url NVARCHAR(500) NOT NULL,
    html_content NVARCHAR(MAX),
    http_status INT,
    scraped_at DATETIME2 DEFAULT GETDATE(),
    content_hash NVARCHAR(64)
);

-- Index pour performances
CREATE INDEX idx_raw_pages_source_date ON raw_pages(source_id, scraped_at DESC);

-- ============================================
-- SILVER LAYER - Données nettoyées
-- ============================================

CREATE TABLE extracted_items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    source_id INT FOREIGN KEY REFERENCES sources(id),
    entity_type NVARCHAR(50) NOT NULL, -- 'weapon', 'class', 'attachment'
    entity_name NVARCHAR(100) NOT NULL,
    tier NVARCHAR(5),
    tier_score FLOAT,
    win_rate FLOAT,
    win_rate_score FLOAT,
    pick_rate FLOAT,
    pick_rate_score FLOAT,
    rank INT,
    rank_score FLOAT,
    average_score FLOAT,
    scraped_at DATETIME2 DEFAULT GETDATE(),
    game_patch NVARCHAR(50),
    evidence_url NVARCHAR(500)
);

-- Index composé pour requêtes fréquentes
CREATE INDEX idx_extracted_entity ON extracted_items(entity_type, entity_name, scraped_at DESC);
CREATE INDEX idx_extracted_source ON extracted_items(source_id, scraped_at DESC);

-- ============================================
-- GOLD LAYER - Consensus final
-- ============================================

CREATE TABLE consensus (
    id INT IDENTITY(1,1) PRIMARY KEY,
    entity_type NVARCHAR(50) NOT NULL,
    entity_name NVARCHAR(100) NOT NULL,
    consensus_score FLOAT NOT NULL,
    tier NVARCHAR(5),
    rank INT,
    sources_count INT,
    sources_used NVARCHAR(MAX), -- JSON array
    recommended_attachments NVARCHAR(MAX), -- JSON array
    avg_win_rate FLOAT,
    avg_pick_rate FLOAT,
    last_updated DATETIME2 DEFAULT GETDATE(),
    most_recent_data DATETIME2,
    justification NVARCHAR(MAX),
    game_patch NVARCHAR(50)
);

-- Index unique pour éviter doublons
CREATE UNIQUE INDEX idx_consensus_entity ON consensus(entity_type, entity_name, game_patch);

-- ============================================
-- TABLES DE CONFIGURATION
-- ============================================

CREATE TABLE scraping_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    source_id INT FOREIGN KEY REFERENCES sources(id),
    status NVARCHAR(20), -- 'SUCCESS', 'FAILED', 'RETRY'
    items_extracted INT DEFAULT 0,
    error_message NVARCHAR(MAX),
    execution_time_ms INT,
    started_at DATETIME2,
    completed_at DATETIME2 DEFAULT GETDATE()
);

-- Vue pour monitoring
CREATE VIEW v_scraping_health AS
SELECT 
    s.name AS source_name,
    s.last_scraped,
    DATEDIFF(day, s.last_scraped, GETDATE()) AS days_since_last_scrape,
    COUNT(CASE WHEN sl.status = 'SUCCESS' THEN 1 END) AS successful_scrapes,
    COUNT(CASE WHEN sl.status = 'FAILED' THEN 1 END) AS failed_scrapes,
    AVG(sl.execution_time_ms) AS avg_execution_time_ms
FROM sources s
LEFT JOIN scraping_logs sl ON s.id = sl.source_id
    AND sl.started_at >= DATEADD(day, -30, GETDATE())
GROUP BY s.name, s.last_scraped;
```

---

## 🔄 Migrations avec Alembic

### 1. Configuration Alembic
```bash
# Initialiser Alembic
alembic init alembic

# Éditer alembic.ini
sqlalchemy.url = mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/battlefield_meta?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

### 2. Créer une migration
```bash
# Créer la migration initiale
alembic revision --autogenerate -m "Initial schema"

# Appliquer la migration
alembic upgrade head

# Voir l'historique
alembic history
```

---

## 🛠️ Outils d'administration

### Azure Data Studio (recommandé)
```bash
# Télécharger depuis :
# https://docs.microsoft.com/sql/azure-data-studio/download

# macOS
brew install --cask azure-data-studio

# Connexion
Server: localhost,1433
User: sa
Password: YourStrong!Passw0rd
Database: battlefield_meta
```

### SQL Server Management Studio (Windows uniquement)
```powershell
# Télécharger depuis :
# https://aka.ms/ssmsfullsetup
```

---

## 🔒 Sécurité

### 1. Changer le mot de passe SA
```sql
ALTER LOGIN sa WITH PASSWORD = 'NewStrongPassword!2024';
GO
```

### 2. Créer un utilisateur dédié
```sql
-- Créer un login
CREATE LOGIN battlefield_app WITH PASSWORD = 'AppPassword!2024';
GO

-- Créer un utilisateur dans la base
USE battlefield_meta;
GO

CREATE USER battlefield_app FOR LOGIN battlefield_app;
GO

-- Donner les droits nécessaires
ALTER ROLE db_datareader ADD MEMBER battlefield_app;
ALTER ROLE db_datawriter ADD MEMBER battlefield_app;
GO
```

### 3. Mettre à jour .env
```env
DB_USER=battlefield_app
DB_PASSWORD=AppPassword!2024
```

---

## 📈 Monitoring et performances

### Requêtes utiles

```sql
-- Taille de la base de données
SELECT 
    DB_NAME() AS DatabaseName,
    SUM(size * 8 / 1024) AS SizeMB
FROM sys.master_files
WHERE database_id = DB_ID();

-- Top 10 tables par taille
SELECT 
    t.NAME AS TableName,
    p.rows AS RowCounts,
    SUM(a.total_pages) * 8 / 1024 AS TotalSpaceMB
FROM sys.tables t
INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
GROUP BY t.Name, p.Rows
ORDER BY TotalSpaceMB DESC;

-- Statistiques de scraping
SELECT 
    source_name,
    days_since_last_scrape,
    successful_scrapes,
    failed_scrapes,
    avg_execution_time_ms
FROM v_scraping_health
ORDER BY days_since_last_scrape DESC;
```

---

## 🚨 Troubleshooting

### Erreur : "Can't connect to SQL Server"
```bash
# Vérifier que le conteneur est démarré
docker-compose ps

# Vérifier les logs
docker-compose logs sqlserver

# Tester la connexion
docker exec -it battlefield_sqlserver /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong!Passw0rd' -Q "SELECT 1"
```

### Erreur : "ODBC Driver not found"
```bash
# Lister les drivers installés
odbcinst -q -d

# Réinstaller si nécessaire (macOS)
brew reinstall msodbcsql18
```

### Erreur : "Certificate verification failed"
```python
# Ajouter TrustServerCertificate=yes dans l'URL
DATABASE_URL="...?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

---

## ✅ Checklist de démarrage

- [ ] Driver ODBC installé
- [ ] SQL Server Docker en cours d'exécution
- [ ] Base de données `battlefield_meta` créée
- [ ] Test de connexion Python réussi
- [ ] Schéma bronze/silver/gold créé
- [ ] Utilisateur dédié créé (production)
- [ ] Azure Data Studio configuré

**Tu es maintenant prêt à utiliser SQL Server avec ton projet ! 🚀**
