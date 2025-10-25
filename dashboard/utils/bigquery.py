"""
BigQuery Connector for BF6 Meta Dashboard

This module provides cached functions to query BigQuery tables
and retrieve data for the Streamlit dashboard.
"""

import streamlit as st
from google.cloud import bigquery
import pandas as pd
from pathlib import Path


@st.cache_resource
def get_bigquery_client():
    """
    Create and cache a BigQuery client using service account credentials.
    
    Returns:
        bigquery.Client: Authenticated BigQuery client
    """
    # Path to credentials relative to project root
    credentials_path = Path(__file__).parent.parent.parent / "config" / "bigquery-key.json"
    
    if not credentials_path.exists():
        st.error(f"❌ BigQuery credentials not found at: {credentials_path}")
        st.stop()
    
    return bigquery.Client.from_service_account_json(str(credentials_path))


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_top_weapons() -> pd.DataFrame:
    """
    Load top 3 weapons from the Gold layer.
    
    Returns:
        pd.DataFrame: Top 3 weapons with stats (weapon_name, weapon_type, 
                     total_kills, avg_accuracy, avg_headshot_pct, player_count)
    """
    client = get_bigquery_client()
    
    query = """
        SELECT 
            weapon_name,
            weapon_type,
            total_kills,
            avg_accuracy,
            avg_headshot_pct,
            player_count,
            avg_damage,
            avg_time_played
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
        ORDER BY total_kills DESC
    """
    
    df = client.query(query).to_dataframe()
    return df


@st.cache_data(ttl=600)
def load_weapon_types_stats() -> pd.DataFrame:
    """
    Load weapon type aggregated statistics from Gold layer.
    
    Returns:
        pd.DataFrame: Stats by weapon type
    """
    client = get_bigquery_client()
    
    query = """
        SELECT 
            weapon_type,
            total_weapons,
            total_kills,
            avg_accuracy,
            avg_headshot_pct,
            avg_damage
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_weapon_type_rankings`
        WHERE weapon_type != 'UNKNOWN'
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
            handle,
            player_rank,
            total_kills,
            avg_accuracy,
            avg_headshot_pct,
            kills_rank,
            accuracy_rank,
            headshot_rank
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_player_rankings`
        ORDER BY total_kills DESC
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
            kills,
            accuracy,
            headshot_pct,
            damage,
            time_played
        FROM `battlefield-meta-aggregator.bf6_meta_silver.silver_player_weapons`
        WHERE handle = '{handle}'
        ORDER BY kills DESC
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
