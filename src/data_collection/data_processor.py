"""
Data Processing Module for Labor Dynamics Analysis

Handles merging, cleaning, and preprocessing of data from multiple sources.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and merge data from multiple sources."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize data processor.
        
        Args:
            cache_dir: Directory for caching processed data
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/processed")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_enrollment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize enrollment data.
        
        Args:
            df: Raw enrollment data
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Standardize year column
        year_cols = ['year', 'data_year', 'academic_year']
        year_col = None
        for col in year_cols:
            if col in df_clean.columns:
                year_col = col
                break
        
        if year_col and year_col != 'year':
            df_clean = df_clean.rename(columns={year_col: 'year'})
        
        # Convert numeric columns
        numeric_cols = df_clean.select_dtypes(include=[object]).columns
        for col in numeric_cols:
            if col not in ['data_source', 'institution_type']:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove rows with all NaN values for key metrics
        key_metrics = ['total_enrollment', 'undergraduate', 'graduate']
        available_metrics = [col for col in key_metrics if col in df_clean.columns]
        if available_metrics:
            df_clean = df_clean.dropna(subset=available_metrics, how='all')
        
        # Sort by year
        if 'year' in df_clean.columns:
            df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        return df_clean
    
    def clean_employment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize employment data.
        
        Args:
            df: Raw employment data
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Convert date column if exists
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
            
            # Extract year if not present
            if 'year' not in df_clean.columns:
                df_clean['year'] = df_clean['date'].dt.year
        
        # Convert employment metrics to numeric
        employment_cols = [
            'civilian_labor_force', 'employment_level', 'unemployment_level',
            'unemployment_rate', 'labor_force_participation'
        ]
        
        for col in employment_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove duplicate entries (same year/period)
        if 'year' in df_clean.columns and 'period' in df_clean.columns:
            df_clean = df_clean.drop_duplicates(subset=['year', 'period'])
        
        return df_clean
    
    def merge_enrollment_employment(self, enrollment_df: pd.DataFrame, 
                                   employment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge enrollment and employment data on common time dimensions.
        
        Args:
            enrollment_df: Cleaned enrollment data
            employment_df: Cleaned employment data
            
        Returns:
            Merged DataFrame
        """
        if enrollment_df.empty or employment_df.empty:
            logger.warning("One or both datasets are empty, cannot merge")
            return pd.DataFrame()
        
        # Prepare enrollment data for merging
        enrollment_merge = enrollment_df.copy()
        if 'year' in enrollment_merge.columns:
            enrollment_agg = enrollment_merge.groupby('year').agg({
                col: 'sum' for col in enrollment_merge.select_dtypes(include=[np.number]).columns
                if col != 'year'
            }).reset_index()
            enrollment_agg.columns = [f"enrollment_{col}" if col != 'year' else col 
                                    for col in enrollment_agg.columns]
        
        # Prepare employment data for merging (use annual averages)
        employment_merge = employment_df.copy()
        if 'year' in employment_merge.columns:
            employment_agg = employment_merge.groupby('year').agg({
                col: 'mean' for col in employment_merge.select_dtypes(include=[np.number]).columns
                if col != 'year'
            }).reset_index()
            employment_agg.columns = [f"employment_{col}" if col != 'year' else col 
                                    for col in employment_agg.columns]
        
        # Merge on year
        merged_df = pd.merge(enrollment_agg, employment_agg, on='year', how='inner')
        
        return merged_df
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics and ratios.
        
        Args:
            df: Merged data DataFrame
            
        Returns:
            DataFrame with additional calculated metrics
        """
        df_with_metrics = df.copy()
        
        # Enrollment ratios
        if 'enrollment_total_enrollment' in df.columns:
            total_col = 'enrollment_total_enrollment'
            
            if 'enrollment_undergraduate' in df.columns:
                df_with_metrics['undergraduate_ratio'] = (
                    df_with_metrics['enrollment_undergraduate'] / 
                    df_with_metrics[total_col]
                )
            
            if 'enrollment_graduate' in df.columns:
                df_with_metrics['graduate_ratio'] = (
                    df_with_metrics['enrollment_graduate'] / 
                    df_with_metrics[total_col]
                )
        
        # Employment ratios
        if 'employment_civilian_labor_force' in df.columns and 'employment_employment_level' in df.columns:
            df_with_metrics['employment_ratio'] = (
                df_with_metrics['employment_employment_level'] / 
                df_with_metrics['employment_civilian_labor_force']
            )
        
        # Year-over-year growth rates
        if 'year' in df.columns:
            df_with_metrics = df_with_metrics.sort_values('year')
            
            # Enrollment growth
            if 'enrollment_total_enrollment' in df.columns:
                df_with_metrics['enrollment_growth_rate'] = (
                    df_with_metrics['enrollment_total_enrollment'].pct_change()
                )
            
            # Employment growth
            if 'employment_employment_level' in df.columns:
                df_with_metrics['employment_growth_rate'] = (
                    df_with_metrics['employment_employment_level'].pct_change()
                )
        
        return df_with_metrics
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> None:
        """
        Save processed data to cache.
        
        Args:
            df: DataFrame to save
            filename: Output filename
        """
        filepath = self.cache_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
    
    def load_processed_data(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load processed data from cache.
        
        Args:
            filename: Filename to load
            
        Returns:
            DataFrame if file exists, None otherwise
        """
        filepath = self.cache_dir / filename
        if filepath.exists():
            logger.info(f"Loading processed data from {filepath}")
            return pd.read_csv(filepath)
        return None


def process_and_merge(enrollment_data: pd.DataFrame, employment_data: pd.DataFrame,
                     save_cache: bool = True) -> pd.DataFrame:
    """
    Convenience function to process and merge datasets.
    
    Args:
        enrollment_data: Raw enrollment data
        employment_data: Raw employment data
        save_cache: Whether to save processed data to cache
        
    Returns:
        Processed and merged DataFrame
    """
    processor = DataProcessor()
    
    # Clean individual datasets
    clean_enrollment = processor.clean_enrollment_data(enrollment_data)
    clean_employment = processor.clean_employment_data(employment_data)
    
    # Merge datasets
    merged_data = processor.merge_enrollment_employment(clean_enrollment, clean_employment)
    
    # Calculate derived metrics
    final_data = processor.calculate_derived_metrics(merged_data)
    
    # Save to cache if requested
    if save_cache and not final_data.empty:
        processor.save_processed_data(final_data, "merged_labor_education_data.csv")
    
    return final_data