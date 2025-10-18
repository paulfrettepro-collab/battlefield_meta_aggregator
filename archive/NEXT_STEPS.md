# 🚀 PROCHAINES ÉTAPES - Battlefield Meta Aggregator

**Projet ELT Data Engineering par Paul Fretté**

---

## 📍 OÙ TU EN ES MAINTENANT

### ✅ Phase 0 : TERMINÉE (100%)
- ✅ Structure projet organisée
- ✅ Git configuré (email correct)
- ✅ README complet avec nouvelle stack
- ✅ MinIO configuré dans docker-compose
- ✅ Documentation complète créée

### 🔍 Phase 0.5 : EXPLORATION DES SOURCES (⚠️ PRIORITÉ ABSOLUE)
**⚠️ AVANT de coder, tu dois explorer les sources de données disponibles !**

- ⏳ Rechercher API officielle EA/DICE (Priorité #1)
- ⏳ Analyser Tracker.gg (API possible)
- ⏳ Tester Reddit API (officielle)
- ⏳ Comparer 10+ sources potentielles
- ⏳ Remplir tableau comparatif (voir `docs/SOURCES_EXPLORATION.md`)
- ⏳ Choisir les 5 meilleures sources (API > Scraping)

**📖 Guide complet** : `docs/SOURCES_EXPLORATION.md`

**Pourquoi c'est critique ?**
- 🚀 Les APIs sont 10x plus rapides que le scraping
- 🛡️ Les APIs sont légales et stables (pas de ban)
- 📊 Données structurées (JSON propre)
- ⚡ Moins de code à écrire et maintenir

**Temps estimé** : 2-3 jours d'exploration

---

### 🔄 Phase 1 : EXTRACTION (APRÈS Phase 0.5)
- ✅ Spider PC Gamer fonctionnel (pour test)
- ✅ Spider WZStats fonctionnel (pour test)
- ⏳ Implémenter APIs trouvées (Priorité #1)
- ⏳ Compléter avec Scrapy si nécessaire
- ⏳ Script upload MinIO à créer
- ⏳ Pipeline complet Bronze à tester

---

## 🎯 LES PROCHAINES ACTIONS (DANS L'ORDRE)

### 🥇 ACTION 0.5 : EXPLORATION DES SOURCES (⚠️ COMMENCE ICI !)

**⚠️ NOUVELLE PRIORITÉ : Ne code RIEN avant d'avoir exploré les APIs disponibles !**

**Objectif** : Trouver les meilleures sources de données (APIs > Scraping)

**Durée** : 2-3 jours d'exploration

**Document complet** : 📖 **`docs/SOURCES_EXPLORATION.md`**

#### Checklist d'exploration

```
[ ] 1. Rechercher API officielle EA/DICE Battlefield
       → Chercher "Battlefield API", "EA Developer Portal"
       → Vérifier BattleLog API

[ ] 2. Tester Tracker.gg (API possible)
       → DevTools → Network → Chercher endpoints API
       → Tester avec curl

[ ] 3. Setup Reddit API (officielle)
       → Créer app Reddit : https://www.reddit.com/prefs/apps
       → Installer praw : pip install praw
       → Tester extraction posts r/Battlefield6

[ ] 4. Remplir tableau comparatif (10+ sources)
       → Scorer chaque source (/55 points)
       → Documenter findings

[ ] 5. Choisir 5 sources finales
       → Privilégier APIs en priorité
       → Scrapy en complément seulement

[ ] 6. Créer plan d'implémentation
       → Ordre : API EA → Tracker → Reddit → Scraping
       → Temps estimé par source
```

#### Livrables attendus

```
/data/exploration/           # Dossier à créer
├── test_api_ea.json        # Si API trouvée
├── test_api_tracker.json   # Réponse Tracker.gg
├── test_api_reddit.json    # Posts Reddit
├── findings_summary.md     # Résumé découvertes
└── final_sources.md        # 5 sources choisies
```

#### Résultat attendu

**Avant exploration** (hypothèse) :
```
5 sources = 5 spiders Scrapy à créer
Temps estimé : 10-15 heures
Risque : Scraping instable, bans possibles
```

**Après exploration** (objectif) :
```
3 APIs + 2 spiders Scrapy
Temps estimé : 6-8 heures
Avantage : Rapide, stable, légal ✅
```

**📖 Guide détaillé** : `docs/SOURCES_EXPLORATION.md`

---

### � ACTION 1 : Implémenter les sources choisies (APRÈS Action 0.5)

**Objectif** : Extraire les données des sources validées

**Cette action sera mise à jour APRÈS ton exploration !**

Structure prévue :
```
/extract/
├── apis/                    # Clients API (si trouvés)
│   ├── ea_client.py        # API EA/DICE
│   ├── tracker_client.py   # Tracker.gg
│   └── reddit_client.py    # Reddit API
├── spiders/                 # Scrapy (complément)
│   ├── pcgamer_spider.py   ✅ Déjà fait
│   └── ...                 # Selon findings
└── README.md
```

**Temps estimé** : Variable selon APIs trouvées (voir Action 0.5)

---

### 🥉 ACTION 2 : Script upload MinIO (1-2 heures)

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

### � ACTION 2 : Script upload MinIO (1-2 heures)

**Objectif** : Sauvegarder automatiquement les données extraites dans MinIO

**⚠️ Cette action reste la même, quel que soit le résultat de l'exploration**

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

## 📅 PLANNING RÉVISÉ

### Cette semaine : Phase 0.5 - EXPLORATION
- [ ] Rechercher API EA/DICE Battlefield (Priorité #1)
- [ ] Tester Tracker.gg API
- [ ] Setup Reddit API
- [ ] Analyser 10+ sources potentielles
- [ ] Remplir tableau comparatif (docs/SOURCES_EXPLORATION.md)
- [ ] Choisir 5 sources finales (API > Scraping)
- [ ] Créer plan d'implémentation détaillé

### Semaine prochaine : Phase 1 - IMPLÉMENTATION
- [ ] Implémenter APIs trouvées (selon findings)
- [ ] Compléter avec spiders Scrapy si nécessaire
- [ ] Script upload MinIO
- [ ] Tests complets extraction

### Semaine +2 : Phase 2 - BigQuery + DBT
- [ ] Setup BigQuery
- [ ] Premier modèle DBT (Bronze)
- [ ] Modèles Silver (nettoyage)

### Semaine +3 : Phase 3 - Airflow
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
