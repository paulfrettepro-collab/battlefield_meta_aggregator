-- models/gold/gold_top_weapons_by_type.sql

{{ config(
    materialized='table',
    description='Top 3 armes par catégorie de weapon_type'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_type,
        weapon_name,
        
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
        ROUND(AVG(accuracy), 3) AS avg_accuracy,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
        
        ROW_NUMBER() OVER (
            PARTITION BY weapon_type 
            ORDER BY SUM(weapon_kills) DESC
        ) AS rank_in_type
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_type, weapon_name
)

SELECT * FROM weapon_aggregates
WHERE rank_in_type <= 3
ORDER BY weapon_type, rank_in_type
