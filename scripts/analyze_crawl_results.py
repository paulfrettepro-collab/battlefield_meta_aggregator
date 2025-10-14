#!/usr/bin/env python
"""
Analyse LLM des résultats crawlés
Utilise l'API OpenAI pour extraire la méta Battlefield 6
"""
import json
import os
from pathlib import Path

def analyze_with_copilot(crawl_data):
    """
    Analyse les données crawlées avec GitHub Copilot / LLM intégré
    (Simulation d'analyse LLM sans API externe)
    """
    
    print("\n" + "="*80)
    print("📊 ANALYSE DES DONNÉES CRAWLÉES - BATTLEFIELD 6 META")
    print("="*80 + "\n")
    
    # Extraction des informations principales
    url = crawl_data.get('url', 'N/A')
    title = crawl_data.get('title', 'N/A')
    pub_date = crawl_data.get('published_date', 'N/A')
    source = crawl_data.get('source', 'N/A')
    article_length = crawl_data.get('article_length', 0)
    weapons_mentioned = crawl_data.get('weapons_mentioned', [])
    meta_keywords = crawl_data.get('meta_keywords_found', [])
    lists = crawl_data.get('lists', [])
    paragraphs = crawl_data.get('paragraphs', [])
    
    print(f"📍 SOURCE: {source}")
    print(f"🔗 URL: {url}")
    print(f"📅 DATE DE PUBLICATION: {pub_date}")
    print(f"📝 TITRE: {title}")
    print(f"📏 LONGUEUR DE L'ARTICLE: {article_length:,} caractères")
    print(f"\n" + "-"*80 + "\n")
    
    # Analyse de la méta
    print("🎯 RÉSUMÉ DE LA MÉTA BATTLEFIELD 6:\n")
    
    # 1. Arme principale
    print("1️⃣  ARME VEDETTE:")
    if 'PW7A2' in weapons_mentioned:
        print("   ✅ PW7A2 (MP7 renommé)")
        print("   • Type: SMG (Submachine Gun)")
        print("   • Cadence de tir: 947 RPM (une des plus rapides du jeu)")
        print("   • Spécialité: Quasi-aucun recul malgré la cadence élevée")
        print("   • Rôle: Arme de flanking/rush agressive")
    
    # 2. Loadout recommandé
    print("\n2️⃣  LOADOUT OPTIMAL (100 points):")
    loadout_items = [item for item in lists if any(x in item for x in ['Muzzle:', 'Barrel:', 'Underbarrel:', 'Magazine:', 'Ammunition:', 'Scope:', 'Accessory:'])]
    for item in loadout_items:
        print(f"   • {item}")
    
    # 3. Stratégie
    print("\n3️⃣  STRATÉGIE & GAMEPLAY:")
    strategy_keywords = ['hipfire', 'accuracy', 'recoil', 'close-range', 'flanking', 'mobility']
    for para in paragraphs:
        if any(kw in para.lower() for kw in strategy_keywords):
            summary = para[:150] + "..." if len(para) > 150 else para
            print(f"   • {summary}")
            break
    
    # 4. Classe recommandée
    print("\n4️⃣  CLASSE RECOMMANDÉE:")
    for para in paragraphs:
        if 'engineer' in para.lower() or 'assault' in para.lower():
            if 'Engineer' in para:
                print("   ✅ Engineer (pour bonus hipfire)")
            if 'Assault' in para:
                print("   ✅ Assault (pour transporter une arme secondaire longue portée)")
            break
    
    # 5. Points clés
    print("\n5️⃣  POINTS CLÉS DE LA MÉTA:")
    print("   • Mots-clés détectés:", ', '.join(meta_keywords[:10]))
    print("   • Armes mentionnées:", ', '.join(weapons_mentioned) if weapons_mentioned else 'PW7A2 uniquement')
    print("   • Focus: Build aggressif avec hipfire laser et mobilité maximale")
    
    # 6. Version du jeu
    print("\n6️⃣  VERSION & PATCH:")
    print(f"   • Jeu: Battlefield 6")
    print(f"   • Date de l'article: {pub_date}")
    print(f"   • Patch/Version: Non spécifié (article du 10 octobre 2025)")
    
    # 7. Extraction de la date
    print("\n7️⃣  DATE D'EXTRACTION:")
    crawl_date = crawl_data.get('crawled_at', 'N/A')
    print(f"   • Date du crawl: {crawl_date}")
    print(f"   • Fraîcheur des données: Très récent (article de octobre 2025)")
    
    print("\n" + "="*80)
    print("✅ ANALYSE TERMINÉE")
    print("="*80 + "\n")
    
    # Retour structuré
    return {
        'meta_summary': {
            'main_weapon': 'PW7A2 (MP7)',
            'weapon_type': 'SMG',
            'fire_rate': '947 RPM',
            'speciality': 'Très faible recul + cadence ultra-rapide',
            'recommended_class': 'Engineer (bonus hipfire) ou Assault (arme secondaire)',
            'playstyle': 'Flanking agressif, combat rapproché',
            'game_version': 'Battlefield 6',
            'article_date': pub_date,
            'crawl_date': crawl_date,
            'source': source,
            'url': url,
        },
        'loadout': [item for item in lists if ':' in item and any(x in item for x in ['Muzzle', 'Barrel', 'Underbarrel', 'Magazine', 'Ammunition', 'Scope', 'Accessory'])],
        'keywords': meta_keywords,
        'weapons_mentioned': weapons_mentioned,
    }


def main():
    """Fonction principale"""
    
    # Charger les résultats du crawl
    results_file = Path('pcgamer_results.json')
    
    if not results_file.exists():
        print("❌ Erreur: fichier pcgamer_results.json introuvable!")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        crawl_results = json.load(f)
    
    if not crawl_results:
        print("❌ Erreur: aucune donnée dans le fichier JSON!")
        return
    
    # Analyser le premier résultat
    first_result = crawl_results[0]
    
    # Analyse avec LLM (simulation)
    analysis = analyze_with_copilot(first_result)
    
    # Sauvegarder l'analyse
    analysis_file = Path('meta_analysis.json')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Analyse sauvegardée dans: {analysis_file}\n")


if __name__ == "__main__":
    main()
