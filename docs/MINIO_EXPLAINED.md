# 🗄️ MinIO expliqué simplement

**Pour débutants : Qu'est-ce que MinIO et comment ça marche ?**

---

## 🎯 C'est quoi MinIO en 1 phrase ?

**MinIO = Dropbox pour développeurs, mais en local et gratuit.**

C'est un "Data Lake" (lac de données) où tu stockes des fichiers bruts (JSON, HTML, images) de manière organisée, avec un historique complet.

---

## 🤔 Pourquoi utiliser MinIO ?

### Le problème sans MinIO

```bash
# Tes fichiers de crawls
pcgamer_results.json        # Crawl du 15 octobre
pcgamer_results.json        # Crawl du 16 octobre (écrase le précédent !)
pcgamer_results.json        # Crawl du 17 octobre (écrase encore !)
```

**❌ Problème** : Tu perds l'historique. Impossible de comparer les métas dans le temps.

### La solution avec MinIO

```bash
# MinIO conserve TOUT
minio://battlefield-bronze/
  └── pcgamer/
      └── 2025/
          └── 10/
              ├── 15/data.json   ← Crawl du 15
              ├── 16/data.json   ← Crawl du 16
              └── 17/data.json   ← Crawl du 17
```

**✅ Avantage** : Tu peux comparer comment le méta a évolué entre le 15 et le 17 octobre !

---

## 🏗️ Comment ça fonctionne ?

### Architecture simple

```
1. EXTRACTION (Scrapy)
   └─> pcgamer_results.json (fichier local sur ton Mac)

2. STOCKAGE (MinIO)
   └─> Upload vers minio://battlefield-bronze/pcgamer/2025/10/15/data.json

3. TRANSFORMATION (DBT + BigQuery)
   └─> BigQuery lit MinIO et transforme les données

4. VISUALISATION (Streamlit)
   └─> Dashboard lit BigQuery et affiche les graphiques
```

### Exemple concret

**1. Tu lances un crawl Scrapy :**
```bash
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json
```

**OUTPUT** : Fichier JSON sur ton Mac
```json
[
  {
    "weapon": "PW7A2",
    "attachments": "Single-Port Brake + Hollow Point",
    "meta_score": 4.5,
    "crawled_at": "2025-10-15T14:30:00"
  },
  {
    "weapon": "MX4 Venom",
    "attachments": "Recoil Booster + Extended Mag",
    "meta_score": 4.3,
    "crawled_at": "2025-10-15T14:30:00"
  }
]
```

**2. Tu upload vers MinIO :**
```bash
python scripts/upload_to_minio.py
```

**OUTPUT** : Fichier identique dans MinIO, organisé par date
- **Chemin** : `battlefield-bronze/pcgamer/2025/10/15/data.json`
- **Accessible via** : http://localhost:9001 (interface web)

**3. MinIO organise automatiquement :**
```
battlefield-bronze/          ← Bucket (= dossier racine)
├── pcgamer/                 ← Source
│   ├── 2025/10/15/data.json
│   ├── 2025/10/16/data.json
│   └── 2025/10/17/data.json
├── reddit/
│   ├── 2025/10/15/data.json
│   └── 2025/10/16/data.json
└── skycoach/
    └── 2025/10/15/data.json
```

---

## 🖥️ Interface Web MinIO

### Comment accéder ?

1. **Démarre MinIO** :
   ```bash
   docker-compose up -d minio
   ```

2. **Ouvre ton navigateur** :
   ```
   http://localhost:9001
   ```

3. **Login** :
   - Username : `minioadmin`
   - Password : `minioadmin`

### Que peux-tu faire ?

- ✅ **Voir tous tes fichiers** (buckets, dossiers, fichiers)
- ✅ **Télécharger un fichier** (clic droit → Download)
- ✅ **Supprimer un fichier** (si erreur de crawl)
- ✅ **Créer des buckets** (dossiers racines)
- ✅ **Voir la taille totale** (statistiques de stockage)

### Capture d'écran conceptuelle

