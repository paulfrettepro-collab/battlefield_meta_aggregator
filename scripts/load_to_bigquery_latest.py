#!/usr/bin/env python3
"""
Script de chargement BigQuery pour les données BF6 Meta
Charge les derniers fichiers leaderboard + weapons dans BigQuery
"""
from google.cloud import bigquery
from pathlib import Path
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "battlefield-meta-aggregator")
DATASET_ID = os.getenv("GCP_DATASET_ID", "bf6_meta")

# Vérifier credentials
if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    print("❌ GOOGLE_APPLICATION_CREDENTIALS non trouvé dans .env")
    print("💡 Configurez la variable dans .env : GOOGLE_APPLICATION_CREDENTIALS=config/bigquery-key.json")
    exit(1)

# Créer client BigQuery
try:
    client = bigquery.Client(project=PROJECT_ID)
    print(f"✅ Connexion BigQuery réussie (projet: {PROJECT_ID})")
except Exception as e:
    print(f"❌ Erreur connexion BigQuery: {e}")
    exit(1)

print("\n" + "=" * 80)
print("📤 CHARGEMENT BIGQUERY - BF6 META AGGREGATOR")
print("=" * 80)

# ============================================================================
# FONCTION UTILITAIRE : Trouver le fichier le plus récent
# ============================================================================
def find_latest_file(directory: Path, pattern: str) -> Path:
    """Trouve le fichier le plus récent matching le pattern"""
    files = list(directory.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé: {directory}/{pattern}")
    
    # Trier par date de modification (plus récent en premier)
    latest = max(files, key=lambda f: f.stat().st_mtime)
    return latest

# ============================================================================
# 1. CHARGEMENT LEADERBOARD
# ============================================================================
print("\n1️⃣  CHARGEMENT LEADERBOARD")
print("-" * 80)

# Trouver le fichier le plus récent
leaderboard_dir = Path("data/bronze/tracker_gg/leaderboard")
leaderboard_file = find_latest_file(leaderboard_dir, "bf6_leaderboard_*.ndjson")

print(f"📁 Fichier: {leaderboard_file.name}")
print(f"📅 Modifié: {datetime.fromtimestamp(leaderboard_file.stat().st_mtime)}")

# Compter les lignes
with open(leaderboard_file, 'r') as f:
    num_players = sum(1 for _ in f)
print(f"👥 Joueurs: {num_players}")

# Schéma leaderboard
leaderboard_schema = [
    bigquery.SchemaField("handle", "STRING", mode="REQUIRED", description="Player username"),
    bigquery.SchemaField("player_id", "STRING", mode="REQUIRED", description="Tracker.gg player ID"),
    bigquery.SchemaField("rank", "INTEGER", mode="REQUIRED", description="Leaderboard rank"),
    bigquery.SchemaField("kills", "INTEGER", mode="REQUIRED", description="Total kills"),
    bigquery.SchemaField("location", "STRING", mode="NULLABLE", description="Player location/avatar"),
    bigquery.SchemaField("matches_played", "INTEGER", mode="NULLABLE", description="Total matches played"),
    bigquery.SchemaField("extraction_date", "TIMESTAMP", mode="REQUIRED", description="Data extraction timestamp"),
]

# Table cible
table_id = f"{PROJECT_ID}.{DATASET_ID}.bronze_leaderboard"

# IMPORTANT: Supprimer les anciennes données AVANT de charger les nouvelles
# Pour éviter les doublons et garder seulement les 3 dernières extractions
print("🗑️  Nettoyage données anciennes (garde 3 dernières extractions)...")
cleanup_query = f"""
DELETE FROM `{table_id}`
WHERE DATE(extraction_date) NOT IN (
    SELECT DATE(extraction_date) as ext_date
    FROM `{table_id}`
    GROUP BY ext_date
    ORDER BY ext_date DESC
    LIMIT 3
)
"""
try:
    cleanup_job = client.query(cleanup_query)
    cleanup_job.result()
    print(f"✅ Nettoyage effectué")
except Exception as e:
    print(f"⚠️  Nettoyage ignoré (table peut être vide): {e}")

# Configuration du job
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    schema=leaderboard_schema,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Ajouter aux données existantes
    autodetect=False,
    max_bad_records=0,  # Aucune erreur tolérée
)

# Charger les données
print(f"⬆️  Chargement vers: {table_id}")
with open(leaderboard_file, "rb") as source_file:
    load_job = client.load_table_from_file(
        source_file,
        table_id,
        job_config=job_config,
    )

# Attendre la fin du job
try:
    load_job.result()
    print(f"✅ {load_job.output_rows} lignes chargées avec succès")
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    if load_job.errors:
        for error in load_job.errors:
            print(f"   • {error}")
    exit(1)

# ============================================================================
# 2. CHARGEMENT WEAPONS (avec UNNEST)
# ============================================================================
print("\n2️⃣  CHARGEMENT WEAPONS (dénormalisation)")
print("-" * 80)

# Trouver le fichier le plus récent
weapons_dir = Path("data/bronze/tracker_gg/weapons")
weapons_file = find_latest_file(weapons_dir, "bf6_weapons_*.ndjson")

print(f"📁 Fichier: {weapons_file.name}")
print(f"📅 Modifié: {datetime.fromtimestamp(weapons_file.stat().st_mtime)}")

# UNNEST en Python: Transformer ARRAY → lignes individuelles
unnested_rows = []
error_count = 0

