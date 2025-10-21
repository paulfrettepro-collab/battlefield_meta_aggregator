"""
EXTRACTION ULTRA-SIMPLE - 100 JOUEURS
Version minimaliste sans CDP commands
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import json
import time
import re
from datetime import datetime, timezone
from pathlib import Path

print("=" * 80)
print("🎮 EXTRACTION TOP 3 WEAPONS")
print("=" * 80)

# Lancement simple sans options complexes
print("\n🚀 Lancement navigateur...")
driver = uc.Chrome()
print("✅ OK\n")

try:
    # ÉTAPE 1: Leaderboard
    print("📋 ÉTAPE 1: Leaderboard")
    driver.get("https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1")
    print("⏳ Attente 15s...")
    time.sleep(15)
    
    # Fermer pop-up cookies
    try:
        btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        btn.click()
        print("✅ Cookies OK")
        time.sleep(2)
    except:
        pass
    
    # Extraire joueurs
    players = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"✅ {len(rows)} lignes\n")
    
    for i, row in enumerate(rows[:100], 1):
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                continue
            
            # Extraire le rank (position dans le classement)
            rank = i  # Le rang correspond à la position dans la boucle
            
            link = cells[1].find_element(By.TAG_NAME, "a")
            url = link.get_attribute("href")
            handle = link.text.strip()
            
            pid_match = re.search(r'/profile/(\d+)', url)
            pid = pid_match.group(1) if pid_match else "unknown"
            
            players.append({
                "rank": rank,  # ✅ Ajout du rank
                "player_id": pid, 
                "handle": handle, 
                "url_profil": url
            })
            print(f"✅ {rank:3d}. {handle} (ID: {pid})")
        except Exception as e:
            print(f"❌ Erreur ligne {i}: {e}")
    
    print(f"\n📊 Total: {len(players)} joueurs\n")
    
    # ÉTAPE 2: Armes
    print("=" * 80)
    print("🔫 ÉTAPE 2: Top 3 armes")
    print("=" * 80)
    
    results = []
    
    for idx, player in enumerate(players, 1):
        print(f"\n[{idx}/{len(players)}] {player['handle']}")
        
        try:
            driver.get(player['url_profil'])
            print("   ⏳ 15s...")
            time.sleep(15)
            
            # Cookies
            try:
                btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                btn.click()
                time.sleep(1)
            except:
                pass
            
            html = driver.page_source
            
            # Extraire armes
            pattern = r'wp_[^.]+\.png/image\.png" alt="([^"]+)"[^>]*>.*?Kills.*?<span[^>]*>([0-9,]+).*?</span>'
            matches = re.findall(pattern, html, re.DOTALL)
            
            weapons = []
            seen = set()
            for name, kills_str in matches:
                if name not in seen and len(weapons) < 3:
                    seen.add(name)
                    kills = int(kills_str.replace(',', ''))
                    weapons.append({"name": name, "kills": kills, "accuracy_pct": None})
                    print(f"   ✅ {name}: {kills:,}")
            
            results.append({
                "source": "tracker.gg",
                "board": "Kills",
                "snapshot_utc": datetime.now(timezone.utc).isoformat(),
                "rank": player['rank'],  # ✅ Ajout du rank dans le résultat
                "player_id": player['player_id'],
                "handle": player['handle'],
                "top_weapons": weapons,
                "status": "success"
            })
            
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ {str(e)[:80]}")
            results.append({
                "source": "tracker.gg",
                "board": "Kills",
                "snapshot_utc": datetime.now(timezone.utc).isoformat(),
                "rank": player['rank'],  # ✅ Ajout du rank même en cas d'échec
                "player_id": player['player_id'],
                "handle": player['handle'],
                "top_weapons": [],
                "status": "failed",
                "error": str(e)[:150]
            })
    
    # ÉTAPE 3: Sauvegarde
    print("\n" + "=" * 80)
    print("💾 SAUVEGARDE")
    print("=" * 80)
    
    out_dir = Path("data/bronze/tracker_gg/top_weapons")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_file = out_dir / f"bf6_top_weapons_{ts}.ndjson"
    
    with open(out_file, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    
    size = out_file.stat().st_size
    success = sum(1 for r in results if r['status'] == 'success')
    
    print(f"✅ Fichier: {out_file}")
    print(f"📦 Taille: {size:,} octets ({size/1024:.2f} KB)")
    print(f"✅ Succès: {success}/{len(results)}")
    print(f"❌ Échecs: {len(results)-success}/{len(results)}")
    
    print("\n✅ EXTRACTION TERMINÉE!")
    
finally:
    print("\n🔄 Fermeture navigateur...")
    time.sleep(1)
    driver.quit()
    print("🏁 FIN")
