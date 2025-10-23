#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction du top 3 armes pour chaque joueur du leaderboard
Source: leaderboard NDJSON → /weapons page pour chaque joueur
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent
LEADERBOARD_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "leaderboard"
OUTPUT_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "top_weapons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = BASE_DIR / "data" / "logs" / "failed_extractions"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def extract_weapons_from_table(html_content):
    """
    Extrait les armes depuis le tableau de la page /weapons
    
    Args:
        html_content (str): HTML de la page
        
    Returns:
        list: Liste de dictionnaires avec stats des armes
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    weapons = []
    
    # Chercher toutes les lignes du tableau avec data-key="wp_*"
    weapon_rows = soup.find_all('tr', {'data-key': lambda x: x and x.startswith('wp_')})
    
    for idx, row in enumerate(weapon_rows, 1):
        try:
            cells = row.find_all('td')
            
            if len(cells) < 8:  # On veut au moins 8 colonnes
                continue
            
            # Extraire les données de chaque cellule
            weapon_data = {}
            
            # Cellule 0: Nom de l'arme + type
            name_cell = cells[0]
            name_span = name_cell.find('span', {'class': 'truncate'})
            if name_span:
                weapon_data['weapon_name'] = name_span.get_text(strip=True)
            
            # Type d'arme (SMG, AR, etc.)
            type_span = name_cell.find('span', {'class': 'text-10'})
            if type_span:
                weapon_data['weapon_type'] = type_span.get_text(strip=True)
            
            # Cellule 1: Time Played
            time_cell = cells[1]
            time_span = time_cell.find('span', {'class': 'truncate'})
            if time_span:
                weapon_data['time_played'] = time_span.get_text(strip=True)
            
            # Cellule 2: Kills (IMPORTANT - c'est notre métrique de tri)
            kills_cell = cells[2]
            kills_span = kills_cell.find('span', {'class': 'truncate'})
            if kills_span:
                kills_text = kills_span.get_text(strip=True)
                weapon_data['kills'] = int(kills_text.replace(',', ''))
            
            # Cellule 5: Damage
            if len(cells) > 5:
                damage_cell = cells[5]
                damage_span = damage_cell.find('span', {'class': 'truncate'})
                if damage_span:
                    damage_text = damage_span.get_text(strip=True)
                    weapon_data['damage'] = int(damage_text.replace(',', ''))
            
            # Cellule 6: Accuracy
            if len(cells) > 6:
                acc_cell = cells[6]
                acc_span = acc_cell.find('span', {'class': 'truncate'})
                if acc_span:
                    acc_text = acc_span.get_text(strip=True)
                    weapon_data['accuracy'] = acc_text
            
            # Cellule 7: Headshot %
            if len(cells) > 7:
                hs_cell = cells[7]
                hs_span = hs_cell.find('span', {'class': 'truncate'})
                if hs_span:
                    hs_text = hs_span.get_text(strip=True)
                    weapon_data['headshot_pct'] = hs_text
            
            # Ajouter le rang
            weapon_data['rank'] = idx
            
            # Seulement si on a le nom et les kills
            if 'weapon_name' in weapon_data and 'kills' in weapon_data:
                weapons.append(weapon_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur parsing arme ligne {idx}: {e}")
            continue
    
    return weapons


def extract_player_weapons(player_id, handle, max_retries=2):
    """
    Extrait les 3 meilleures armes d'un joueur
    
    Args:
        player_id (str): ID du joueur
        handle (str): Pseudo du joueur
        max_retries (int): Nombre de tentatives
        
    Returns:
        dict: Résultat de l'extraction
    """
    url = f"https://tracker.gg/bf6/profile/{player_id}/weapons"
    
    logger.info(f"\n🎮 {handle} (ID: {player_id})")
    
    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            if attempt > 1:
                logger.info(f"🔄 Tentative {attempt}/{max_retries}")
            
            # Créer le driver Chrome (sans headless)
            driver = uc.Chrome()
            driver.get(url)
            
            # Attendre le chargement
            time.sleep(20)
            
            # Récupérer le HTML
            html = driver.page_source
            html_size = len(html)
            
            # Vérifier si les armes sont présentes
            if 'wp_' not in html or html_size < 100000:
                logger.warning(f"⚠️ HTML trop petit ({html_size:,} chars) ou pas d'armes")
                if attempt < max_retries:
                    driver.quit()
                    continue
                else:
                    # Sauvegarder pour debug
                    html_path = LOGS_DIR / f"{handle}_{player_id}_no_weapons.html"
                    html_path.write_text(html, encoding='utf-8')
                    logger.warning(f"💾 HTML sauvegardé: {html_path}")
                    
                    return {
                        'handle': handle,
                        'player_id': player_id,
                        'top_weapons': [],
                        'status': 'no_weapons_found',
                        'extraction_date': datetime.now().isoformat()
                    }
            
            # Extraire les armes
            all_weapons = extract_weapons_from_table(html)
            
            # Prendre le top 3
            top_3 = all_weapons[:3]
            
            if top_3:
                logger.info(f"✅ {len(all_weapons)} armes extraites, top 3:")
                for w in top_3:
                    logger.info(f"  {w['rank']}. {w['weapon_name']} ({w.get('weapon_type', 'N/A')}): {w['kills']:,} kills")
            else:
                logger.warning(f"⚠️ Aucune arme extraite malgré {html_size:,} chars")
            
            return {
                'handle': handle,
                'player_id': player_id,
                'top_weapons': top_3,
                'total_weapons_found': len(all_weapons),
                'status': 'success',
                'extraction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur tentative {attempt}: {e}")
            if attempt == max_retries:
                return {
                    'handle': handle,
                    'player_id': player_id,
                    'top_weapons': [],
                    'status': f'error: {str(e)}',
                    'extraction_date': datetime.now().isoformat()
                }
        
        finally:
            if driver:
                driver.quit()
    
    return None


def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage de l'extraction des armes")
    
    # Chercher le dernier fichier leaderboard
    leaderboard_files = sorted(LEADERBOARD_DIR.glob("bf6_leaderboard_*.ndjson"))
    
    if not leaderboard_files:
        logger.error(f"❌ Aucun fichier leaderboard trouvé dans {LEADERBOARD_DIR}")
        logger.error("➡️  Exécutez d'abord: extract_bf6_leaderboard.py")
        return
    
    leaderboard_file = leaderboard_files[-1]
    logger.info(f"📂 Fichier leaderboard: {leaderboard_file.name}")
    
    # Charger les joueurs
    with open(leaderboard_file, 'r', encoding='utf-8') as f:
        players = [json.loads(line) for line in f]
    
    logger.info(f"🎯 {len(players)} joueurs à traiter")
    
    # Demander confirmation
    print(f"\n⚠️  Cela va ouvrir {len(players)} pages Chrome (sans headless)")
    print(f"⏱️  Temps estimé: ~{len(players) * 25 / 60:.0f} minutes")
    response = input("\n▶️  Continuer ? (o/n): ")
    
    if response.lower() != 'o':
        logger.info("❌ Extraction annulée par l'utilisateur")
        return
    
    # Extraire les armes
    results = []
    stats = {'success': 0, 'no_weapons': 0, 'error': 0}
    
    for idx, player in enumerate(players, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Joueur {idx}/{len(players)}")
        
        result = extract_player_weapons(
            player_id=player['player_id'],
            handle=player['handle']
        )
        
        if result:
            results.append(result)
            
            # Stats
            if result['status'] == 'success':
                stats['success'] += 1
            elif result['status'] == 'no_weapons_found':
                stats['no_weapons'] += 1
            else:
                stats['error'] += 1
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = OUTPUT_DIR / f"bf6_top_weapons_{timestamp}.ndjson"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    logger.info(f"\n{'='*80}")
    logger.info("📊 RÉSULTATS FINAUX")
    logger.info(f"✅ Succès: {stats['success']}/{len(players)} ({stats['success']/len(players)*100:.1f}%)")
    logger.info(f"⚠️ Pas d'armes: {stats['no_weapons']}")
    logger.info(f"❌ Erreurs: {stats['error']}")
    logger.info(f"💾 Fichier sauvegardé: {output_file}")


if __name__ == '__main__':
    main()
