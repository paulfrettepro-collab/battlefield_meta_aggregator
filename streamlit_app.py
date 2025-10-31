"""
BF6 Meta Aggregator Dashboard

A Streamlit dashboard to visualize Battlefield 6 weapon meta statistics.
This is the MVP version focusing on Top 3 Weapons display.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import utilities from dashboard folder
from dashboard.utils import (
    load_top_weapons,
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
        /* Main background */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Headers */
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: {accent_color};
            margin-bottom: 1rem;
        }}
        .sub-header {{
            font-size: 1.2rem;
            text-align: center;
            color: {secondary_text};
            margin-bottom: 2rem;
        }}
        
        /* Metric cards */
        [data-testid="stMetricValue"] {{
            color: {text_color};
            font-size: 2rem;
            font-weight: bold;
        }}
        [data-testid="stMetricLabel"] {{
            color: {secondary_text};
            font-size: 1rem;
        }}
        
        /* Tables */
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
            border-bottom: 2px solid {accent_color} !important;
        }}
        .dataframe td {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border-color: {border_color} !important;
            padding: 10px !important;
        }}
        .dataframe tr:hover td {{
            background-color: {accent_color}22 !important;
        }}
        
        /* Metric cards with borders */
        [data-testid="stMetric"] {{
            background-color: {card_bg};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        [data-testid="stMetric"]:hover {{
            border-color: {accent_color};
            box-shadow: 0 4px 8px rgba(255,107,107,0.2);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {card_bg};
        }}
        
        /* Text elements */
        p, span, div {{
            color: {text_color};
        }}
        
        /* Headers h1-h6 */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        
        /* Tab labels */
        .stTabs [data-baseweb="tab-list"] button {{
            color: {secondary_text};
        }}
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
            color: {accent_color};
        }}
        
        /* Info boxes */
        .stAlert {{
            background-color: {card_bg};
            color: {text_color};
            border-color: {border_color};
            border-radius: 10px;
            border-width: 2px;
        }}
        
        /* Tab content */
        .stTabs [data-baseweb="tab-panel"] {{
            background-color: {card_bg};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 20px;
            margin-top: 10px;
        }}
        
        /* Weapon cards */
        .weapon-card {{
            background-color: {card_bg};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .weapon-card:hover {{
            border-color: {accent_color};
            box-shadow: 0 4px 12px rgba(255,107,107,0.3);
            transform: translateY(-4px);
            transition: all 0.3s ease;
        }}
        </style>
    """, unsafe_allow_html=True)


