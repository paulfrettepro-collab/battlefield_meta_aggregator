#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraction du leaderboard BF6 (top 100 joueurs par Kills)
Source: https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1
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
DATA_DIR = BASE_DIR / "data" / "bronze" / "tracker_gg" / "leaderboard"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# URL du leaderboard
LEADERBOARD_URL = "https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1"


def extract_leaderboard(max_players=50):
    """
    Extrait le top N du leaderboard BF6
    
    Args:
        max_players: Nombre max de joueurs à extraire (défaut: 50 pour MVP)
    
    Returns:
        list: Liste des joueurs avec {handle, player_id, rank, kills, location, matches_played}
    """
    logger.info(f"🚀 Démarrage de l'extraction du leaderboard (top {max_players})")
    logger.info(f"🔗 URL: {LEADERBOARD_URL}")
    
    driver = None
    try:
        # Créer le driver Chrome (sans headless)
        logger.info("🌐 Lancement du navigateur Chrome...")
        driver = uc.Chrome()
        driver.get(LEADERBOARD_URL)
        
        # Attendre le chargement de la page
        logger.info("⏳ Attente 20s pour le chargement de la page...")
        time.sleep(20)
        
        # Récupérer le HTML
        html = driver.page_source
        html_size = len(html)
        logger.info(f"📄 HTML récupéré: {html_size:,} caractères")
        
        # Sauvegarder le HTML pour debug
        debug_file = DATA_DIR / "leaderboard_debug.html"
        debug_file.write_text(html, encoding='utf-8')
        logger.info(f"💾 HTML debug sauvegardé: {debug_file}")
        
        # Parser avec BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Chercher toutes les lignes du leaderboard
        # Structure RÉELLE: <tr data-key="1">, <tr data-key="2">, etc. (valeurs numériques)
        player_rows = soup.find_all('tr', {'data-key': lambda x: x and x.isdigit()})
        
        logger.info(f"🔍 Trouvé {len(player_rows)} joueurs dans le tableau")
        
        players = []
        for row in player_rows:
            # Limiter au nombre demandé
            if len(players) >= max_players:
                logger.info(f"🎯 Limite de {max_players} joueurs atteinte")
                break
                
            try:
                # Récupérer toutes les cellules
                cells = row.find_all('td')
                
                if len(cells) < 5:
                    continue
                
                # Cellule 0: Rank (avec classe 'min-w-9')
                rank_cell = cells[0]
                rank_span = rank_cell.find('span', class_=lambda x: x and 'min-w-9' in x if x else False)
                if not rank_span:
                    continue
                rank = int(rank_span.get_text(strip=True))
                
                # Cellule 1: Lien du joueur avec handle et player_id + location
                player_link = cells[1].find('a', href=lambda x: x and '/bf6/profile/' in x if x else False)
                if not player_link:
                    continue
                
                # Extraire player_id depuis href: "/bf6/profile/1006806438138"
                # Format: ['', 'bf6', 'profile', '{player_id}']
                href_parts = player_link['href'].split('/')
                if len(href_parts) < 4:
                    continue
                player_id = href_parts[-1]  # Dernier segment = player_id
                
                # Extraire handle depuis span avec classe 'truncate' dans le lien
                handle_span = player_link.find('span', class_='truncate')
                if not handle_span:
                    continue
                handle = handle_span.get_text(strip=True)
                
                # Extraire location (flag emoji ou country code)
                location = None
                # Chercher l'img du flag dans la cellule 1
                flag_img = cells[1].find('img', alt=True)
                if flag_img:
                    location = flag_img['alt']  # ex: "United States", "Canada", etc.
                
                # Cellule 3 ou 4: Kills (grand nombre avec virgule comme séparateur)
                kills = 0
                for cell_idx in [3, 4]:  # Chercher dans les cellules 3 et 4
                    if cell_idx < len(cells):
                        kills_span = cells[cell_idx].find('span', class_='truncate')
                        if kills_span:
                            kills_text = kills_span.get_text(strip=True).replace(',', '').replace(' ', '')
                            # Vérifier si c'est un nombre et suffisamment grand (kills > 1000)
                            if kills_text.replace('.', '').isdigit():
                                test_kills = int(kills_text.split('.')[0])  # Enlever les décimales éventuelles
                                if test_kills > 1000:  # Les kills doivent être > 1000 pour le top
                                    kills = test_kills
                                    break
                
                # Cellule 5 ou 6: Matches Played (nombre avec virgule)
                matches_played = None
                for cell_idx in [4, 5]:  # Chercher dans les cellules après kills
                    if cell_idx < len(cells):
                        matches_span = cells[cell_idx].find('span', class_='truncate')
                        if matches_span:
                            matches_text = matches_span.get_text(strip=True).replace(',', '').replace(' ', '')
                            # Vérifier si c'est un nombre raisonnable (< 10000 généralement)
                            if matches_text.isdigit():
                                test_matches = int(matches_text)
                                if 10 < test_matches < 10000:  # Matches raisonnables
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
                        'extraction_date': datetime.now().isoformat(),
                        'url_source': LEADERBOARD_URL
                    })
                    
                    # Log tous les 10 joueurs
                    if len(players) % 10 == 0:
                        logger.info(f"  ✅ {len(players)} joueurs extraits...")
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing joueur: {e}")
                continue
        
        logger.info(f"\n✅ {len(players)} joueurs extraits avec succès")
        
        # Afficher les 5 premiers
        if players:
            logger.info("\n🏆 Top 5:")
            for p in players[:5]:
                loc = p.get('location', 'N/A')
                matches = p.get('matches_played', 'N/A')
                logger.info(f"  {p['rank']}. {p['handle']} - {p['kills']:,} kills - {loc} - {matches} matches (ID: {p['player_id']})")
        
        return players
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'extraction: {e}")
        raise
        
    finally:
        if driver:
            driver.quit()
            logger.info("🔒 Navigateur fermé")


def main():
    """Fonction principale"""
    try:
        # Extraire le leaderboard
        players = extract_leaderboard()
        
        if not players:
            logger.error("❌ Aucun joueur extrait")
            return
        
        # Sauvegarder en NDJSON
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        output_file = DATA_DIR / f"bf6_leaderboard_{timestamp}.ndjson"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for player in players:
                f.write(json.dumps(player, ensure_ascii=False) + '\n')
        
        logger.info(f"\n💾 Fichier sauvegardé: {output_file}")
        logger.info(f"📊 {len(players)} joueurs")
        logger.info("\n✅ Extraction du leaderboard terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        raise


if __name__ == '__main__':
    main()
