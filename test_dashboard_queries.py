"""
Test script to verify BigQuery queries work for Streamlit dashboard
"""

from google.cloud import bigquery
import os

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'config/bigquery-key.json'

# Create client
client = bigquery.Client(project='battlefield-meta-aggregator')

print("=" * 60)
print("TESTING BIGQUERY QUERIES FOR DASHBOARD")
print("=" * 60)

# Test 1: Check gold_top_weapons_global
print("\n1️⃣  Testing gold_top_weapons_global...")
query1 = """
    SELECT 
        global_rank,
        weapon_name,
        total_kills,
        nb_players_using,
        avg_kills_per_player,
        avg_accuracy
    FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
    ORDER BY global_rank
    LIMIT 5
"""

try:
    result1 = client.query(query1).to_dataframe()
    print(f"✅ SUCCESS: {len(result1)} rows returned")
    print(result1[['global_rank', 'weapon_name', 'total_kills', 'nb_players_using']].to_string(index=False))
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Check gold_top_weapons_by_type
print("\n2️⃣  Testing gold_top_weapons_by_type...")
query2 = """
    SELECT 
        weapon_rank,
        weapon_name,
        total_kills,
        nb_players_using
    FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_by_type`
    ORDER BY weapon_rank
    LIMIT 5
"""

try:
    result2 = client.query(query2).to_dataframe()
    print(f"✅ SUCCESS: {len(result2)} rows returned")
    print(result2.to_string(index=False))
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Check gold_player_rankings
print("\n3️⃣  Testing gold_player_rankings...")
query3 = """
    SELECT 
        player_handle,
        player_rank,
        player_total_kills,
        main_weapon
    FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_player_rankings`
    ORDER BY player_rank
    LIMIT 5
"""

try:
    result3 = client.query(query3).to_dataframe()
    print(f"✅ SUCCESS: {len(result3)} rows returned")
    print(result3.to_string(index=False))
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Check last extraction date
print("\n4️⃣  Testing last extraction date...")
query4 = """
    SELECT MAX(extraction_date) AS last_date
    FROM `battlefield-meta-aggregator.bf6_meta.bronze_leaderboard`
"""

try:
    result4 = client.query(query4).to_dataframe()
    print(f"✅ SUCCESS: Last extraction date = {result4['last_date'].iloc[0]}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
