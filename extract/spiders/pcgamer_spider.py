"""
Spider de test pour crawler PC Gamer - Article Battlefield 6
Extrait un article réel avec loadout et méta
"""
import scrapy
from datetime import datetime


class PCGamerSpider(scrapy.Spider):
    name = "pcgamer"
    allowed_domains = ["pcgamer.com"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
    }
    
    def start_requests(self):
        """URL réelle d'un article Battlefield 6 sur PC Gamer"""
        url = "https://www.pcgamer.com/games/fps/battlefield-6-pw7a2-loadout-build"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """Parse l'article PC Gamer"""
        self.logger.info(f"🕷️  Crawling: {response.url}")
        
        # Métadonnées
        result = {
            'url': response.url,
            'crawled_at': datetime.now().isoformat(),
            'status_code': response.status,
            'source': 'PC Gamer',
        }
        
        # Extraction du titre
        title = response.css('h1::text').get()
        if title:
            result['title'] = title.strip()
        
        # Extraction de tous les headings
        headings = []
        for h in response.css('h1, h2, h3, h4'):
            text = h.css('::text').get()
            if text and text.strip():
                headings.append({
                    'level': h.root.tag,
                    'text': text.strip()
                })
        result['headings'] = headings
        
        # Extraction des paragraphes
        paragraphs = []
        for p in response.css('article p::text, .content p::text, .article-body p::text').getall():
            if p.strip() and len(p.strip()) > 20:
                paragraphs.append(p.strip())
        result['paragraphs'] = paragraphs[:20]  # Premier 20 paragraphes
        
        # Extraction des listes (armes, loadouts)
        lists = []
        for li in response.css('article li, .content li, .article-body li'):
            text = ''.join(li.css('::text').getall()).strip()
            if text and len(text) > 5:
                lists.append(text)
        result['lists'] = lists
        
        # Extraction du contenu complet de l'article
        article_text = ' '.join(response.css('article ::text, .content ::text, .article-body ::text').getall())
        article_text = ' '.join(article_text.split())  # Nettoie les espaces
        result['full_article_text'] = article_text[:3000] if len(article_text) > 3000 else article_text
        result['article_length'] = len(article_text)
        
        # Extraction de la date de publication
        pub_date = response.css('time::attr(datetime)').get()
        if pub_date:
            result['published_date'] = pub_date
        
        # Recherche de mots-clés de méta
        meta_keywords = ['loadout', 'build', 'weapon', 'gun', 'meta', 'best', 'tier', 'attachment', 'barrel', 'magazine', 'optic', 'muzzle']
        found_keywords = [kw for kw in meta_keywords if kw.lower() in article_text.lower()]
        result['meta_keywords_found'] = found_keywords
        
        # Extraction des armes mentionnées (patterns courants)
        weapons_mentioned = []
        weapon_patterns = ['PW7A2', 'M4A1', 'AK47', 'SCAR', 'MP5', 'XM8', 'SVD', 'M16A3']
        for weapon in weapon_patterns:
            if weapon.lower() in article_text.lower():
                weapons_mentioned.append(weapon)
        result['weapons_mentioned'] = weapons_mentioned
        
        self.logger.info(f"✅ Extraction terminée : {len(headings)} titres, {len(paragraphs)} paragraphes, {len(lists)} listes")
        
        yield result
