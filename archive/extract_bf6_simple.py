"""
Extraction simple du leaderboard BF6 avec requests + BeautifulSoup

Ce script contourne les limitations de Scrapy en utilisant une approche plus directe
avec des headers qui simulent un navigateur réel.
"""

import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime
from pathlib import Path
import time


def get_realistic_headers():
    """Headers qui simulent un vrai navigateur Chrome sur Mac"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }


def anonymize_username(username):
    """Anonymise un pseudo via hash SHA256"""
    if not username:
        return "unknown"
    hash_obj = hashlib.sha256(username.encode())
    return f"player_{hash_obj.hexdigest()[:8]}"


def extract_leaderboard():
    """Extrait le leaderboard avec une approche progressive"""
    
    print("\n" + "=" * 80)
    print("🎮 BATTLEFIELD 6 - EXTRACTION LEADERBOARD (MÉTHODE DIRECTE)")
    print("=" * 80)
    
    url = "https://tracker.gg/bf6/leaderboards"
    print(f"\n📡 URL cible: {url}")
    print(f"⏳ Téléchargement de la page...\n")
    
    try:
        # Session pour persistance des cookies
        session = requests.Session()
        
        # Première requête
        response = session.get(url, headers=get_realistic_headers(), timeout=15)
        
        print(f"✅ Statut HTTP: {response.status_code}")
        print(f"📄 Taille HTML: {len(response.text)} caractères")
        print(f"🔑 Cookies reçus: {len(response.cookies)} cookies")
        
        if response.status_code == 403:
            print("\n⚠️  Erreur 403 - Le site bloque notre requête")
            print("💡 Possible que le site utilise JavaScript pour charger le leaderboard")
            print("💡 Solutions:")
            print("   1. Utiliser Selenium/Playwright pour navigateur headless")
            print("   2. Reverse engineer l'API utilisée par le site")
            print("   3. Contacter Tracker.gg pour accès API officiel")
            return None
        
        response.raise_for_status()
        
        # Sauvegarder le HTML
        html_file = Path('data/exploration/leaderboard_direct.html')
        html_file.parent.mkdir(parents=True, exist_ok=True)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"💾 HTML sauvegardé: {html_file}")
        
        # Parser avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Analyser la structure
        print("\n" + "━" * 80)
        print("🔍 ANALYSE DE LA STRUCTURE")
        print("━" * 80)
        
        # Chercher le titre de la page
        title = soup.find('title')
        print(f"\n📌 Titre de la page: {title.string if title else 'Non trouvé'}")
        
        # Chercher les scripts JSON (Next.js utilise souvent __NEXT_DATA__)
        next_data = soup.find('script', {'id': '__NEXT_DATA__'})
        if next_data:
            print(f"\n🎯 Trouvé __NEXT_DATA__ (Next.js) - {len(next_data.string)} caractères")
            try:
                data = json.loads(next_data.string)
                
                # Sauvegarder le JSON complet
                json_file = Path('data/exploration/next_data.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"💾 JSON sauvegardé: {json_file}")
                
                # Explorer la structure JSON
                print(f"\n📦 Structure JSON:")
                if 'props' in data:
                    print(f"   ├── props")
                    if 'pageProps' in data['props']:
                        pageProps = data['props']['pageProps']
                        print(f"   │   ├── pageProps")
                        for key in pageProps.keys():
                            print(f"   │   │   ├── {key}")
                        
                        # Chercher les données du leaderboard
                        if 'data' in pageProps:
                            leaderboard_data = pageProps['data']
                            if isinstance(leaderboard_data, dict):
                                if 'entries' in leaderboard_data:
                                    entries = leaderboard_data['entries']
                                    print(f"\n🎉 LEADERBOARD TROUVÉ ! {len(entries)} joueurs")
                                    return extract_from_json(entries)
                                elif 'players' in leaderboard_data:
                                    players = leaderboard_data['players']
                                    print(f"\n🎉 LEADERBOARD TROUVÉ ! {len(players)} joueurs")
                                    return extract_from_json(players)
                        
                        # Exploration récursive
                        leaderboard = find_leaderboard_in_json(pageProps)
                        if leaderboard:
                            print(f"\n🎉 LEADERBOARD TROUVÉ (recherche récursive) ! {len(leaderboard)} joueurs")
                            return extract_from_json(leaderboard)
                
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON: {e}")
        
        # Si pas de __NEXT_DATA__, chercher dans le HTML
        print("\n⚠️  __NEXT_DATA__ non trouvé ou ne contient pas le leaderboard")
        print("🔍 Recherche dans la structure HTML...")
        
        # Chercher des patterns de tableau
        tables = soup.find_all(['table', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['table', 'leaderboard', 'list', 'rank']
        ))
        print(f"\n📊 Conteneurs trouvés: {len(tables)}")
        
        for i, table in enumerate(tables[:3], 1):
            classes = ' '.join(table.get('class', []))
            print(f"   [{i}] {table.name} - Classes: {classes[:80]}")
        
        # Afficher les 500 premiers caractères du body
        body = soup.find('body')
        if body:
            body_text = body.get_text()[:500]
            print(f"\n📝 Début du contenu (500 premiers caractères):")
            print(f"   {body_text.strip()}")
        
        print(f"\n💡 Pour continuer:")
        print(f"   1. Ouvrir {html_file} dans un navigateur")
        print(f"   2. Ouvrir DevTools (F12) et chercher 'leaderboard' dans le HTML")
        print(f"   3. Identifier les sélecteurs CSS corrects")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
        return None


def find_leaderboard_in_json(data, depth=0):
    """Recherche récursive du leaderboard dans un objet JSON"""
    if depth > 15:
        return None
    
    if isinstance(data, dict):
        # Chercher des clés évidentes
        for key in ['leaderboard', 'entries', 'players', 'data', 'items', 'results']:
            if key in data:
                value = data[key]
                if isinstance(value, list) and len(value) > 0:
                    # Vérifier si ça ressemble à des données de joueurs
                    first = value[0]
                    if isinstance(first, dict) and any(k in first for k in ['username', 'rank', 'player', 'name', 'displayName']):
                        return value
        
        # Recherche récursive
        for value in data.values():
            result = find_leaderboard_in_json(value, depth + 1)
            if result:
                return result
    
    elif isinstance(data, list) and len(data) > 0:
        first = data[0]
        if isinstance(first, dict) and any(k in first for k in ['username', 'rank', 'player', 'name', 'displayName']):
            return data
    
    return None


def extract_from_json(entries):
    """Extrait les données depuis la liste JSON"""
    players = []
    
    print(f"\n" + "━" * 80)
    print(f"📊 EXTRACTION DES DONNÉES")
    print(f"━" * 80)
    
    for i, entry in enumerate(entries[:100], 1):  # Limiter à 100
        try:
            # Tentative d'extraction des champs communs
            username = (
                entry.get('username') or
                entry.get('displayName') or
                entry.get('name') or
                entry.get('player', {}).get('username') or
                entry.get('player', {}).get('displayName') or
                'unknown'
            )
            
            rank = entry.get('rank') or entry.get('position') or i
            
            # Stats diverses
            stats = {
                'kills': entry.get('kills') or entry.get('stats', {}).get('kills'),
                'deaths': entry.get('deaths') or entry.get('stats', {}).get('deaths'),
                'kd': entry.get('kd') or entry.get('stats', {}).get('kd'),
                'score': entry.get('score') or entry.get('stats', {}).get('score'),
            }
            
            # Filtrer les None
            stats = {k: v for k, v in stats.items() if v is not None}
            
            player = {
                'extraction_date': datetime.now().isoformat(),
                'rank': rank,
                'username_original': username,
                'username_hash': anonymize_username(username),
                'stats': stats,
                'source_url': 'https://tracker.gg/bf6/leaderboards',
                'extraction_method': 'json_extraction'
            }
            
            players.append(player)
            
            if i <= 5:  # Afficher les 5 premiers
                print(f"   [{rank:3d}] {username:20s} → {player['username_hash']}")
                if stats:
                    print(f"        Stats: {stats}")
        
        except Exception as e:
            print(f"   ⚠️  Erreur joueur {i}: {e}")
    
    # Sauvegarder
    output_dir = Path('data/bronze')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"bf6_leaderboard_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.ndjson"
    output_file = output_dir / filename
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for player in players:
            f.write(json.dumps(player) + '\n')
    
    print(f"\n💾 Résultats sauvegardés: {output_file}")
    print(f"📊 Nombre de joueurs: {len(players)}")
    
    return players


if __name__ == "__main__":
    print("\n🎮" * 40)
    print("   BATTLEFIELD 6 - EXTRACTION LEADERBOARD")
    print("🎮" * 40)
    
    players = extract_leaderboard()
    
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 80)
    
    if players:
        print(f"\n✅ SUCCESS ! {len(players)} joueurs extraits")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Fichier: data/bronze/bf6_leaderboard_*.ndjson")
        print(f"\n💡 Prochaine étape: Upload vers MinIO")
    else:
        print(f"\n⚠️  Extraction incomplète")
        print(f"📂 Fichiers d'analyse disponibles:")
        print(f"   - data/exploration/leaderboard_direct.html")
        print(f"   - data/exploration/next_data.json (si trouvé)")
        print(f"\n💡 Analyser ces fichiers pour identifier la structure des données")
    
    print("=" * 80 + "\n")
