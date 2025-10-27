"""
BigQuery Connector for BF6 Meta Dashboard

This module provides cached functions to query BigQuery tables
and retrieve data for the Streamlit dashboard.

Supports both local development (JSON credentials) and Streamlit Cloud (secrets).
"""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from pathlib import Path
import os


@st.cache_resource
def get_bigquery_client():
    """
    Create and cache a BigQuery client using service account credentials.
    
    Detects environment automatically:
    - Streamlit Cloud: Uses st.secrets
    - Local development: Uses JSON file from config/
    
    Returns:
        bigquery.Client: Authenticated BigQuery client
    """
    # Check if running on Streamlit Cloud (secrets available)
    if "gcp_service_account" in st.secrets:
        # Streamlit Cloud: use secrets.toml
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        project_id = st.secrets["gcp_service_account"]["project_id"]
        return bigquery.Client(credentials=credentials, project=project_id)
    
    else:
        # Local development: use JSON file
        credentials_path = Path(__file__).parent.parent.parent / "config" / "bigquery-key.json"
        
        if not credentials_path.exists():
            st.error(f"❌ BigQuery credentials not found at: {credentials_path}")
            st.info("💡 For local dev: place bigquery-key.json in config/")
            st.info("💡 For Streamlit Cloud: configure secrets in dashboard settings")
            st.stop()
        
        return bigquery.Client.from_service_account_json(str(credentials_path))


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_top_weapons() -> pd.DataFrame:
    """
    Load top 3 weapons from the Gold layer.
    
    Returns:
        pd.DataFrame: Top 3 weapons with stats (weapon_name, weapon_type, 
                     total_kills, avg_accuracy, avg_headshot_pct, nb_players_using)
    """
    client = get_bigquery_client()
    
    query = """
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
            generated_at
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
        ORDER BY global_rank
    """
    
    df = client.query(query).to_dataframe()
    
    # Rename columns to match dashboard expectations
    df = df.rename(columns={
        'nb_players_using': 'player_count',
        'total_damage_dealt': 'avg_damage'
    })
    
    return df


@st.cache_data(ttl=600)
def load_weapon_types_stats() -> pd.DataFrame:
    """
    Load weapon type aggregated statistics from Gold layer.
    
    Returns:
        pd.DataFrame: Stats by weapon type
    """
    client = get_bigquery_client()
    
    # Use aggregation on silver_weapons since we don't have a dedicated weapon_type table
    query = """
        SELECT 
            weapon_type,
            COUNT(DISTINCT weapon_name) AS total_weapons,
            SUM(weapon_kills) AS total_kills,
            ROUND(AVG(accuracy), 3) AS avg_accuracy,
            ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
            SUM(total_damage) AS avg_damage
        FROM `battlefield-meta-aggregator.bf6_meta_silver.silver_weapons`
        WHERE weapon_type != 'UNKNOWN'
        GROUP BY weapon_type
        ORDER BY total_kills DESC
        LIMIT 10
    """
    
    df = client.query(query).to_dataframe()
    return df


@st.cache_data(ttl=600)
def load_player_rankings() -> pd.DataFrame:
    """
    Load player rankings from Gold layer.
    
    Returns:
        pd.DataFrame: Player rankings with all stats
    """
    client = get_bigquery_client()
    
    query = """
        SELECT 
            player_handle AS handle,
            player_rank,
            player_total_kills AS total_kills,
            main_weapon,
            main_weapon_type,
            main_weapon_kills,
            avg_accuracy_top3 AS avg_accuracy,
            avg_headshot_pct_top3 AS avg_headshot_pct
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_player_rankings`
        ORDER BY player_total_kills DESC
    """
    
    df = client.query(query).to_dataframe()
    return df


@st.cache_data(ttl=600)
def load_player_weapons(handle: str) -> pd.DataFrame:
    """
    Load weapons for a specific player from Silver layer.
    
    Args:
        handle: Player handle (e.g., "RoboCat")
        
    Returns:
        pd.DataFrame: Player's weapons with stats
    """
    client = get_bigquery_client()
    
    query = f"""
        SELECT 
            weapon_name,
            weapon_type,
            weapon_kills AS kills,
            accuracy,
            headshot_pct,
            total_damage AS damage,
            time_played,
            weapon_rank_for_player
        FROM `battlefield-meta-aggregator.bf6_meta_silver.silver_player_weapons`
        WHERE player_handle = '{handle}'
        ORDER BY weapon_kills DESC
    """
    
    df = client.query(query).to_dataframe()
    return df


@st.cache_data(ttl=600)
def get_last_extraction_date() -> str:
    """
    Get the date of the last data extraction.
    
    Returns:
        str: Last extraction date formatted as "YYYY-MM-DD HH:MM UTC"
    """
    client = get_bigquery_client()
    
    query = """
        SELECT MAX(extraction_date) AS last_date
        FROM `battlefield-meta-aggregator.bf6_meta.bf6_leaderboard_raw`
    """
    
    result = client.query(query).to_dataframe()
    
    if not result.empty and result['last_date'].iloc[0] is not None:
        return result['last_date'].iloc[0].strftime("%Y-%m-%d %H:%M UTC")
    
    return "Unknown"


def clear_cache():
    """
    Clear all Streamlit caches to force data refresh.
    """
    st.cache_data.clear()
