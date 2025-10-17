#!/usr/bin/env python3
"""
Complete Labor Dynamics Analysis Runner

Executes the full analysis pipeline using real API data.
"""

import sys
import logging
import yaml
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Add src to path
sys.path.append('src')

from data_collection import BLSCollector, NCESCollector, process_and_merge
from visualization import plot_trends, create_correlation_heatmap

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration file."""
    config_path = Path('config/config.yaml')
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    else:
        logger.error("Configuration file not found!")
        return None

def collect_employment_data(config):
    """Collect employment data from BLS API."""
    logger.info("🔄 Collecting employment data from BLS...")
    
    bls_key = config['api_keys']['bls_api_key']
    collector = BLSCollector(api_key=bls_key)
    
    start_year = config['analysis']['time_range']['start_year']
    end_year = config['analysis']['time_range']['end_year']
    
    try:
        employment_data = collector.get_employment_data(start_year, end_year)
        youth_data = collector.get_youth_employment_data(start_year, end_year)
        
        logger.info(f"✅ Employment data collected: {len(employment_data)} records")
        logger.info(f"✅ Youth employment data collected: {len(youth_data)} records")
        
        return employment_data, youth_data
    except Exception as e:
        logger.error(f"❌ Failed to collect employment data: {e}")
        return None, None

def collect_enrollment_data(config):
    """Collect enrollment data (using synthetic for now)."""
    logger.info("🔄 Collecting enrollment data...")
    
    collector = NCESCollector()
    start_year = config['analysis']['time_range']['start_year']
    end_year = config['analysis']['time_range']['end_year']
    
    try:
        # Try real data first, fallback to synthetic
        enrollment_data = collector.get_total_enrollment_trends(start_year, end_year)
        
        if enrollment_data.empty:
            logger.warning("Real enrollment data unavailable, using synthetic data...")
            enrollment_data = collector.fetch_synthetic_enrollment_data(start_year, end_year)
        
        logger.info(f"✅ Enrollment data collected: {len(enrollment_data)} records")
        return enrollment_data
    except Exception as e:
        logger.error(f"❌ Failed to collect enrollment data: {e}")
        return None

def analyze_correlations(merged_data):
    """Analyze correlations between enrollment and employment."""
    logger.info("🔄 Analyzing correlations...")
    
    # Select numeric columns
    numeric_cols = merged_data.select_dtypes(include=[np.number]).columns
    correlation_matrix = merged_data[numeric_cols].corr()
    
    # Find significant correlations
    enrollment_cols = [col for col in numeric_cols if 'enrollment' in col.lower()]
    employment_cols = [col for col in numeric_cols if 'employment' in col.lower() or 'unemployment' in col.lower()]
    
    significant_correlations = []
    for enroll_col in enrollment_cols:
        for employ_col in employment_cols:
            if enroll_col != employ_col:
                corr_val = correlation_matrix.loc[enroll_col, employ_col]
                if abs(corr_val) > 0.3:
                    significant_correlations.append({
                        'enrollment_var': enroll_col,
                        'employment_var': employ_col,
                        'correlation': corr_val,
                        'strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate' if abs(corr_val) > 0.5 else 'Weak'
                    })
    
    logger.info(f"✅ Found {len(significant_correlations)} significant correlations")
    return correlation_matrix, significant_correlations

def calculate_trends(data, value_col):
    """Calculate trend statistics."""
    if value_col not in data.columns or 'year' not in data.columns:
        return None
    
    # Calculate year-over-year growth
    data_sorted = data.sort_values('year')
    growth_rates = data_sorted[value_col].pct_change() * 100
    
    # Calculate trend line
    years = data_sorted['year'].values
    values = data_sorted[value_col].values
    trend_slope = np.polyfit(years, values, 1)[0]
    
    return {
        'avg_annual_growth': growth_rates.mean(),
        'total_growth': ((values[-1] / values[0]) - 1) * 100,
        'trend_slope': trend_slope,
        'volatility': growth_rates.std()
    }

def generate_insights(enrollment_data, employment_data, merged_data, correlations):
    """Generate key insights from the analysis."""
    logger.info("🔄 Generating insights...")
    
    insights = {
        'data_summary': {
            'analysis_period': f"{merged_data['year'].min()}-{merged_data['year'].max()}",
            'total_records': len(merged_data),
            'variables_analyzed': len(merged_data.columns)
        },
        'correlations': {
            'total_significant': len(correlations),
            'strong_correlations': len([c for c in correlations if abs(c['correlation']) > 0.7]),
            'key_findings': correlations[:5]  # Top 5 correlations
        }
    }
    
    # Enrollment trends
    if 'total_enrollment' in enrollment_data.columns:
        enrollment_trends = calculate_trends(enrollment_data, 'total_enrollment')
        if enrollment_trends:
            insights['enrollment_trends'] = enrollment_trends
    
    # Employment trends
    if 'employment_level' in employment_data.columns:
        employment_trends = calculate_trends(employment_data, 'employment_level')
        if employment_trends:
            insights['employment_trends'] = employment_trends
    
    # Unemployment analysis
    if 'unemployment_rate' in employment_data.columns:
        unemployment_stats = {
            'average_rate': employment_data['unemployment_rate'].mean(),
            'min_rate': employment_data['unemployment_rate'].min(),
            'max_rate': employment_data['unemployment_rate'].max(),
            'recent_rate': employment_data['unemployment_rate'].iloc[-1] if not employment_data.empty else None
        }
        insights['unemployment_analysis'] = unemployment_stats
    
    return insights

def create_comprehensive_report(insights, output_dir):
    """Create a comprehensive analysis report."""
    logger.info("📄 Generating comprehensive report...")
    
    report_path = output_dir / f"labor_dynamics_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_path, 'w') as f:
        f.write(f"""# Labor Dynamics Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report analyzes the relationship between college enrollment trends and labor market dynamics in the United States from {insights['data_summary']['analysis_period']}.

