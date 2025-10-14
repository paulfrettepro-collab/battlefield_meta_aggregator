#!/usr/bin/env python
"""
Script de test pour crawler wzstats.gg sans utiliser la commande scrapy
Permet d'exécuter le spider directement avec Python
"""
import sys
import json
from pathlib import Path

# Ajouter le dossier racine du projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess

# Import du spider
from backend.crawler.spiders.wzstats_spider import WZStatsSpider


def run_crawler():
    """Lance le crawler et sauvegarde les résultats"""
    
    # Configuration personnalisée
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            'wzstats_results.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            }
        }
    }
    
    # Création du processus de crawling
    process = CrawlerProcess(settings)
    
    print("🕷️  Lancement du crawler wzstats.gg...")
    print("📍 URL: https://wzstats.gg/battlefield-6/meta")
    print("⏳ Veuillez patienter...\n")
    
    # Lancement du spider
    process.crawl(WZStatsSpider)
    process.start()
    
    print("\n✅ Crawling terminé!")
    print("📄 Résultats sauvegardés dans: wzstats_results.json")


if __name__ == "__main__":
    run_crawler()