```
┌─────────────────────────────────────────────┐
│ MinIO Console                               │
├─────────────────────────────────────────────┤
│ Buckets                                     │
│  └── 📁 battlefield-bronze (125 MB)         │
│       ├── 📁 pcgamer/ (45 MB)               │
│       │    ├── 📁 2025/                     │
│       │    │    └── 📁 10/                  │
│       │    │         ├── 📄 15/data.json    │
│       │    │         └── 📄 16/data.json    │
│       ├── 📁 reddit/ (60 MB)                │
│       └── 📁 skycoach/ (20 MB)              │
└─────────────────────────────────────────────┘
```

---

## 🔄 Workflow complet

### Cas d'usage : Crawl quotidien

**Chaque jour à 2h du matin** (avec Airflow plus tard) :

```python
# 1. Scrapy crawle les 5 sources
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json
scrapy crawl reddit -o data/outputs/reddit_results.json
# ... (3 autres sources)

# 2. Script upload automatique vers MinIO
python scripts/upload_to_minio.py
# ✅ Résultat : 5 nouveaux fichiers dans MinIO
#    battlefield-bronze/pcgamer/2025/10/16/data.json
#    battlefield-bronze/reddit/2025/10/16/data.json
#    ...

# 3. BigQuery charge depuis MinIO (via DBT)
# Les fichiers MinIO sont lus et transformés

# 4. Streamlit affiche les nouvelles données
# Dashboard mis à jour automatiquement
```

### Historique conservé

**Avantage majeur** : Comparer l'évolution du méta

```sql
-- Dans BigQuery, tu peux faire :
SELECT 
  weapon,
  AVG(meta_score) as avg_score,
  crawl_date
FROM battlefield_meta.silver_weapons
WHERE crawl_date BETWEEN '2025-10-01' AND '2025-10-31'
GROUP BY weapon, crawl_date
ORDER BY crawl_date

-- ✅ Tu vois l'évolution de chaque arme jour par jour !
```

---

## 🆚 MinIO vs Alternatives

| Fonctionnalité | MinIO | AWS S3 | Google Cloud Storage | Dossier local |
|---|---|---|---|---|
| **Coût** | ✅ Gratuit | ❌ Payant | ❌ Payant | ✅ Gratuit |
| **Local** | ✅ Oui | ❌ Cloud | ❌ Cloud | ✅ Oui |
| **API S3** | ✅ Oui | ✅ Oui | ❌ Non | ❌ Non |
| **Interface Web** | ✅ Oui | ✅ Oui | ✅ Oui | ❌ Non |
| **Versioning** | ✅ Oui | ✅ Oui | ✅ Oui | ❌ Non |
| **Production** | ✅ Oui | ✅ Oui | ✅ Oui | ❌ Non |

**Conclusion** : MinIO = Meilleur des deux mondes (gratuit + professionnel)

---

## 🛠️ Configuration technique

### Dans `docker-compose.yml`

```yaml
services:
  minio:
    image: minio/minio:latest
    container_name: battlefield-minio
    ports:
      - "9000:9000"   # API (pour ton code Python)
      - "9001:9001"   # Web UI (pour toi)
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - ./data/minio:/data   # Données sur ton Mac
    command: server /data --console-address ":9001"
```

**Explications** :
- **Port 9000** : API pour scripts Python (upload/download)
- **Port 9001** : Interface web pour visualiser
- **Volumes** : Les données sont stockées dans `data/minio/` sur ton Mac (pas perdu si tu redémarres Docker)

### Dans ton code Python

```python
from minio import Minio

# Connexion MinIO
client = Minio(
    "localhost:9000",          # Adresse MinIO
    access_key="minioadmin",   # Username
    secret_key="minioadmin",   # Password
    secure=False               # HTTP (True pour HTTPS en prod)
)

# Upload d'un fichier
client.fput_object(
    bucket_name="battlefield-bronze",
    object_name="pcgamer/2025/10/15/data.json",
    file_path="data/outputs/pcgamer_results.json"
)
# ✅ Fichier uploadé !
```

---

## 📚 Concepts clés

### 1. **Bucket**
- = Dossier racine (comme un disque dur virtuel)
- Exemple : `battlefield-bronze`
- Tu en crées un par "environnement" (bronze, silver, gold)

### 2. **Object**
- = Fichier (JSON, HTML, image, etc.)
- Exemple : `pcgamer/2025/10/15/data.json`
- Chemin complet : `minio://battlefield-bronze/pcgamer/2025/10/15/data.json`

