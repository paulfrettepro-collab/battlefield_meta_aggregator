-- models/silver/silver_weapons.sql

{{ config(
    materialized='table',
    description='Top 3 armes par joueur avec métriques nettoyées et normalisées'
) }}

WITH latest_extraction AS (
    SELECT MAX(DATE(extraction_date)) AS max_date
    FROM {{ source('bronze', 'bronze_weapons') }}
),

cleaned_weapons AS (
    SELECT
        -- Identifiants joueur
        TRIM(player_handle) AS player_handle,
        TRIM(player_id) AS player_id,
        CAST(player_rank AS INT64) AS player_rank,
        CAST(player_kills AS INT64) AS player_total_kills,
        
        -- Arme
        UPPER(TRIM(weapon_name)) AS weapon_name,
        
        -- Métriques principales
        CAST(weapon_kills AS INT64) AS weapon_kills,
        CAST(weapon_rank AS INT64) AS weapon_rank_for_player,
        
        -- Accuracy (déjà en FLOAT dans bronze)
        CAST(weapon_accuracy AS FLOAT64) / 100 AS accuracy,
        
        -- Métadonnées
        CAST(extraction_date AS TIMESTAMP) AS extracted_at,
        DATE(extraction_date) AS extraction_date,
        
        -- Flags de qualité
        CASE 
            WHEN weapon_kills > 0 THEN TRUE 
            ELSE FALSE 
        END AS is_valid_weapon
        
    FROM {{ source('bronze', 'bronze_weapons') }}
    WHERE DATE(extraction_date) = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_weapons
WHERE is_valid_weapon = TRUE
ORDER BY player_handle, weapon_rank_for_player
