"""
Visualization Module for Labor Dynamics Analysis

Provides plotting utilities and dashboard functions for analysis results.
"""

from .plots import create_trend_plot, create_correlation_heatmap, plot_trends
from .dashboard import create_dashboard, generate_report

__all__ = [
    'create_trend_plot',
    'create_correlation_heatmap', 
    'plot_trends',
    'create_dashboard',
    'generate_report'
]