#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXTRACTION COMPLÈTE BF6 META - 2 ÉTAPES
Extraction du leaderboard actuel PUIS extraction des top 3 armes par joueur

OBJECTIF: Capturer la meta actuelle des armes jouées par le top 50 du leaderboard
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent
LEADERBOARD_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "leaderboard"
WEAPONS_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "weapons"
LEADERBOARD_DIR.mkdir(parents=True, exist_ok=True)
WEAPONS_DIR.mkdir(parents=True, exist_ok=True)

# URLs
LEADERBOARD_URL = "https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1"
# Format correct : /bf6/profile/{ID} sans le handle (comme les liens du leaderboard)
PLAYER_WEAPONS_URL = "https://tracker.gg/bf6/profile/{player_id}/weapons"


class ExtractionCheckpoint:
    """Gestion des points de sauvegarde pour reprendre l'extraction"""
    
    def __init__(self, checkpoint_file):
        self.checkpoint_file = checkpoint_file
        self.extracted = set()
        self.load()
    
    def load(self):
        """Charger les joueurs déjà extraits"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                self.extracted = set(json.load(f))
            logger.info(f"📋 {len(self.extracted)} joueurs déjà extraits (checkpoint)")
    
    def save(self, handle):
        """Sauvegarder un joueur extrait"""
        self.extracted.add(handle)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(list(self.extracted), f)
    
    def is_extracted(self, handle):
        """Vérifier si un joueur a déjà été extrait"""
        return handle in self.extracted


def get_driver():
    """Créer un driver Chrome non détecté"""
    options = uc.ChromeOptions()
    # Mode headless désactivé pour éviter détection
    # options.add_argument('--headless=new')
    
    driver = uc.Chrome(
        options=options,
        version_main=141,  # Forcer version Chrome 141
        driver_executable_path=None
    )
    return driver


def extract_current_leaderboard(driver, max_players=50):
    """
    ÉTAPE 1: Extraire le leaderboard ACTUEL (live)
    
    Args:
        driver: Selenium WebDriver
        max_players: Nombre max de joueurs (défaut 50 pour MVP)
    
    Returns:
        list: Joueurs avec {handle, player_id, rank, kills, location, matches_played}
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 ÉTAPE 1: EXTRACTION LEADERBOARD ACTUEL (TOP {max_players})")
    logger.info(f"{'='*70}")
    logger.info(f"🔗 URL: {LEADERBOARD_URL}")
    
    try:
        driver.get(LEADERBOARD_URL)
        
        # Attendre le chargement
        logger.info("⏳ Attente chargement page (20s)...")
        time.sleep(20)
        
        # Parser HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # DEBUG: Sauvegarder HTML pour inspection
        debug_file = LEADERBOARD_DIR / "leaderboard_debug_latest.html"
        debug_file.write_text(html, encoding='utf-8')
        logger.info(f"💾 HTML debug sauvegardé: {debug_file}")
        
        # Chercher les lignes du leaderboard
        player_rows = soup.find_all('tr', {'data-key': lambda x: x and x.isdigit()})
        logger.info(f"🔍 {len(player_rows)} joueurs trouvés dans le tableau")
        
        players = []
        for row in player_rows:
            if len(players) >= max_players:
                logger.info(f"🎯 Limite de {max_players} joueurs atteinte")
                break
            
            try:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                
                # Rank
                rank_span = cells[0].find('span', class_=lambda x: x and 'min-w-9' in x if x else False)
                if not rank_span:
                    continue
                rank = int(rank_span.get_text(strip=True))
                
                # Player link (handle + player_id)
                player_link = cells[1].find('a', href=lambda x: x and '/bf6/profile/' in x if x else False)
                if not player_link:
                    continue
                
                # Extraire player_id depuis href: "/bf6/profile/1006806438138"
                # Format: ['', 'bf6', 'profile', '{player_id}']
                href_parts = player_link['href'].split('/')
                if len(href_parts) < 4:
                    continue
                player_id = href_parts[-1]  # Dernier segment = player_id
                
                handle_span = player_link.find('span', class_='truncate')
                if not handle_span:
                    continue
                handle = handle_span.get_text(strip=True)
                
                # Location (flag)
                location = None
                flag_img = cells[1].find('img', alt=True)
                if flag_img:
                    location = flag_img['alt']
                
                # Kills
                kills = 0
                for cell_idx in [3, 4]:
                    if cell_idx < len(cells):
                        kills_span = cells[cell_idx].find('span', class_='truncate')
                        if kills_span:
                            kills_text = kills_span.get_text(strip=True).replace(',', '').replace(' ', '')
                            if kills_text.replace('.', '').isdigit():
                                test_kills = int(kills_text.split('.')[0])
                                if test_kills > 1000:
                                    kills = test_kills
                                    break
                
                # Matches played
                matches_played = None
                for cell_idx in [4, 5]:
                    if cell_idx < len(cells):
                        matches_span = cells[cell_idx].find('span', class_='truncate')
                        if matches_span:
                            matches_text = matches_span.get_text(strip=True).replace(',', '').replace(' ', '')
                            if matches_text.isdigit():
                                test_matches = int(matches_text)
                                if 10 < test_matches < 10000:
                                    matches_played = test_matches
                                    break
                
                if handle and player_id and kills > 0:
                    players.append({
                        'handle': handle,
                        'player_id': player_id,
                        'rank': rank,
                        'kills': kills,
                        'location': location,
                        'matches_played': matches_played,
                        'extraction_date': datetime.now().isoformat()
                    })
                    
                    if len(players) % 10 == 0:
                        logger.info(f"  ✅ {len(players)} joueurs extraits...")
            
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing joueur: {e}")
                continue
        
        logger.info(f"\n✅ {len(players)} joueurs extraits du leaderboard")
        
        # Afficher top 5
        if players:
            logger.info("\n🏆 Top 5:")
            for p in players[:5]:
                loc = p.get('location', 'N/A')
                matches = p.get('matches_played', 'N/A')
                logger.info(f"  {p['rank']}. {p['handle']} - {p['kills']:,} kills - {loc} - {matches} matches")
        
        return players
    
    except Exception as e:
        logger.error(f"❌ Erreur extraction leaderboard: {e}")
        raise


