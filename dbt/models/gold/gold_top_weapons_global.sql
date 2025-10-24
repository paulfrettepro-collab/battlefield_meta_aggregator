-- models/gold/gold_top_weapons_global.sql

{{ config(
    materialized='table',
    description='Top 3 armes qui font le plus de kills (MVP Dashboard)'
) }}

WITH weapon_aggregates AS (
    SELECT
        weapon_name,
        weapon_type,
        
        -- Métriques principales (MVP)
        SUM(weapon_kills) AS total_kills,
        COUNT(DISTINCT player_handle) AS nb_players_using,
        ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
        
        -- Métriques secondaires (Phase 2)
        ROUND(AVG(accuracy), 3) AS avg_accuracy,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
        SUM(total_damage) AS total_damage_dealt,
        
        -- Ranking
        ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS global_rank
        
    FROM {{ ref('silver_weapons') }}
    GROUP BY weapon_name, weapon_type
)

SELECT
    global_rank,
    weapon_name,
    weapon_type,
    total_kills,
    nb_players_using,
    avg_kills_per_player,
    avg_accuracy,
    avg_headshot_pct,
    total_damage_dealt,
    
    -- Métadonnées
    CURRENT_TIMESTAMP() AS generated_at

FROM weapon_aggregates
WHERE global_rank <= 3  -- TOP 3 ONLY (MVP)
ORDER BY global_rank
