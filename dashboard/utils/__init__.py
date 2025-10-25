"""Dashboard utilities package"""

from .bigquery import (
    get_bigquery_client,
    load_top_weapons,
    load_weapon_types_stats,
    load_player_rankings,
    load_player_weapons,
    get_last_extraction_date,
    clear_cache
)

from .charts import (
    plot_top_weapons_bar,
    plot_weapon_types_comparison,
    plot_accuracy_scatter,
    plot_player_weapons_pie,
    format_number,
    format_percentage
)

__all__ = [
    # BigQuery functions
    'get_bigquery_client',
    'load_top_weapons',
    'load_weapon_types_stats',
    'load_player_rankings',
    'load_player_weapons',
    'get_last_extraction_date',
    'clear_cache',
    
    # Chart functions
    'plot_top_weapons_bar',
    'plot_weapon_types_comparison',
    'plot_accuracy_scatter',
    'plot_player_weapons_pie',
    'format_number',
    'format_percentage',
]
