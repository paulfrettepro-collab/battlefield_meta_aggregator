#!/usr/bin/env python3
"""
Upload NDJSON files to BigQuery avec schéma correct
"""
from google.cloud import bigquery
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
PROJECT_ID = "battlefield-meta-aggregator"
DATASET_ID = "bf6_meta"

# Vérifier que les credentials sont configurées
if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    print("❌ GOOGLE_APPLICATION_CREDENTIALS non trouvé dans .env")
    exit(1)

client = bigquery.Client(project=PROJECT_ID)

print("=" * 80)
print("📤 UPLOAD BIGQUERY")
print("=" * 80)

# ============================================================================
# 1. TABLE LEADERBOARD
# ============================================================================
print("\n1️⃣  Upload bf6_leaderboard_raw")
print("-" * 80)

leaderboard_file = Path("data/bronze/tracker_gg/leaderboard/bf6_leaderboard_2025-10-24_213134.ndjson")

# Schéma leaderboard (simple, pas d'ARRAY)
leaderboard_schema = [
    bigquery.SchemaField("handle", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("rank", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("kills", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("extraction_date", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("url_source", "STRING", mode="NULLABLE"),
]

table_id = f"{PROJECT_ID}.{DATASET_ID}.bf6_leaderboard_raw"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    schema=leaderboard_schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    autodetect=False,
)

with open(leaderboard_file, "rb") as source_file:
    load_job = client.load_table_from_file(
        source_file,
        table_id,
        job_config=job_config,
    )

load_job.result()  # Wait for completion
print(f"✅ {load_job.output_rows} rows loaded into {table_id}")

# ============================================================================
# 2. TABLE WEAPONS (avec UNNEST en Python avant upload)
# ============================================================================
print("\n2️⃣  Upload bf6_top_weapons_raw (UNNEST)")
print("-" * 80)

weapons_file = Path("data/bronze/tracker_gg/top_weapons/bf6_top_weapons_2025-10-24_223302.ndjson")

# Schéma weapons (dénormalisé, sans ARRAY)
weapons_schema = [
    bigquery.SchemaField("handle", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("weapon_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("weapon_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("weapon_rank", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("kills", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("time_played", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("damage", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("accuracy", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("headshot_pct", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("total_weapons_found", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("extraction_status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("extraction_date", "TIMESTAMP", mode="REQUIRED"),
]

# UNNEST en Python: Transformer ARRAY → lignes individuelles
unnested_rows = []
with open(weapons_file, 'r') as f:
    for line in f:
        player = json.loads(line)
        
        # Pour chaque arme du joueur
        for weapon in player.get('top_weapons', []):
            row = {
                'handle': player['handle'],
                'player_id': player['player_id'],
                'weapon_name': weapon['weapon_name'],
                'weapon_type': weapon.get('weapon_type'),
                'weapon_rank': weapon['rank'],
                'kills': weapon['kills'],
                'time_played': weapon.get('time_played'),
                'damage': weapon.get('damage'),
                'accuracy': weapon.get('accuracy'),
                'headshot_pct': weapon.get('headshot_pct'),
                'total_weapons_found': player.get('total_weapons_found'),
                'extraction_status': player['status'],
                'extraction_date': player['extraction_date'],
            }
            unnested_rows.append(row)

print(f"📊 {len(unnested_rows)} armes extraites (97 players × 3 weapons)")

# Upload vers BigQuery
table_id = f"{PROJECT_ID}.{DATASET_ID}.bf6_top_weapons_raw"

job_config = bigquery.LoadJobConfig(
    schema=weapons_schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

load_job = client.load_table_from_json(
    unnested_rows,
    table_id,
    job_config=job_config,
)

load_job.result()  # Wait for completion
print(f"✅ {load_job.output_rows} rows loaded into {table_id}")

# ============================================================================
# 3. VÉRIFICATION
# ============================================================================
print("\n3️⃣  Vérification")
print("-" * 80)

# Count leaderboard
query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.bf6_leaderboard_raw`"
result = list(client.query(query).result())
print(f"✅ bf6_leaderboard_raw: {result[0]['cnt']} joueurs")

# Count weapons
query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.bf6_top_weapons_raw`"
result = list(client.query(query).result())
print(f"✅ bf6_top_weapons_raw: {result[0]['cnt']} armes")

# Top 3 armes globales
print("\n🏆 Top 3 armes (preview):")
query = f"""
SELECT 
    weapon_name,
    weapon_type,
    SUM(kills) as total_kills,
    COUNT(DISTINCT handle) as nb_players
FROM `{PROJECT_ID}.{DATASET_ID}.bf6_top_weapons_raw`
GROUP BY weapon_name, weapon_type
ORDER BY total_kills DESC
LIMIT 3
"""
results = client.query(query).result()
for i, row in enumerate(results, 1):
    print(f"  {i}. {row['weapon_name']} ({row['weapon_type']}): {row['total_kills']:,} kills ({row['nb_players']} players)")

print("\n" + "=" * 80)
print("🎉 Upload BigQuery terminé !")
print("=" * 80)
print("\n💡 Prochaine étape: DBT transformations (Phase 3)")
