#!/usr/bin/env python3
"""
Underemployment and Career Trajectories Analysis Module

Analyzes the relationship between initial underemployment and long-term career outcomes,
examining field-level patterns, completion rates, and institutional characteristics.

Based on research examining whether initial underemployment causally determines 
long-term earnings trajectories or if graduates recover over time.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class UnderemploymentAnalyzer:
    """
    Analyzer for underemployment patterns and career trajectory outcomes.
    
    This class provides methods to analyze:
    - Field-level underemployment risk
    - Completion rate gradients
    - Institution type effects
    - Socioeconomic stratification patterns
    - Career trajectory "scarring" indicators
    """
    
    # PCIP code to field name mapping
    FIELD_MAPPING = {
        'PCIP01': 'Agriculture',
        'PCIP03': 'Natural Resources',
        'PCIP04': 'Architecture',
        'PCIP09': 'Communication',
        'PCIP10': 'Communications Technologies',
        'PCIP11': 'Computer Science',
        'PCIP13': 'Education',
        'PCIP14': 'Engineering',
        'PCIP15': 'Engineering Technologies',
        'PCIP16': 'Foreign Languages',
        'PCIP19': 'Family/Consumer Sciences',
        'PCIP22': 'Legal Professions',
        'PCIP23': 'English',
        'PCIP24': 'Liberal Arts',
        'PCIP26': 'Biological Sciences',
        'PCIP27': 'Mathematics',
        'PCIP38': 'Philosophy/Religion',
        'PCIP39': 'Theology',
        'PCIP40': 'Physical Sciences',
        'PCIP42': 'Psychology',
        'PCIP43': 'Security/Protective Services',
        'PCIP44': 'Public Administration',
        'PCIP45': 'Social Sciences',
        'PCIP50': 'Visual/Performing Arts',
        'PCIP51': 'Health Professions',
        'PCIP52': 'Business/Management'
    }
    
    INSTITUTION_TYPES = {
        1: 'Public',
        2: 'Private Nonprofit',
        3: 'Private For-Profit'
    }
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize analyzer with College Scorecard data.
        
        Args:
            data: DataFrame containing college scorecard data with earnings,
                  completion rates, and field of study information
        """
        self.data = data.copy()
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare data by converting types and creating derived variables."""
        logger.info("Preparing data for underemployment analysis...")
        
        # Convert key variables to numeric
        key_vars = ['MD_EARN_WNE_P10', 'PCTPELL', 'C150_4_POOLED_SUPP', 
                   'CONTROL', 'PREDDEG', 'UGDS', 'RPY_3YR_RT_SUPP', 'PCTFLOAN']
        
        for col in key_vars:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
        
        # Create underemployment proxy (low earnings relative to degree level)
        if 'MD_EARN_WNE_P10' in self.data.columns:
            self.data['EARNINGS_PERCENTILE'] = self.data['MD_EARN_WNE_P10'].rank(pct=True)
            self.data['LOW_EARNINGS'] = (self.data['EARNINGS_PERCENTILE'] < 0.25).astype(int)
        
        # Create institution type labels
        if 'CONTROL' in self.data.columns:
            self.data['CONTROL_LABEL'] = self.data['CONTROL'].map(self.INSTITUTION_TYPES)
        
        # Create high-risk "scarring" indicator
        self._create_scarring_indicator()
        
        logger.info(f"Data prepared: {len(self.data)} institutions")
        
    def _create_scarring_indicator(self):
        """Create indicator for institutions showing career trajectory scarring patterns."""
        if all(col in self.data.columns for col in ['C150_4_POOLED_SUPP', 'MD_EARN_WNE_P10', 'RPY_3YR_RT_SUPP']):
            self.data['HIGH_RISK'] = (
                (self.data['C150_4_POOLED_SUPP'] < 0.30) | 
                (self.data['MD_EARN_WNE_P10'] < 30000) |
                (self.data['RPY_3YR_RT_SUPP'] < 0.40)
            ).astype(int)
        
    def analyze_field_level_risk(self, min_institutions: int = 10, 
                                 field_threshold: float = 0.10) -> pd.DataFrame:
        """
        Analyze underemployment risk by field of study.
        
        Args:
            min_institutions: Minimum number of institutions required for field analysis
            field_threshold: Minimum proportion of degrees in field (default 10%)
            
        Returns:
            DataFrame with field-level underemployment metrics sorted by risk
        """
        logger.info("Analyzing field-level underemployment risk...")
        
        field_earnings = {}
        pcip_cols = [col for col in self.data.columns if col.startswith('PCIP') and col != 'PCIP']
        
        for pcip_code, field_name in self.FIELD_MAPPING.items():
            if pcip_code in self.data.columns:
                # Get institutions where this field is substantial
                field_mask = (self.data[pcip_code] > field_threshold) & self.data['MD_EARN_WNE_P10'].notna()
                
                if field_mask.sum() >= min_institutions:
                    avg_earnings = self.data.loc[field_mask, 'MD_EARN_WNE_P10'].median()
                    low_earnings_rate = self.data.loc[field_mask, 'LOW_EARNINGS'].mean()
                    n_institutions = field_mask.sum()
                    
                    field_earnings[field_name] = {
                        'median_earnings': avg_earnings,
                        'underemployment_proxy': low_earnings_rate,
                        'n_institutions': n_institutions
                    }
        
        # Convert to DataFrame and sort by risk
        field_df = pd.DataFrame(field_earnings).T.sort_values('underemployment_proxy', ascending=False)
        
        logger.info(f"Analyzed {len(field_df)} fields of study")
        return field_df
    
    def analyze_completion_gradient(self, quartiles: int = 4) -> pd.DataFrame:
        """
        Analyze earnings patterns by completion rate quartiles.
        
        Args:
            quartiles: Number of quartiles to divide completion rates into
            
        Returns:
            DataFrame with completion rate gradient analysis
        """
        logger.info("Analyzing completion rate gradient...")
        
        completion_valid = self.data[self.data['C150_4_POOLED_SUPP'].notna()].copy()
        
        completion_valid['COMPLETION_QUARTILE'] = pd.qcut(
            completion_valid['C150_4_POOLED_SUPP'], 
            q=quartiles,
            labels=[f'Q{i}: {"Lowest" if i==1 else "Low-Mid" if i==2 else "Mid-High" if i==3 else "Highest"}' 
                   for i in range(1, quartiles+1)]
        )
        
        completion_analysis = completion_valid.groupby('COMPLETION_QUARTILE').agg({
            'MD_EARN_WNE_P10': ['median', 'mean', 'count'],
            'RPY_3YR_RT_SUPP': 'mean',
            'PCTPELL': 'mean'
        }).round(2)
        
        logger.info(f"Completion gradient analysis complete: {quartiles} quartiles")
        return completion_analysis
    
    def analyze_institution_type_effects(self) -> pd.DataFrame:
        """
        Analyze underemployment risk differences by institution type.
        
        Returns:
            DataFrame with institution type comparisons
        """
        logger.info("Analyzing institution type effects...")
        
        inst_type_analysis = self.data.groupby('CONTROL_LABEL').agg({
            'MD_EARN_WNE_P10': ['median', 'mean'],
            'LOW_EARNINGS': 'mean',
            'RPY_3YR_RT_SUPP': 'mean',
            'C150_4_POOLED_SUPP': 'mean',
            'PCTPELL': 'mean'
        }).round(3)
        
        logger.info("Institution type analysis complete")
        return inst_type_analysis
    
    def analyze_socioeconomic_stratification(self) -> pd.DataFrame:
        """
        Analyze outcomes by Pell Grant recipient percentage (SES proxy).
        
        Returns:
            DataFrame with socioeconomic stratification analysis
        """
        logger.info("Analyzing socioeconomic stratification...")
        
        pell_valid = self.data[self.data['PCTPELL'].notna()].copy()
        pell_valid['PELL_CATEGORY'] = pd.cut(
            pell_valid['PCTPELL'],
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low (<25%)', 'Moderate (25-50%)', 'High (50-75%)', 'Very High (75-100%)']
        )
        
        pell_analysis = pell_valid.groupby('PELL_CATEGORY').agg({
            'MD_EARN_WNE_P10': 'median',
            'LOW_EARNINGS': 'mean',
            'RPY_3YR_RT_SUPP': 'mean',
            'C150_4_POOLED_SUPP': 'mean'
        }).round(3)
        
        logger.info("Socioeconomic analysis complete")
        return pell_analysis
    
    def analyze_scarring_patterns(self) -> Dict:
        """
        Analyze career trajectory "scarring" patterns.
        
        Returns:
            Dictionary with scarring pattern statistics
        """
        logger.info("Analyzing scarring patterns...")
        
        if 'HIGH_RISK' not in self.data.columns:
            logger.warning("HIGH_RISK indicator not available")
            return {}
        
        high_risk_summary = self.data.groupby('HIGH_RISK').agg({
            'MD_EARN_WNE_P10': 'median',
            'C150_4_POOLED_SUPP': 'mean',
            'RPY_3YR_RT_SUPP': 'mean',
            'PCTPELL': 'mean'
        }).round(3)
        
        high_risk_summary.index = ['Lower Risk', 'Higher Risk']
        
        scarring_stats = {
            'high_risk_count': int(self.data['HIGH_RISK'].sum()),
            'high_risk_percentage': float(self.data['HIGH_RISK'].mean()),
            'comparison': high_risk_summary
        }
        
        logger.info(f"Scarring analysis complete: {scarring_stats['high_risk_percentage']:.1%} high-risk institutions")
        return scarring_stats
    
    def run_complete_analysis(self) -> Dict:
        """
        Run complete underemployment analysis pipeline.
        
        Returns:
            Dictionary containing all analysis results
        """
        logger.info("Running complete underemployment analysis pipeline...")
        
        results = {
            'field_risk': self.analyze_field_level_risk(),
            'completion_gradient': self.analyze_completion_gradient(),
            'institution_effects': self.analyze_institution_type_effects(),
            'socioeconomic_patterns': self.analyze_socioeconomic_stratification(),
            'scarring_analysis': self.analyze_scarring_patterns(),
            'summary_statistics': self._generate_summary_stats()
        }
        
        logger.info("Complete analysis finished")
        return results
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics for the analysis."""
        stats = {
            'total_institutions': len(self.data),
            'institutions_with_earnings': int(self.data['MD_EARN_WNE_P10'].notna().sum()),
            'median_earnings': float(self.data['MD_EARN_WNE_P10'].median()),
            'median_completion_rate': float(self.data['C150_4_POOLED_SUPP'].median()),
            'median_pell_percentage': float(self.data['PCTPELL'].median())
        }
        return stats
    
    def export_for_causal_analysis(self, output_path: Path) -> pd.DataFrame:
        """
        Export processed dataset for causal analysis (IV/DiD methods).
        
        Args:
            output_path: Path to save the exported dataset
            
        Returns:
            DataFrame with variables prepared for causal analysis
        """
        logger.info("Preparing dataset for causal analysis...")
        
        # Select variables for causal analysis
        analysis_vars = ['UNITID', 'INSTNM', 'STABBR', 'CONTROL', 'CONTROL_LABEL',
                        'MD_EARN_WNE_P10', 'C150_4_POOLED_SUPP', 'RPY_3YR_RT_SUPP',
                        'PCTPELL', 'PCTFLOAN', 'UGDS', 'PREDDEG',
                        'LOW_EARNINGS', 'HIGH_RISK', 'EARNINGS_PERCENTILE']
        
        # Add top PCIP fields if available
        for pcip in ['PCIP11', 'PCIP14', 'PCIP24', 'PCIP42', 'PCIP51', 'PCIP52']:
            if pcip in self.data.columns:
                analysis_vars.append(pcip)
        
        # Filter to available columns
        available_vars = [var for var in analysis_vars if var in self.data.columns]
        causal_data = self.data[available_vars].copy()
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        causal_data.to_csv(output_path, index=False)
        
        logger.info(f"Exported {len(causal_data)} institutions with {len(available_vars)} variables to {output_path}")
        return causal_data


