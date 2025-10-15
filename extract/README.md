# 📥 Extract - Scrapy Crawlers

**Rôle** : Extraire les données de loadouts Battlefield depuis les sites web

## 🎯 Qu'est-ce que c'est ?

Ce dossier contient tous les **spiders Scrapy** qui crawlent les sources de données :
- PC Gamer
- Reddit (r/Battlefield6)
- Skycoach
- Gam3s.gg
- Beebom

## 📁 Structure

```
extract/
├── spiders/               # Tous les spiders
│   ├── pcgamer_spider.py  # Crawl PC Gamer
│   ├── reddit_spider.py   # Crawl Reddit
│   └── ...
├── items.py              # Définition des objets crawlés
├── settings.py           # Configuration Scrapy
└── scrapy.cfg            # Config projet Scrapy
```

## 🚀 Comment utiliser ?

### Lancer un spider

```bash
# Depuis la racine du projet
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json

# Avec logs détaillés
scrapy crawl pcgamer -o data/outputs/pcgamer_results.json -L DEBUG
```

### Créer un nouveau spider

```bash
# Template automatique
scrapy genspider nom_site url_du_site.com

# Exemple
scrapy genspider reddit reddit.com
```

## 📊 Output

Chaque spider génère un fichier JSON :

```json
[
  {
    "weapon": "PW7A2",
    "attachments": "Single-Port Brake, Hollow Point",
    "meta_score": 4.5,
    "source": "PC Gamer",
    "url": "https://...",
    "crawled_at": "2025-10-15T14:30:00"
  }
]
```

## 🔗 Prochaines étapes

Les données crawlées sont ensuite :
1. **Uploadées vers MinIO** (Bronze layer)
2. **Chargées dans BigQuery** (via DBT)
3. **Transformées** (Silver → Gold)
4. **Affichées** dans le dashboard Streamlit