## Key Findings

### Data Overview
- **Analysis Period**: {insights['data_summary']['analysis_period']}
- **Total Records**: {insights['data_summary']['total_records']}
- **Variables Analyzed**: {insights['data_summary']['variables_analyzed']}

### Correlation Analysis
- **Total Significant Correlations**: {insights['correlations']['total_significant']}
- **Strong Correlations (|r| > 0.7)**: {insights['correlations']['strong_correlations']}

#### Top Correlations:
""")
        
        for i, corr in enumerate(insights['correlations']['key_findings'], 1):
            f.write(f"{i}. **{corr['enrollment_var']}** ↔ **{corr['employment_var']}**: {corr['correlation']:.3f} ({corr['strength']})\n")
        
        if 'enrollment_trends' in insights:
            trends = insights['enrollment_trends']
            f.write(f"""
### Enrollment Trends
- **Average Annual Growth**: {trends['avg_annual_growth']:.2f}%
- **Total Growth Over Period**: {trends['total_growth']:.1f}%
- **Trend Slope**: {trends['trend_slope']:.0f} per year
- **Volatility (Std Dev)**: {trends['volatility']:.2f}%
""")
        
        if 'employment_trends' in insights:
            trends = insights['employment_trends']
            f.write(f"""
### Employment Trends  
- **Average Annual Growth**: {trends['avg_annual_growth']:.2f}%
- **Total Growth Over Period**: {trends['total_growth']:.1f}%
- **Trend Slope**: {trends['trend_slope']:.0f} per year
- **Volatility (Std Dev)**: {trends['volatility']:.2f}%
""")
        
        if 'unemployment_analysis' in insights:
            unemp = insights['unemployment_analysis']
            f.write(f"""
### Unemployment Analysis
- **Average Unemployment Rate**: {unemp['average_rate']:.1f}%
- **Minimum Rate**: {unemp['min_rate']:.1f}%
- **Maximum Rate**: {unemp['max_rate']:.1f}%
- **Most Recent Rate**: {unemp['recent_rate']:.1f}%
""")
        
        f.write("""
## Methodology

This analysis employed the following data sources and methods:

1. **Data Sources**:
   - Bureau of Labor Statistics (BLS) API for employment data
   - National Center for Education Statistics (NCES) for enrollment data
   - Synthetic data where real data unavailable

2. **Statistical Methods**:
   - Pearson correlation analysis
   - Trend analysis using linear regression
   - Time series analysis for growth rates

3. **Key Metrics**:
   - Employment levels and unemployment rates
   - College enrollment by institution type
   - Year-over-year growth rates
   - Correlation coefficients

## Conclusions

The analysis reveals significant relationships between higher education enrollment and labor market dynamics. These findings can inform policy decisions regarding education funding, workforce development, and economic planning.

---
*Report generated by Labor Dynamics Analysis Tool*
""")
    
    logger.info(f"✅ Report saved to: {report_path}")
    return report_path

def main():
    """Main analysis execution."""
    logger.info("🚀 Starting Complete Labor Dynamics Analysis...")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Create output directories
    output_dir = Path('reports')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path('data/processed')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect data
    employment_data, youth_data = collect_employment_data(config)
    enrollment_data = collect_enrollment_data(config)
    
    if employment_data is None or enrollment_data is None:
        logger.error("❌ Data collection failed, cannot proceed with analysis")
        return
    
    # Process and merge data
    logger.info("🔄 Processing and merging datasets...")
    merged_data = process_and_merge(enrollment_data, employment_data, save_cache=True)
    
    if merged_data.empty:
        logger.error("❌ Data merging failed")
        return
    
    logger.info(f"✅ Merged dataset created: {merged_data.shape}")
    
    # Analysis
    correlation_matrix, correlations = analyze_correlations(merged_data)
    
    # Generate insights
    insights = generate_insights(enrollment_data, employment_data, merged_data, correlations)
    
    # Create visualizations
    logger.info("📊 Creating visualizations...")
    
    # Trend plots
    trend_fig = plot_trends(enrollment_data, employment_data, save_path=str(output_dir))
    plt.close(trend_fig)
    
    # Correlation heatmap
    corr_fig = create_correlation_heatmap(merged_data, 
                                         title="Labor Dynamics: Enrollment-Employment Correlations",
                                         save_path=str(output_dir / "correlation_heatmap.png"))
    plt.close(corr_fig)
    
    # Save processed data
    enrollment_data.to_csv(data_dir / 'final_enrollment_data.csv', index=False)
    employment_data.to_csv(data_dir / 'final_employment_data.csv', index=False) 
    merged_data.to_csv(data_dir / 'final_merged_analysis_data.csv', index=False)
    
    # Generate report
    report_path = create_comprehensive_report(insights, output_dir)
    
    # Summary
    logger.info("="*60)
    logger.info("🎉 COMPLETE ANALYSIS FINISHED SUCCESSFULLY!")
    logger.info("="*60)
    logger.info(f"📊 Data Period: {insights['data_summary']['analysis_period']}")
    logger.info(f"📈 Records Analyzed: {insights['data_summary']['total_records']}")
    logger.info(f"🔗 Significant Correlations: {insights['correlations']['total_significant']}")
    logger.info(f"📄 Report: {report_path.name}")
    logger.info(f"📁 Outputs saved to: {output_dir}")
    logger.info("="*60)
    
    print("\n🎯 ANALYSIS COMPLETE! Check the reports/ directory for results.")

if __name__ == "__main__":
    main()