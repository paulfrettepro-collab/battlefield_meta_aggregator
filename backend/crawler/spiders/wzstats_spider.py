"""
Spider de test pour crawler wzstats.gg - Méta Battlefield 6
Extrait les armes performantes, tier lists et méta actuelle
"""
import scrapy
from datetime import datetime
import json


class WZStatsSpider(scrapy.Spider):
    name = "wzstats"
    allowed_domains = ["wzstats.gg"]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
        },
    }
    
    def start_requests(self):
        """Génère les requêtes initiales avec Playwright"""
        url = "https://wzstats.gg/battlefield-6/meta"
        yield scrapy.Request(
            url,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [3000]},  # Attend 3 secondes supplémentaires
                ]
            },
            callback=self.parse,
            errback=self.errback_close_page,
        )
    
    async def errback_close_page(self, failure):
        """Gestion des erreurs Playwright"""
        self.logger.error(f"❌ Erreur lors du crawl: {failure}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()

    def parse(self, response):
        """
        Parse la page principale de la méta Battlefield 6
        """
        self.logger.info(f"🕷️  Crawling: {response.url}")
        
        # Métadonnées de base
        meta_data = {
            'url': response.url,
            'crawled_at': datetime.now().isoformat(),
            'status_code': response.status,
            'page_title': response.css('title::text').get(),
        }
        
        # Extraction du titre de la page
        page_title = response.css('h1::text').get()
        if page_title:
            meta_data['main_title'] = page_title.strip()
        
        # Extraction de toutes les sections de texte importantes
        sections = []
        
        # Extraction des headings (h1, h2, h3)
        for heading in response.css('h1, h2, h3, h4'):
            text = heading.css('::text').get()
            if text:
                sections.append({
                    'type': heading.root.tag,
                    'text': text.strip()
                })
        
        # Extraction des paragraphes
        paragraphs = response.css('p::text').getall()
        for p in paragraphs:
            if p.strip() and len(p.strip()) > 20:
                sections.append({
                    'type': 'paragraph',
                    'text': p.strip()
                })
        
        # Extraction des listes (armes, tier lists)
        list_items = response.css('li::text').getall()
        weapons = []
        for item in list_items:
            if item.strip() and len(item.strip()) > 2:
                weapons.append(item.strip())
        
        # Extraction des tables (si présentes)
        tables = []
        for table in response.css('table'):
            headers = table.css('th::text').getall()
            rows = []
            for row in table.css('tr'):
                cells = row.css('td::text').getall()
                if cells:
                    rows.append(cells)
            if headers or rows:
                tables.append({
                    'headers': headers,
                    'rows': rows
                })
        
        # Extraction de tout le texte visible de la page
        all_text = ' '.join(response.css('body ::text').getall())
        # Nettoyage du texte
        all_text = ' '.join(all_text.split())  # Normalise les espaces
        
        # Construction du résultat final
        result = {
            **meta_data,
            'sections': sections,
            'weapons_found': weapons if weapons else [],
            'tables': tables if tables else [],
            'full_text_sample': all_text[:2000] if len(all_text) > 2000 else all_text,  # Premier 2000 caractères
            'full_text_length': len(all_text),
            'html_snapshot': response.text[:1000],  # Premier 1000 caractères du HTML
        }
        
        # Recherche spécifique de patterns de méta
        meta_keywords = ['tier', 'meta', 'best', 'weapon', 'gun', 'loadout', 'patch', 'version', 'update']
        matching_keywords = [kw for kw in meta_keywords if kw.lower() in all_text.lower()]
        result['meta_keywords_found'] = matching_keywords
        
        self.logger.info(f"✅ Extraction terminée : {len(sections)} sections, {len(weapons)} armes")
        
        yield result
