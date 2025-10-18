"""
Extraction BF6 Leaderboard avec Selenium (navigateur automatisé)

Ce script utilise Chrome en headless pour contourner la protection anti-bot 403.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import hashlib
from datetime import datetime
from pathlib import Path
import time


def anonymize_username(username):
    """Anonymise un pseudo via hash SHA256"""
    if not username:
        return "unknown"
    hash_obj = hashlib.sha256(username.encode())
    return f"player_{hash_obj.hexdigest()[:8]}"


def setup_browser(headless=True):
    """Configure le navigateur Chrome"""
    print("🌐 Configuration du navigateur Chrome...")
    
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless=new')  # Mode headless moderne
    
    # Options pour paraître plus "humain"
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Supprimer les indicateurs "automation"
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Installer ChromeDriver automatiquement
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Masquer webdriver property
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        '''
    })
    
    print("✅ Navigateur configuré\n")
    return driver


def extract_leaderboard():
    """Extrait le leaderboard avec Selenium"""
    
    print("\n" + "=" * 80)
    print("🎮 BATTLEFIELD 6 - EXTRACTION LEADERBOARD (SELENIUM)")
    print("=" * 80)
    
    url = "https://tracker.gg/bf6/leaderboards"
    print(f"\n📡 URL: {url}")
    
    driver = None
    
    try:
        # Initialiser le navigateur
        driver = setup_browser(headless=False)  # Mode visible pour debug
        
        # Charger la page
        print(f"⏳ Chargement de la page...")
        driver.get(url)
        
        # Attendre quelques secondes pour que la page charge
        print(f"⏳ Attente du chargement JavaScript (10 secondes)...")
        time.sleep(10)
        
        # Sauvegarder la page HTML complète
        html_file = Path('data/exploration/leaderboard_selenium.html')
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = driver.page_source
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Page chargée ({len(html_content)} caractères)")
        print(f"💾 HTML sauvegardé: {html_file}")
        
        # Chercher __NEXT_DATA__ dans le HTML
        print(f"\n🔍 Recherche des données JSON embarquées...")
        
        try:
            next_data_element = driver.find_element(By.ID, '__NEXT_DATA__')
            next_data_json = next_data_element.get_attribute('textContent')
            
            print(f"✅ __NEXT_DATA__ trouvé ({len(next_data_json)} caractères)")
            
            # Parser le JSON
            data = json.loads(next_data_json)
            
            # Sauvegarder le JSON
            json_file = Path('data/exploration/next_data_selenium.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 JSON sauvegardé: {json_file}")
            
            # Explorer la structure
            print(f"\n📦 Exploration de la structure JSON...")
            
            if 'props' in data and 'pageProps' in data['props']:
                pageProps = data['props']['pageProps']
                
                print(f"   Clés principales: {list(pageProps.keys())}")
                
                # Chercher le leaderboard
                leaderboard = find_leaderboard_in_json(pageProps)
                
                if leaderboard:
                    print(f"\n🎉 LEADERBOARD TROUVÉ ! {len(leaderboard)} entrées")
                    players = extract_from_json(leaderboard)
                    return players
                else:
                    print(f"\n⚠️  Leaderboard non trouvé dans __NEXT_DATA__")
                    print(f"💡 Analyser manuellement: {json_file}")
        
        except Exception as e:
            print(f"⚠️  __NEXT_DATA__ non trouvé ou erreur: {e}")
        
        # Tentative d'extraction HTML directe
        print(f"\n🔍 Tentative d'extraction des éléments HTML...")
        
        try:
            # Attendre que les éléments du leaderboard soient présents
            wait = WebDriverWait(driver, 10)
            
            # Essayer différents sélecteurs CSS
            selectors = [
                'table tbody tr',
                'div[class*="leaderboard"] div[class*="row"]',
                'div[class*="player"]',
                'tr[class*="row"]'
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"\n✅ Trouvé {len(elements)} éléments avec: {selector}")
                        
                        for i, elem in enumerate(elements[:5], 1):
                            text = elem.text.strip()[:100]
                            print(f"   [{i}] {text}...")
                        
                        break
                except:
                    continue
        
        except Exception as e:
            print(f"⚠️  Extraction HTML échouée: {e}")
        
        print(f"\n💡 Prochaines étapes:")
        print(f"   1. Analyser: {html_file}")
        print(f"   2. Analyser: data/exploration/next_data_selenium.json")
        print(f"   3. Identifier les bons sélecteurs CSS/XPath")
        
        input(f"\n⏸️  Appuyer sur Enter pour fermer le navigateur...")
        
        return None
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        if driver:
            print(f"\n🔒 Fermeture du navigateur...")
            driver.quit()


def find_leaderboard_in_json(data, depth=0):
    """Recherche récursive du leaderboard"""
    if depth > 15:
        return None
    
    if isinstance(data, dict):
        # Clés potentielles
        for key in ['leaderboard', 'entries', 'players', 'data', 'items', 'results']:
            if key in data:
                value = data[key]
                if isinstance(value, list) and len(value) > 0:
                    first = value[0]
                    if isinstance(first, dict) and any(k in first for k in ['username', 'rank', 'player', 'name', 'displayName']):
                        return value
        
        # Récursion
        for value in data.values():
            result = find_leaderboard_in_json(value, depth + 1)
            if result:
                return result
    
    elif isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and any(k in first for k in ['username', 'rank', 'player', 'name', 'displayName']):
            return data
    
    return None


def extract_from_json(entries):
    """Extrait les données JSON vers NDJSON"""
    players = []
    
    print(f"\n" + "━" * 80)
    print(f"📊 EXTRACTION DES {len(entries)} ENTRÉES")
    print(f"━" * 80)
    
    for i, entry in enumerate(entries[:100], 1):
        try:
            username = (
                entry.get('username') or
                entry.get('displayName') or
                entry.get('name') or
                entry.get('player', {}).get('username') or
                entry.get('player', {}).get('displayName') or
                'unknown'
            )
            
            rank = entry.get('rank') or entry.get('position') or i
            
            stats = {
                'kills': entry.get('kills') or entry.get('stats', {}).get('kills'),
                'deaths': entry.get('deaths') or entry.get('stats', {}).get('deaths'),
                'kd': entry.get('kd') or entry.get('stats', {}).get('kd'),
                'score': entry.get('score') or entry.get('stats', {}).get('score'),
            }
            stats = {k: v for k, v in stats.items() if v is not None}
            
            player = {
                'extraction_date': datetime.now().isoformat(),
                'rank': rank,
                'username_original': username,
                'username_hash': anonymize_username(username),
                'stats': stats,
                'source_url': 'https://tracker.gg/bf6/leaderboards',
                'extraction_method': 'selenium_json'
            }
            
            players.append(player)
            
            if i <= 5:
                print(f"   [{rank:3d}] {username:20s} → {player['username_hash']}")
                if stats:
                    print(f"        {stats}")
        
        except Exception as e:
            print(f"   ⚠️  Erreur joueur {i}: {e}")
    
    # Sauvegarder
    output_dir = Path('data/bronze')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"bf6_leaderboard_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.ndjson"
    output_file = output_dir / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for player in players:
            f.write(json.dumps(player) + '\n')
    
    print(f"\n💾 Résultats: {output_file}")
    print(f"📊 Joueurs: {len(players)}")
    
    return players


if __name__ == "__main__":
    print("\n🎮" * 40)
    print("   BATTLEFIELD 6 - EXTRACTION AVEC SELENIUM")
    print("🎮" * 40)
    
    players = extract_leaderboard()
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if players:
        print(f"\n✅ SUCCESS ! {len(players)} joueurs extraits")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n💡 Prochaine étape: Upload vers MinIO")
    else:
        print(f"\n⚠️  Extraction incomplète")
        print(f"📂 Fichiers d'analyse:")
        print(f"   - data/exploration/leaderboard_selenium.html")
        print(f"   - data/exploration/next_data_selenium.json")
    
    print("=" * 80 + "\n")
