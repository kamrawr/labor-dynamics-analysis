"""
Plotting utilities for Labor Dynamics Analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple, Dict


def create_trend_plot(df: pd.DataFrame, x_col: str, y_col: str, 
                     title: str = None, save_path: str = None) -> plt.Figure:
    """
    Create a trend plot with trend line.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Main trend line
    ax.plot(df[x_col], df[y_col], marker='o', linewidth=2, markersize=6)
    
    # Add trend line
    z = np.polyfit(df[x_col], df[y_col], 1)
    p = np.poly1d(z)
    ax.plot(df[x_col], p(df[x_col]), "--", alpha=0.7, color='red', label='Trend')
    
    ax.set_xlabel(x_col.replace('_', ' ').title())
    ax.set_ylabel(y_col.replace('_', ' ').title())
    ax.set_title(title or f'{y_col.replace("_", " ").title()} Trend')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame, title: str = None, 
                             save_path: str = None) -> plt.Figure:
    """
    Create a correlation heatmap.
    
    Args:
        df: DataFrame to calculate correlations
        title: Plot title
        save_path: Path to save the plot
        
    Returns:
        matplotlib Figure object
    """
    # Calculate correlation matrix
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr_matrix = df[numeric_cols].corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.3f', cbar_kws={"shrink": .8}, ax=ax)
    
    ax.set_title(title or 'Correlation Matrix')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_trends(enrollment_data: pd.DataFrame, employment_data: pd.DataFrame,
               save_path: str = None) -> plt.Figure:
    """
    Create comprehensive trend plots for enrollment and employment data.
    
    Args:
        enrollment_data: Enrollment DataFrame
        employment_data: Employment DataFrame  
        save_path: Directory to save plots
        
    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Labor Dynamics: Comprehensive Trend Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Total Enrollment
    if 'total_enrollment' in enrollment_data.columns and 'year' in enrollment_data.columns:
        axes[0,0].plot(enrollment_data['year'], enrollment_data['total_enrollment']/1_000_000,
                      marker='o', linewidth=2, color='blue')
        axes[0,0].set_title('Total College Enrollment')
        axes[0,0].set_ylabel('Enrollment (Millions)')
        axes[0,0].grid(True, alpha=0.3)
    
    # Plot 2: Employment Level
    if 'employment_level' in employment_data.columns and 'year' in employment_data.columns:
        axes[0,1].plot(employment_data['year'], employment_data['employment_level']/1_000,
                      marker='s', linewidth=2, color='green')
        axes[0,1].set_title('Employment Level')
        axes[0,1].set_ylabel('Employment (Thousands)')
        axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Unemployment Rate
    if 'unemployment_rate' in employment_data.columns:
        axes[1,0].plot(employment_data['year'], employment_data['unemployment_rate'],
                      marker='^', linewidth=2, color='red')
        axes[1,0].set_title('Unemployment Rate')
        axes[1,0].set_ylabel('Rate (%)')
        axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: Enrollment Breakdown
    if all(col in enrollment_data.columns for col in ['undergraduate', 'graduate']):
        axes[1,1].plot(enrollment_data['year'], enrollment_data['undergraduate']/1_000_000,
                      label='Undergraduate', linewidth=2)
        axes[1,1].plot(enrollment_data['year'], enrollment_data['graduate']/1_000_000,
                      label='Graduate', linewidth=2)
        axes[1,1].set_title('Enrollment by Level')
        axes[1,1].set_ylabel('Enrollment (Millions)')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
    
    # Set x-labels for bottom plots
    axes[1,0].set_xlabel('Year')
    axes[1,1].set_xlabel('Year')
    
    plt.tight_layout()
    
    if save_path:
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_dir / 'comprehensive_trends.png', dpi=300, bbox_inches='tight')
    
    return fig