def extract_player_weapons(driver, player_handle, player_id, max_retries=3):
    """
    Extraire les top 3 armes d'un joueur
    
    Args:
        driver: Selenium WebDriver
        player_handle: Pseudo du joueur
        player_id: ID tracker.gg du joueur
        max_retries: Nombre max de tentatives
    
    Returns:
        dict: Résultat avec {success: bool, weapons: list, error: str}
    """
    url = PLAYER_WEAPONS_URL.format(player_id=player_id)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🎮 {player_handle} (ID: {player_id}) - {url} (tentative {attempt}/{max_retries})")
            
            driver.get(url)
            
            # Attente dynamique du tableau d'armes
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
                )
                # Attente supplémentaire pour stabilité
                time.sleep(3)
            except TimeoutException:
                logger.warning(f"⚠️ Timeout attente tableau armes")
                if attempt < max_retries:
                    backoff = attempt * 2
                    logger.info(f"⏳ Retry dans {backoff}s...")
                    time.sleep(backoff)
                    continue
                else:
                    return {
                        'success': False,
                        'weapons': [],
                        'error': 'Timeout chargement tableau armes'
                    }
            
            # Parser HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # DEBUG: Sauvegarder le HTML pour inspection
            if attempt == 1:  # Seulement la première tentative
                debug_file = LEADERBOARD_DIR / f"weapons_debug_{player_id}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"💾 HTML armes sauvegardé: {debug_file}")
            
            # Chercher les lignes du tableau d'armes
            # Les data-key commencent par 'wp_' pour weapons (ex: wp_crb_m417a2)
            weapon_rows = soup.find_all('tr', {'data-key': lambda x: x and x.startswith('wp_')})
            
            if not weapon_rows:
                logger.warning(f"⚠️ Aucune arme trouvée pour {player_handle}")
                if attempt < max_retries:
                    backoff = attempt * 2
                    logger.info(f"⏳ Retry dans {backoff}s...")
                    time.sleep(backoff)
                    continue
                else:
                    return {
                        'success': False,
                        'weapons': [],
                        'error': 'Aucune arme trouvée'
                    }
            
            weapons = []
            for row in weapon_rows[:3]:  # Top 3 seulement
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue
                    
                    # Nom de l'arme (dans la première cellule sticky - cells[0])
                    # Structure: <td> -> <div class="stat-ver"> -> <div class="name-value"> -> <span class="stat-value"> -> <span class="truncate">NOM</span>
                    weapon_name = None
                    if len(cells) > 0:
                        name_div = cells[0].find('div', class_='name-value')
                        if name_div:
                            stat_value = name_div.find('span', class_='stat-value')
                            if stat_value:
                                name_span = stat_value.find('span', class_='truncate')
                                if name_span:
                                    weapon_name = name_span.get_text(strip=True)
                    
                    if not weapon_name:
                        continue
                    
                    # Kills avec arme (chercher dans plusieurs cellules)
                    weapon_kills = None
                    for cell_idx in range(2, min(len(cells), 6)):
                        span = cells[cell_idx].find('span', class_='truncate')
                        if span:
                            text = span.get_text(strip=True).replace(',', '')
                            if text.isdigit():
                                test_kills = int(text)
                                if test_kills > 10:  # Minimum raisonnable
                                    weapon_kills = test_kills
                                    break
                    
                    # Accuracy (chercher "%" dans les cellules)
                    accuracy = None
                    for cell_idx in range(2, len(cells)):
                        span = cells[cell_idx].find('span', class_='truncate')
                        if span:
                            text = span.get_text(strip=True)
                            if '%' in text:
                                try:
                                    accuracy = float(text.replace('%', '').strip())
                                    break
                                except ValueError:
                                    continue
                    
                    weapons.append({
                        'weapon_name': weapon_name,
                        'kills': weapon_kills,
                        'accuracy': accuracy
                    })
                
                except Exception as e:
                    logger.warning(f"⚠️ Erreur parsing arme: {e}")
                    continue
            
            # Validation
            if len(weapons) < 3:
                logger.warning(f"⚠️ Seulement {len(weapons)} armes extraites pour {player_handle}")
                if attempt < max_retries:
                    backoff = attempt * 2
                    logger.info(f"⏳ Retry dans {backoff}s...")
                    time.sleep(backoff)
                    continue
            
            logger.info(f"  ✅ {len(weapons)} armes extraites")
            return {
                'success': True,
                'weapons': weapons,
                'error': None
            }
        
        except Exception as e:
            logger.warning(f"❌ {player_handle} - Tentative {attempt}/{max_retries} échouée : {e}")
            if attempt < max_retries:
                backoff = attempt * 2
                logger.info(f"⏳ Retry dans {backoff}s...")
                time.sleep(backoff)
            else:
                return {
                    'success': False,
                    'weapons': [],
                    'error': str(e)
                }
    
    return {
        'success': False,
        'weapons': [],
        'error': 'Max retries atteint'
    }


