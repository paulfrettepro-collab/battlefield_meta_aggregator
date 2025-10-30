-- models/silver/silver_player_weapons.sql

{{ config(
    materialized='table',
    description='Vue enrichie combinant joueurs et leurs top 3 armes'
) }}

SELECT
    -- Joueur
    p.player_handle,
    p.player_id,
    p.player_rank,
    p.total_kills AS player_total_kills,
    p.matches_played AS player_matches,
    p.location AS player_location,
    p.tier AS player_tier,
    
    -- Arme
    w.weapon_name,
    w.weapon_kills,
    w.weapon_rank_for_player,
    w.accuracy AS weapon_accuracy,
    
    -- Métriques calculées
    ROUND(w.weapon_kills * 100.0 / p.total_kills, 2) AS pct_kills_with_weapon,
    
    -- Métadonnées
    p.extraction_date,
    p.extracted_at

FROM {{ ref('silver_players') }} p
INNER JOIN {{ ref('silver_weapons') }} w
    ON p.player_handle = w.player_handle
    AND p.extraction_date = w.extraction_date

ORDER BY p.player_rank, w.weapon_rank_for_player
