#!/usr/bin/env python
"""
Script de test pour crawler PC Gamer
"""
import sys
from pathlib import Path

# Ajouter le dossier racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess
from backend.crawler.spiders.pcgamer_spider import PCGamerSpider


def run_crawler():
    """Lance le crawler PC Gamer"""
    
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            'pcgamer_results.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
                'indent': 2,
            }
        }
    }
    
    process = CrawlerProcess(settings)
    
    print("🕷️  Lancement du crawler PC Gamer...")
    print("📍 URL: https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build")
    print("⏳ Veuillez patienter...\n")
    
    process.crawl(PCGamerSpider)
    process.start()
    
    print("\n✅ Crawling terminé!")
    print("📄 Résultats sauvegardés dans: pcgamer_results.json")


if __name__ == "__main__":
    run_crawler()
