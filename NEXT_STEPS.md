# 🚀 PROCHAINES ÉTAPES - Battlefield Meta Aggregator

**Projet ELT Data Engineering par Paul Fretté**

---

## 📍 OÙ TU EN ES MAINTENANT

### ✅ Phase 0 : TERMINÉE (100%)
- ✅ Structure projet organisée
- ✅ Git configuré (email correct)
- ✅ README complet avec nouvelle stack
- ✅ MinIO configuré dans docker-compose
- ✅ 2 spiders testés (PC Gamer, WZStats)

### 🔄 Phase 1 : EN COURS (50%)
- ✅ Spider PC Gamer fonctionnel
- ✅ Extraction loadouts testée
- ⏳ 4 autres spiders à créer
- ⏳ Script upload MinIO à créer
- ⏳ Pipeline complet Bronze à tester

---

## 🎯 LES 3 PROCHAINES ACTIONS (CETTE SEMAINE)

### 🥇 ACTION 1 : Compléter les spiders Scrapy (2-3 heures)

**Objectif** : Crawler les 5 sources principales Battlefield

**Fichiers à créer dans `extract/spiders/`** :
```bash
1. reddit_spider.py        # Posts /r/Battlefield6
2. skycoach_spider.py      # Guides loadouts
3. gam3s_spider.py         # Tier lists
4. beebom_spider.py        # Best weapons
```

**Comment faire** :
1. Copie `pcgamer_spider.py` comme template
2. Change `name`, `start_urls`, et sélecteurs CSS
3. Teste chaque spider : `scrapy crawl reddit -o data/outputs/reddit.json`

**Template spider** (copie-colle et adapte) :
```python
import scrapy
from datetime import datetime

class RedditSpider(scrapy.Spider):
    name = "reddit"
    allowed_domains = ["reddit.com"]
    
    def start_requests(self):
        url = "https://www.reddit.com/r/Battlefield6/hot/"
        yield scrapy.Request(url, callback=self.parse)
    
    def parse(self, response):
        # Extraire les posts
        for post in response.css('div[data-testid="post-container"]'):
            yield {
                'title': post.css('h3::text').get(),
                'content': post.css('div[data-click-id="text"]::text').get(),
                'upvotes': post.css('div[id*="vote-arrows"] span::text').get(),
                'url': response.url,
                'crawled_at': datetime.now().isoformat(),
                'source': 'Reddit',
            }
```

**Validation** : 5 fichiers JSON dans `data/outputs/`

---

### 🥈 ACTION 2 : Script upload MinIO automatique (1-2 heures)

**Objectif** : Sauvegarder automatiquement les données crawlées dans MinIO

**Fichier à créer** : `scripts/upload_to_minio.py`

**Code complet** (copie-colle) :
```python
#!/usr/bin/env python
"""
Script d'upload automatique des résultats crawlés vers MinIO
Organise par date : /bronze/{source}/2025/10/15/data.json
"""
import os
import json
from datetime import datetime
from pathlib import Path
from minio import Minio
from minio.error import S3Error

# Configuration MinIO (variables d'environnement)
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
BUCKET_NAME = 'battlefield-bronze'

def upload_crawl_results(source_name: str, json_file_path: str):
    """
    Upload un fichier JSON crawlé vers MinIO
    
    Args:
        source_name: Nom de la source (pcgamer, reddit, etc.)
        json_file_path: Chemin vers le fichier JSON à uploader
    """
    # Connexion MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  # True en production avec HTTPS
    )
    
    # Créer le bucket s'il n'existe pas
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        print(f"✅ Bucket '{BUCKET_NAME}' créé")
    
    # Organisation par date : /bronze/pcgamer/2025/10/15/data.json
    today = datetime.now()
    object_path = f"bronze/{source_name}/{today.year}/{today.month:02d}/{today.day:02d}/data.json"
    
    # Upload du fichier
    try:
        client.fput_object(
            bucket_name=BUCKET_NAME,
            object_name=object_path,
            file_path=json_file_path,
            content_type='application/json'
        )
        print(f"✅ Uploadé : {json_file_path} → minio://{BUCKET_NAME}/{object_path}")
        
        # Ajouter métadonnées
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            nb_items = len(data) if isinstance(data, list) else 1
        
        print(f"   📊 Items crawlés : {nb_items}")
        return object_path
        
    except S3Error as e:
        print(f"❌ Erreur upload : {e}")
        return None

def upload_all_sources():
    """Upload tous les fichiers de data/outputs/ vers MinIO"""
    outputs_dir = Path('data/outputs')
    
    if not outputs_dir.exists():
        print("❌ Dossier data/outputs/ introuvable")
        return
    
    # Mapping fichiers → sources
    file_mapping = {
        'pcgamer_results.json': 'pcgamer',
        'reddit_results.json': 'reddit',
        'skycoach_results.json': 'skycoach',
        'gam3s_results.json': 'gam3s',
        'beebom_results.json': 'beebom',
    }
    
    uploaded = 0
    for filename, source in file_mapping.items():
        filepath = outputs_dir / filename
        if filepath.exists():
            result = upload_crawl_results(source, str(filepath))
            if result:
                uploaded += 1
    
    print(f"\n✅ Upload terminé : {uploaded} sources uploadées vers MinIO")

if __name__ == "__main__":
    print("🚀 Upload des données crawlées vers MinIO...\n")
    upload_all_sources()
```

