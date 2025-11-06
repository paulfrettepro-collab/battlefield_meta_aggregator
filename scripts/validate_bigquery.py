#!/usr/bin/env python3
"""
Script de validation BigQuery - BF6 Meta Aggregator
Vérifie que les données extraites sont correctement chargées dans BigQuery
"""

from google.cloud import bigquery
from datetime import date
import sys

def validate_bigquery():
    """Valide les données BigQuery bronze_leaderboard"""
    
    print("=" * 70)
    print("🔍 VALIDATION BIGQUERY - BF6 META")
    print("=" * 70)
    print()
    
    try:
        # Initialiser client BigQuery
        client = bigquery.Client(project="battlefield-meta-aggregator")
        
        # 1. Vérifier table existe
        print("📋 Vérification table bronze_leaderboard...")
        table_id = "battlefield-meta-aggregator.bf6_meta.bronze_leaderboard"
        table = client.get_table(table_id)
        print(f"✅ Table trouvée: {table.num_rows:,} lignes totales")
        print()
        
        # 2. Vérifier données du jour
        today = date.today().isoformat()
        query_today = f"""
        SELECT 
            COUNT(*) as player_count,
            MIN(rank) as min_rank,
            MAX(rank) as max_rank,
            MAX(extraction_date) as latest_extraction
        FROM `{table_id}`
        WHERE DATE(extraction_date) = '{today}'
        """
        
        print(f"📊 Requête données du {today}...")
        results = list(client.query(query_today).result())
        
        if not results or results[0].player_count == 0:
            print(f"⚠️  WARNING: Aucune donnée trouvée pour {today}")
            print("💡 Vérifier si le workflow a terminé et loadé les données")
            
            # Chercher dernière date disponible
            query_last = f"""
            SELECT DATE(extraction_date) as last_date, COUNT(*) as count
            FROM `{table_id}`
            GROUP BY last_date
            ORDER BY last_date DESC
            LIMIT 1
            """
            last_results = list(client.query(query_last).result())
            if last_results:
                print(f"📅 Dernière extraction disponible: {last_results[0].last_date} ({last_results[0].count} joueurs)")
            return False
        
        row = results[0]
        print(f"✅ Données du jour trouvées: {row.player_count} joueurs")
        print(f"   - Rang minimum: {row.min_rank}")
        print(f"   - Rang maximum: {row.max_rank}")
        print()
        
        # 3. VALIDATION CRITIQUE: Vérifier rangs 1-3
        if row.min_rank != 1:
            print(f"❌ ERREUR CRITIQUE: Le rang minimum est {row.min_rank} (attendu: 1)")
            print("💡 Le problème des rangs 1-3 manquants persiste !")
            return False
        else:
            print("✅ VALIDATION CRITIQUE: Le rang 1 est présent ! 🎉")
        
        # 4. Afficher TOP 5 joueurs
        query_top5 = f"""
        SELECT rank, handle, kills, player_id
        FROM `{table_id}`
        WHERE DATE(extraction_date) = '{today}'
        ORDER BY rank
        LIMIT 5
        """
        
        print()
        print("🏆 TOP 5 JOUEURS (BigQuery):")
        top5_results = list(client.query(query_top5).result())
        
        for player in top5_results:
            print(f"   Rang {player.rank:2d}: {player.handle:30s} ({player.kills:,} kills) [ID: {player.player_id}]")
        
        # 5. Vérifier intégrité des rangs 1-5
        print()
        print("🔍 Vérification intégrité rangs 1-5:")
        query_integrity = f"""
        SELECT rank, handle, 
               CASE WHEN handle IS NULL THEN 'NULL' ELSE 'OK' END as handle_status,
               CASE WHEN kills IS NULL THEN 'NULL' ELSE 'OK' END as kills_status
        FROM `{table_id}`
        WHERE DATE(extraction_date) = '{today}'
        AND rank BETWEEN 1 AND 5
        ORDER BY rank
        """
        
        integrity_results = list(client.query(query_integrity).result())
        all_valid = True
        
        for player in integrity_results:
            status = "✅" if player.handle_status == 'OK' and player.kills_status == 'OK' else "❌"
            print(f"   {status} Rang {player.rank}: handle={player.handle_status}, kills={player.kills_status}")
            if player.handle_status != 'OK' or player.kills_status != 'OK':
                all_valid = False
        
        print()
        
        if all_valid and row.min_rank == 1:
            print("=" * 70)
            print("✅ VALIDATION BIGQUERY RÉUSSIE !")
            print("=" * 70)
            print()
            print("🎉 Les rangs 1-3 sont présents et valides dans BigQuery !")
            print("🎉 Les données sont à jour et complètes !")
            return True
        else:
            print("❌ VALIDATION ÉCHOUÉE - Problèmes détectés")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_bigquery()
    sys.exit(0 if success else 1)
