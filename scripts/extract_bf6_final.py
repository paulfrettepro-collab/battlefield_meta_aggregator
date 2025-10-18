"""
EXTRACTION FINALE BF6 LEADERBOARD - VERSION PRODUCTION

Ce script extrait automatiquement les 100 meilleurs joueurs de Battlefield 6
depuis tracker.gg et sauvegarde les données en NDJSON.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


def setup_browser():
    """Configure Chrome en mode headless"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    
    return driver


def extract_leaderboard():
    """Extrait le Top 100 du leaderboard"""
    
    print("\n" + "=" * 80)
    print("🎮 BATTLEFIELD 6 - EXTRACTION LEADERBOARD")
    print("=" * 80)
    
    url = "https://tracker.gg/bf6/leaderboards"
    print(f"\n📡 URL: {url}")
    print("🌐 Démarrage Chrome headless...")
    
    driver = None
    players = []
    
    try:
        driver = setup_browser()
        
        print("⏳ Chargement de la page...")
        driver.get(url)
        
        # Attendre que le JavaScript charge
        time.sleep(10)
        
        print("✅ Page chargée\n")
        print("━" * 80)
        print("📊 EXTRACTION DES JOUEURS")
        print("━" * 80)
        
        # Extraire toutes les lignes
        rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')
        
        print(f"\n✅ {len(rows)} lignes trouvées\n")
        
        for i, row in enumerate(rows, 1):
            try:
                # Extraire toutes les cellules
                cells = row.find_elements(By.TAG_NAME, 'td')
                
                if len(cells) >= 4:
                    # Structure: [rank, username, (vide), kills, score/deaths]
                    rank_text = cells[0].text.strip()
                    username = cells[1].text.strip()
                    kills_text = cells[3].text.strip() if len(cells) > 3 else None
                    score_text = cells[4].text.strip() if len(cells) > 4 else None
                    
                    # Nettoyer les nombres (enlever virgules)
                    kills = int(kills_text.replace(',', '')) if kills_text and kills_text.replace(',', '').isdigit() else None
                    score = int(score_text.replace(',', '')) if score_text and score_text.replace(',', '').isdigit() else None
                    
                    player = {
                        'extraction_date': datetime.now().isoformat(),
                        'rank': int(rank_text) if rank_text.isdigit() else i,
                        'username_original': username,
                        'username_hash': anonymize_username(username),
                        'stats': {
                            'kills': kills,
                            'score': score
                        },
                        'source_url': url,
                        'extraction_method': 'selenium_html'
                    }
                    
                    players.append(player)
                    
                    # Afficher les 10 premiers
                    if i <= 10:
                        stats_str = f"💀 {kills:,} kills" if kills else "Stats N/A"
                        print(f"   [{player['rank']:3d}] {username:20s} → {player['username_hash']} ({stats_str})")
                    elif i == 11:
                        print(f"   ... {len(rows) - 10} autres joueurs ...")
            
            except Exception as e:
                print(f"   ⚠️  Erreur ligne {i}: {e}")
        
        # Sauvegarder
        output_dir = Path('data/bronze')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"bf6_leaderboard_{timestamp}.ndjson"
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for player in players:
                f.write(json.dumps(player) + '\n')
        
        print(f"\n" + "━" * 80)
        print(f"💾 SAUVEGARDE RÉUSSIE")
        print(f"━" * 80)
        print(f"\n📂 Fichier: {output_file}")
        print(f"📊 Joueurs: {len(players)}")
        print(f"📅 Date: {timestamp}")
        
        # Statistiques
        if players:
            players_with_kills = [p for p in players if p['stats'].get('kills')]
            if players_with_kills:
                total_kills = sum(p['stats']['kills'] for p in players_with_kills)
                avg_kills = total_kills / len(players_with_kills)
                top_player = players_with_kills[0]
                
                print(f"\n📈 STATISTIQUES")
                print(f"   Joueurs avec stats: {len(players_with_kills)}/{len(players)}")
                print(f"   Total Kills: {total_kills:,}")
                print(f"   Moyenne Kills: {avg_kills:,.0f}")
                print(f"   Top 1: {top_player['username_hash']} ({top_player['stats']['kills']:,} kills)")
            else:
                print(f"\n⚠️  Aucune stat kills extraite")
        
        return players
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        if driver:
            driver.quit()
            print(f"\n🔒 Navigateur fermé")


if __name__ == "__main__":
    print("\n🎮" * 40)
    print("   BATTLEFIELD 6 - EXTRACTION AUTOMATIQUE")
    print("🎮" * 40)
    
    start_time = time.time()
    players = extract_leaderboard()
    duration = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 80)
    
    if players:
        print(f"\n✅ SUCCESS !")
        print(f"   📊 {len(players)} joueurs extraits")
        print(f"   ⏱️  Durée: {duration:.1f}s")
        print(f"   📂 Format: NDJSON")
        print(f"   🔐 Pseudos: Anonymisés (SHA256)")
        print(f"\n💡 PROCHAINE ÉTAPE: Upload vers MinIO")
        print(f"   docker-compose up -d minio")
        print(f"   python scripts/upload_to_minio.py")
    else:
        print(f"\n⚠️  Extraction échouée")
        print(f"   Vérifier les logs ci-dessus")
    
    print("=" * 80 + "\n")
