"""
Spider Scrapy pour extraire le leaderboard Battlefield 6

Usage:
    scrapy crawl bf6_leaderboard -o data/bronze/bf6_leaderboard.ndjson
"""

import scrapy
import hashlib
from datetime import datetime


class BF6LeaderboardSpider(scrapy.Spider):
    name = "bf6_leaderboard"
    allowed_domains = ["tracker.gg"]
    start_urls = ["https://tracker.gg/bf6/leaderboards"]
    
    # Configuration pour paraître "humain"
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,  # 2 secondes entre chaque requête
        'CONCURRENT_REQUESTS': 1,  # Une seule requête à la fois
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'FEEDS': {
            'data/bronze/bf6_leaderboard_%(time)s.ndjson': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'overwrite': False,
            }
        }
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.players_count = 0
        self.start_time = datetime.now()
    
    def parse(self, response):
        """Parse la page du leaderboard"""
        self.logger.info("=" * 80)
        self.logger.info("🎮 BATTLEFIELD 6 - EXTRACTION LEADERBOARD")
        self.logger.info("=" * 80)
        self.logger.info(f"📡 URL: {response.url}")
        self.logger.info(f"✅ Status: {response.status}")
        self.logger.info(f"📄 HTML size: {len(response.text)} chars")
        
        # Sauvegarder le HTML pour analyse
        filename = f'data/exploration/leaderboard_page_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info(f"💾 HTML saved: {filename}")
        
        # ÉTAPE 1 : Analyser la structure de la page
        self.logger.info("\n" + "━" * 80)
        self.logger.info("🔍 ANALYSE DE LA STRUCTURE HTML")
        self.logger.info("━" * 80)
        
        # Chercher les conteneurs potentiels
        tables = response.css('table, div[class*="table"], div[class*="leaderboard"], div[class*="list"]')
        self.logger.info(f"\n📊 Conteneurs trouvés: {len(tables)}")
        
        for i, table in enumerate(tables[:5], 1):
            classes = ' '.join(table.css('::attr(class)').getall())
            tag = table.xpath('name()').get()
            self.logger.info(f"   [{i}] Tag: {tag}, Classes: {classes[:100]}")
        
        # Chercher des patterns de lignes
        rows = response.css('tr, div[class*="row"]')
        self.logger.info(f"\n📋 Lignes potentielles: {len(rows)}")
        
        # Afficher quelques exemples de texte
        for i, row in enumerate(rows[:5], 1):
            text = row.css('::text').getall()
            text_clean = ' '.join([t.strip() for t in text if t.strip()])[:100]
            self.logger.info(f"   [{i}] {text_clean}...")
        
        # ÉTAPE 2 : Chercher les données JSON embarquées
        self.logger.info("\n" + "━" * 80)
        self.logger.info("📦 RECHERCHE DE DONNÉES JSON")
        self.logger.info("━" * 80)
        
        json_scripts = response.css('script[type="application/json"]::text').getall()
        self.logger.info(f"\n🔍 Scripts JSON trouvés: {len(json_scripts)}")
        
        for i, script in enumerate(json_scripts[:3], 1):
            self.logger.info(f"   [{i}] Taille: {len(script)} chars")
            if len(script) < 500:
                self.logger.info(f"       Contenu: {script[:200]}...")
        
        # ÉTAPE 3 : Tentative d'extraction avec différents sélecteurs
        self.logger.info("\n" + "━" * 80)
        self.logger.info("🎯 TENTATIVES D'EXTRACTION")
        self.logger.info("━" * 80)
        
        # Sélecteur 1 : Lignes de tableau classique
        player_rows = response.css('table tbody tr')
        if player_rows:
            self.logger.info(f"\n✅ Sélecteur 'table tbody tr' : {len(player_rows)} éléments")
            for row in player_rows[:100]:  # Top 100
                yield self.extract_player_from_row(row, method="table_row")
        
        # Sélecteur 2 : Divs avec classe "player" ou similaire
        player_divs = response.css('div[class*="player"], div[class*="entry"]')
        if player_divs:
            self.logger.info(f"\n✅ Sélecteur 'div player/entry' : {len(player_divs)} éléments")
            for div in player_divs[:100]:
                yield self.extract_player_from_div(div, method="player_div")
        
        # Si aucun pattern trouvé
        if not player_rows and not player_divs:
            self.logger.warning("\n⚠️  Aucun pattern standard détecté")
            self.logger.info("💡 Prochaine étape: Analyser le HTML sauvegardé manuellement")
            self.logger.info("    Ouvrir: " + filename)
            self.logger.info("    Chercher: la structure qui contient les joueurs")
    
    def extract_player_from_row(self, row, method="unknown"):
        """Extrait les données d'un joueur depuis une ligne de tableau"""
        try:
            cells = row.css('td')
            
            if len(cells) >= 3:
                # Structure probable: [rank, username, stats...]
                rank_text = cells[0].css('::text').get('').strip()
                username = cells[1].css('::text').get('').strip()
                
                # Extraire les stats disponibles
                stats = {}
                for i, cell in enumerate(cells[2:], 2):
                    cell_text = cell.css('::text').get('').strip()
                    if cell_text:
                        stats[f'stat_{i}'] = cell_text
                
                player_data = {
                    'extraction_date': datetime.now().isoformat(),
                    'rank': self.extract_number(rank_text),
                    'username_original': username,
                    'username_hash': self.anonymize_username(username),
                    'stats': stats,
                    'extraction_method': method,
                    'source_url': self.start_urls[0]
                }
                
                self.players_count += 1
                if self.players_count <= 5:  # Log les 5 premiers
                    self.logger.info(f"\n   ✅ Joueur #{player_data['rank']}: {username} → {player_data['username_hash']}")
                
                return player_data
        
        except Exception as e:
            self.logger.error(f"❌ Erreur extraction row: {e}")
        
        return None
    
    def extract_player_from_div(self, div, method="unknown"):
        """Extrait les données d'un joueur depuis un div"""
        try:
            # Chercher le username dans différents endroits possibles
            username = (
                div.css('span[class*="username"]::text').get() or
                div.css('div[class*="name"]::text').get() or
                div.css('a::text').get() or
                ''
            ).strip()
            
            # Chercher le rank
            rank = div.css('span[class*="rank"]::text, div[class*="rank"]::text').get('').strip()
            
            if username:
                player_data = {
                    'extraction_date': datetime.now().isoformat(),
                    'rank': self.extract_number(rank),
                    'username_original': username,
                    'username_hash': self.anonymize_username(username),
                    'extraction_method': method,
                    'source_url': self.start_urls[0]
                }
                
                self.players_count += 1
                if self.players_count <= 5:
                    self.logger.info(f"\n   ✅ Joueur #{player_data['rank']}: {username} → {player_data['username_hash']}")
                
                return player_data
        
        except Exception as e:
            self.logger.error(f"❌ Erreur extraction div: {e}")
        
        return None
    
    def anonymize_username(self, username):
        """Anonymise un pseudo via hash SHA256"""
        if not username:
            return "unknown"
        hash_obj = hashlib.sha256(username.encode())
        return f"player_{hash_obj.hexdigest()[:8]}"
    
    def extract_number(self, text):
        """Extrait un nombre d'un texte"""
        if not text:
            return None
        # Enlever les caractères non-numériques
        clean = ''.join(c for c in text if c.isdigit())
        return int(clean) if clean else None
    
    def closed(self, reason):
        """Appelé à la fin du scraping"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 RÉSUMÉ DE L'EXTRACTION")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ Joueurs extraits: {self.players_count}")
        self.logger.info(f"⏱️  Durée: {duration:.1f}s")
        self.logger.info(f"🎯 Raison fermeture: {reason}")
        self.logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
