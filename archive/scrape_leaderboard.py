"""
Extraction du Leaderboard Battlefield 6 via Scraping HTML

Ce script extrait le Top 100 des joueurs directement depuis le site Tracker.gg
sans dépendre de l'API (qui n'est peut-être pas disponible pour BF6).
"""

import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime
from pathlib import Path


class BF6LeaderboardScraper:
    """Scraper du leaderboard Battlefield 6"""
    
    def __init__(self):
        self.base_url = "https://tracker.gg/bf6/leaderboards"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.players = []
    
    def anonymize_username(self, username):
        """Anonymise un pseudo via hash SHA256"""
        hash_obj = hashlib.sha256(username.encode())
        return f"player_{hash_obj.hexdigest()[:8]}"
    
    def scrape_leaderboard(self):
        """Scrape le leaderboard"""
        print("━" * 70)
        print("🎮 BATTLEFIELD 6 - EXTRACTION LEADERBOARD")
        print("━" * 70)
        print(f"\n📡 URL : {self.base_url}")
        print(f"⏳ Téléchargement de la page...\n")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            print(f"✅ Page téléchargée ({len(response.text)} caractères)")
            print(f"📄 Parsing HTML...\n")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sauvegarder le HTML pour analyse
            html_file = Path('data/exploration/leaderboard_page.html')
            html_file.parent.mkdir(parents=True, exist_ok=True)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 HTML sauvegardé : {html_file}\n")
            
            # Analyser la structure
            self.analyze_page_structure(soup)
            
            # Tenter d'extraire les données
            self.extract_players(soup)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau : {e}")
            return False
    
    def analyze_page_structure(self, soup):
        """Analyse la structure HTML de la page"""
        print("━" * 70)
        print("🔍 ANALYSE DE LA STRUCTURE HTML")
        print("━" * 70)
        
        # Recherche de patterns courants pour les tableaux
        tables = soup.find_all(['table', 'div'], class_=lambda x: x and ('table' in x.lower() or 'leaderboard' in x.lower() or 'list' in x.lower()))
        print(f"\n📊 Conteneurs trouvés : {len(tables)}")
        
        for i, table in enumerate(tables[:5], 1):  # Limiter à 5 premiers
            classes = table.get('class', [])
            print(f"\n   [{i}] Tag: {table.name}, Classes: {', '.join(classes)}")
            
            # Compter les éléments enfants
            rows = table.find_all(['tr', 'div'], recursive=False)
            print(f"       Lignes directes: {len(rows)}")
        
        # Recherche de données dans les scripts JSON
        scripts = soup.find_all('script', type='application/json')
        print(f"\n📦 Scripts JSON trouvés : {len(scripts)}")
        
        for i, script in enumerate(scripts[:3], 1):
            try:
                data = json.loads(script.string)
                print(f"\n   [{i}] Taille JSON: {len(str(data))} caractères")
                # Afficher les clés principales
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"       Clés principales: {', '.join(keys)}")
            except:
                pass
    
    def extract_players(self, soup):
        """Tente d'extraire les joueurs"""
        print("\n━" * 70)
        print("📊 TENTATIVE D'EXTRACTION DES JOUEURS")
        print("━" * 70)
        
        # Stratégie 1 : Chercher dans les scripts JSON
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Chercher récursivement les données de joueurs
                players = self.find_players_in_json(data)
                if players:
                    print(f"\n✅ Joueurs trouvés dans JSON : {len(players)}")
                    self.players = players
                    return
            except:
                continue
        
        # Stratégie 2 : Chercher dans les balises <tr> ou <div> avec patterns
        rows = soup.find_all(['tr', 'div'], class_=lambda x: x and ('row' in str(x).lower() or 'player' in str(x).lower()))
        print(f"\n📋 Lignes potentielles trouvées : {len(rows)}")
        
        if rows:
            for i, row in enumerate(rows[:5], 1):
                text = row.get_text(strip=True)
                print(f"   [{i}] {text[:100]}...")
        
        print("\n⚠️  Extraction automatique difficile - Structure complexe")
        print("💡 Prochaine étape : Analyser le HTML sauvegardé manuellement")
    
    def find_players_in_json(self, data, depth=0):
        """Recherche récursive de données de joueurs dans JSON"""
        if depth > 10:  # Limiter la profondeur
            return None
        
        if isinstance(data, dict):
            # Chercher des clés qui pourraient contenir des joueurs
            for key in ['players', 'leaderboard', 'entries', 'data', 'items']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            
            # Recherche récursive
            for value in data.values():
                result = self.find_players_in_json(value, depth + 1)
                if result:
                    return result
        
        elif isinstance(data, list):
            # Si c'est une liste et qu'elle contient des dicts avec 'username' ou 'rank'
            if len(data) > 0 and isinstance(data[0], dict):
                if any(key in data[0] for key in ['username', 'rank', 'player', 'name']):
                    return data
        
        return None
    
    def save_results(self):
        """Sauvegarde les résultats"""
        if not self.players:
            print("\n❌ Aucune donnée à sauvegarder")
            return
        
        output_dir = Path('data/bronze')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"bf6_leaderboard_{datetime.now().strftime('%Y-%m-%d')}.ndjson"
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for player in self.players:
                f.write(json.dumps(player) + '\n')
        
        print(f"\n💾 Résultats sauvegardés : {output_file}")
        print(f"📊 Nombre de joueurs : {len(self.players)}")
    
    def run(self):
        """Exécute le scraping complet"""
        print("\n🎮" * 35)
        print("   BATTLEFIELD 6 LEADERBOARD SCRAPER")
        print("🎮" * 35 + "\n")
        
        success = self.scrape_leaderboard()
        
        if success:
            self.save_results()
        
        print("\n" + "=" * 70)
        print("📋 RÉSUMÉ")
        print("=" * 70)
        print(f"\n📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Source : tracker.gg/bf6/leaderboards")
        print(f"📊 Joueurs extraits : {len(self.players)}")
        
        if not self.players:
            print("\n💡 PROCHAINES ÉTAPES :")
            print("   1. Analyser le fichier HTML sauvegardé : data/exploration/leaderboard_page.html")
            print("   2. Identifier les sélecteurs CSS/XPath corrects")
            print("   3. Mettre à jour le script avec les bons sélecteurs")
            print("   4. Relancer l'extraction")
        else:
            print(f"\n✅ SUCCESS ! Données extraites et sauvegardées")
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    scraper = BF6LeaderboardScraper()
    scraper.run()