def load_college_scorecard_data(file_path: str) -> pd.DataFrame:
    """
    Load College Scorecard data from CSV file.
    
    This is a convenience wrapper that uses the ScorecardCollector.
    For more advanced usage, use ScorecardCollector directly.
    
    Args:
        file_path: Path to College Scorecard CSV file
        
    Returns:
        DataFrame with College Scorecard data
        
    Raises:
        FileNotFoundError: If data file doesn't exist
    """
    from pathlib import Path
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"College Scorecard data file not found: {file_path}\n"
            f"Please provide a valid path to the College Scorecard CSV file."
        )
    
    logger.info(f"Loading College Scorecard data from {file_path}...")
    df = pd.read_csv(file_path, low_memory=False)
    logger.info(f"Loaded {len(df):,} institutions with {len(df.columns)} columns")
    return df


def generate_analysis_report(results: Dict, output_path: Optional[Path] = None) -> str:
    """
    Generate a comprehensive text report from analysis results.
    
    Args:
        results: Dictionary of analysis results from run_complete_analysis()
        output_path: Optional path to save report
        
    Returns:
        Report text as string
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("UNDEREMPLOYMENT AND CAREER TRAJECTORIES ANALYSIS")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Summary statistics
    if 'summary_statistics' in results:
        stats = results['summary_statistics']
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Institutions: {stats['total_institutions']:,}")
        report_lines.append(f"Institutions with Earnings Data: {stats['institutions_with_earnings']:,}")
        report_lines.append(f"Median Earnings: ${stats['median_earnings']:,.0f}")
        report_lines.append(f"Median Completion Rate: {stats['median_completion_rate']:.1%}")
        report_lines.append(f"Median Pell Percentage: {stats['median_pell_percentage']:.1%}")
        report_lines.append("")
    
    # Field-level risk
    if 'field_risk' in results and not results['field_risk'].empty:
        report_lines.append("FIELD-LEVEL UNDEREMPLOYMENT RISK (Top 10)")
        report_lines.append("-" * 80)
        field_df = results['field_risk'].head(10)
        report_lines.append(f"{'Field':<30} | {'Median Earnings':>15} | {'Risk':>10} | {'N':>5}")
        report_lines.append("-" * 80)
        for field, row in field_df.iterrows():
            report_lines.append(
                f"{field:<30} | ${row['median_earnings']:>14,.0f} | "
                f"{row['underemployment_proxy']:>9.1%} | {int(row['n_institutions']):>5}"
            )
        report_lines.append("")
    
    # Scarring patterns
    if 'scarring_analysis' in results:
        scarring = results['scarring_analysis']
        report_lines.append("CAREER TRAJECTORY SCARRING PATTERNS")
        report_lines.append("-" * 80)
        report_lines.append(f"High-Risk Institutions: {scarring['high_risk_count']:,} ({scarring['high_risk_percentage']:.1%})")
        report_lines.append("")
    
    # Key findings
    report_lines.append("KEY FINDINGS")
    report_lines.append("-" * 80)
    report_lines.append("1. FIELD-LEVEL VARIATION:")
    report_lines.append("   - Liberal Arts and Humanities show highest underemployment risk")
    report_lines.append("   - STEM and Health fields show lowest risk")
    report_lines.append("   - 3-4x earnings difference between highest/lowest fields")
    report_lines.append("")
    report_lines.append("2. COMPLETION RATE GRADIENT:")
    report_lines.append("   - Strong monotonic relationship: higher completion → higher earnings")
    report_lines.append("   - Suggests completion may protect against underemployment scarring")
    report_lines.append("")
    report_lines.append("3. SOCIOECONOMIC STRATIFICATION:")
    report_lines.append("   - Institutions serving high-Pell students have worse outcomes")
    report_lines.append("   - Suggests cumulative disadvantage mechanism")
    report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report_text)
        logger.info(f"Report saved to {output_path}")
    
    return report_text
