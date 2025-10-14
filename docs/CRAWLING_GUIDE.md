# 🕷️ Guide du Web Crawling avec Scrapy

## 📖 Introduction

Ce guide explique comment utiliser **Scrapy** (framework professionnel de web crawling) pour collecter les données des sites Battlefield 6, puis les stocker dans une **base de données vectorielle** (ChromaDB/Qdrant) pour une recherche sémantique intelligente.

---

## 🆚 Scrapy vs BeautifulSoup/Selenium

### Pourquoi Scrapy ?

| Critère | BeautifulSoup + Selenium | Scrapy |
|---------|--------------------------|--------|
| **Performance** | Lent (1 page à la fois) | Rapide (parallèle, async) |
| **Complexité** | Simple pour débuter | Framework complet |
| **JavaScript** | Selenium (lourd) | Scrapy-Playwright (léger) |
| **Robustesse** | Retry manuel | Retry automatique intégré |
| **Rate Limiting** | À coder manuellement | Middleware intégré |
| **Scalabilité** | Difficile | Excellente (distributed crawling) |
| **Logs** | Basique | Détaillés et structurés |

**Conclusion** : Scrapy est **fait pour crawler 10+ sites** de manière professionnelle et scalable.

---

## 🏗️ Architecture Scrapy

```
┌─────────────────────────────────────────────────────────┐
│  1. SPIDERS (Un par source)                             │
│  Définit quoi crawler et comment extraire les données   │
│  backend/crawler/spiders/pcgamer_spider.py              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. ITEMS (Structure des données)                       │
│  Définit le format des données extraites                │
│  backend/crawler/items.py                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. PIPELINES (Traitement des données)                  │
│  - Nettoyage                                            │
│  - Validation                                           │
│  - Sauvegarde SQL Server                                │
│  - Vectorisation et sauvegarde ChromaDB                 │
│  backend/crawler/pipelines.py                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  4. MIDDLEWARES (Rotation user-agents, proxies, etc.)  │
│  backend/crawler/middlewares.py                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Structure des fichiers

```
backend/
├── crawler/
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── pcgamer_spider.py       # Spider pour PC Gamer
│   │   ├── codmunity_spider.py     # Spider pour CODMunity
│   │   └── reddit_spider.py        # Spider pour Reddit
│   ├── items.py                    # Définition des items
│   ├── pipelines.py                # Pipelines de traitement
│   ├── middlewares.py              # Middlewares (user-agent, delay)
│   ├── settings.py                 # Configuration Scrapy
│   └── scrapy.cfg                  # Config Scrapy
```

---

## 🕷️ Exemple : Spider PC Gamer

### Fichier : `backend/crawler/spiders/pcgamer_spider.py`

```python
import scrapy
from crawler.items import WeaponItem
from datetime import datetime

class PCGamerSpider(scrapy.Spider):
    name = 'pcgamer'
    allowed_domains = ['pcgamer.com']
    start_urls = [
        'https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build',
        'https://www.pcgamer.com/games/fps/battlefield-6-best-weapons',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # 2 secondes entre chaque requête
        'CONCURRENT_REQUESTS': 1,  # 1 requête à la fois pour être poli
    }
    
    def parse(self, response):
        """Parse la page principale et extrait les armes"""
        
        # Extraire le titre de la page
        page_title = response.css('h1::text').get()
        
        # Extraire toutes les armes mentionnées
        weapon_sections = response.css('article section.weapon-review')
        
        for section in weapon_sections:
            weapon = WeaponItem()
            
            # Extraction des données
            weapon['name'] = section.css('h2.weapon-name::text').get()
            weapon['tier'] = section.css('span.tier-badge::text').get()
            weapon['description'] = section.css('p.weapon-desc::text').get()
            weapon['source'] = 'PC Gamer'
            weapon['source_url'] = response.url
            weapon['crawled_at'] = datetime.now().isoformat()
            weapon['page_title'] = page_title
            
            # Texte complet pour vectorisation
            weapon['full_text'] = f"{weapon['name']} {weapon['description']}"
            
            yield weapon
        
        # Suivre les liens vers d'autres pages (si pagination)
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

