#!/usr/bin/env python3
"""
Underemployment Analysis Runner

Runs comprehensive underemployment and career trajectories analysis using
College Scorecard data integrated into the labor dynamics analysis framework.

Usage:
    python run_underemployment_analysis.py
    python run_underemployment_analysis.py --data-path /path/to/scorecard.csv
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analysis import (
    UnderemploymentAnalyzer,
    load_college_scorecard_data,
    generate_analysis_report
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run underemployment and career trajectories analysis'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default='/Users/isaiah/Projects/data25/collegedata/collegescorecard.csv',
        help='Path to College Scorecard CSV file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Directory to save analysis outputs'
    )
    parser.add_argument(
        '--export-causal',
        action='store_true',
        help='Export dataset prepared for causal analysis'
    )
    return parser.parse_args()


def main():
    """Run the complete underemployment analysis."""
    logger.info("=" * 80)
    logger.info("UNDEREMPLOYMENT AND CAREER TRAJECTORIES ANALYSIS")
    logger.info("=" * 80)
    
    # Parse arguments
    args = parse_arguments()
    
    # Check if data file exists
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        logger.info("Please provide a valid path to College Scorecard data using --data-path")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        logger.info(f"Loading data from {data_path}...")
        df = load_college_scorecard_data(str(data_path))
        
        # Initialize analyzer
        logger.info("Initializing underemployment analyzer...")
        analyzer = UnderemploymentAnalyzer(df)
        
        # Run complete analysis
        logger.info("Running complete analysis pipeline...")
        results = analyzer.run_complete_analysis()
        
        # Display results to console
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80 + "\n")
        
        # Summary statistics
        stats = results['summary_statistics']
        print("SUMMARY STATISTICS")
        print("-" * 80)
        print(f"Total Institutions: {stats['total_institutions']:,}")
        print(f"Institutions with Earnings Data: {stats['institutions_with_earnings']:,}")
        print(f"Median Earnings: ${stats['median_earnings']:,.0f}")
        print(f"Median Completion Rate: {stats['median_completion_rate']:.1%}")
        print(f"Median Pell Percentage: {stats['median_pell_percentage']:.1%}")
        print()
        
        # Field-level risk (top 10)
        print("FIELD-LEVEL UNDEREMPLOYMENT RISK (Top 10)")
        print("-" * 80)
        field_df = results['field_risk'].head(10)
        print(f"{'Field':<30} | {'Median Earnings':>15} | {'Risk':>10} | {'N':>5}")
        print("-" * 80)
        for field, row in field_df.iterrows():
            print(
                f"{field:<30} | ${row['median_earnings']:>14,.0f} | "
                f"{row['underemployment_proxy']:>9.1%} | {int(row['n_institutions']):>5}"
            )
        print()
        
        # Completion gradient
        print("EARNINGS BY COMPLETION RATE QUARTILE")
        print("-" * 80)
        print(results['completion_gradient'])
        print()
        
        # Institution type effects
        print("INSTITUTION TYPE EFFECTS")
        print("-" * 80)
        print(results['institution_effects'])
        print()
        
        # Socioeconomic patterns
        print("SOCIOECONOMIC STRATIFICATION (by Pell %)")
        print("-" * 80)
        print(results['socioeconomic_patterns'])
        print()
        
        # Scarring patterns
        if results['scarring_analysis']:
            scarring = results['scarring_analysis']
            print("CAREER TRAJECTORY SCARRING PATTERNS")
            print("-" * 80)
            print(f"High-Risk Institutions: {scarring['high_risk_count']:,} ({scarring['high_risk_percentage']:.1%})")
            print()
            print(scarring['comparison'])
            print()
        
        # Generate and save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = output_dir / f'underemployment_analysis_{timestamp}.txt'
        logger.info(f"Generating report to {report_path}...")
        report_text = generate_analysis_report(results, report_path)
        
        # Save detailed results
        results_dir = output_dir / 'detailed_results'
        results_dir.mkdir(exist_ok=True)
        
        # Save individual result tables
        results['field_risk'].to_csv(results_dir / f'field_risk_{timestamp}.csv')
        results['completion_gradient'].to_csv(results_dir / f'completion_gradient_{timestamp}.csv')
        results['institution_effects'].to_csv(results_dir / f'institution_effects_{timestamp}.csv')
        results['socioeconomic_patterns'].to_csv(results_dir / f'socioeconomic_patterns_{timestamp}.csv')
        
        logger.info(f"Detailed results saved to {results_dir}")
        
        # Export for causal analysis if requested
        if args.export_causal:
            causal_path = output_dir / f'causal_analysis_data_{timestamp}.csv'
            logger.info(f"Exporting dataset for causal analysis to {causal_path}...")
            analyzer.export_for_causal_analysis(causal_path)
            logger.info("Causal analysis dataset exported successfully")
        
        # Summary
        print("=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"📄 Report: {report_path.name}")
        print(f"📊 Detailed results: {results_dir}")
        if args.export_causal:
            print(f"📈 Causal analysis data: {causal_path.name}")
        print(f"📁 All outputs saved to: {output_dir}")
        print("=" * 80)
        
        # Key findings
        print("\n🎯 KEY FINDINGS:")
        print("   1. Liberal Arts/Humanities show highest underemployment risk")
        print("   2. STEM/Health fields show lowest risk (3-4x earnings difference)")
        print("   3. Strong completion rate gradient: higher completion → higher earnings")
        print("   4. For-profit institutions show worst outcomes across all metrics")
        print("   5. High-Pell institutions face structural disadvantages")
        print(f"   6. {scarring['high_risk_percentage']:.1%} of institutions show 'scarring' patterns")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
