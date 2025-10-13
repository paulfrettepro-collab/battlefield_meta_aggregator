# 🗄️ Data Lake - Architecture et Utilisation

## 📌 Qu'est-ce qu'un Data Lake ?

Un **Data Lake** est un référentiel centralisé qui permet de stocker **toutes** les données structurées et non structurées à n'importe quelle échelle.

### Différence avec une base de données traditionnelle

| Aspect | Base de données (SQL Server) | Data Lake (MinIO/Azure Blob) |
|--------|----------------------------|------------------------------|
| **Type de données** | Structurées (tables, colonnes) | Structurées ET non structurées |
| **Format** | Schéma fixe | Tout format (HTML, JSON, images, vidéos) |
| **Stockage** | Optimisé pour requêtes | Optimisé pour volume massif |
| **Coût** | Plus cher au GB | Très économique |
| **Cas d'usage** | Données transactionnelles | Archives, ML, analytics |

---

## 🎯 Pourquoi un Data Lake pour Battlefield Meta Aggregator ?

### 1. **Conservation des données brutes**
- ✅ HTML complet des pages → permet de re-parser si algo change
- ✅ Historique des patchnotes → analyse tendances
- ✅ Screenshots d'armes → analyse visuelle future (IA)

### 2. **Analyses futures avec IA**
- 🤖 Analyser images d'armes avec Computer Vision
- 🤖 Transcrire vidéos YouTube avec Speech-to-Text
- 🤖 Analyser sentiment dans commentaires Reddit
- 🤖 Entraîner modèles ML sur historique

### 3. **Conformité et audit**
- 📋 Preuve de collecte éthique (respecter robots.txt)
- 📋 Traçabilité complète des sources
- 📋 Possibilité de supprimer à la demande

### 4. **Économie**
- 💰 Stockage massif pas cher (MinIO gratuit, Azure Blob ~$0.02/GB/mois)
- 💰 SQL Server réservé aux données critiques

---

## 🏗️ Architecture avec Data Lake

```
┌─────────────────────────────────────────────────────────────────┐
│                          SCRAPING                                │
│  Python (Requests, BeautifulSoup, Selenium)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
┌───────────────────────┐  ┌────────────────────────────┐
│   DATA LAKE (MinIO)   │  │  SQL SERVER (Métadonnées)  │
│                       │  │                            │
│ /pcgamer/html/        │  │  Table: raw_pages          │
│   2025/10/13/         │  │  - id                      │
│     weapon-guide.html │  │  - source_id               │
│                       │  │  - datalake_path ←─────────┼─┐
│ /reddit/json/         │  │  - content_hash            │ │
│   2025/10/13/         │  │  - scraped_at              │ │
│     meta-post.json    │  │                            │ │
│                       │  └────────────────────────────┘ │
│ /images/              │                                 │
│   acw-r-screenshot.png│                                 │
└───────────────────────┘                                 │
         │                                                │
         └────────────────────────────────────────────────┘
                          Référence

┌─────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION (Silver)                       │
│  Parser le HTML/JSON depuis Data Lake → Extraire données        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SQL SERVER (Silver)                          │
│  Table: extracted_items (données structurées)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SQL SERVER (Gold)                            │
│  Table: consensus (résultat final)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Organisation du Data Lake

### Structure des dossiers

```
battlefield-data-lake/
│
├── raw-html/                    # Pages HTML brutes
│   ├── pcgamer/
│   │   ├── 2025/
│   │   │   └── 10/
│   │   │       └── 13/
│   │   │           ├── weapon-guide-acwr.html
│   │   │           └── best-loadouts.html
│   │   └── 2025/
│   │       └── 09/
│   │           └── 28/
│   │               └── patch-notes.html
│   ├── reddit/
│   └── ea-forums/
│
├── raw-json/                    # Réponses API brutes
│   ├── battlefield-api/
│   │   └── 2025/10/13/
│   │       └── weapon-stats.json
│   └── reddit-api/
│
├── images/                      # Screenshots, patchnotes
│   ├── weapons/
│   │   ├── acw-r.png
│   │   └── m4a1.png
│   └── patchnotes/
│       └── patch-2.3-screenshot.png
│
├── videos/                      # Tutoriels YouTube (futurs)
│   └── gameplay/
│       └── acw-r-gameplay.mp4
│
└── logs/                        # Logs de scraping détaillés
    └── 2025/10/13/
        └── scraping-log.json
