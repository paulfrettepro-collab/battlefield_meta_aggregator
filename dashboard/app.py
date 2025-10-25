"""
BF6 Meta Aggregator Dashboard

A Streamlit dashboard to visualize Battlefield 6 weapon meta statistics.
This is the MVP version focusing on Top 3 Weapons display.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import utilities
from utils import (
    load_top_weapons,
    load_weapon_types_stats,
    get_last_extraction_date,
    clear_cache,
    plot_top_weapons_bar,
    plot_accuracy_scatter,
    format_number,
    format_percentage
)

# Page configuration
st.set_page_config(
    page_title="BF6 Meta Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎮 Battlefield 6 Meta Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Top Weapons & Player Statistics</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/FF6B6B/FFFFFF?text=BF6+Meta", use_container_width=True)
        st.title("⚙️ Controls")
        
        # Data refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            clear_cache()
            st.success("✅ Cache cleared! Data will be refreshed.")
            st.rerun()
        
        # Last extraction date
        st.divider()
        st.subheader("📅 Data Status")
        last_date = get_last_extraction_date()
        st.info(f"**Last Update:**\n\n{last_date}")
        
        # About section
        st.divider()
        st.subheader("ℹ️ About")
        st.markdown("""
        This dashboard displays real-time statistics from the Battlefield 6 
        top 100 leaderboard.
        
        **Data Pipeline:**
        - Web scraping (Tracker.gg)
        - MinIO storage
        - BigQuery warehouse
        - DBT transformations
        - Streamlit dashboard
        
        **GitHub:** [BF6 Meta Aggregator](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator)
        """)
    
    # Main content
    try:
        # Load data
        with st.spinner("📊 Loading data from BigQuery..."):
            df_top_weapons = load_top_weapons()
            df_weapon_types = load_weapon_types_stats()
        
        if df_top_weapons.empty:
            st.error("❌ No data available. Please check BigQuery connection.")
            st.stop()
        
        # === SECTION 1: KEY METRICS ===
        st.header("📊 Key Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_kills = int(df_top_weapons['total_kills'].sum())
            st.metric(
                label="🔫 Total Kills (Top 3)",
                value=format_number(total_kills)
            )
        
        with col2:
            total_players = int(df_top_weapons['player_count'].sum())
            st.metric(
                label="👥 Total Players",
                value=format_number(total_players)
            )
        
        with col3:
            avg_accuracy = df_top_weapons['avg_accuracy'].mean()
            st.metric(
                label="🎯 Avg Accuracy",
                value=format_percentage(avg_accuracy)
            )
        
        with col4:
            avg_headshot = df_top_weapons['avg_headshot_pct'].mean()
            st.metric(
                label="💀 Avg Headshot %",
                value=format_percentage(avg_headshot)
            )
        
        st.divider()
        
        # === SECTION 2: TOP 3 WEAPONS CHART ===
        st.header("🏆 Top 3 Weapons by Total Kills")
        
        # Bar chart
        fig_bar = plot_top_weapons_bar(df_top_weapons)
        st.plotly_chart(fig_bar, use_column_width=True)
        
        st.divider()
        
        # === SECTION 3: DETAILED BREAKDOWN ===
        st.header("🔍 Detailed Weapon Statistics")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📋 Table View", "📈 Accuracy Analysis"])
        
        with tab1:
            # Prepare detailed table
            df_display = df_top_weapons.copy()
            df_display['total_kills'] = df_display['total_kills'].apply(lambda x: format_number(x))
            df_display['avg_accuracy'] = df_display['avg_accuracy'].apply(lambda x: format_percentage(x))
            df_display['avg_headshot_pct'] = df_display['avg_headshot_pct'].apply(lambda x: format_percentage(x))
            df_display['avg_damage'] = df_display['avg_damage'].apply(lambda x: format_number(x, 0))
            
            # Rename columns for display
            df_display = df_display.rename(columns={
                'weapon_name': 'Weapon',
                'weapon_type': 'Type',
                'total_kills': 'Total Kills',
                'avg_accuracy': 'Avg Accuracy',
                'avg_headshot_pct': 'Avg Headshot %',
                'player_count': 'Players',
                'avg_damage': 'Avg Damage',
                'avg_time_played': 'Avg Time Played'
            })
            
            # Select columns to display
            columns_to_show = ['Weapon', 'Type', 'Total Kills', 'Players', 'Avg Accuracy', 'Avg Headshot %', 'Avg Damage']
            st.dataframe(
                df_display[columns_to_show],
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = df_top_weapons.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"bf6_top_weapons_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with tab2:
            # Accuracy vs Kills scatter plot
            fig_scatter = plot_accuracy_scatter(df_top_weapons)
            st.plotly_chart(fig_scatter, use_column_width=True)
            
            st.markdown("""
            **Insights:**
            - Bubble size represents the number of players using each weapon
            - Higher accuracy doesn't always mean more kills
            - Popular weapons tend to have moderate accuracy due to larger player base
            """)
        
        st.divider()
        
        # === SECTION 4: WEAPON CARDS ===
        st.header("🎖️ Top 3 Weapon Profiles")
        
        cols = st.columns(3)
        
        for idx, (_, weapon) in enumerate(df_top_weapons.iterrows()):
            with cols[idx]:
                # Card container
                with st.container():
                    # Rank badge
                    rank_emoji = ["🥇", "🥈", "🥉"][idx]
                    st.markdown(f"### {rank_emoji} #{idx + 1}: {weapon['weapon_name']}")
                    
                    # Weapon type badge
                    st.caption(f"**Type:** {weapon['weapon_type']}")
                    
                    # Stats
                    st.metric("Total Kills", format_number(weapon['total_kills']))
                    st.metric("Players Using", format_number(weapon['player_count']))
                    st.metric("Avg Accuracy", format_percentage(weapon['avg_accuracy']))
                    st.metric("Avg Headshot %", format_percentage(weapon['avg_headshot_pct']))
                    st.metric("Avg Damage", format_number(weapon['avg_damage'], 0))
        
        # Footer
        st.divider()
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>Made with ❤️ using Streamlit, DBT, and BigQuery</p>
            <p>Data sourced from <a href='https://tracker.gg/bf6/leaderboards' target='_blank'>Tracker.gg</a></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
