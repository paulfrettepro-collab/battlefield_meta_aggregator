# 🧠 Guide de la Base de Données Vectorielle

## 📖 Qu'est-ce qu'une base vectorielle ?

Une **base de données vectorielle** stocke des représentations numériques (vecteurs) du texte appelées **embeddings**. Ces vecteurs capturent la **signification sémantique** du contenu.

### Analogie simple : La boussole du sens

Imagine que chaque phrase est un point sur une carte :
- Les phrases avec un **sens similaire** sont **proches** géographiquement
- Les phrases avec un **sens différent** sont **éloignées**

```
Carte sémantique (2D simplifié) :

"ACW-R best weapon" ●────0.2──── ● "ACW-R top gun"
                        │
                       1.5
                        │
          "M4A1 for beginners" ●
                        │
                       2.8
                        │
         "How to cook pasta" ●
```

**Distance** = Similarité sémantique (plus c'est proche, plus c'est similaire)

---

## 🆚 Base Vectorielle vs Base Relationnelle

### SQL Server (Relationnel)
```sql
-- Recherche par mots-clés EXACTS
SELECT * FROM weapons 
WHERE description LIKE '%best weapon%'

-- ❌ Ne trouve pas "top gun" ou "excellent firearm"
```

### ChromaDB (Vectoriel)
```python
# Recherche par SENS
results = collection.query(
    query="best weapon",
    n_results=5
)

# ✅ Trouve aussi "top gun", "excellent firearm", "premier choix"
```

---

## 🏗️ Architecture : Pourquoi 3 systèmes de stockage ?

```
┌────────────────────────────────────────────────────────┐
│  1. SQL SERVER (Données structurées)                   │
│  - Tables avec colonnes fixes                          │
│  - Scores, tiers, statistiques                         │
│  - Consensus final calculé                             │
│  Exemple : weapon_name, tier, final_score, rank        │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  2. CHROMADB/QDRANT (Base vectorielle)                 │
│  - Texte complet + embeddings                          │
│  - Recherche sémantique intelligente                   │
│  - Contexte et justifications                          │
│  Exemple : "ACW-R is the best short-range weapon..."   │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  3. MINIO/AZURE BLOB (Fichiers bruts)                  │
│  - HTML complet des pages                              │
│  - Images, vidéos, JSON brut                           │
│  - Archive pour ré-analyse future                      │
│  Exemple : pcgamer/html/2025/10/14/weapons.html        │
└────────────────────────────────────────────────────────┘
```

### Cas d'usage

| Besoin | Système à utiliser |
|--------|-------------------|
| "Top 10 armes par score" | SQL Server |
| "Pourquoi ACW-R est bon ?" | ChromaDB (recherche texte) |
| "Re-parser les pages d'hier" | MinIO (fichiers HTML) |
| "Armes pour débutants" | ChromaDB (recherche sémantique) |
| "Calculer moyenne pondérée" | SQL Server |

---

## 🎯 ChromaDB : Installation et Configuration

### Option 1 : ChromaDB en local (Dev)

```python
# backend/vectorstore/chromadb_client.py
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"  # Stockage local
))

collection = client.get_or_create_collection("battlefield_weapons")
```

### Option 2 : ChromaDB avec Docker (Recommandé)

Déjà configuré dans `docker-compose.yml` :
```yaml
chromadb:
  image: chromadb/chroma:latest
  ports:
    - "8001:8000"
  volumes:
    - chromadb_data:/chroma/chroma
```

```python
# Connexion au conteneur Docker
import chromadb

client = chromadb.HttpClient(host='localhost', port=8001)
collection = client.get_or_create_collection("battlefield_weapons")
```

### Option 3 : Qdrant (Production)

```python
from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key="your-api-key"
)

client.create_collection(
    collection_name="battlefield_weapons",
    vectors_config={"size": 384, "distance": "Cosine"}
)
```

---

## 🔢 Embeddings : Convertir texte en vecteurs

### Qu'est-ce qu'un embedding ?

Un **embedding** est une représentation numérique d'un texte.

```python
Texte : "ACW-R is the best weapon for close combat"

Embedding (simplifié à 5 dimensions) :
[0.23, -0.45, 0.78, 0.12, -0.33]

En réalité : 384 ou 768 dimensions !
```

### Génération d'embeddings

#### Option 1 : Sentence-Transformers (Local, Gratuit)

```python
# backend/vectorstore/embeddings.py
from sentence_transformers import SentenceTransformer

# Modèle léger (384 dimensions)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str):
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

# Exemple
text = "ACW-R is the best weapon"
embedding = generate_embedding(text)
print(len(embedding))  # 384
```

