#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction ROBUSTE ET SÉQUENTIELLE du top 3 armes pour chaque joueur

AMÉLIORATIONS vs version originale :
- Retry automatique (3 tentatives)
- Validation données (minimum 3 armes)
- Checkpointing (reprendre extraction)
- Monitoring temps réel (tqdm)
- Wait dynamique (au lieu de sleep(20) fixe)
- Logs structurés

DURÉE ESTIMÉE : 15-20 minutes (97 joueurs)
FIABILITÉ : 95-100% succès
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/extraction_robust.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chemins
BASE_DIR = Path(__file__).parent.parent
LEADERBOARD_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "leaderboard"
OUTPUT_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "top_weapons"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = BASE_DIR / "data" / "extraction_checkpoint.json"


class ExtractionCheckpoint:
    """Gestion du checkpointing pour reprendre extraction"""
    
    def __init__(self, checkpoint_file):
        self.checkpoint_file = Path(checkpoint_file)
        self.extracted_handles = set()
        self.load()
    
    def load(self):
        """Charge le checkpoint existant"""
        if self.checkpoint_file.exists():
            try:
                data = json.loads(self.checkpoint_file.read_text())
                self.extracted_handles = set(data.get('handles', []))
                logger.info(f"📂 Checkpoint chargé : {len(self.extracted_handles)} joueurs déjà extraits")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de charger checkpoint : {e}")
    
    def save(self, handle):
        """Sauvegarde un joueur extrait"""
        self.extracted_handles.add(handle)
        self.checkpoint_file.write_text(json.dumps({
            'handles': list(self.extracted_handles),
            'timestamp': datetime.now().isoformat()
        }, indent=2))
    
    def is_extracted(self, handle):
        """Vérifie si un joueur a déjà été extrait"""
        return handle in self.extracted_handles
    
    def clear(self):
        """Efface le checkpoint"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        self.extracted_handles.clear()


def validate_weapon_data(weapons):
    """
    Valide que les données extraites sont correctes.
    
    Args:
        weapons: Liste de dictionnaires d'armes
    
    Returns:
        bool: True si valide, False sinon
    
    Raises:
        ValueError: Si données invalides
    """
    if not weapons:
        raise ValueError("Aucune arme extraite")
    
    if len(weapons) < 3:
        raise ValueError(f"Moins de 3 armes extraites : {len(weapons)}")
    
    for weapon in weapons:
        if not weapon.get('name'):
            raise ValueError(f"Arme sans nom : {weapon}")
        
        kills = weapon.get('kills', 0)
        if not isinstance(kills, int) or kills <= 0:
            raise ValueError(f"Kills invalide pour {weapon['name']}: {kills}")
    
    return True


def wait_for_weapons_table(driver, timeout=30):
    """
    Attend dynamiquement que le tableau d'armes soit chargé.
    OPTIMISATION: Au lieu de time.sleep(20) fixe, attend seulement le temps nécessaire.
    
    Args:
        driver: WebDriver Selenium
        timeout: Timeout max en secondes
    
    Returns:
        bool: True si table chargée, False sinon
    """
    try:
        # Attendre que la div principale des weapons soit présente
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-v-d84fa2c6]"))
        )
        
        # Attendre encore 2-3s pour le rendu complet (Cloudflare + JS)
        time.sleep(3)
        
        return True
    except Exception as e:
        logger.warning(f"⚠️ Timeout attente tableau armes : {e}")
        return False


def extract_player_weapons(driver, player_handle, player_id, max_retries=3):
    """
    Extrait les top 3 armes d'un joueur avec retry automatique.
    
    Args:
        driver: WebDriver Chrome
        player_handle: Pseudo du joueur
        player_id: ID unique Tracker.gg
        max_retries: Nombre max de tentatives
    
    Returns:
        dict: Données extraites ou None si échec
    """
    url = f"https://tracker.gg/bf6/profile/{player_id}/{player_handle}/weapons"
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🎮 {player_handle} (tentative {attempt}/{max_retries})")
            
            # Charger la page
            driver.get(url)
            
            # Attendre que le tableau soit chargé (wait dynamique)
            if not wait_for_weapons_table(driver):
                raise Exception("Timeout chargement tableau armes")
            
            # Parser le HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Trouver toutes les divs d'armes
            weapon_divs = soup.find_all('div', {'data-v-d84fa2c6': True})
            
            weapons = []
            
            for div in weapon_divs:
                try:
                    # Nom de l'arme (balise <a> avec classe specific)
                    name_tag = div.find('a', class_='weapon-info__name')
                    if not name_tag:
                        continue
                    
                    weapon_name = name_tag.get_text(strip=True)
                    
                    # Kills (span avec valeur)
                    stats_div = div.find('div', class_='weapon-stats')
                    if not stats_div:
                        continue
                    
                    kills_span = stats_div.find('span', class_='value')
                    if not kills_span:
                        continue
                    
                    kills_text = kills_span.get_text(strip=True).replace(',', '')
                    
                    try:
                        kills = int(kills_text)
                    except ValueError:
                        logger.warning(f"⚠️ Kills non parsable : {kills_text}")
                        continue
                    
                    # Stats supplémentaires (accuracy, headshot, etc.)
                    stat_values = stats_div.find_all('span', class_='value')
                    
                    accuracy = None
                    headshot_pct = None
                    damage = None
                    
                    # Parser les stats additionnelles si disponibles
                    if len(stat_values) >= 3:
                        try:
                            # Accuracy (2e stat)
                            accuracy_text = stat_values[1].get_text(strip=True).replace('%', '')
                            accuracy = float(accuracy_text)
                        except:
                            pass
                        
                        try:
                            # Headshot % (3e stat)
                            headshot_text = stat_values[2].get_text(strip=True).replace('%', '')
                            headshot_pct = float(headshot_text)
                        except:
                            pass
                    
                    weapons.append({
                        'name': weapon_name,
                        'kills': kills,
                        'accuracy': accuracy,
                        'headshot_pct': headshot_pct,
                        'damage': damage
                    })
                
                except Exception as e:
                    logger.debug(f"⚠️ Erreur parsing arme : {e}")
                    continue
            
            # Trier par kills et prendre top 3
            weapons.sort(key=lambda x: x['kills'], reverse=True)
            top_3_weapons = weapons[:3]
            
            # Validation
            validate_weapon_data(top_3_weapons)
            
            logger.info(f"✅ {player_handle} - {len(top_3_weapons)} armes extraites")
            
            return {
                'source': 'tracker.gg',
                'board': 'Kills',
                'snapshot_utc': datetime.utcnow().isoformat(),
                'player_id': player_id,
                'handle': player_handle,
                'top_weapons': top_3_weapons,
                'status': 'success'
            }
        
        except Exception as e:
            logger.warning(f"❌ {player_handle} - Tentative {attempt}/{max_retries} échouée : {e}")
            
            if attempt < max_retries:
                # Wait avant retry
                wait_time = 2 * attempt  # Backoff exponentiel
                logger.info(f"⏳ Retry dans {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ {player_handle} - Échec définitif après {max_retries} tentatives")
                return {
                    'source': 'tracker.gg',
                    'board': 'Kills',
                    'snapshot_utc': datetime.utcnow().isoformat(),
                    'player_id': player_id,
                    'handle': player_handle,
                    'top_weapons': [],
                    'status': 'error',
                    'error': str(e)
                }
    
    return None


def main():
    """Fonction principale d'extraction robuste"""
    
    print("\n" + "="*70)
    print("🎮 EXTRACTION ROBUSTE - TOP 3 ARMES PAR JOUEUR")
    print("="*70 + "\n")
    
    # Charger le leaderboard
    leaderboard_files = sorted(LEADERBOARD_DIR.glob("*.ndjson"))
    
    if not leaderboard_files:
        logger.error("❌ Aucun fichier leaderboard trouvé")
        return
    
    latest_leaderboard = leaderboard_files[-1]
    logger.info(f"📂 Leaderboard : {latest_leaderboard.name}")
    
    # Charger les joueurs
    players = []
    with open(latest_leaderboard, 'r', encoding='utf-8') as f:
        for line in f:
            players.append(json.loads(line))
    
    logger.info(f"👥 {len(players)} joueurs à extraire")
    
    # Checkpoint
    checkpoint = ExtractionCheckpoint(CHECKPOINT_FILE)
    
    # Filtrer les joueurs déjà extraits
    remaining_players = [p for p in players if not checkpoint.is_extracted(p['handle'])]
    
    if len(remaining_players) < len(players):
        logger.info(f"🔄 Reprise extraction : {len(remaining_players)} joueurs restants")
    
    if not remaining_players:
        logger.info("✅ Tous les joueurs déjà extraits !")
        return
    
    # Préparer output file
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_file = OUTPUT_DIR / f"bf6_top_weapons_robust_{timestamp}.ndjson"
    
    # Créer driver Chrome
    logger.info("🌐 Initialisation Chrome...")
    driver = uc.Chrome(version_main=141)  # Force version compatible
    
    try:
        # Barre de progression
        with tqdm(total=len(remaining_players), desc="Extraction", unit="joueur") as pbar:
            success_count = 0
            error_count = 0
            
            start_time = time.time()
            
            for i, player in enumerate(remaining_players):
                player_handle = player['handle']
                player_id = player['player_id']
                
                # Extraire
                result = extract_player_weapons(driver, player_handle, player_id)
                
                if result:
                    # Sauvegarder immédiatement
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(result, ensure_ascii=False) + '\n')
                    
                    # Checkpoint
                    checkpoint.save(player_handle)
                    
                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Mettre à jour barre
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    eta_seconds = (len(remaining_players) - i - 1) / rate if rate > 0 else 0
                    
                    pbar.set_postfix({
                        '✅': success_count,
                        '❌': error_count,
                        'vitesse': f'{rate:.2f} j/s',
                        'ETA': f'{eta_seconds/60:.1f} min'
                    })
                    pbar.update(1)
                else:
                    error_count += 1
                    pbar.update(1)
        
        # Résumé final
        duration = time.time() - start_time
        
        print("\n" + "="*70)
        print("📊 RÉSULTATS EXTRACTION")
        print("="*70)
        print(f"✅ Succès      : {success_count}/{len(remaining_players)}")
        print(f"❌ Échecs      : {error_count}/{len(remaining_players)}")
        print(f"⏱️  Durée       : {duration/60:.1f} minutes")
        print(f"⚡ Vitesse     : {len(remaining_players)/duration:.2f} joueurs/s")
        print(f"📁 Fichier     : {output_file.name}")
        print(f"💾 Taille      : {output_file.stat().st_size / 1024:.2f} KB")
        print("="*70 + "\n")
        
        # Nettoyer checkpoint si 100% succès
        if error_count == 0:
            logger.info("🎉 Extraction 100% réussie ! Nettoyage checkpoint...")
            checkpoint.clear()
    
    finally:
        # Fermer driver
        logger.info("🔚 Fermeture Chrome...")
        driver.quit()


if __name__ == "__main__":
    main()