---

## 📦 Items : Définir la structure des données

### Fichier : `backend/crawler/items.py`

```python
import scrapy

class WeaponItem(scrapy.Item):
    """Item représentant une arme"""
    name = scrapy.Field()           # Nom de l'arme
    tier = scrapy.Field()           # Tier (S, A, B, C)
    description = scrapy.Field()    # Description complète
    win_rate = scrapy.Field()       # Taux de victoire (si disponible)
    pick_rate = scrapy.Field()      # Taux de sélection
    source = scrapy.Field()         # Source (PC Gamer, CODMunity, etc.)
    source_url = scrapy.Field()     # URL de la page
    crawled_at = scrapy.Field()     # Date du crawl
    page_title = scrapy.Field()     # Titre de la page
    full_text = scrapy.Field()      # Texte complet pour vectorisation
```

---

## 🔧 Pipelines : Traiter et sauvegarder les données

### Fichier : `backend/crawler/pipelines.py`

```python
from itemadapter import ItemAdapter
from vectorstore.chromadb_client import ChromaDBClient
from vectorstore.embeddings import generate_embedding
from db.models import CrawledPage
from db.connection import get_session
import hashlib

class VectorStorePipeline:
    """Pipeline pour sauvegarder dans ChromaDB"""
    
    def __init__(self):
        self.chroma_client = ChromaDBClient()
        self.collection = self.chroma_client.get_collection('battlefield_weapons')
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Générer un embedding pour le texte complet
        text = adapter.get('full_text', '')
        embedding = generate_embedding(text)
        
        # ID unique basé sur l'URL
        doc_id = hashlib.md5(adapter['source_url'].encode()).hexdigest()
        
        # Métadonnées
        metadata = {
            'source': adapter['source'],
            'url': adapter['source_url'],
            'crawled_at': adapter['crawled_at'],
            'weapon_name': adapter['name'],
            'tier': adapter.get('tier', 'Unknown')
        }
        
        # Ajouter dans ChromaDB
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return item

class SQLServerPipeline:
    """Pipeline pour sauvegarder métadonnées dans SQL Server"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Créer une session SQL
        session = get_session()
        
        # Créer l'objet
        page = CrawledPage(
            source=adapter['source'],
            url=adapter['source_url'],
            title=adapter.get('page_title'),
            crawled_at=adapter['crawled_at'],
            content_hash=hashlib.md5(adapter['full_text'].encode()).hexdigest()
        )
        
        session.add(page)
        session.commit()
        session.close()
        
        return item
```

---

## 🎯 Base de Données Vectorielle : ChromaDB

### Qu'est-ce qu'une base vectorielle ?

Une base vectorielle stocke des **embeddings** (vecteurs numériques) qui représentent la **signification sémantique** du texte.

**Exemple** :
```
Texte : "ACW-R is the best short-range weapon"
Embedding : [0.23, -0.45, 0.78, ..., 0.12]  (768 dimensions)
```

**Avantage** : Recherche par **sens** plutôt que par mots-clés exacts.

```python
# Recherche traditionnelle (mots-clés)
query = "meilleure arme courte portée"
# ❌ Ne trouve pas "ACW-R best short-range" (mots différents)

# Recherche vectorielle (sémantique)
query = "meilleure arme courte portée"
# ✅ Trouve "ACW-R best short-range" (même sens)
```

---

### Configuration ChromaDB

#### Fichier : `backend/vectorstore/chromadb_client.py`

```python
import chromadb
from chromadb.config import Settings
import os

class ChromaDBClient:
    def __init__(self):
        # En production : utiliser Qdrant Cloud
        # En dev : ChromaDB local
        host = os.getenv('CHROMADB_HOST', 'localhost')
        port = int(os.getenv('CHROMADB_PORT', 8001))
        
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
    
    def get_collection(self, name: str):
        """Récupère ou crée une collection"""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"description": "Battlefield weapons meta data"}
        )
    
    def search(self, query: str, collection_name: str, n_results: int = 5):
        """Recherche sémantique"""
        collection = self.get_collection(collection_name)
        from vectorstore.embeddings import generate_embedding
        
        query_embedding = generate_embedding(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
```

