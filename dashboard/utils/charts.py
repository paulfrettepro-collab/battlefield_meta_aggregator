"""
Chart Utilities for BF6 Meta Dashboard

This module provides reusable Plotly chart functions for the dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_top_weapons_bar(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Create a horizontal bar chart of top weapons by total kills.
    
    Args:
        df: DataFrame with columns: weapon_name, total_kills, weapon_type
        theme: "dark" or "light" mode
        
    Returns:
        plotly.graph_objects.Figure: Configured bar chart
    """
    # Define color palette
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    # Theme colors
    if theme == "dark":
        bg_color = 'rgba(14, 17, 23, 0)'
        text_color = '#FAFAFA'
        grid_color = 'rgba(255, 255, 255, 0.1)'
    else:
        bg_color = 'rgba(255, 255, 255, 0)'
        text_color = '#262730'
        grid_color = 'rgba(0, 0, 0, 0.1)'
    
    fig = px.bar(
        df,
        x='total_kills',
        y='weapon_name',
        orientation='h',
        color='weapon_type',
        color_discrete_sequence=colors,
        hover_data={
            'weapon_name': False,
            'weapon_type': True,
            'total_kills': ':,',
            'avg_accuracy': ':.1%',
            'player_count': True
        },
        labels={
            'total_kills': 'Total Kills',
            'weapon_name': 'Weapon',
            'weapon_type': 'Type'
        }
    )
    
    fig.update_layout(
        title={
            'text': '🏆 Top 3 Weapons by Total Kills',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'weight': 'bold', 'color': text_color}
        },
        xaxis_title="Total Kills",
        yaxis_title="",
        showlegend=True,
        legend_title="Weapon Type",
        height=400,
        hovermode='closest',
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font={'color': text_color}
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=grid_color,
        color=text_color
    )
    fig.update_yaxes(showgrid=False, color=text_color)
    
    return fig


def plot_weapon_types_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Create a grouped bar chart comparing weapon types.
    
    Args:
        df: DataFrame with columns: weapon_type, total_kills, avg_accuracy, avg_damage
        
    Returns:
        plotly.graph_objects.Figure: Configured grouped bar chart
    """
    fig = go.Figure()
    
    # Add bars for each metric
    fig.add_trace(go.Bar(
        name='Total Kills',
        x=df['weapon_type'],
        y=df['total_kills'],
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
        title={
            'text': '📊 Weapon Types Comparison',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Weapon Type",
        yaxis_title="Total Kills",
        height=500,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig


def plot_accuracy_scatter(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """
    Create a scatter plot of accuracy vs kills.
    
    Args:
        df: DataFrame with columns: weapon_name, total_kills, avg_accuracy
        theme: "dark" or "light" mode
        
    Returns:
        plotly.graph_objects.Figure: Configured scatter plot
    """
    # Theme colors
    if theme == "dark":
        bg_color = 'rgba(14, 17, 23, 0)'
        text_color = '#FAFAFA'
        grid_color = 'rgba(255, 255, 255, 0.1)'
    else:
        bg_color = 'rgba(255, 255, 255, 0)'
        text_color = '#262730'
        grid_color = 'rgba(0, 0, 0, 0.1)'
    
    fig = px.scatter(
        df,
        x='avg_accuracy',
        y='total_kills',
        size='player_count',
        color='weapon_type',
        hover_name='weapon_name',
        hover_data={
            'avg_accuracy': ':.1%',
            'total_kills': ':,',
            'player_count': True
        },
        labels={
            'avg_accuracy': 'Average Accuracy',
            'total_kills': 'Total Kills',
            'weapon_type': 'Type'
        }
    )
    
    fig.update_layout(
        title={
            'text': '🎯 Accuracy vs Kills',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': text_color}
        },
        height=500,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font={'color': text_color}
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=grid_color,
        tickformat='.0%',
        color=text_color
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=grid_color,
        color=text_color
    )
    
    return fig


def plot_player_weapons_pie(df: pd.DataFrame) -> go.Figure:
    """
    Create a pie chart of player's weapon distribution by kills.
    
    Args:
        df: DataFrame with columns: weapon_name, kills
        
    Returns:
        plotly.graph_objects.Figure: Configured pie chart
    """
    fig = px.pie(
        df,
        values='kills',
        names='weapon_name',
        hole=0.4,  # Donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        title={
            'text': '🔫 Weapon Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=400,
        showlegend=True
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Kills: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )
    
    return fig


def create_metric_card(label: str, value: str, delta: str = None) -> dict:
    """
    Create data for a Streamlit metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        
    Returns:
        dict: Metric configuration
    """
    return {
        'label': label,
        'value': value,
        'delta': delta
    }


def format_number(num: float, precision: int = 0) -> str:
    """
    Format a number with thousands separator.
    
    Args:
        num: Number to format
        precision: Decimal precision
        
    Returns:
        str: Formatted number
    """
    if precision == 0:
        return f"{int(num):,}"
    return f"{num:,.{precision}f}"


def format_percentage(num: float, precision: int = 1) -> str:
    """
    Format a number as percentage.
    
    Args:
        num: Number to format (0.235 -> 23.5%)
        precision: Decimal precision
        
    Returns:
        str: Formatted percentage
    """
    return f"{num * 100:.{precision}f}%"
