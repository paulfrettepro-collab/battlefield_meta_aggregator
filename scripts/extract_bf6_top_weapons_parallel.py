#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction PARALLÈLE du top 3 armes pour chaque joueur du leaderboard
OPTIMISATIONS:
- ThreadPoolExecutor (5 workers parallèles)
- Wait dynamique (au lieu de time.sleep(20) fixe)
- Gain: 32 min → 4-6 min (85% plus rapide)

Source: leaderboard NDJSON → /weapons page pour chaque joueur
"""

import json
import time
import logging
import argparse
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)-10s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent
LEADERBOARD_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "leaderboard"
OUTPUT_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "top_weapons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = BASE_DIR / "data" / "logs" / "failed_extractions"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Thread-local storage pour les drivers Chrome
thread_local = threading.local()


def get_driver():
    """
    Retourne un driver Chrome unique par thread.
    Utilise thread-local storage pour éviter les conflits.
    
    Returns:
        webdriver.Chrome: Instance du driver
    """
    if not hasattr(thread_local, "driver"):
        logger.info("🌐 Création d'un nouveau driver Chrome pour ce thread")
        thread_local.driver = uc.Chrome()
    return thread_local.driver


def cleanup_driver():
    """Ferme le driver du thread actuel"""
    if hasattr(thread_local, "driver"):
        try:
            thread_local.driver.quit()
            del thread_local.driver
        except Exception as e:
            logger.warning(f"⚠️ Erreur fermeture driver: {e}")


def wait_for_weapons_table(driver, timeout=30):
    """
    Attend dynamiquement que le tableau d'armes soit chargé.
    OPTIMISATION: Au lieu de time.sleep(20) fixe, attend seulement le temps nécessaire.
    
    Args:
        driver: WebDriver instance
        timeout (int): Temps max d'attente en secondes
        
    Returns:
        bool: True si tableau chargé, False si timeout
    """
    try:
        # Attendre qu'au moins une ligne d'arme soit visible
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr[data-key^='wp_']"))
        )
        
        # Buffer de sécurité pour le rendu complet
        time.sleep(2)
        
        logger.debug("✅ Tableau d'armes détecté")
        return True
        
    except Exception as e:
        logger.warning(f"⏱️ Timeout ({timeout}s) en attendant le tableau: {e}")
        return False


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


def extract_player_weapons_threadsafe(player_data, max_retries=2):
    """
    VERSION THREAD-SAFE: Extrait les 3 meilleures armes d'un joueur.
    Chaque thread utilise son propre driver Chrome via thread-local storage.
    
    Args:
        player_data (dict): Données du joueur (handle, player_id)
        max_retries (int): Nombre de tentatives
        
    Returns:
        dict: Résultat de l'extraction
    """
    handle = player_data['handle']
    player_id = player_data['player_id']
    url = f"https://tracker.gg/bf6/profile/{player_id}/weapons"
    
    logger.info(f"🎮 {handle} (ID: {player_id})")
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                logger.info(f"🔄 {handle} - Tentative {attempt}/{max_retries}")
            
            # Récupérer le driver du thread actuel
            driver = get_driver()
            driver.get(url)
            
            # OPTIMISATION: Wait dynamique au lieu de time.sleep(20)
            if not wait_for_weapons_table(driver, timeout=30):
                logger.warning(f"⚠️ {handle} - Timeout waiting for weapons table")
                if attempt < max_retries:
                    continue
                else:
                    return {
                        'handle': handle,
                        'player_id': player_id,
                        'top_weapons': [],
                        'status': 'timeout',
                        'extraction_date': datetime.now().isoformat()
                    }
            
            # Récupérer le HTML
            html = driver.page_source
            html_size = len(html)
            
            # Vérifier si les armes sont présentes
            if 'wp_' not in html or html_size < 100000:
                logger.warning(f"⚠️ {handle} - HTML trop petit ({html_size:,} chars)")
                if attempt < max_retries:
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
                logger.info(f"✅ {handle} - {len(all_weapons)} armes, top 3:")
                for w in top_3:
                    logger.info(f"  {w['rank']}. {w['weapon_name']}: {w['kills']:,} kills")
            else:
                logger.warning(f"⚠️ {handle} - Aucune arme extraite")
            
            return {
                'handle': handle,
                'player_id': player_id,
                'top_weapons': top_3,
                'total_weapons_found': len(all_weapons),
                'status': 'success',
                'extraction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ {handle} - Erreur tentative {attempt}: {e}")
            if attempt == max_retries:
                return {
                    'handle': handle,
                    'player_id': player_id,
                    'top_weapons': [],
                    'status': f'error: {str(e)}',
                    'extraction_date': datetime.now().isoformat()
                }
    
    return None


def extract_all_parallel(players, max_workers=5):
    """
    OPTIMISATION PRINCIPALE: Extrait les armes de tous les joueurs en parallèle.
    
    Args:
        players (list): Liste des joueurs
        max_workers (int): Nombre de threads parallèles (5 recommandé)
        
    Returns:
        list: Résultats d'extraction
    """
    results = []
    stats = {'success': 0, 'no_weapons': 0, 'timeout': 0, 'error': 0}
    
    logger.info(f"🚀 Lancement de l'extraction parallèle ({max_workers} workers)")
    start_time = time.time()
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Soumettre toutes les tâches
            future_to_player = {
                executor.submit(extract_player_weapons_threadsafe, player): player
                for player in players
            }
            
            # Traiter les résultats au fur et à mesure
            for idx, future in enumerate(as_completed(future_to_player), 1):
                player = future_to_player[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Stats
                    if result['status'] == 'success':
                        stats['success'] += 1
                    elif result['status'] == 'no_weapons_found':
                        stats['no_weapons'] += 1
                    elif result['status'] == 'timeout':
                        stats['timeout'] += 1
                    else:
                        stats['error'] += 1
                    
                    # Progress
                    elapsed = time.time() - start_time
                    rate = idx / elapsed if elapsed > 0 else 0
                    eta = (len(players) - idx) / rate if rate > 0 else 0
                    
                    logger.info(f"📊 Progression: {idx}/{len(players)} ({idx/len(players)*100:.1f}%) | "
                               f"✅ {stats['success']} | "
                               f"Vitesse: {rate:.2f} joueurs/s | "
                               f"ETA: {eta/60:.1f} min")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur traitement {player['handle']}: {e}")
                    results.append({
                        'handle': player['handle'],
                        'player_id': player['player_id'],
                        'top_weapons': [],
                        'status': f'executor_error: {str(e)}',
                        'extraction_date': datetime.now().isoformat()
                    })
                    stats['error'] += 1
    
    finally:
        # Fermer tous les drivers
        logger.info("🧹 Nettoyage des drivers Chrome...")
        cleanup_driver()
    
    duration = time.time() - start_time
    
    logger.info(f"\n{'='*80}")
    logger.info("📊 RÉSULTATS FINAUX")
    logger.info(f"⏱️ Durée totale: {duration/60:.1f} minutes ({duration:.1f}s)")
    logger.info(f"⚡ Vitesse moyenne: {len(players)/duration:.2f} joueurs/s")
    logger.info(f"✅ Succès: {stats['success']}/{len(players)} ({stats['success']/len(players)*100:.1f}%)")
    logger.info(f"⚠️ Pas d'armes: {stats['no_weapons']}")
    logger.info(f"⏱️ Timeout: {stats['timeout']}")
    logger.info(f"❌ Erreurs: {stats['error']}")
    
    return results


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Extraction parallèle des top 3 armes')
    parser.add_argument('--workers', type=int, default=5, 
                       help='Nombre de workers parallèles (default: 5)')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Limiter à N joueurs pour tests (default: tous)')
    args = parser.parse_args()
    
    logger.info("🚀 Démarrage de l'extraction PARALLÈLE des armes")
    logger.info(f"⚙️ Configuration: {args.workers} workers")
    
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
    
    # Limiter si demandé
    if args.limit:
        players = players[:args.limit]
        logger.info(f"🎯 Limite: {args.limit} joueurs (test)")
    
    logger.info(f"🎯 {len(players)} joueurs à traiter")
    
    # Estimation du temps
    estimated_time_sequential = len(players) * 20 / 60  # 20s par joueur
    estimated_time_parallel = len(players) / args.workers * 4 / 60  # ~4s par joueur avec parallélisation
    
    print(f"\n{'='*80}")
    print(f"⏱️  Temps estimé (séquentiel): ~{estimated_time_sequential:.0f} minutes")
    print(f"⚡ Temps estimé (parallèle {args.workers} workers): ~{estimated_time_parallel:.0f} minutes")
    print(f"🚀 Gain: {(1 - estimated_time_parallel/estimated_time_sequential)*100:.0f}%")
    print(f"{'='*80}\n")
    
    # Demander confirmation
    if not args.limit or args.limit > 10:
        print(f"⚠️  Cela va ouvrir {args.workers} Chrome simultanément")
        print(f"💾 RAM requise: ~{args.workers * 500} MB")
        response = input("\n▶️  Continuer ? (o/n): ")
        
        if response.lower() != 'o':
            logger.info("❌ Extraction annulée par l'utilisateur")
            return
    
    # Extraire en parallèle
    results = extract_all_parallel(players, max_workers=args.workers)
    
    # Sauvegarder les résultats
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = OUTPUT_DIR / f"bf6_top_weapons_{timestamp}_parallel.ndjson"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    logger.info(f"💾 Fichier sauvegardé: {output_file}")
    logger.info(f"📊 {len(results)} résultats enregistrés")


if __name__ == '__main__':
    main()