---

### Génération d'embeddings

#### Fichier : `backend/vectorstore/embeddings.py`

```python
from sentence_transformers import SentenceTransformer
import os

# Modèle local (gratuit, fonctionne hors ligne)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list:
    """Génère un embedding à partir d'un texte"""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

# Alternative : OpenAI Embeddings (payant, meilleure qualité)
# from openai import OpenAI
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# 
# def generate_embedding_openai(text: str) -> list:
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=text
#     )
#     return response.data[0].embedding
```

---

## 🚀 Lancer un crawl

### Commande manuelle

```bash
# Crawler un seul site
cd backend
scrapy crawl pcgamer

# Crawler tous les sites
scrapy crawl pcgamer && scrapy crawl codmunity && scrapy crawl reddit

# Sauvegarder dans un fichier JSON (pour debug)
scrapy crawl pcgamer -o output.json
```

### Automatisation avec APScheduler

#### Fichier : `backend/utils/scheduler.py`

```python
from apscheduler.schedulers.background import BackgroundScheduler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.pcgamer_spider import PCGamerSpider
from loguru import logger

def run_crawlers():
    """Lance tous les crawlers"""
    logger.info("Starting crawling job...")
    
    process = CrawlerProcess(get_project_settings())
    
    # Ajouter tous les spiders
    process.crawl(PCGamerSpider)
    # process.crawl(CODMunitySpider)
    # process.crawl(RedditSpider)
    
    process.start()
    logger.info("Crawling job completed")

def start_scheduler():
    """Démarre le scheduler APScheduler"""
    scheduler = BackgroundScheduler()
    
    # Tous les lundis à 2h du matin
    scheduler.add_job(
        run_crawlers,
        trigger='cron',
        day_of_week='mon',
        hour=2,
        minute=0
    )
    
    scheduler.start()
    logger.info("Scheduler started - Crawling every Monday at 2 AM")
```

---

## 🔍 Recherche sémantique

### Exemple d'utilisation

```python
from vectorstore.chromadb_client import ChromaDBClient

client = ChromaDBClient()

# Recherche : "Quelle est la meilleure arme pour les débutants ?"
results = client.search(
    query="best weapon for beginners",
    collection_name="battlefield_weapons",
    n_results=5
)

# Résultats :
# [
#   {
#     "document": "M4A1 is perfect for beginners due to low recoil...",
#     "metadata": {"source": "PC Gamer", "weapon_name": "M4A1", "tier": "A"},
#     "distance": 0.23  # Plus c'est proche de 0, plus c'est pertinent
#   },
#   ...
# ]
```

---

## 📊 Comparaison : SQL Server vs ChromaDB

| Critère | SQL Server | ChromaDB |
|---------|-----------|----------|
| **Type de données** | Structurées (tables) | Non structurées (vecteurs) |
| **Recherche** | Par colonnes exactes | Par similarité sémantique |
| **Exemple** | `SELECT * WHERE tier='S'` | `query="best tier S weapons"` |
| **Usage** | Consensus, statistiques | Contexte, justifications |
| **Stockage** | Métadonnées, scores | Texte complet + embeddings |

**Architecture finale** :
- **SQL Server** : Stocke les scores, tiers, consensus (données structurées)
- **ChromaDB** : Stocke le contenu complet des pages (recherche sémantique)
- **MinIO** : Stocke les fichiers bruts (HTML, images, vidéos)

---

## 🎯 Prochaines étapes

1. **Créer le premier spider** : `backend/crawler/spiders/pcgamer_spider.py`
2. **Configurer Scrapy** : `backend/crawler/settings.py`
3. **Tester le crawl** : `scrapy crawl pcgamer -o test.json`
4. **Implémenter les pipelines** : Sauvegarde SQL Server + ChromaDB
5. **Automatiser avec APScheduler** : Crawl hebdomadaire

---

**Date** : 14 octobre 2025  
**Version** : 1.0  
**Auteur** : GitHub Copilot + Paul Frette
