-- models/gold/gold_top_weapons_by_type.sql

{{ config(
    materialized='table',
    description='Top 20 armes par nombre de kills totaux'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_name,
        
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
        ROUND(AVG(accuracy), 3) AS avg_accuracy,
        
        ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS weapon_rank
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_name
)

SELECT * FROM weapon_aggregates
WHERE weapon_rank <= 20
ORDER BY weapon_rank