### 3. **Object Path**
- = Chemin du fichier dans le bucket
- Structure recommandée : `{source}/{year}/{month}/{day}/{filename}`
- Permet de filtrer facilement par date

### 4. **API S3-compatible**
- MinIO utilise les mêmes commandes qu'Amazon S3
- Ton code fonctionne sur MinIO ET sur AWS S3 sans changement
- Idéal pour migrer en production plus tard

---

## 🎓 Analogie simple

**MinIO = Bibliothèque organisée**

```
📚 Bibliothèque (Bucket)
  └── 📖 Section "Battlefield" (battlefield-bronze/)
       ├── 📕 Étagère "PC Gamer" (pcgamer/)
       │    ├── 📄 Magazine Octobre 15 (2025/10/15/data.json)
       │    ├── 📄 Magazine Octobre 16 (2025/10/16/data.json)
       │    └── 📄 Magazine Octobre 17 (2025/10/17/data.json)
       ├── 📗 Étagère "Reddit" (reddit/)
       └── 📘 Étagère "Skycoach" (skycoach/)
```

**Avantages** :
- ✅ Tout est classé (par source et date)
- ✅ Rien ne se perd (historique complet)
- ✅ Facile à retrouver (interface web)
- ✅ Évolutif (des millions de fichiers supportés)

---

## 🔍 Cas d'usage réels

### 1. **Comparer deux crawls**

```python
# Télécharger le crawl d'hier
client.fget_object(
    "battlefield-bronze",
    "pcgamer/2025/10/15/data.json",
    "temp/yesterday.json"
)

# Télécharger le crawl d'aujourd'hui
client.fget_object(
    "battlefield-bronze",
    "pcgamer/2025/10/16/data.json",
    "temp/today.json"
)

# Comparer les différences
# ✅ Voir quelles armes ont changé de score
```

### 2. **Analyser l'évolution du méta**

```python
# Télécharger tous les crawls d'octobre
for day in range(1, 32):
    path = f"pcgamer/2025/10/{day:02d}/data.json"
    # Analyser chaque jour
    # ✅ Graphique de l'évolution des scores
```

### 3. **Sauvegarder avant nettoyage**

```bash
# Avant de modifier ton code Scrapy
python scripts/upload_to_minio.py
# ✅ Backup de l'ancien format
# Tu peux maintenant changer ton code sans peur de perdre les données
```

---

## 🚀 Prochaines étapes

### Cette semaine

1. **Tester MinIO** :
   ```bash
   docker-compose up -d minio
   open http://localhost:9001
   ```

2. **Upload ton premier fichier** :
   ```bash
   python scripts/upload_to_minio.py
   ```

3. **Voir le résultat** :
   - Ouvre MinIO Console
   - Clique sur "battlefield-bronze"
   - Vois ton fichier organisé par date

### Semaine prochaine

- Connecter BigQuery à MinIO
- DBT lit les fichiers MinIO automatiquement
- Dashboard affiche les données en temps réel

---

## 🆘 FAQ

**Q : MinIO est-il vraiment gratuit ?**
- ✅ Oui, 100% open source. Tu peux l'utiliser gratuitement, même en production.

**Q : Mes données sont-elles sécurisées ?**
- ✅ Oui, elles restent sur ton Mac (dans `data/minio/`). Rien n'est envoyé sur Internet.

**Q : Combien de données puis-je stocker ?**
- ✅ Aucune limite (sauf la taille de ton disque dur).

**Q : Puis-je utiliser MinIO en production ?**
- ✅ Oui, des entreprises comme Adobe, Uber, Spotify l'utilisent.

**Q : Dois-je apprendre AWS S3 ?**
- ✅ Non, MinIO et S3 fonctionnent pareil. Si tu maîtrises MinIO, tu maîtrises S3.

**Q : Que se passe-t-il si je redémarre Docker ?**
- ✅ Tes données sont conservées (grâce au volume `./data/minio`).

---

## 📖 Ressources

- **Documentation officielle** : https://min.io/docs/minio/linux/index.html
- **Python SDK** : https://min.io/docs/minio/linux/developers/python/API.html
- **Tutoriel vidéo** : https://www.youtube.com/watch?v=tmzGsZaZSKc

---

**MinIO en résumé** : Un Dropbox local, gratuit, compatible AWS S3, avec historique complet. Parfait pour ton Data Lake Battlefield ! 🎮🗄️
