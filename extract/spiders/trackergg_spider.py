"""
Spider Scrapy pour Tracker.gg Battlefield 2042

Objectifs :
1. Extraire le leaderboard (top 100 joueurs)
2. Pour chaque joueur, récupérer son loadout détaillé
3. Anonymiser les pseudos
4. Stocker au format NDJSON pour MinIO

Données extraites :
- Leaderboard: rank, username (anonymisé), platform, url_profil
- Loadouts: weapon, attachments [optic, barrel, magazine, underbarrel, stock], timestamp

Usage:
    scrapy crawl trackergg -o data/bronze/trackergg_$(date +%Y-%m-%d).ndjson
"""

import scrapy
from datetime import datetime
import hashlib
from typing import Generator


class TrackerGGSpider(scrapy.Spider):
    name = "trackergg"
    allowed_domains = ["tracker.gg"]
    
    # URL de départ - à adapter après exploration
    start_urls = [
        "https://tracker.gg/battlefield-2042/leaderboards/stats/all/default?page=1&platform=pc"
    ]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,  # Rate limiting respectueux
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    def __init__(self, max_players: int = 100, *args, **kwargs):
        super(TrackerGGSpider, self).__init__(*args, **kwargs)
        self.max_players = int(max_players)
        self.players_crawled = 0
    
    def parse(self, response):
        """
        Parse la page leaderboard
        
        TODO: Implémenter après exploration avec DevTools
        - Identifier sélecteurs CSS/XPath pour lignes du tableau
        - Extraire: rank, username, stats, lien profil
        - Suivre les liens profil pour get_player_loadout
        """
        self.logger.info(f"Parsing leaderboard page: {response.url}")
        
        # Exemple de structure à adapter
        # for player_row in response.css('div.player-row'):
        #     rank = player_row.css('.rank::text').get()
        #     username = player_row.css('.username::text').get()
        #     profile_url = player_row.css('a.player-link::attr(href)').get()
        #     
        #     # Anonymiser le pseudo
        #     anonymous_id = self._anonymize_username(username)
        #     
        #     # Yield leaderboard data
        #     yield {
        #         'type': 'leaderboard',
        #         'rank': int(rank),
        #         'player_id': anonymous_id,
        #         'platform': 'pc',
        #         'crawled_at': datetime.utcnow().isoformat()
        #     }
        #     
        #     # Suivre le profil pour loadout
        #     if self.players_crawled < self.max_players:
        #         yield response.follow(profile_url, self.parse_player_profile,
        #                               meta={'player_id': anonymous_id, 'rank': rank})
        #         self.players_crawled += 1
        
        raise NotImplementedError(
            "⚠️ Ce spider nécessite une exploration préalable de Tracker.gg\n"
            "Actions requises:\n"
            "1. Visiter https://tracker.gg/battlefield-2042/leaderboards\n"
            "2. Ouvrir DevTools (F12) > Elements\n"
            "3. Identifier les sélecteurs CSS pour:\n"
            "   - Lignes du tableau leaderboard\n"
            "   - Rank, Username, Stats, Profile URL\n"
            "4. Vérifier si un endpoint JSON existe (Network > XHR)\n"
            "5. Adapter les sélecteurs dans ce fichier\n"
        )
    
    def parse_player_profile(self, response):
        """
        Parse la page profil d'un joueur pour extraire le loadout
        
        TODO: Implémenter après exploration
        - Identifier où sont affichées les armes utilisées
        - Extraire les accessoires par arme
        - Structure: weapon, optic, barrel, magazine, underbarrel, stock
        """
        player_id = response.meta['player_id']
        rank = response.meta['rank']
        
        self.logger.info(f"Parsing profile for player {player_id} (rank {rank})")
        
        # Exemple de structure à adapter
        # for weapon_card in response.css('section.weapon-card'):
        #     weapon_name = weapon_card.css('h3.weapon-name::text').get()
        #     
        #     attachments = {}
        #     for attachment in weapon_card.css('li.attachment'):
        #         slot = attachment.css('.slot::text').get()  # optic, barrel, etc.
        #         item = attachment.css('.name::text').get()
        #         attachments[slot] = item
        #     
        #     yield {
        #         'type': 'loadout',
        #         'player_id': player_id,
        #         'rank': rank,
        #         'weapon': weapon_name,
        #         'attachments': attachments,
        #         'crawled_at': datetime.utcnow().isoformat(),
        #         'source_url': response.url
        #     }
        
        raise NotImplementedError("À implémenter après exploration")
    
    def _anonymize_username(self, username: str) -> str:
        """
        Anonymise un pseudo via hash SHA256
        
        Args:
            username: Pseudo du joueur
            
        Returns:
            Hash anonymisé (ex: "player_a3f5b9c2")
        """
        hash_obj = hashlib.sha256(username.encode())
        return f"player_{hash_obj.hexdigest()[:8]}"