```

---

## 🔧 Utilisation du Data Lake

### 1. **Initialiser le Data Lake**

```python
from backend.utils.datalake import DataLakeManager

# Développement local (MinIO)
manager = DataLakeManager(use_azure=False)

# Production (Azure Blob Storage)
manager = DataLakeManager(use_azure=True)
```

### 2. **Sauvegarder une page HTML**

```python
import requests
from backend.utils.datalake import save_html_to_datalake

# Scraper une page
url = "https://www.pcgamer.com/games/fps/battlefield-6-weapon-guide"
response = requests.get(url)
html_content = response.text

# Sauvegarder dans le Data Lake
datalake_path = save_html_to_datalake(
    source="pcgamer",
    url=url,
    html_content=html_content,
    manager=manager
)

print(f"✅ Sauvegardé dans : {datalake_path}")
# Output: pcgamer/html/2025/10/13/www.pcgamer.com_games_fps_battlefield-6-weapon-guide.html
```

### 3. **Sauvegarder des données dans SQL Server avec référence Data Lake**

```python
from backend.db.models import RawPage, session

# Créer l'entrée SQL Server
raw_page = RawPage(
    source_id=1,  # ID de "pcgamer" dans la table sources
    url=url,
    datalake_path=datalake_path,  # Référence vers Data Lake
    content_hash=hashlib.sha256(html_content.encode()).hexdigest(),
    http_status=response.status_code,
    scraped_at=datetime.now()
)

session.add(raw_page)
session.commit()
```

### 4. **Récupérer une page depuis le Data Lake**

```python
# Récupérer depuis SQL Server
raw_page = session.query(RawPage).filter_by(id=123).first()

# Télécharger depuis Data Lake
html_content = manager.download_file(raw_page.datalake_path)

# Parser le contenu
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
```

### 5. **Lister les fichiers**

```python
# Lister tous les fichiers PC Gamer
files = manager.list_files(prefix="pcgamer/html/")

for file in files:
    print(file)
# Output:
# pcgamer/html/2025/10/13/weapon-guide-acwr.html
# pcgamer/html/2025/10/12/best-loadouts.html
```

---

## 🐳 Configuration Docker

### Démarrer MinIO (Data Lake local)

```bash
# Démarrer tous les services
docker-compose up -d

# Accéder à la console web MinIO
# http://localhost:9001
# User: minioadmin
# Password: minioadmin123
```

### Créer le bucket

```bash
# Le bucket est créé automatiquement au premier upload
# Ou manuellement via la console web
```

---

## ☁️ Configuration Azure Blob Storage (Production)

### 1. Créer un compte de stockage Azure

```bash
# Via Azure CLI
az storage account create \
  --name battlefieldmeta \
  --resource-group battlefield-rg \
  --location westeurope \
  --sku Standard_LRS

# Récupérer la connection string
az storage account show-connection-string \
  --name battlefieldmeta \
  --resource-group battlefield-rg
```

### 2. Créer le conteneur

```bash
az storage container create \
  --name battlefield-data-lake \
  --account-name battlefieldmeta \
  --public-access off