def main():
    """Fonction principale - Extraction complète en 2 étapes"""
    
    print(f"""
{'='*70}
🎮 EXTRACTION COMPLÈTE BF6 META
{'='*70}
Étape 1: Extraction leaderboard actuel (top 50)
Étape 2: Extraction top 3 armes par joueur
{'='*70}
""")
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    
    # Fichiers de sortie
    leaderboard_file = LEADERBOARD_DIR / f"bf6_leaderboard_{timestamp}.ndjson"
    weapons_file = WEAPONS_DIR / f"bf6_weapons_{timestamp}.ndjson"
    checkpoint_file = WEAPONS_DIR / f".checkpoint_{timestamp}.json"
    
    # Checkpoint
    checkpoint = ExtractionCheckpoint(checkpoint_file)
    
    driver = None
    try:
        # Initialiser Chrome
        logger.info("🌐 Initialisation Chrome...")
        driver = get_driver()
        
        # ========================================
        # ÉTAPE 1: LEADERBOARD ACTUEL
        # ========================================
        players = extract_current_leaderboard(driver, max_players=50)
        
        if not players:
            logger.error("❌ Aucun joueur extrait du leaderboard")
            return
        
        # Sauvegarder leaderboard
        with open(leaderboard_file, 'w', encoding='utf-8') as f:
            for player in players:
                f.write(json.dumps(player, ensure_ascii=False) + '\n')
        
        logger.info(f"\n💾 Leaderboard sauvegardé: {leaderboard_file}")
        logger.info(f"📊 {len(players)} joueurs")
        
        # ========================================
        # ÉTAPE 2: ARMES PAR JOUEUR
        # ========================================
        logger.info(f"\n{'='*70}")
        logger.info(f"🔫 ÉTAPE 2: EXTRACTION ARMES (TOP 3 PAR JOUEUR)")
        logger.info(f"{'='*70}")
        
        # Filtrer joueurs déjà extraits
        players_to_extract = [p for p in players if not checkpoint.is_extracted(p['handle'])]
        logger.info(f"👥 {len(players_to_extract)} joueurs à extraire")
        
        if not players_to_extract:
            logger.info("✅ Tous les joueurs ont déjà été extraits")
            return
        
        # Extraction avec barre de progression
        success_count = 0
        error_count = 0
        
        with tqdm(total=len(players_to_extract), desc="Extraction armes") as pbar:
            for player in players_to_extract:
                result = extract_player_weapons(
                    driver,
                    player['handle'],
                    player['player_id']
                )
                
                # Créer l'entrée complète
                entry = {
                    'player_handle': player['handle'],
                    'player_id': player['player_id'],
                    'rank': player['rank'],
                    'kills': player['kills'],
                    'location': player.get('location'),
                    'matches_played': player.get('matches_played'),
                    'weapons': result['weapons'],
                    'extraction_success': result['success'],
                    'extraction_error': result['error'],
                    'snapshot_utc': datetime.utcnow().isoformat()
                }
                
                # Sauvegarder immédiatement
                with open(weapons_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                
                # Marquer comme extrait
                checkpoint.save(player['handle'])
                
                # Stats
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                
                pbar.update(1)
                pbar.set_postfix({
                    '✅': success_count,
                    '❌': error_count,
                    'joueur': player['handle'][:15]
                })
        
        # ========================================
        # RÉSUMÉ FINAL
        # ========================================
        print(f"""
{'='*70}
✅ EXTRACTION TERMINÉE
{'='*70}
📊 Leaderboard: {leaderboard_file.name}
   - {len(players)} joueurs

🔫 Armes: {weapons_file.name}
   - ✅ Succès: {success_count}
   - ❌ Erreurs: {error_count}
   - 📈 Taux succès: {success_count/len(players_to_extract)*100:.1f}%

{'='*70}
""")
        
        # Nettoyer checkpoint si 100% succès
        if error_count == 0 and checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info("🧹 Checkpoint supprimé (extraction complète)")
    
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        raise
    
    finally:
        if driver:
            logger.info("🔚 Fermeture Chrome...")
            driver.quit()


if __name__ == '__main__':
    main()