with open(weapons_file, 'r') as f:
    for line_num, line in enumerate(f, 1):
        try:
            player = json.loads(line)
            
            # Vérifier si extraction réussie
            if not player.get('extraction_success', False):
                print(f"⚠️  Ligne {line_num}: Extraction échouée pour {player.get('player_handle', 'Unknown')}")
                error_count += 1
                continue
            
            # Pour chaque arme du joueur
            for rank, weapon in enumerate(player.get('weapons', []), 1):
                row = {
                    'player_handle': player['player_handle'],
                    'player_id': player['player_id'],
                    'player_rank': player['rank'],
                    'player_kills': player['kills'],
                    'weapon_name': weapon['weapon_name'],
                    'weapon_rank': rank,  # 1, 2, ou 3
                    'weapon_kills': weapon['kills'],
                    'weapon_accuracy': weapon.get('accuracy'),
                    'extraction_date': player['snapshot_utc'],
                }
                unnested_rows.append(row)
                
        except Exception as e:
            print(f"⚠️  Ligne {line_num}: Erreur parsing - {e}")
            error_count += 1

print(f"📊 {len(unnested_rows)} armes extraites")
if error_count > 0:
    print(f"⚠️  {error_count} erreurs détectées")

# Schéma weapons (dénormalisé)
weapons_schema = [
    bigquery.SchemaField("player_handle", "STRING", mode="REQUIRED", description="Player username"),
    bigquery.SchemaField("player_id", "STRING", mode="REQUIRED", description="Tracker.gg player ID"),
    bigquery.SchemaField("player_rank", "INTEGER", mode="REQUIRED", description="Player leaderboard rank"),
    bigquery.SchemaField("player_kills", "INTEGER", mode="REQUIRED", description="Player total kills"),
    bigquery.SchemaField("weapon_name", "STRING", mode="REQUIRED", description="Weapon name"),
    bigquery.SchemaField("weapon_rank", "INTEGER", mode="REQUIRED", description="Weapon rank for player (1-3)"),
    bigquery.SchemaField("weapon_kills", "INTEGER", mode="REQUIRED", description="Kills with this weapon"),
    bigquery.SchemaField("weapon_accuracy", "FLOAT", mode="NULLABLE", description="Weapon accuracy percentage"),
    bigquery.SchemaField("extraction_date", "TIMESTAMP", mode="REQUIRED", description="Data extraction timestamp"),
]

# Table cible
table_id = f"{PROJECT_ID}.{DATASET_ID}.bronze_weapons"

# IMPORTANT: Supprimer les anciennes données AVANT de charger les nouvelles
print("🗑️  Nettoyage données anciennes (garde 3 dernières extractions)...")
cleanup_query = f"""
DELETE FROM `{table_id}`
WHERE DATE(extraction_date) NOT IN (
    SELECT DATE(extraction_date) as ext_date
    FROM `{table_id}`
    GROUP BY ext_date
    ORDER BY ext_date DESC
    LIMIT 3
)
"""
try:
    cleanup_job = client.query(cleanup_query)
    cleanup_job.result()
    print(f"✅ Nettoyage effectué")
except Exception as e:
    print(f"⚠️  Nettoyage ignoré (table peut être vide): {e}")

# Configuration du job
job_config = bigquery.LoadJobConfig(
    schema=weapons_schema,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Ajouter aux données existantes
)

# Charger les données
print(f"⬆️  Chargement vers: {table_id}")
load_job = client.load_table_from_json(
    unnested_rows,
    table_id,
    job_config=job_config,
)

# Attendre la fin du job
try:
    load_job.result()
    print(f"✅ {load_job.output_rows} lignes chargées avec succès")
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    if load_job.errors:
        for error in load_job.errors:
            print(f"   • {error}")
    exit(1)

# ============================================================================
# 3. VÉRIFICATION
# ============================================================================
print("\n3️⃣  VÉRIFICATION")
print("-" * 80)

# Count leaderboard
query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.bronze_leaderboard`"
result = list(client.query(query).result())
print(f"✅ bronze_leaderboard: {result[0]['cnt']} joueurs au total")

# Count weapons
query = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{DATASET_ID}.bronze_weapons`"
result = list(client.query(query).result())
print(f"✅ bronze_weapons: {result[0]['cnt']} armes au total")

# Top 3 armes globales (dernière extraction)
print("\n🏆 TOP 3 ARMES (dernière extraction):")
query = f"""
SELECT 
    weapon_name,
    COUNT(DISTINCT player_handle) as num_players,
    SUM(weapon_kills) as total_kills,
    ROUND(AVG(weapon_accuracy), 1) as avg_accuracy
FROM `{PROJECT_ID}.{DATASET_ID}.bronze_weapons`
WHERE DATE(extraction_date) = CURRENT_DATE()
GROUP BY weapon_name
ORDER BY total_kills DESC
LIMIT 3
"""
try:
    results = client.query(query).result()
    for i, row in enumerate(results, 1):
        print(f"   {i}. {row['weapon_name']:20} | {row['num_players']:2} joueurs | {row['total_kills']:,} kills | {row['avg_accuracy']}% accuracy")
except Exception as e:
    print(f"   ⚠️  Requête échouée: {e}")

print("\n" + "=" * 80)
print("✅ CHARGEMENT TERMINÉ")
print("=" * 80)
print(f"\n💡 Prochaine étape: cd dbt && dbt run && dbt test")
