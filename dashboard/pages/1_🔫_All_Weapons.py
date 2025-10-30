"""
All Weapons Statistics Page

Displays complete list of all weapons with detailed statistics.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    get_bigquery_client,
    get_last_extraction_date,
    format_number,
    format_percentage
)

# Page configuration
st.set_page_config(
    page_title="All Weapons - BF6 Meta",
    page_icon="🔫",
    layout="wide"
)


def apply_custom_css(theme_mode="dark"):
    """Apply custom CSS based on theme mode"""
    
    if theme_mode == "dark":
        bg_color = "#0E1117"
        text_color = "#FAFAFA"
        card_bg = "#1E1E1E"
        border_color = "#333333"
        accent_color = "#FF6B6B"
        secondary_text = "#B0B0B0"
    else:  # light
        bg_color = "#FFFFFF"
        text_color = "#262730"
        card_bg = "#F0F2F6"
        border_color = "#E0E0E0"
        accent_color = "#FF6B6B"
        secondary_text = "#666666"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        
        p, span, div {{
            color: {text_color};
        }}
        
        .dataframe {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border: 2px solid {accent_color} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }}
        .dataframe th {{
            background-color: {accent_color} !important;
            color: white !important;
            font-weight: bold;
            padding: 12px !important;
        }}
        .dataframe td {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            padding: 10px !important;
        }}
        .dataframe tr:hover td {{
            background-color: {accent_color}22 !important;
        }}
        
        [data-testid="stMetric"] {{
            background-color: {card_bg};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 15px;
        }}
        
        .stAlert {{
            background-color: {card_bg};
            color: {text_color};
            border-radius: 10px;
            border-width: 2px;
        }}
        </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=600)
def load_all_weapons() -> pd.DataFrame:
    """Load all weapons from Gold layer (top 20 weapons by kills)"""
    client = get_bigquery_client()
    
    query = """
        SELECT 
            weapon_rank AS global_rank,
            weapon_name,
            total_kills,
            nb_players_using AS nb_players,
            avg_kills_per_player,
            avg_accuracy
        FROM `battlefield-meta-aggregator.bf6_meta_gold.gold_top_weapons_by_type`
        ORDER BY weapon_rank
    """
    
    df = client.query(query).to_dataframe()
    return df


def main():
    """Main page for all weapons statistics"""
    
    # Theme selector
    theme_mode = st.sidebar.radio(
        "🎨 Theme",
        options=["Dark", "Light"],
        index=0,
        horizontal=True
    )
    
    apply_custom_css(theme_mode.lower())
    
    # Sidebar info
    st.sidebar.divider()
    st.sidebar.subheader("📅 Data Status")
    last_date = get_last_extraction_date()
    st.sidebar.info(f"**Last Update:**\n\n{last_date}")
    
    st.sidebar.divider()
    st.sidebar.subheader("🗄️ Data Source")
    st.sidebar.markdown("""
    **BigQuery Table:**
    - `gold_top_weapons_by_type` (Top 20)
    
    Showing the top 20 weapons by total kills.
    """)
    
    # Main header
    st.title("🔫 Top 20 Weapons Statistics")
    st.markdown("Top 20 weapons by total kills from the leaderboard")
    
    # Load data
    with st.spinner("📊 Loading weapons data..."):
        df_all_weapons = load_all_weapons()
    
    if df_all_weapons.empty:
        st.error("❌ No weapons data available")
        st.stop()
    
    # Summary metrics
    st.header("📊 Global Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Weapons", len(df_all_weapons))
    
    with col2:
        total_kills = int(df_all_weapons['total_kills'].sum())
        st.metric("Total Kills (Top 20)", format_number(total_kills))
    
    with col3:
        avg_accuracy = df_all_weapons['avg_accuracy'].mean()
        st.metric("Avg Accuracy", format_percentage(avg_accuracy))
    
    st.divider()
    
    # Filters
    st.header("🔍 Filters")
    
    # Search box
    search_term = st.text_input(
        "Search Weapon Name",
        placeholder="e.g., M4A1, SG 553R..."
    )
    
    # Apply filters
    df_filtered = df_all_weapons.copy()
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered['weapon_name'].str.contains(search_term, case=False, na=False)
        ]
    
    st.info(f"📊 Showing **{len(df_filtered)}** weapons (out of {len(df_all_weapons)} total)")
    
    st.divider()
    
    # Detailed table
    st.header("📋 Top 20 Weapons List")
    
    # Format the dataframe
    df_display = df_filtered.copy()
    df_display['Rank'] = df_display['global_rank']
    df_display['Weapon'] = df_display['weapon_name']
    df_display['Total Kills'] = df_display['total_kills'].apply(lambda x: format_number(x))
    df_display['Players'] = df_display['nb_players']
    df_display['Avg Kills/Player'] = df_display['avg_kills_per_player'].apply(lambda x: format_number(x, 0))
    df_display['Avg Accuracy'] = df_display['avg_accuracy'].apply(lambda x: format_percentage(x))
    
    # Select columns to display
    columns_to_show = [
        'Rank', 'Weapon', 'Total Kills', 'Players', 
        'Avg Kills/Player', 'Avg Accuracy'
    ]
    
    st.dataframe(
        df_display[columns_to_show],
        use_container_width=True,
        hide_index=True,
        height=600
    )
    
    # Download button
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"bf6_top20_weapons_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Data from BigQuery Gold Layer (gold_top_weapons_by_type)</p>
        <p>Updated: Real-time from latest extraction</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
