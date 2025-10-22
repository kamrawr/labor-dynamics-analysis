"""
College Scorecard Data Collector

Handles fetching and processing College Scorecard data for labor market outcomes analysis.
"""

import pandas as pd
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ScorecardCollector:
    """Collector for College Scorecard institutional data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Scorecard collector.
        
        Args:
            api_key: College Scorecard API key (optional, for API access)
        """
        self.api_key = api_key
        self.base_url = "https://api.data.gov/ed/collegescorecard/v1/"
        
    def load_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Load College Scorecard data from CSV file.
        
        Args:
            file_path: Path to College Scorecard CSV file
            
        Returns:
            DataFrame with College Scorecard data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"College Scorecard data file not found: {file_path}")
        
        logger.info(f"Loading College Scorecard data from {file_path}")
        df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Loaded {len(df):,} institutions with {len(df.columns)} columns")
        
        return df
    
    def fetch_from_api(self, year: int = 2021, fields: Optional[list] = None) -> pd.DataFrame:
        """
        Fetch College Scorecard data from API.
        
        Args:
            year: Academic year to fetch
            fields: List of field names to retrieve (optional)
            
        Returns:
            DataFrame with College Scorecard data
        """
        # Placeholder for API implementation
        logger.warning("API fetching not yet implemented - use load_from_file() instead")
        return pd.DataFrame()
    
    def get_earnings_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract earnings-related variables from Scorecard data.
        
        Args:
            df: Full College Scorecard DataFrame
            
        Returns:
            DataFrame with earnings variables
        """
        earnings_cols = [
            'UNITID', 'INSTNM', 'STABBR',
            'MD_EARN_WNE_P10',  # Median earnings 10 years after entry
            'MD_EARN_WNE_P6',   # Median earnings 6 years after entry
            'GT_25K_P10',        # Share earning >$25K after 10 years
        ]
        
        available_cols = [col for col in earnings_cols if col in df.columns]
        
        if not available_cols:
            logger.warning("No earnings columns found in data")
            return pd.DataFrame()
        
        return df[available_cols].copy()
    
    def get_completion_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract completion rate variables from Scorecard data.
        
        Args:
            df: Full College Scorecard DataFrame
            
        Returns:
            DataFrame with completion variables
        """
        completion_cols = [
            'UNITID', 'INSTNM', 'STABBR',
            'C150_4_POOLED_SUPP',  # Completion rate (150% time, 4-year)
            'C200_4_POOLED_SUPP',  # Completion rate (200% time, 4-year)
        ]
        
        available_cols = [col for col in completion_cols if col in df.columns]
        return df[available_cols].copy()
    
    def get_field_of_study_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract field of study (PCIP) variables from Scorecard data.
        
        Args:
            df: Full College Scorecard DataFrame
            
        Returns:
            DataFrame with field of study percentages
        """
        base_cols = ['UNITID', 'INSTNM', 'STABBR']
        pcip_cols = [col for col in df.columns if col.startswith('PCIP') and col != 'PCIP']
        
        if not pcip_cols:
            logger.warning("No PCIP (field of study) columns found")
            return df[base_cols].copy()
        
        return df[base_cols + pcip_cols].copy()


def load_scorecard_data(file_path: str) -> pd.DataFrame:
    """
    Convenience function to load College Scorecard data.
    
    Args:
        file_path: Path to College Scorecard CSV file
        
    Returns:
        DataFrame with College Scorecard data
    """
    collector = ScorecardCollector()
    return collector.load_from_file(file_path)
