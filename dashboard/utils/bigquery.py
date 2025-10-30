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
    Load top 10 weapons from the Gold layer.
    
    Returns:
        pd.DataFrame: Top 10 weapons with stats (weapon_name, 
                     total_kills, avg_accuracy, nb_players_using)
    """
    client = get_bigquery_client()
    
    query = """
        SELECT 
            global_rank,
            weapon_name,
            total_kills,
            nb_players_using,
            avg_kills_per_player,
            avg_accuracy,
            generated_at
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_global`
        ORDER BY global_rank
    """
    
    df = client.query(query).to_dataframe()
    
    # Rename columns to match dashboard expectations
    df = df.rename(columns={
        'nb_players_using': 'player_count'
    })
    
    return df


@st.cache_data(ttl=600)
def load_all_weapons() -> pd.DataFrame:
    """
    Load top 20 weapons by kills from Gold layer.
    
    Returns:
        pd.DataFrame: Top 20 weapons with stats
    """
    client = get_bigquery_client()
    
    query = """
        SELECT 
            weapon_rank,
            weapon_name,
            total_kills,
            nb_players_using,
            avg_kills_per_player,
            avg_accuracy,
            generated_at
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_by_type`
        ORDER BY weapon_rank
    """
    
    df = client.query(query).to_dataframe()
    
    # Rename columns to match dashboard expectations
    df = df.rename(columns={
        'nb_players_using': 'player_count'
    })
    
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
            player_matches,
            player_location,
            main_weapon,
            main_weapon_kills,
            main_weapon_accuracy,
            secondary_weapon,
            secondary_weapon_kills,
            tertiary_weapon,
            tertiary_weapon_kills
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
            weapon_kills AS kills,
            weapon_accuracy AS accuracy,
            weapon_rank_for_player,
            pct_kills_with_weapon
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
        FROM `battlefield-meta-aggregator.bf6_meta.bronze_leaderboard`
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
