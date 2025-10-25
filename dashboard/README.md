# BF6 Meta Dashboard

Streamlit dashboard for visualizing Battlefield 6 weapon meta statistics.

## Features

### MVP Version (Current)
- **Top 3 Weapons Display**: Bar chart showing the most popular weapons by total kills
- **Key Metrics**: Total kills, player count, average accuracy, and headshot percentage
- **Detailed Statistics**: Table view with all weapon stats
- **Accuracy Analysis**: Scatter plot showing relationship between accuracy and kills
- **Weapon Profiles**: Individual cards for each top weapon
- **Data Refresh**: Manual refresh button to clear cache
- **CSV Export**: Download statistics as CSV file

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Dashboard

```bash
# From project root
streamlit run dashboard/app.py

# The dashboard will open in your browser at http://localhost:8501
```

## Configuration

The dashboard requires:
1. **BigQuery credentials**: `config/bigquery-key.json` (service account)
2. **BigQuery tables**: Gold layer tables from DBT transformations
   - `bf6_meta_gold.gold_top_weapons_global`
   - `bf6_meta_gold.gold_weapon_type_rankings`
   - `bf6_meta_gold.gold_player_rankings`

## Project Structure

```
dashboard/
├── app.py                  # Main Streamlit application
├── utils/
│   ├── __init__.py        # Package initialization
│   ├── bigquery.py        # BigQuery connector with caching
│   └── charts.py          # Plotly visualization functions
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features Breakdown

### Main Dashboard (app.py)
- **Header**: Project branding and title
- **Sidebar**: Controls, data status, about section
- **Key Metrics**: 4 metric cards with summary statistics
- **Top 3 Chart**: Horizontal bar chart (Plotly)
- **Detailed View**: Tabs for table and scatter plot
- **Weapon Cards**: 3 cards with individual weapon profiles

### BigQuery Module (utils/bigquery.py)
- **Cached Queries**: 10-minute TTL for performance
- **Functions**:
  - `load_top_weapons()`: Get top 3 weapons
  - `load_weapon_types_stats()`: Stats by weapon type
  - `load_player_rankings()`: Player leaderboard
  - `get_last_extraction_date()`: Last data update
  - `clear_cache()`: Force refresh

### Charts Module (utils/charts.py)
- **Plotly Charts**:
  - `plot_top_weapons_bar()`: Horizontal bar chart
  - `plot_accuracy_scatter()`: Accuracy vs Kills scatter
  - `plot_weapon_types_comparison()`: Grouped bar chart
  - `plot_player_weapons_pie()`: Weapon distribution pie chart
- **Formatters**:
  - `format_number()`: Thousands separator
  - `format_percentage()`: Decimal to percentage

## Data Flow

```
BigQuery Gold Layer
    ↓
Cached Query (10 min TTL)
    ↓
Pandas DataFrame
    ↓
Plotly Chart / Streamlit Table
    ↓
Browser Display
```

## Usage Tips

1. **First Load**: May take 2-3 seconds to query BigQuery
2. **Cache**: Subsequent loads are instant (10-minute cache)
3. **Refresh**: Click "Refresh Data" to force new query
4. **Export**: Use "Download as CSV" button for offline analysis

## Future Enhancements (Phase 4.1)

- [ ] Page 2: Weapon Type Comparison
- [ ] Page 3: Player Profiles
- [ ] Filters: Date range, weapon type, player tier
- [ ] Historical Trends: Week-over-week changes
- [ ] Auto-refresh: Scheduled data updates
- [ ] Deploy: Streamlit Cloud hosting

## Troubleshooting

### "BigQuery credentials not found"
- Ensure `config/bigquery-key.json` exists
- Check file path is correct relative to project root

### "No data available"
- Run `dbt run` to populate Gold tables
- Verify tables exist in BigQuery console

### Charts not displaying
- Check browser console for JavaScript errors
- Try clearing browser cache

## Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python Graphing](https://plotly.com/python/)
- [BigQuery Client Library](https://cloud.google.com/python/docs/reference/bigquery/latest)