**Comment tester** :
```bash
# 1. Démarrer MinIO
docker-compose up -d minio

# 2. Lancer l'upload
python scripts/upload_to_minio.py

# 3. Vérifier dans MinIO Web UI
# Ouvrir http://localhost:9001
# Login : minioadmin / minioadmin
# Voir le bucket "battlefield-bronze"
```

**Validation** : Fichiers visibles dans MinIO Console

---

### 🥉 ACTION 3 : Setup BigQuery + DBT (3-4 heures)

**Objectif** : Préparer le Data Warehouse et les transformations

#### **Étape 3.1 : Créer compte Google Cloud (gratuit)**

1. Va sur https://console.cloud.google.com
2. Crée un compte (300$ de crédit gratuit)
3. Crée un nouveau projet : `battlefield-meta-aggregator`
4. Active l'API BigQuery (gratuit jusqu'à 1TB/mois)

#### **Étape 3.2 : Créer dataset BigQuery**

```bash
# Dans Google Cloud Console
# BigQuery → Créer un dataset
Nom : battlefield_meta
Région : europe-west9 (Paris)
```

#### **Étape 3.3 : Service Account (authentification)**

```bash
# Cloud Console → IAM → Service Accounts
# Créer un compte de service
Nom : battlefield-etl
Rôle : BigQuery Admin

# Télécharger la clé JSON
# Sauvegarder dans : config/bigquery-key.json
# ⚠️ NE PAS COMMITTER CE FICHIER (déjà dans .gitignore)
```

#### **Étape 3.4 : Installer DBT**

```bash
# Installer DBT pour BigQuery
pip install dbt-bigquery

# Vérifier installation
dbt --version
```

#### **Étape 3.5 : Initialiser projet DBT**

```bash
# Dans le dossier dbt/
cd dbt
dbt init battlefield_dbt

# Configurer profiles.yml
# Fichier : ~/.dbt/profiles.yml
```

**Contenu `profiles.yml`** :
```yaml
battlefield_dbt:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: battlefield-meta-aggregator  # Ton projet GCP
      dataset: battlefield_meta
      keyfile: /chemin/vers/bigquery-key.json
      threads: 4
      timeout_seconds: 300
      location: europe-west9
```

**Tester connexion** :
```bash
dbt debug
# ✅ Doit afficher "Connection test: OK"
```

**Validation** : DBT connecté à BigQuery

---

## 📅 PLANNING SEMAINE PROCHAINE

### Lundi - Mardi : Phase 1 complète
- [ ] Créer les 4 spiders manquants
- [ ] Script upload MinIO
- [ ] Tests complets extraction

### Mercredi - Jeudi : Phase 2 BigQuery + DBT
- [ ] Setup BigQuery
- [ ] Premier modèle DBT (Bronze)
- [ ] Modèles Silver (nettoyage)

### Vendredi : Phase 3 Airflow
- [ ] Docker-compose Airflow
- [ ] Premier DAG simple
- [ ] Test orchestration

---

## 🎓 COMPRENDRE MINIO EN 3 PHRASES

### Qu'est-ce que MinIO ?

**MinIO = Dropbox pour ton code** 🗄️

1. **C'est un "Data Lake"** : Tu stockes des fichiers bruts (JSON, HTML, images) sans structure imposée
2. **Compatible S3** : Même API qu'Amazon S3, mais gratuit et local (sur ton Mac)
3. **Organisation simple** : `battlefield-bronze/pcgamer/2025/10/15/data.json`

### Comment ça marche ?

```
Scrapy crawl → JSON généré → Upload MinIO → Organisé par date
                ↓
         pcgamer_results.json
                ↓
    minio://battlefield-bronze/pcgamer/2025/10/15/data.json
```

### L'output de MinIO

**INPUT** : `pcgamer_results.json` (sur ton Mac)
```json
[{
  "weapon": "PW7A2",
  "loadout": "Single-Port Brake + Hollow Point",
  "meta_score": 4.5
}]
```

**OUTPUT** : Fichier identique stocké dans MinIO
- **Accessible via** : http://localhost:9001 (interface web)
- **Chemin** : `battlefield-bronze/pcgamer/2025/10/15/data.json`
- **Avantage** : Historique conservé (tu peux comparer les métas dans le temps)

### Pourquoi MinIO ?

