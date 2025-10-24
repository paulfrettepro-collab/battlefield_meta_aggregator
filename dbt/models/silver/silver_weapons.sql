-- models/silver/silver_weapons.sql

{{ config(
    materialized='table',
    description='Top 3 armes par joueur avec métriques nettoyées et normalisées'
) }}

WITH latest_extraction AS (
    SELECT MAX(DATE(extraction_date)) AS max_date
    FROM {{ source('bronze', 'bf6_top_weapons_raw') }}
),

cleaned_weapons AS (
    SELECT
        -- Identifiants joueur
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        
        -- Arme
        UPPER(TRIM(weapon_name)) AS weapon_name,
        UPPER(TRIM(COALESCE(weapon_type, 'Unknown'))) AS weapon_type,
        
        -- Métriques principales (MVP)
        CAST(kills AS INT64) AS weapon_kills,
        CAST(weapon_rank AS INT64) AS weapon_rank_for_player,
        
        -- Métriques secondaires (disponibles mais pas encore utilisées dans MVP)
        CAST(time_played AS STRING) AS time_played,
        CAST(damage AS INT64) AS total_damage,
        
        -- Conversion accuracy "23.5%" → 0.235 (FLOAT64)
        CASE 
            WHEN accuracy IS NOT NULL AND accuracy != ''
            THEN CAST(REPLACE(accuracy, '%', '') AS FLOAT64) / 100
            ELSE NULL
        END AS accuracy,
        
        -- Conversion headshot_pct "18.2%" → 0.182 (FLOAT64)
        CASE 
            WHEN headshot_pct IS NOT NULL AND headshot_pct != ''
            THEN CAST(REPLACE(headshot_pct, '%', '') AS FLOAT64) / 100
            ELSE NULL
        END AS headshot_pct,
        
        -- Métadonnées
        CAST(extraction_date AS TIMESTAMP) AS extracted_at,
        DATE(extraction_date) AS extraction_date,
        
        -- Flags de qualité
        CASE 
            WHEN kills > 0 THEN TRUE 
            ELSE FALSE 
        END AS is_valid_weapon
        
    FROM {{ source('bronze', 'bf6_top_weapons_raw') }}
    WHERE DATE(extraction_date) = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_weapons
WHERE is_valid_weapon = TRUE
ORDER BY player_handle, weapon_rank_for_player