def main():
    """Main dashboard application"""
    
    # Sidebar - Theme selector (must be before other UI elements)
    with st.sidebar:
        st.title("⚙️ Controls")
        
        # Theme toggle
        theme_mode = st.radio(
            "🎨 Theme",
            options=["Dark", "Light"],
            index=0,  # Default to Dark
            horizontal=True
        )
        
        # Apply theme CSS
        apply_custom_css(theme_mode.lower())
        
        st.divider()
        
        st.image("https://via.placeholder.com/300x100/FF6B6B/FFFFFF?text=BF6+Meta", use_column_width=True)
        
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
        
        st.caption("📊 **Dataset:** 50 players × 3 weapons = 150 weapons analyzed")
        
        # Data source info
        st.divider()
        st.subheader("🗄️ Data Source")
        st.markdown("""
        **BigQuery Tables:**
        - 🥉 Bronze: Raw NDJSON data
        - 🥈 Silver: Cleaned & enriched
        - 🥇 **Gold: Analytics** ✅
        
        This dashboard displays data from the **Gold layer** 
        (aggregated & analytics-ready).
        
        **Top 3 Weapons:**
        1. 🥇 SG 553R (86,897 kills)
        2. 🥈 TR-7 (50,394 kills)
        3. 🥉 M4A1 (39,049 kills)
        """)
        
        # About section
        st.divider()
        st.subheader("ℹ️ About")
        st.markdown("""
        This dashboard displays real-time statistics from the **Battlefield 6 
        top 50 leaderboard** (by total kills).
        
        **Data Pipeline:**
        1. 🕷️ Web scraping (Selenium + Tracker.gg)
        2. 💾 Local storage (NDJSON files)
        3. ☁️ BigQuery warehouse (Bronze tables)
        4. 🏗️ DBT transformations (Silver → Gold)
        5. 📊 Streamlit dashboard (this app!)
        
        **Tech Stack:** Python 3.12, Selenium, BigQuery, DBT Core, Streamlit, Plotly
        
        **Automation:** Weekly extractions via Cron/GitHub Actions
        
        **GitHub:** [BF6 Meta Aggregator](https://github.com/paulfrettepro-collab/battlefield_meta_aggregator)
        """)
    
    # Header (after sidebar to apply CSS)
    st.markdown('<h1 class="main-header">🎮 Battlefield 6 Meta Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Top Weapons & Player Statistics from Gold Layer</p>', unsafe_allow_html=True)
    
    # Main content
    try:
        # Load data
        with st.spinner("📊 Loading data from BigQuery..."):
            df_top_weapons = load_top_weapons()
        
        if df_top_weapons.empty:
            st.error("❌ No data available. Please check BigQuery connection.")
            st.stop()
        
        # === SECTION 1: KEY METRICS ===
        st.header("📊 Key Statistics")
        
        # Info badge about data source
        st.info("📊 **Data Source:** BigQuery Gold Layer (`gold_top_weapons_global`) - Aggregated analytics-ready data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_kills = int(df_top_weapons['total_kills'].sum())
            st.metric(
                label="🔫 Total Kills (Top 10)",
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
        
        st.divider()
        
        # === SECTION 2: TOP 3 WEAPONS CHART ===
        st.header("🏆 Top 3 Weapons by Total Kills")
        
        # Bar chart
        fig_bar = plot_top_weapons_bar(df_top_weapons, theme=theme_mode.lower())
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
            df_display['avg_kills_per_player'] = df_display['avg_kills_per_player'].apply(lambda x: format_number(x, 0))
            
            # Rename columns for display
            df_display = df_display.rename(columns={
                'weapon_name': 'Weapon',
                'total_kills': 'Total Kills',
                'avg_accuracy': 'Avg Accuracy',
                'player_count': 'Players',
                'avg_kills_per_player': 'Avg Kills/Player'
            })
            
            # Select columns to display
            columns_to_show = ['Weapon', 'Total Kills', 'Players', 'Avg Kills/Player', 'Avg Accuracy']
            
            # Style the dataframe
            st.dataframe(
                df_display[columns_to_show],
                use_container_width=True,
                hide_index=True,
                height=400
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
            fig_scatter = plot_accuracy_scatter(df_top_weapons, theme=theme_mode.lower())
            st.plotly_chart(fig_scatter, use_column_width=True)
            
            st.markdown("""
            **Insights:**
            - Bubble size represents the number of players using each weapon
            - Higher accuracy doesn't always mean more kills
            - Popular weapons tend to have varied accuracy depending on weapon characteristics
            """)
        
        st.divider()
        
        # === SECTION 4: TOP WEAPON CARDS ===
        st.header("🎖️ Top Weapon Profiles")
        
        # Display top 3 weapons
        cols = st.columns(3)
        
        for idx in range(min(3, len(df_top_weapons))):
            weapon = df_top_weapons.iloc[idx]
            
            with cols[idx]:
                # Card container with custom class
                st.markdown('<div class="weapon-card">', unsafe_allow_html=True)
                
                # Rank badge
                rank_emoji = ["🥇", "🥈", "🥉"][idx]
                st.markdown(f"### {rank_emoji} #{idx + 1}: {weapon['weapon_name']}")
                
                st.divider()
                
                # Stats
                st.metric("Total Kills", format_number(weapon['total_kills']))
                st.metric("Players Using", format_number(weapon['player_count']))
                st.metric("Avg Kills/Player", format_number(weapon['avg_kills_per_player'], 0))
                st.metric("Avg Accuracy", format_percentage(weapon['avg_accuracy']))
                
                st.markdown('</div>', unsafe_allow_html=True)
        
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