- ✅ **Gratuit** (vs AWS S3 payant)
- ✅ **Local** (données sur ton Mac)
- ✅ **Historique** (chaque crawl est daté et conservé)
- ✅ **Compatible** (code fonctionne sur AWS S3 en production sans changement)

**En résumé** : MinIO = Ton disque dur organisé, accessible via une API professionnelle.

---

## 🗂️ NOUVELLE STRUCTURE DU PROJET

```
battlefield_meta_aggregator/
│
├── 📁 extract/                    ← SCRAPY CRAWLERS
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── pcgamer_spider.py     ✅ Fait
│   │   ├── wzstats_spider.py     ✅ Fait
│   │   ├── reddit_spider.py      ⏳ À créer
│   │   ├── skycoach_spider.py    ⏳ À créer
│   │   ├── gam3s_spider.py       ⏳ À créer
│   │   └── beebom_spider.py      ⏳ À créer
│   ├── items.py                  ✅ Fait
│   ├── settings.py               ✅ Fait
│   └── scrapy.cfg                ✅ Fait
│
├── 📁 dbt/                        ← TRANSFORMATIONS SQL
│   ├── models/
│   │   ├── bronze/               ⏳ Modèles Bronze (raw data)
│   │   ├── silver/               ⏳ Modèles Silver (nettoyé)
│   │   └── gold/                 ⏳ Modèles Gold (KPIs)
│   ├── dbt_project.yml           ⏳ À créer
│   └── profiles.yml              ⏳ À configurer
│
├── 📁 airflow/                    ← ORCHESTRATION
│   ├── dags/
│   │   └── battlefield_pipeline.py  ⏳ DAG principal
│   └── logs/
│
├── 📁 dashboard/                  ← STREAMLIT
│   ├── app.py                    ⏳ Application principale
│   └── pages/                    ⏳ Pages multi-vues
│
├── 📁 scripts/                    ← UTILITAIRES
│   ├── upload_to_minio.py        ⏳ À créer (Action 2)
│   ├── load_bigquery.py          ⏳ À créer (Phase 2)
│   └── test_minio.py             ✅ Existe
│
├── 📁 data/                       ← DONNÉES LOCALES
│   ├── bronze/                   ✅ Créé (vide pour l'instant)
│   └── outputs/                  ✅ Résultats crawls
│       ├── pcgamer_results.json  ✅ Déplacé ici
│       └── meta_analysis.json    ✅ Déplacé ici
│
├── 📁 docs/                       ← DOCUMENTATION
│   ├── CRAWLING_GUIDE.md         ✅ Existe
│   └── ... (autres guides)
│
├── 📁 backend/                    ⚠️ ANCIEN (À SUPPRIMER APRÈS MIGRATION)
│   └── ... (ne plus utiliser)
│
├── docker-compose.yml            ✅ MinIO configuré
├── requirements.txt              ⏳ À mettre à jour
├── readme.md                     ✅ Mis à jour
└── NEXT_STEPS.md                 ✅ Ce fichier !
```

---

## 📋 CHECKLIST RAPIDE

**Cette semaine** :
- [ ] Créer 4 spiders (reddit, skycoach, gam3s, beebom)
- [ ] Script `upload_to_minio.py`
- [ ] Tester upload MinIO (voir fichiers dans http://localhost:9001)
- [ ] Setup BigQuery + Service Account
- [ ] Installer DBT et tester connexion

**Semaine prochaine** :
- [ ] Modèles DBT (Bronze, Silver, Gold)
- [ ] Airflow DAG
- [ ] Dashboard Streamlit

---

## 🆘 BESOIN D'AIDE ?

### Commandes utiles

```bash
# Lancer un spider
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json

# Upload vers MinIO
python scripts/upload_to_minio.py

# Voir MinIO Web UI
open http://localhost:9001

# Tester DBT
cd dbt && dbt debug

# Démarrer Airflow
docker-compose up -d airflow
```

### Ressources

- **Scrapy** : https://docs.scrapy.org/en/latest/intro/tutorial.html
- **MinIO Python** : https://min.io/docs/minio/linux/developers/python/API.html
- **DBT** : https://docs.getdbt.com/docs/introduction
- **BigQuery** : https://cloud.google.com/bigquery/docs/quickstarts

---

## 🎯 OBJECTIF FINAL

**Dans 2 semaines** :
- ✅ 5+ sources Battlefield crawlées quotidiennement
- ✅ Données stockées dans MinIO + BigQuery
- ✅ Transformations DBT automatiques (Bronze → Silver → Gold)
- ✅ Dashboard Streamlit avec top armes/loadouts
- ✅ Pipeline 100% automatisé avec Airflow

**Portfolio** : Un projet ELT complet pour ton CV Data Engineer ! 🚀

---

**Prêt à commencer ? Lance l'ACTION 1 : Créer les 4 spiders !** 💪
