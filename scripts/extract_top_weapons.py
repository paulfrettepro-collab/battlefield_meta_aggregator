"""
EXTRACTION TOP 3 WEAPONS PAR JOUEUR - BF6 TRACKER.GG

Ce script extrait les 3 armes les plus jouées par chaque joueur du leaderboard
avec leurs statistiques (kills, accuracy).

Étapes :
1. Récupère les 100 joueurs du leaderboard
2. Visite chaque profil joueur
3. Clique sur "View All" dans la section Weapons
4. Extrait les 3 armes avec le plus de kills
5. Sauvegarde en NDJSON (1 ligne = 1 joueur)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import random
from datetime import datetime
from pathlib import Path
import re


def setup_browser():
    """Configure Chrome en mode headless avec anti-détection"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    
    return driver


def extract_leaderboard_players(driver, max_players=100):
    """
    Extrait les joueurs du leaderboard avec player_id, handle, url_profil
    
    Returns:
        list: [{"player_id": "3208849653", "handle": "Happy_3201", "url_profil": "..."}, ...]
    """
    url = "https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1"
    print(f"🌐 Chargement du leaderboard : {url}")
    
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # Attente chargement page
    
    players = []
    
    # Trouve toutes les lignes de joueurs
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"✅ {len(rows)} lignes trouvées dans le tableau")
    
    for i, row in enumerate(rows[:max_players], 1):
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) < 2:
                continue
            
            # Trouve le lien profil (contient /bf6/profile/{player_id})
            profile_link = cells[1].find_element(By.TAG_NAME, "a")
            url_profil = profile_link.get_attribute("href")
            handle = profile_link.text.strip()
            
            # Extrait player_id de l'URL (ex: /bf6/profile/3208849653 ou /bf6/profile/3208849653/overview)
            match = re.search(r'/bf6/profile/(\d+)', url_profil)
            if not match:
                print(f"⚠️  Ligne {i} : player_id non trouvé dans {url_profil}")
                continue
            
            player_id = match.group(1)
            
            players.append({
                "player_id": player_id,
                "handle": handle,
                "url_profil": url_profil
            })
            
            print(f"✅ Joueur {i:3d} : {handle:25s} (ID: {player_id})")
            
        except Exception as e:
            print(f"❌ Erreur ligne {i} : {e}")
            continue
    
    print(f"\n📊 Total extrait : {len(players)} joueurs")
    return players


def normalize_number(value_str):
    """
    Normalise un nombre (supprime virgules, convertit en float/int)
    
    Examples:
        "11,950" -> 11950
        "48.9%" -> 48.9
        "1,208.5%" -> 1208.5
    """
    if not value_str:
        return None
    
    # Supprime les séparateurs de milliers et le symbole %
    cleaned = value_str.replace(',', '').replace('%', '').strip()
    
    try:
        # Si contient un point décimal, retourne float
        if '.' in cleaned:
            return round(float(cleaned), 1)
        else:
            return int(cleaned)
    except ValueError:
        return None


