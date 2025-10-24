-- models/gold/gold_player_rankings.sql

{{ config(
    materialized='table',
    description='Classement des joueurs avec leurs armes principales'
) }}

WITH player_main_weapon AS (
    SELECT
        player_handle,
        player_rank,
        player_total_kills,
        player_tier,
        
        -- Arme #1 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_name END) AS main_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_type END) AS main_weapon_type,
        MAX(CASE WHEN weapon_rank_for_player = 1 THEN weapon_kills END) AS main_weapon_kills,
        
        -- Arme #2 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 2 THEN weapon_name END) AS secondary_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 2 THEN weapon_kills END) AS secondary_weapon_kills,
        
        -- Arme #3 du joueur
        MAX(CASE WHEN weapon_rank_for_player = 3 THEN weapon_name END) AS tertiary_weapon,
        MAX(CASE WHEN weapon_rank_for_player = 3 THEN weapon_kills END) AS tertiary_weapon_kills,
        
        -- Stats globales
        ROUND(AVG(accuracy), 3) AS avg_accuracy_top3,
        ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct_top3
        
    FROM {{ ref('silver_player_weapons') }}
    GROUP BY player_handle, player_rank, player_total_kills, player_tier
)

SELECT * FROM player_main_weapon
ORDER BY player_rank