```

### 3. Configurer .env

```env
# Production
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=battlefieldmeta;AccountKey=...;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER=battlefield-data-lake
```

---

## 💰 Coûts estimés

### MinIO (Développement local)
- ✅ **Gratuit** (auto-hébergé)
- Limité par l'espace disque local

### Azure Blob Storage (Production)

| Stockage | Coût/mois | Pour 100 GB |
|----------|-----------|-------------|
| Hot (accès fréquent) | $0.020/GB | $2.00 |
| Cool (accès rare) | $0.010/GB | $1.00 |
| Archive (long terme) | $0.002/GB | $0.20 |

**Stratégie recommandée** :
- Données < 30 jours : **Hot** ($2/100GB)
- Données 30-180 jours : **Cool** ($1/100GB)
- Données > 180 jours : **Archive** ($0.20/100GB)

**Estimation pour ton projet** :
- 10 sources × 1 scraping/semaine = 40 pages/mois
- 500 KB/page × 40 = 20 MB/mois
- **Coût : < $0.50/mois** 💸

---

## 📊 Schéma SQL Server avec Data Lake

### Nouvelle table : `datalake_files`

```sql
CREATE TABLE datalake_files (
    id INT IDENTITY(1,1) PRIMARY KEY,
    source_id INT FOREIGN KEY REFERENCES sources(id),
    file_path NVARCHAR(500) NOT NULL UNIQUE,  -- Chemin dans Data Lake
    content_type NVARCHAR(50) NOT NULL,       -- 'html', 'json', 'image', 'video'
    content_hash NVARCHAR(64) NOT NULL,       -- SHA256 hash
    file_size BIGINT,                          -- Taille en bytes
    original_url NVARCHAR(MAX),                -- URL d'origine
    uploaded_at DATETIME2 DEFAULT GETDATE(),
    expires_at DATETIME2,                      -- Date d'expiration (rétention)
    storage_tier NVARCHAR(20) DEFAULT 'hot'   -- 'hot', 'cool', 'archive'
);

-- Index pour recherches fréquentes
CREATE INDEX idx_datalake_source_date ON datalake_files(source_id, uploaded_at DESC);
CREATE INDEX idx_datalake_hash ON datalake_files(content_hash);
```

### Mise à jour table `raw_pages`

```sql
ALTER TABLE raw_pages
ADD datalake_file_id INT FOREIGN KEY REFERENCES datalake_files(id);
```

---

## 🔄 Workflow complet avec Data Lake

```python
# 1. SCRAPING
html = scrape_pcgamer_page(url)

# 2. SAUVEGARDER DANS DATA LAKE
datalake_path = manager.upload_file(
    source="pcgamer",
    content_type="html",
    filename="weapon-guide.html",
    data=html.encode('utf-8')
)

# 3. SAUVEGARDER MÉTADONNÉES SQL SERVER
datalake_file = DataLakeFile(
    source_id=1,
    file_path=datalake_path,
    content_type="html",
    content_hash=hashlib.sha256(html.encode()).hexdigest(),
    file_size=len(html),
    original_url=url
)
session.add(datalake_file)
session.commit()

# 4. PARSER LES DONNÉES (Silver layer)
weapons = parse_pcgamer_html(html)

# 5. SAUVEGARDER DANS SQL SERVER (Silver)
for weapon in weapons:
    extracted_item = ExtractedItem(
        source_id=1,
        entity_name=weapon['name'],
        tier=weapon['tier'],
        datalake_reference_id=datalake_file.id  # Lien vers fichier source
    )
    session.add(extracted_item)
session.commit()
```

---

## 🚀 Prochaines utilisations avancées (Phase 4)

### 1. Analyse d'images avec Computer Vision

```python
# Détecter les armes dans des screenshots
from azure.ai.vision import ImageAnalysis

image_bytes = manager.download_file("images/weapons/acw-r.png")
analysis = ImageAnalysis(image_bytes)

print(analysis.objects)  # ['assault rifle', 'scope', 'grip']
```

### 2. Transcription de vidéos

```python
# Analyser des tutoriels YouTube
video_bytes = manager.download_file("videos/gameplay/acw-r-guide.mp4")

# Speech-to-text
transcript = transcribe_video(video_bytes)

# Extraire mentions d'armes
mentions = extract_weapon_mentions(transcript)
```

### 3. Entraînement de modèles ML

```python
# Utiliser l'historique pour prédire la prochaine meta
historical_data = load_from_datalake(prefix="pcgamer/html/2025/")

model = train_meta_prediction_model(historical_data)
prediction = model.predict_next_patch()
```

---

## ✅ Checklist Data Lake

- [ ] MinIO démarré avec Docker
- [ ] Console web accessible (http://localhost:9001)
- [ ] Bucket `battlefield-data-lake` créé
- [ ] Module `datalake.py` testé
- [ ] Table `datalake_files` créée dans SQL Server
- [ ] Premier fichier HTML uploadé avec succès
- [ ] Référence Data Lake dans `raw_pages` fonctionnelle

**Tu es maintenant prêt à utiliser le Data Lake ! 🎉**
