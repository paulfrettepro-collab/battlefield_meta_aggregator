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
    """Load all weapons from Silver layer with aggregation"""
    client = get_bigquery_client()
    
    query = """
        SELECT 
            weapon_name,
            weapon_type,
            SUM(weapon_kills) AS total_kills,
            COUNT(DISTINCT player_handle) AS nb_players,
            ROUND(AVG(weapon_kills), 0) AS avg_kills_per_player,
            ROUND(AVG(accuracy), 3) AS avg_accuracy,
            ROUND(AVG(headshot_pct), 3) AS avg_headshot_pct,
            SUM(total_damage) AS total_damage,
            ROUND(AVG(total_damage), 0) AS avg_damage,
            ROW_NUMBER() OVER (ORDER BY SUM(weapon_kills) DESC) AS global_rank
        FROM `battlefield-meta-aggregator.bf6_meta_silver.silver_weapons`
        GROUP BY weapon_name, weapon_type
        ORDER BY total_kills DESC
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
    - `silver_weapons` (cleaned)
    
    Aggregated by weapon_name to show global statistics.
    """)
    
    # Main header
    st.title("🔫 All Weapons Statistics")
    st.markdown("Complete list of all weapons extracted from the top 100 players")
    
    # Load data
    with st.spinner("📊 Loading all weapons data..."):
        df_all_weapons = load_all_weapons()
    
    if df_all_weapons.empty:
        st.error("❌ No weapons data available")
        st.stop()
    
    # Summary metrics
    st.header("📊 Global Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Weapons", len(df_all_weapons))
    
    with col2:
        total_kills = int(df_all_weapons['total_kills'].sum())
        st.metric("Total Kills", format_number(total_kills))
    
    with col3:
        avg_accuracy = df_all_weapons['avg_accuracy'].mean()
        st.metric("Avg Accuracy", format_percentage(avg_accuracy))
    
    with col4:
        total_players = int(df_all_weapons['nb_players'].sum())
        st.metric("Total Player-Weapon Combos", format_number(total_players))
    
    st.divider()
    
    # Filters
    st.header("🔍 Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weapon type filter
        weapon_types = ['All'] + sorted(df_all_weapons['weapon_type'].unique().tolist())
        selected_type = st.selectbox(
            "Filter by Weapon Type",
            options=weapon_types
        )
    
    with col2:
        # Search box
        search_term = st.text_input(
            "Search Weapon Name",
            placeholder="e.g., M4A1, SG 553R..."
        )
    
    # Apply filters
    df_filtered = df_all_weapons.copy()
    
    if selected_type != 'All':
        df_filtered = df_filtered[df_filtered['weapon_type'] == selected_type]
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered['weapon_name'].str.contains(search_term, case=False, na=False)
        ]
    
    st.info(f"📊 Showing **{len(df_filtered)}** weapons (out of {len(df_all_weapons)} total)")
    
    st.divider()
    
    # Detailed table
    st.header("📋 Complete Weapons List")
    
    # Format the dataframe
    df_display = df_filtered.copy()
    df_display['Rank'] = df_display['global_rank']
    df_display['Weapon'] = df_display['weapon_name']
    df_display['Type'] = df_display['weapon_type']
    df_display['Total Kills'] = df_display['total_kills'].apply(lambda x: format_number(x))
    df_display['Players'] = df_display['nb_players']
    df_display['Avg Kills/Player'] = df_display['avg_kills_per_player'].apply(lambda x: format_number(x, 0))
    df_display['Avg Accuracy'] = df_display['avg_accuracy'].apply(lambda x: format_percentage(x))
    df_display['Avg Headshot %'] = df_display['avg_headshot_pct'].apply(lambda x: format_percentage(x))
    df_display['Total Damage'] = df_display['total_damage'].apply(lambda x: format_number(x, 0))
    df_display['Avg Damage'] = df_display['avg_damage'].apply(lambda x: format_number(x, 0))
    
    # Select columns to display
    columns_to_show = [
        'Rank', 'Weapon', 'Type', 'Total Kills', 'Players', 
        'Avg Kills/Player', 'Avg Accuracy', 'Avg Headshot %', 
        'Total Damage', 'Avg Damage'
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
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"bf6_all_weapons_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # Top weapons by category
    st.header("🏆 Top 3 by Weapon Type")
    
    weapon_types_list = sorted([t for t in df_all_weapons['weapon_type'].unique() if t != 'UNKNOWN'])
    
    for weapon_type in weapon_types_list[:5]:  # Show top 5 categories
        st.subheader(f"{weapon_type}")
        
        df_type = df_all_weapons[df_all_weapons['weapon_type'] == weapon_type].head(3)
        
        cols = st.columns(3)
        for idx, (_, weapon) in enumerate(df_type.iterrows()):
            with cols[idx]:
                st.markdown(f"**#{idx + 1}: {weapon['weapon_name']}**")
                st.write(f"Kills: {format_number(weapon['total_kills'])}")
                st.write(f"Players: {weapon['nb_players']}")
                st.write(f"Accuracy: {format_percentage(weapon['avg_accuracy'])}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Data from BigQuery Silver Layer (silver_weapons)</p>
        <p>Updated: Real-time aggregation</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