**Avantages** : Gratuit, fonctionne hors ligne, rapide  
**Inconvénients** : Moins précis que OpenAI

#### Option 2 : OpenAI Embeddings (Cloud, Payant)

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_embedding_openai(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",  # 1536 dimensions
        input=text
    )
    return response.data[0].embedding

# Exemple
text = "ACW-R is the best weapon"
embedding = generate_embedding_openai(text)
print(len(embedding))  # 1536
```

**Avantages** : Très précis, multilingue  
**Inconvénients** : Payant (~$0.02 / 1M tokens)

---

## 💾 Stocker des données dans ChromaDB

### Étape 1 : Créer une collection

```python
from vectorstore.chromadb_client import ChromaDBClient

client = ChromaDBClient()
collection = client.get_collection('battlefield_weapons')
```

### Étape 2 : Ajouter des documents

```python
from vectorstore.embeddings import generate_embedding

# Texte à stocker
text = "The ACW-R excels in close-quarters combat with its high fire rate"

# Générer l'embedding
embedding = generate_embedding(text)

# Métadonnées
metadata = {
    'source': 'PC Gamer',
    'weapon_name': 'ACW-R',
    'tier': 'S',
    'url': 'https://pcgamer.com/...',
    'crawled_at': '2025-10-14T10:30:00'
}

# Ajouter dans ChromaDB
collection.add(
    documents=[text],
    embeddings=[embedding],
    metadatas=[metadata],
    ids=['pcgamer_acwr_001']  # ID unique
)
```

### Étape 3 : Ajout en batch (plus rapide)

```python
texts = [
    "ACW-R excels in close combat",
    "M4A1 is perfect for beginners",
    "SVD-12 dominates long range"
]

embeddings = [generate_embedding(t) for t in texts]

metadatas = [
    {'weapon_name': 'ACW-R', 'tier': 'S'},
    {'weapon_name': 'M4A1', 'tier': 'A'},
    {'weapon_name': 'SVD-12', 'tier': 'S'}
]

ids = ['weapon_001', 'weapon_002', 'weapon_003']

collection.add(
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)
```

---

## 🔍 Recherche sémantique

### Recherche simple

```python
# Question de l'utilisateur
query = "Quelle arme est bonne pour les débutants ?"

# Générer embedding de la question
query_embedding = generate_embedding(query)

# Rechercher dans ChromaDB
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3  # Top 3 résultats
)

# Résultats
print(results)
# {
#   'documents': [
#     ["M4A1 is perfect for beginners due to low recoil"],
#     ["AK-74 is good for new players with its stability"],
#     ["SCAR-L offers a gentle learning curve"]
#   ],
#   'metadatas': [...],
#   'distances': [0.15, 0.23, 0.31]  # Plus proche = plus pertinent
# }
```

### Recherche avec filtres

```python
# Chercher uniquement dans les armes Tier S
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"tier": "S"}  # Filtre sur métadonnées
)

# Chercher par source
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"source": "PC Gamer"}
)

# Filtres multiples
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={
        "$and": [
            {"tier": "S"},
            {"source": "PC Gamer"}
        ]
    }
)
```

---

## 🎯 Cas d'usage concrets

### 1. Trouver le contexte d'un consensus

```python
def get_weapon_justification(weapon_name: str):
    """Trouve pourquoi une arme a un certain tier"""
    
    query = f"Why is {weapon_name} considered a top weapon?"
    query_embedding = generate_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"weapon_name": weapon_name}
    )
    
    # Retourner les justifications
    return [doc for doc in results['documents'][0]]

# Exemple
justifications = get_weapon_justification("ACW-R")
# ["ACW-R excels in close combat with 900 RPM",
#  "ACW-R dominates in small maps like Locker",
#  "ACW-R has the best TTK under 20 meters"]
```

### 2. Recherche multi-critères

```python
def find_weapons_by_criteria(criteria: str):
    """Trouve des armes selon des critères textuels"""
    
    query_embedding = generate_embedding(criteria)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10
    )
    
    # Extraire les noms d'armes uniques
    weapons = set()
    for meta in results['metadatas'][0]:
        weapons.add(meta['weapon_name'])
    
    return list(weapons)

# Exemples
find_weapons_by_criteria("low recoil good for headshots")
# ['M4A1', 'SCAR-L', 'AK-12']

