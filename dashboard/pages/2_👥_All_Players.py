"""
All Players Statistics Page

Displays complete list of all players with their rankings and stats.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    load_player_rankings,
    get_last_extraction_date,
    format_number,
    format_percentage
)

# Page configuration
st.set_page_config(
    page_title="All Players - BF6 Meta",
    page_icon="👥",
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
        
        .player-card {{
            background-color: {card_bg};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 10px;
        }}
        .player-card:hover {{
            border-color: {accent_color};
            box-shadow: 0 4px 12px rgba(255,107,107,0.3);
        }}
        </style>
    """, unsafe_allow_html=True)


def main():
    """Main page for all players statistics"""
    
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
    - `gold_player_rankings`
    
    Top 100 players with their main weapons and stats.
    """)
    
    # Main header
    st.title("👥 All Players Rankings")
    st.markdown("Top 100 players from the leaderboard with their statistics")
    
    # Load data
    with st.spinner("📊 Loading players data..."):
        df_players = load_player_rankings()
    
    if df_players.empty:
        st.error("❌ No players data available")
        st.stop()
    
    # Summary metrics
    st.header("📊 Global Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(df_players))
    
    with col2:
        total_kills = int(df_players['total_kills'].sum())
        st.metric("Total Kills", format_number(total_kills))
    
    with col3:
        avg_accuracy = df_players['avg_accuracy'].mean()
        st.metric("Avg Accuracy", format_percentage(avg_accuracy))
    
    with col4:
        avg_headshot = df_players['avg_headshot_pct'].mean()
        st.metric("Avg Headshot %", format_percentage(avg_headshot))
    
    st.divider()
    
    # Search
    st.header("🔍 Search Player")
    search_term = st.text_input(
        "Search by player name",
        placeholder="e.g., RoboCat, ViteZ..."
    )
    
    # Apply filter
    df_filtered = df_players.copy()
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered['handle'].str.contains(search_term, case=False, na=False)
        ]
    
    st.info(f"📊 Showing **{len(df_filtered)}** players (out of {len(df_players)} total)")
    
    st.divider()
    
    # Detailed table
    st.header("📋 Complete Players List")
    
    # Format the dataframe
    df_display = df_filtered.copy()
    df_display['Rank'] = df_display['player_rank']
    df_display['Player'] = df_display['handle']
    df_display['Total Kills'] = df_display['total_kills'].apply(lambda x: format_number(x))
    df_display['Main Weapon'] = df_display['main_weapon']
    df_display['Main Weapon Type'] = df_display['main_weapon_type']
    df_display['Main Weapon Kills'] = df_display['main_weapon_kills'].apply(lambda x: format_number(x) if pd.notna(x) else 'N/A')
    df_display['Avg Accuracy'] = df_display['avg_accuracy'].apply(lambda x: format_percentage(x))
    df_display['Avg Headshot %'] = df_display['avg_headshot_pct'].apply(lambda x: format_percentage(x))
    
    # Select columns to display
    columns_to_show = [
        'Rank', 'Player', 'Total Kills', 'Main Weapon', 
        'Main Weapon Type', 'Main Weapon Kills', 
        'Avg Accuracy', 'Avg Headshot %'
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
        label="📥 Download Players Data as CSV",
        data=csv,
        file_name=f"bf6_all_players_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # Top 10 players cards
    st.header("🏆 Top 10 Players")
    
    for idx, (_, player) in enumerate(df_players.head(10).iterrows()):
        st.markdown('<div class="player-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        
        with col1:
            rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx + 1}"
            st.markdown(f"### {rank_emoji}")
        
        with col2:
            st.markdown(f"**{player['handle']}**")
            st.caption(f"Rank: {player['player_rank']}")
        
        with col3:
            st.metric("Total Kills", format_number(player['total_kills']))
            st.caption(f"Main: {player['main_weapon']}")
        
        with col4:
            st.metric("Accuracy", format_percentage(player['avg_accuracy']))
            st.metric("Headshot %", format_percentage(player['avg_headshot_pct']))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Data from BigQuery Gold Layer (gold_player_rankings)</p>
        <p>Showing top 100 players from Tracker.gg leaderboard</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