def extract_top_weapons(driver, player_id, handle, url_profil, max_retries=3):
    """
    Extrait les 3 armes top d'un joueur avec kills et accuracy
    
    Args:
        driver: WebDriver Selenium
        player_id: ID numérique du joueur
        handle: Pseudo du joueur
        url_profil: URL du profil
        max_retries: Nombre de tentatives en cas d'échec
    
    Returns:
        dict: {"player_id": ..., "handle": ..., "top_weapons": [...], "status": "success/failed"}
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🔍 [{attempt}/{max_retries}] Visite du profil : {handle} ({player_id})")
            
            driver.get(url_profil)
            time.sleep(random.uniform(2, 4))
            
            # Cherche le bouton "View All" dans la section Weapons
            try:
                wait = WebDriverWait(driver, 10)
                view_all_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View All')]"))
                )
                print("   🖱️  Clic sur 'View All'")
                view_all_button.click()
                time.sleep(random.uniform(1, 2))
            except TimeoutException:
                print("   ℹ️  Pas de bouton 'View All' (toutes les armes déjà visibles)")
            
            # Trouve tous les blocs d'armes - stratégie simple : parse le texte HTML brut
            page_html = driver.page_source
            
            # Sauvegarde le HTML pour débogage
            debug_file = Path("data/exploration") / f"debug_{player_id}.html"
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"   💾 HTML sauvegardé : {debug_file}")
            
            # Parse le texte brut pour trouver les armes
            # Pattern typique : nom_arme ... Kills XXX ... Accuracy YY.Y%
            import re
            weapons = []
            
            # Regex pour capturer : Kills suivi d'un nombre avec virgules
            kills_pattern = r'Kills[:\s]+([0-9,]+)'
            accuracy_pattern = r'Accuracy[:\s]+([0-9,.]+%?)'
            
            # Split le HTML par lignes et cherche les patterns
            lines = page_html.split('\n')
            current_weapon = None
            current_kills = None
            current_accuracy = None
            
            for line in lines:
                # Cherche "Kills"
                kills_match = re.search(kills_pattern, line)
                if kills_match:
                    current_kills = normalize_number(kills_match.group(1))
                
                # Cherche "Accuracy"
                accuracy_match = re.search(accuracy_pattern, line)
                if accuracy_match:
                    current_accuracy = normalize_number(accuracy_match.group(1))
                
                # Si on a kills ET accuracy, on a probablement une arme complète
                if current_kills is not None and current_accuracy is not None:
                    # Le nom de l'arme est souvent dans les 5 lignes précédentes
                    # On prend la ligne actuelle comme nom temporaire
                    weapon_name = line.strip()[:50]  # Limite à 50 caractères
                    
                    weapons.append({
                        "name": weapon_name if weapon_name else "Unknown",
                        "kills": current_kills,
                        "accuracy_pct": current_accuracy
                    })
                    
                    # Reset pour la prochaine arme
                    current_kills = None
                    current_accuracy = None
            
            print(f"   📦 {len(weapons)} armes extraites du HTML brut")
            
            # Trie par kills décroissant et prend le top 3
            weapons_sorted = sorted(weapons, key=lambda x: x['kills'], reverse=True)
            top_3 = weapons_sorted[:3]
            
            if len(top_3) == 0:
                raise Exception("Aucune arme extraite")
            
            print(f"   ✅ {len(top_3)} armes extraites :")
            for i, w in enumerate(top_3, 1):
                print(f"      {i}. {w['name']:20s} | Kills: {w['kills']:>7} | Accuracy: {w['accuracy_pct']}%")
            
            # Délai aléatoire entre profils (rate limiting)
            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)
            
            return {
                "source": "tracker.gg",
                "board": "Kills",
                "snapshot_utc": datetime.utcnow().isoformat(),
                "player_id": player_id,
                "handle": handle,
                "top_weapons": top_3,
                "status": "success"
            }
        
        except Exception as e:
            print(f"   ❌ Tentative {attempt} échouée : {e}")
            
            if attempt < max_retries:
                # Backoff exponentiel : 2^attempt secondes
                backoff = 2 ** attempt
                print(f"   ⏳ Attente {backoff}s avant retry...")
                time.sleep(backoff)
            else:
                print(f"   💥 Échec définitif pour {handle}")
                return {
                    "source": "tracker.gg",
                    "board": "Kills",
                    "snapshot_utc": datetime.utcnow().isoformat(),
                    "player_id": player_id,
                    "handle": handle,
                    "top_weapons": [],
                    "status": "failed",
                    "error": str(e)
                }


def main():
    """Script principal"""
    print("=" * 80)
    print("🎮 EXTRACTION TOP 3 WEAPONS - BF6 TRACKER.GG")
    print("=" * 80)
    
    driver = setup_browser()
    
    try:
        # ÉTAPE 1 : Extraction du leaderboard
        print("\n📋 ÉTAPE 1 : Extraction du leaderboard (3 joueurs - TEST)")
        players = extract_leaderboard_players(driver, max_players=3)
        
        if not players:
            print("❌ Aucun joueur extrait du leaderboard. Abandon.")
            return
        
        # ÉTAPE 2 : Extraction des armes pour chaque joueur
        print(f"\n🔫 ÉTAPE 2 : Extraction des top 3 armes pour {len(players)} joueurs")
        print("-" * 80)
        
        results = []
        failed_players = []
        
        for i, player in enumerate(players, 1):
            print(f"\n[{i}/{len(players)}] Traitement : {player['handle']}")
            
            result = extract_top_weapons(
                driver,
                player['player_id'],
                player['handle'],
                player['url_profil']
            )
            
            results.append(result)
            
            if result['status'] == 'failed':
                failed_players.append({
                    "player_id": player['player_id'],
                    "handle": player['handle'],
                    "reason": result.get('error', 'unknown')
                })
        
        # ÉTAPE 3 : Sauvegarde NDJSON
        print("\n" + "=" * 80)
        print("💾 ÉTAPE 3 : Sauvegarde des résultats")
        print("=" * 80)
        
        output_dir = Path("data/bronze/tracker_gg/top_weapons")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_file = output_dir / f"bf6_top_weapons_{timestamp}.ndjson"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        
        print(f"✅ Fichier sauvegardé : {output_file}")
        print(f"📊 Statistiques :")
        print(f"   • Total joueurs : {len(results)}")
        print(f"   • Succès : {sum(1 for r in results if r['status'] == 'success')}")
        print(f"   • Échecs : {len(failed_players)}")
        
        if failed_players:
            print(f"\n⚠️  Joueurs échoués :")
            for fp in failed_players:
                print(f"   • {fp['handle']} (ID: {fp['player_id']}) - Raison : {fp['reason']}")
        
        # Calcul taux d'échec
        failure_rate = (len(failed_players) / len(results)) * 100
        print(f"\n📈 Taux d'échec : {failure_rate:.1f}%")
        
        if failure_rate < 5:
            print("✅ Critère d'acceptation OK (< 5% d'échecs)")
        else:
            print("⚠️  Taux d'échec élevé (> 5%)")
    
    finally:
        driver.quit()
        print("\n🏁 Extraction terminée.")


if __name__ == "__main__":
    main()
