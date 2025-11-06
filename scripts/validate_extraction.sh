#!/bin/bash
# Script de validation automatique des extractions BF6
# Usage: ./validate_extraction.sh <path_to_ndjson_leaderboard_file>

set -e

LEADERBOARD_FILE="$1"

if [ -z "$LEADERBOARD_FILE" ]; then
    echo "❌ Usage: $0 <path_to_ndjson_leaderboard_file>"
    exit 1
fi

if [ ! -f "$LEADERBOARD_FILE" ]; then
    echo "❌ Fichier non trouvé: $LEADERBOARD_FILE"
    exit 1
fi

echo "=================================="
echo "🔍 VALIDATION EXTRACTION BF6 META"
echo "=================================="
echo "📄 Fichier: $LEADERBOARD_FILE"
echo ""

# 1. Vérifier nombre de lignes
PLAYER_COUNT=$(wc -l < "$LEADERBOARD_FILE")
echo "✅ Joueurs extraits: $PLAYER_COUNT"

if [ "$PLAYER_COUNT" -lt 45 ]; then
    echo "❌ ERREUR: Moins de 45 joueurs extraits (attendu: 50)"
    exit 1
fi

# 2. Vérifier que le fichier commence au rang 1
FIRST_RANK=$(head -1 "$LEADERBOARD_FILE" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['rank'])")
echo "✅ Premier rang: $FIRST_RANK"

if [ "$FIRST_RANK" != "1" ]; then
    echo "❌ ERREUR CRITIQUE: Le fichier commence au rang $FIRST_RANK (attendu: 1)"
    echo "💡 Le problème des rangs 1-3 manquants persiste !"
    exit 1
fi

# 3. Afficher les 3 premiers joueurs
echo ""
echo "🏆 TOP 3 JOUEURS:"
head -3 "$LEADERBOARD_FILE" | python3 -c "
import sys, json
for line in sys.stdin:
    data = json.loads(line)
    print(f\"  Rang {data['rank']:2d}: {data['handle']:30s} ({data['kills']:,} kills)\")
"

# 4. Vérifier date d'extraction
EXTRACTION_DATE=$(head -1 "$LEADERBOARD_FILE" | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['extraction_date'][:10])")
TODAY=$(date +%Y-%m-%d)
echo ""
echo "✅ Date extraction: $EXTRACTION_DATE"

if [ "$EXTRACTION_DATE" != "$TODAY" ]; then
    echo "⚠️  WARNING: Données pas du jour (attendu: $TODAY)"
else
    echo "✅ Données du jour !"
fi

# 5. Vérifier structure données rangs 1-5
echo ""
echo "🔍 Validation structure rangs 1-5:"
head -5 "$LEADERBOARD_FILE" | python3 -c "
import sys, json

required_fields = ['rank', 'handle', 'player_id', 'kills', 'extraction_date']
all_valid = True

for i, line in enumerate(sys.stdin, 1):
    data = json.loads(line)
    missing = [f for f in required_fields if f not in data or data[f] is None]
    
    if missing:
        print(f\"  ❌ Rang {i}: Champs manquants: {missing}\")
        all_valid = False
    else:
        print(f\"  ✅ Rang {i}: Structure valide ({len(data)} champs)\")

if all_valid:
    print(\"\n✅ TOUS LES RANGS 1-5 SONT VALIDES !\")
else:
    print(\"\n❌ ERREURS DE STRUCTURE DÉTECTÉES\")
    sys.exit(1)
"

echo ""
echo "=================================="
echo "✅ VALIDATION RÉUSSIE !"
echo "=================================="
echo "📊 Résumé:"
echo "  - Joueurs: $PLAYER_COUNT"
echo "  - Premier rang: $FIRST_RANK ✅"
echo "  - Date: $EXTRACTION_DATE"
echo "  - Structure: Valide ✅"
echo ""
echo "🎉 Les rangs 1-3 sont présents et valides !"
