#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction des armes depuis la page /weapons via parsing du tableau HTML
"""

import json
import time
import logging
import re
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
DATA_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "top_weapons"
LOGS_DIR = BASE_DIR / "data" / "logs" / "failed_extractions"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def extract_weapons_from_table(html_content):
    """
    Extrait les armes depuis le tableau de la page /weapons
    
    Args:
        html_content (str): HTML de la page
        
    Returns:
        list: Liste de dictionnaires {weapon_name, kills, rank}
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    weapons = []
    
    # Chercher toutes les lignes du tableau avec data-key="wp_*"
    weapon_rows = soup.find_all('tr', {'data-key': re.compile(r'^wp_')})
    
    logger.info(f"🔍 Trouvé {len(weapon_rows)} lignes d'armes dans le tableau")
    
    for idx, row in enumerate(weapon_rows, 1):
        try:
            # Récupérer toutes les cellules de la ligne
            cells = row.find_all('td')
            
            if len(cells) < 3:
                continue
            
            # Cellule 1 : nom de l'arme
            name_cell = cells[0]
            weapon_name = None
            
            # Chercher le nom dans les <span> de la cellule
            name_span = name_cell.find('span', {'class': 'truncate'})
            if name_span:
                weapon_name = name_span.get_text(strip=True)
            
            if not weapon_name:
                continue
            
            # Cellule 3 (index 2) : kills
            kills_cell = cells[2]
            kills_span = kills_cell.find('span', {'class': 'truncate'})
            
            if not kills_span:
                continue
            
            kills_text = kills_span.get_text(strip=True)
            # Enlever les virgules : "8,535" -> 8535
            kills = int(kills_text.replace(',', ''))
            
            weapons.append({
                'weapon_name': weapon_name,
                'kills': kills,
                'rank': idx  # Position dans le tableau (trié par kills)
            })
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur parsing ligne {idx}: {e}")
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
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🎮 Joueur: {handle} (ID: {player_id})")
    logger.info(f"🔗 URL: {url}")
    
    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            logger.info(f"🔄 Tentative {attempt}/{max_retries}")
            
            # Créer le driver Chrome (SANS HEADLESS pour éviter Cloudflare)
            driver = uc.Chrome()
            driver.get(url)
            
            # Attendre 20 secondes pour le chargement
            logger.info("⏳ Attente 20s pour le chargement de la page...")
            time.sleep(20)
            
            # Récupérer le HTML
            html = driver.page_source
            html_size = len(html)
            logger.info(f"📄 HTML récupéré: {html_size:,} caractères")
            
            # Vérifier si les images d'armes sont présentes
            if 'wp_' not in html:
                logger.warning("⚠️ Aucune image d'arme détectée (wp_)")
                if attempt < max_retries:
                    continue
                else:
                    # Sauvegarder le HTML pour analyse
                    html_path = LOGS_DIR / f"{handle}_{player_id}_no_weapons.html"
                    html_path.write_text(html, encoding='utf-8')
                    logger.warning(f"💾 HTML sauvegardé: {html_path}")
                    
                    return {
                        'player_id': player_id,
                        'handle': handle,
                        'url_profil': url,
                        'top_weapons': [],
                        'status': 'no_weapons_found',
                        'extraction_date': datetime.utcnow().isoformat()
                    }
            
            # Extraire les armes
            all_weapons = extract_weapons_from_table(html)
            logger.info(f"✅ {len(all_weapons)} armes extraites")
            
            # Prendre le top 3
            top_3 = all_weapons[:3]
            
            if top_3:
                logger.info("🏆 Top 3 armes:")
                for w in top_3:
                    logger.info(f"  {w['rank']}. {w['weapon_name']}: {w['kills']:,} kills")
            
            return {
                'player_id': player_id,
                'handle': handle,
                'url_profil': url,
                'top_weapons': top_3,
                'status': 'success',
                'extraction_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la tentative {attempt}: {e}")
            if attempt == max_retries:
                return {
                    'player_id': player_id,
                    'handle': handle,
                    'url_profil': url,
                    'top_weapons': [],
                    'status': f'error: {str(e)}',
                    'extraction_date': datetime.utcnow().isoformat()
                }
        
        finally:
            if driver:
                driver.quit()
    
    return None


def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage de l'extraction des armes (parsing HTML)")
    
    # Test sur 3 joueurs spécifiques
    test_players = [
        {'player_id': '1000380403530', 'handle': 'RoboCat'},  # Celui qu'on a testé
        {'player_id': '2480703860', 'handle': 'tails21c'},   # Celui du debug
        {'player_id': '3115975313', 'handle': 'BnanaMilk'}   # Premier du leaderboard
    ]
    
    logger.info(f"🎯 Test sur {len(test_players)} joueurs spécifiques")
    
    # Résultats
    results = []
    stats = {'success': 0, 'no_weapons': 0, 'error': 0}
    
    for idx, player in enumerate(test_players, 1):
        logger.info(f"\n{'#'*80}")
        logger.info(f"Joueur {idx}/{len(test_players)}")
        
        result = extract_player_weapons(
            player_id=player['player_id'],
            handle=player['handle']
        )
        
        if result:
            results.append(result)
            
            # Statistiques
            if result['status'] == 'success':
                stats['success'] += 1
            elif result['status'] == 'no_weapons_found':
                stats['no_weapons'] += 1
            else:
                stats['error'] += 1
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = DATA_DIR / f"bf6_top_weapons_table_parser_{timestamp}.ndjson"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    logger.info(f"\n{'='*80}")
    logger.info("📊 RÉSULTATS FINAUX")
    logger.info(f"✅ Succès: {stats['success']}/{len(test_players)} ({stats['success']/len(test_players)*100:.1f}%)")
    logger.info(f"⚠️ Pas d'armes: {stats['no_weapons']}")
    logger.info(f"❌ Erreurs: {stats['error']}")
    logger.info(f"💾 Fichier sauvegardé: {output_file}")


if __name__ == '__main__':
    main()
