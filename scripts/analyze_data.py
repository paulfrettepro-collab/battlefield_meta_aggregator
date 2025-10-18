"""
Analyse simple des données BF6 extraites
"""

import json
from pathlib import Path
from collections import Counter


def analyze_leaderboard():
    """Analyse le fichier NDJSON"""
    
    print("\n" + "=" * 80)
    print("📊 ANALYSE BATTLEFIELD 6 LEADERBOARD")
    print("=" * 80)
    
    # Charger les données
    bronze_dir = Path("data/bronze")
    ndjson_files = sorted(bronze_dir.glob("bf6_leaderboard_*.ndjson"), reverse=True)
    
    if not ndjson_files:
        print("❌ Aucun fichier trouvé")
        return
    
    latest_file = ndjson_files[0]
    print(f"\n📂 Fichier: {latest_file.name}")
    
    players = []
    with open(latest_file, 'r') as f:
        for line in f:
            players.append(json.loads(line))
    
    print(f"📊 Joueurs: {len(players)}")
    
    # Statistiques
    print(f"\n" + "━" * 80)
    print(f"📈 TOP 10 JOUEURS")
    print(f"━" * 80)
    
    for p in players[:10]:
        rank = p['rank']
        username = p['username_hash']
        kills = p['stats'].get('kills', 0)
        print(f"   {rank:3d}. {username:20s} - {kills:>8,} kills")
    
    # Statistiques globales
    total_kills = sum(p['stats'].get('kills', 0) for p in players)
    avg_kills = total_kills / len(players)
    median_player = players[49]  # Position 50
    
    print(f"\n" + "━" * 80)
    print(f"📊 STATISTIQUES GLOBALES")
    print(f"━" * 80)
    
    print(f"\n   Total Kills (Top 100):     {total_kills:>12,}")
    print(f"   Moyenne Kills:             {avg_kills:>12,.0f}")
    print(f"   Médiane (rang 50):         {median_player['stats'].get('kills', 0):>12,}")
    print(f"   Maximum (rang 1):          {players[0]['stats'].get('kills', 0):>12,}")
    print(f"   Minimum (rang 100):        {players[-1]['stats'].get('kills', 0):>12,}")
    
    # Distribution
    print(f"\n" + "━" * 80)
    print(f"📊 DISTRIBUTION PAR TRANCHE")
    print(f"━" * 80)
    
    ranges = [
        (90000, float('inf'), "90k+"),
        (80000, 90000, "80k-90k"),
        (70000, 80000, "70k-80k"),
        (60000, 70000, "60k-70k"),
        (50000, 60000, "50k-60k"),
        (0, 50000, "<50k")
    ]
    
    for min_val, max_val, label in ranges:
        count = sum(1 for p in players if min_val <= p['stats'].get('kills', 0) < max_val)
        percent = (count / len(players)) * 100
        bar = "█" * int(percent / 2)
        print(f"   {label:>10s}: {count:3d} joueurs {bar:20s} ({percent:>5.1f}%)")
    
    print(f"\n" + "=" * 80)
    print(f"✅ Analyse terminée")
    print(f"=" * 80 + "\n")


if __name__ == "__main__":
    analyze_leaderboard()
