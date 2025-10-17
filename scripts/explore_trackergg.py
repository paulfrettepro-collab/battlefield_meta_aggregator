"""
Script d'exploration automatique de Tracker.gg Battlefield 2042

Ce script visite les pages clés et génère un rapport d'exploration
pour identifier les sélecteurs CSS et la structure des données.

Usage:
    python scripts/explore_trackergg.py
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path


class TrackerGGExplorer:
    """Explorateur automatique de Tracker.gg"""
    
    BASE_URL = "https://tracker.gg/battlefield-2042"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.report = {
            'exploration_date': datetime.utcnow().isoformat(),
            'leaderboard': {},
            'player_profile': {},
            'recommendations': []
        }
    
    def explore_leaderboard(self):
        """Explore la page leaderboard"""
        url = f"{self.BASE_URL}/leaderboards/stats/all/default?page=1&platform=pc"
        
        print(f"🔍 Exploration du leaderboard : {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche de patterns communs
            self.report['leaderboard'] = {
                'url': url,
                'status_code': response.status_code,
                'page_title': soup.title.string if soup.title else None,
                'potential_containers': self._find_table_containers(soup),
                'links_found': len(soup.find_all('a')),
                'scripts_count': len(soup.find_all('script')),
            }
            
            # Chercher des indices d'API JSON
            json_scripts = [s.string for s in soup.find_all('script') 
                           if s.string and ('window.__INITIAL_STATE__' in s.string or 'data' in s.string)]
            
            if json_scripts:
                self.report['leaderboard']['json_data_found'] = True
                self.report['recommendations'].append(
                    "✅ Données JSON détectées dans les scripts ! Vérifier Network > XHR pour endpoints"
                )
            
            print("✅ Leaderboard exploré")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exploration du leaderboard : {e}")
            self.report['leaderboard']['error'] = str(e)
    
    def _find_table_containers(self, soup):
        """Trouve les conteneurs potentiels de tableaux"""
        containers = []
        
        # Recherche de patterns communs
        for tag in ['table', 'div']:
            for class_pattern in ['table', 'leaderboard', 'list', 'grid', 'rows']:
                elements = soup.find_all(tag, class_=lambda c: c and class_pattern in c.lower())
                for elem in elements[:3]:  # Limite à 3 résultats
                    containers.append({
                        'tag': tag,
                        'class': elem.get('class'),
                        'id': elem.get('id'),
                        'children_count': len(elem.find_all())
                    })
        
        return containers
    
    def explore_sample_profile(self):
        """
        Tente d'explorer un profil joueur (nécessite URL valide)
        Note: Cette méthode nécessite une URL de profil réelle
        """
        print("\n⚠️ Exploration de profil nécessite une URL valide")
        print("👉 Action manuelle requise :")
        print("   1. Visitez https://tracker.gg/battlefield-2042/leaderboards")
        print("   2. Cliquez sur un joueur")
        print("   3. Notez l'URL du profil")
        print("   4. Inspectez la structure HTML (DevTools)")
        
        self.report['player_profile'] = {
            'status': 'manual_exploration_required',
            'instructions': 'Voir docs/TRACKER_GG_EXPLORATION.md'
        }
    
    def check_robots_txt(self):
        """Vérifie le fichier robots.txt"""
        url = "https://tracker.gg/robots.txt"
        
        print(f"\n🤖 Vérification de {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                self.report['robots_txt'] = {
                    'content': response.text,
                    'scraping_allowed': 'Disallow: /' not in response.text,
                }
                
                # Chercher crawl-delay
                for line in response.text.split('\n'):
                    if 'crawl-delay' in line.lower():
                        self.report['robots_txt']['crawl_delay'] = line
                        print(f"⚠️ Rate limit détecté : {line}")
                
                print("✅ robots.txt vérifié")
            else:
                print(f"⚠️ robots.txt non trouvé (status {response.status_code})")
                
        except Exception as e:
            print(f"❌ Erreur robots.txt : {e}")
    
    def generate_report(self):
        """Génère le rapport d'exploration"""
        output_dir = Path('data/exploration')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'trackergg_exploration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Rapport sauvegardé : {output_file}")
        
        # Afficher recommandations
        print("\n📋 Recommandations :")
        if self.report['recommendations']:
            for rec in self.report['recommendations']:
                print(f"  {rec}")
        else:
            print("  ⚠️ Exploration manuelle requise avec DevTools")
            print("  📖 Voir : docs/TRACKER_GG_EXPLORATION.md")
    
    def run(self):
        """Exécute l'exploration complète"""
        print("🚀 Début de l'exploration de Tracker.gg Battlefield 2042\n")
        
        self.check_robots_txt()
        self.explore_leaderboard()
        self.explore_sample_profile()
        
        self.generate_report()
        
        print("\n✅ Exploration terminée !")
        print("\n🎯 Prochaines étapes :")
        print("  1. Ouvrir le rapport JSON dans data/exploration/")
        print("  2. Visiter manuellement Tracker.gg avec DevTools")
        print("  3. Identifier les sélecteurs CSS précis")
        print("  4. Compléter extract/spiders/trackergg_spider.py")


if __name__ == '__main__':
    explorer = TrackerGGExplorer()
    explorer.run()
