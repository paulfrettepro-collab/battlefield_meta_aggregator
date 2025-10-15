"""
Scrapy Items - Définition de la structure des données crawlées
"""
import scrapy


class WeaponItem(scrapy.Item):
    """Item représentant une arme dans Battlefield 6"""
    
    # Informations de base
    name = scrapy.Field()                # Nom de l'arme (ex: "ACW-R")
    category = scrapy.Field()            # Catégorie (ex: "Assault Rifle", "SMG")
    tier = scrapy.Field()                # Tier (S, A, B, C, D)
    
    # Statistiques (si disponibles)
    win_rate = scrapy.Field()            # Taux de victoire (ex: 54.5)
    pick_rate = scrapy.Field()           # Taux de sélection (ex: 12.3)
    kd_ratio = scrapy.Field()            # K/D ratio moyen
    ttk = scrapy.Field()                 # Time to kill (ms)
    
    # Contenu textuel
    description = scrapy.Field()         # Description complète
    pros = scrapy.Field()                # Points forts (liste)
    cons = scrapy.Field()                # Points faibles (liste)
    recommended_loadout = scrapy.Field() # Loadout recommandé
    
    # Métadonnées de crawling
    source = scrapy.Field()              # Source (ex: "PC Gamer")
    source_url = scrapy.Field()          # URL de la page
    page_title = scrapy.Field()          # Titre de la page
    crawled_at = scrapy.Field()          # Date/heure du crawl
    content_hash = scrapy.Field()        # Hash du contenu pour déduplication
    
    # Texte complet pour vectorisation
    full_text = scrapy.Field()           # Texte complet combiné


class ClassItem(scrapy.Item):
    """Item représentant une classe dans Battlefield 6"""
    
    name = scrapy.Field()                # Nom de la classe (ex: "Assault")
    tier = scrapy.Field()                # Tier (S, A, B, C, D)
    best_weapons = scrapy.Field()        # Meilleures armes (liste)
    best_gadgets = scrapy.Field()        # Meilleurs gadgets (liste)
    playstyle = scrapy.Field()           # Style de jeu recommandé
    description = scrapy.Field()         # Description
    
    # Métadonnées
    source = scrapy.Field()
    source_url = scrapy.Field()
    crawled_at = scrapy.Field()
    full_text = scrapy.Field()


class MetaSnapshotItem(scrapy.Item):
    """Item représentant un snapshot complet de la méta"""
    
    patch_version = scrapy.Field()       # Version du patch (ex: "2.5.1")
    top_weapons = scrapy.Field()         # Top armes (liste avec tiers)
    top_classes = scrapy.Field()         # Top classes
    meta_summary = scrapy.Field()        # Résumé de la méta
    
    # Métadonnées
    source = scrapy.Field()
    source_url = scrapy.Field()
    crawled_at = scrapy.Field()
    full_text = scrapy.Field()