find_weapons_by_criteria("best for aggressive close range")
# ['ACW-R', 'MP7', 'P90']
```

### 3. Détection de changements de méta

```python
def detect_meta_changes():
    """Compare les crawls récents vs anciens"""
    
    # Rechercher contenu récent (cette semaine)
    recent_results = collection.query(
        query_embeddings=[generate_embedding("current meta weapons")],
        where={"crawled_at": {"$gte": "2025-10-07"}},
        n_results=20
    )
    
    # Rechercher contenu ancien (il y a 1 mois)
    old_results = collection.query(
        query_embeddings=[generate_embedding("current meta weapons")],
        where={"crawled_at": {"$lt": "2025-09-14"}},
        n_results=20
    )
    
    # Comparer les armes mentionnées
    recent_weapons = extract_weapons(recent_results)
    old_weapons = extract_weapons(old_results)
    
    new_meta = recent_weapons - old_weapons
    disappeared = old_weapons - recent_weapons
    
    return {
        "new_in_meta": list(new_meta),
        "no_longer_meta": list(disappeared)
    }
```

---

## 📊 Performances et Scalabilité

### Capacité de stockage

| Solution | Max Documents | Latence | Coût |
|----------|---------------|---------|------|
| **ChromaDB (local)** | ~1M documents | ~10ms | Gratuit |
| **Qdrant (cloud)** | ~10M+ documents | ~5ms | $25/mois (1M vecteurs) |
| **Pinecone** | Illimité | ~5ms | $70/mois (100k vecteurs) |

### Optimisation

```python
# 1. Batch inserts (plus rapide)
collection.add(
    documents=texts,  # Liste de 100+ documents
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

# 2. Utiliser des modèles légers
# all-MiniLM-L6-v2 (384 dim) au lieu de OpenAI (1536 dim)

# 3. Indexation HNSW (déjà par défaut dans ChromaDB)
# Recherche approximative ultra-rapide
```

---

## 🔄 Migration ChromaDB → Qdrant (Production)

### Pourquoi migrer ?

- **Scalabilité** : Qdrant gère des milliards de vecteurs
- **Performance** : Recherche distribuée sur plusieurs serveurs
- **Backup** : Snapshots automatiques
- **Sécurité** : API keys, encryption

### Code de migration

```python
# backend/vectorstore/migrate_to_qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import chromadb

# 1. Récupérer les données de ChromaDB
chroma_client = chromadb.HttpClient(host='localhost', port=8001)
chroma_collection = chroma_client.get_collection('battlefield_weapons')

all_data = chroma_collection.get()

# 2. Créer collection Qdrant
qdrant_client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key="your-api-key"
)

qdrant_client.create_collection(
    collection_name="battlefield_weapons",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# 3. Migrer les données
from qdrant_client.models import PointStruct

points = []
for i, (doc, emb, meta, id_) in enumerate(zip(
    all_data['documents'],
    all_data['embeddings'],
    all_data['metadatas'],
    all_data['ids']
)):
    point = PointStruct(
        id=i,
        vector=emb,
        payload={**meta, 'text': doc}
    )
    points.append(point)

qdrant_client.upsert(
    collection_name="battlefield_weapons",
    points=points
)

print(f"Migrated {len(points)} documents to Qdrant")
```

---

## 🎓 Résumé : Quand utiliser quoi ?

```
┌─────────────────────────────────────────────────────────┐
│  SQL SERVER                                             │
│  ✅ Données structurées (tableaux)                      │
│  ✅ Calculs (moyennes, agrégations)                     │
│  ✅ Consensus final, scores normalisés                  │
│  ✅ Requêtes sur colonnes précises                      │
│  Exemple : "SELECT * WHERE tier='S' AND score > 0.8"    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CHROMADB / QDRANT                                      │
│  ✅ Texte complet, descriptions                         │
│  ✅ Recherche sémantique ("armes pour débutants")       │
│  ✅ Contexte, justifications                            │
│  ✅ Analyse de sentiment                                │
│  Exemple : "Trouve armes similaires à ACW-R"            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  MINIO / AZURE BLOB                                     │
│  ✅ Fichiers bruts (HTML, images, vidéos)               │
│  ✅ Archive pour ré-analyse future                      │
│  ✅ Data Lake non structuré                             │
│  ✅ Backup des pages originales                         │
│  Exemple : "Re-parser HTML du 10 octobre"               │
└─────────────────────────────────────────────────────────┘
```

---

**Date** : 14 octobre 2025  
**Version** : 1.0  
**Auteur** : GitHub Copilot + Paul Frette
