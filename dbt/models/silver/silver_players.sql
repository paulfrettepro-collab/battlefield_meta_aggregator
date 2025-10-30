-- models/silver/silver_players.sql

{{ config(
    materialized='table',
    description='Joueurs du top 100 leaderboard avec données nettoyées'
) }}

WITH latest_extraction AS (
    SELECT MAX(DATE(extraction_date)) AS max_date
    FROM {{ source('bronze', 'bronze_leaderboard') }}
),

cleaned_players AS (
    SELECT
        -- Identifiants
        TRIM(handle) AS player_handle,
        TRIM(player_id) AS player_id,
        
        -- Métriques
        CAST(rank AS INT64) AS player_rank,
        CAST(kills AS INT64) AS total_kills,
        CAST(matches_played AS INT64) AS matches_played,
        
        -- Localisation (nouveau champ)
        TRIM(location) AS location,
        
        -- Métadonnées
        CAST(extraction_date AS TIMESTAMP) AS extracted_at,
        DATE(extraction_date) AS extraction_date,
        
        -- Flags de qualité
        CASE 
            WHEN kills > 0 THEN TRUE 
            ELSE FALSE 
        END AS is_valid_data,
        
        -- Catégorisation
        CASE
            WHEN rank <= 10 THEN 'Top 10'
            WHEN rank <= 50 THEN 'Top 50'
            WHEN rank <= 100 THEN 'Top 100'
            ELSE 'Other'
        END AS tier
        
    FROM {{ source('bronze', 'bronze_leaderboard') }}
    WHERE DATE(extraction_date) = (SELECT max_date FROM latest_extraction)
)

SELECT * FROM cleaned_players
WHERE is_valid_data = TRUE
ORDER BY player_rank
