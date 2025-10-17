"""
National Center for Education Statistics (NCES) Data Collector

Handles fetching college enrollment and education data from NCES/IPEDS APIs.
"""

import requests
import pandas as pd
import logging
from typing import List, Dict, Optional, Union
import json

logger = logging.getLogger(__name__)


class NCESCollector:
    """Collector for National Center for Education Statistics data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NCES collector.
        
        Args:
            api_key: NCES API key (optional)
        """
        self.api_key = api_key
        self.base_url = "https://educationdata.urban.org/api/v1/"
        self.ipeds_url = "https://api.ed.gov/data/ipeds/"
        self.headers = {'Content-Type': 'application/json'}
        
        # Common enrollment data endpoints
        self.endpoints = {
            'enrollment_by_race': 'college-university/ipeds/fall-enrollment/race',
            'enrollment_by_gender': 'college-university/ipeds/fall-enrollment/gender', 
            'enrollment_totals': 'college-university/ipeds/fall-enrollment/totals',
            'completions': 'college-university/ipeds/completions-awards/degrees',
            'finance': 'college-university/ipeds/finance',
            'institutional_chars': 'college-university/ipeds/institutional-characteristics'
        }
        
    def fetch_enrollment_data(self, year: int, endpoint: str = 'enrollment_totals',
                             filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Fetch enrollment data for a specific year.
        
        Args:
            year: Academic year to fetch
            endpoint: Data endpoint to use
            filters: Additional filters for the API
            
        Returns:
            DataFrame with enrollment data
        """
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        url = f"{self.base_url}{self.endpoints[endpoint]}"
        
        params = {'year': year}
        if filters:
            params.update(filters)
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                df = pd.DataFrame(data['results'])
                df['data_year'] = year
                return df
            else:
                logger.warning(f"No results found for {endpoint} in {year}")
                return pd.DataFrame()
                
        except requests.RequestException as e:
            logger.error(f"Error fetching NCES data: {e}")
            return pd.DataFrame()
    
    def get_total_enrollment_trends(self, start_year: int = 2000, 
                                   end_year: int = 2023) -> pd.DataFrame:
        """
        Get total enrollment trends over multiple years.
        
        Args:
            start_year: Starting academic year
            end_year: Ending academic year
            
        Returns:
            DataFrame with enrollment trends
        """
        all_data = []
        
        for year in range(start_year, end_year + 1):
            df = self.fetch_enrollment_data(year, 'enrollment_totals')
            if not df.empty:
                all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Aggregate by year and institution type
            summary = combined_df.groupby(['data_year', 'inst_level']).agg({
                'fall_enrollment': 'sum',
                'unitid': 'count'  # Count of institutions
            }).reset_index()
            
            summary = summary.rename(columns={'unitid': 'institution_count'})
            
            return summary
        else:
            return pd.DataFrame()
    
    def get_enrollment_by_demographics(self, start_year: int = 2015, 
                                     end_year: int = 2023) -> Dict[str, pd.DataFrame]:
        """
        Get enrollment data segmented by demographics.
        
        Args:
            start_year: Starting academic year
            end_year: Ending academic year
            
        Returns:
            Dictionary of DataFrames for different demographic breakdowns
        """
        demographic_data = {}
        
        # Get race/ethnicity breakdown
        race_data = []
        for year in range(start_year, end_year + 1):
            df = self.fetch_enrollment_data(year, 'enrollment_by_race')
            if not df.empty:
                race_data.append(df)
        
        if race_data:
            demographic_data['by_race'] = pd.concat(race_data, ignore_index=True)
        
        # Get gender breakdown  
        gender_data = []
        for year in range(start_year, end_year + 1):
            df = self.fetch_enrollment_data(year, 'enrollment_by_gender')
            if not df.empty:
                gender_data.append(df)
        
        if gender_data:
            demographic_data['by_gender'] = pd.concat(gender_data, ignore_index=True)
        
        return demographic_data
    
    def get_completion_data(self, start_year: int = 2015, 
                           end_year: int = 2023) -> pd.DataFrame:
        """
        Get degree completion data.
        
        Args:
            start_year: Starting academic year
            end_year: Ending academic year
            
        Returns:
            DataFrame with completion data
        """
        completion_data = []
        
        for year in range(start_year, end_year + 1):
            df = self.fetch_enrollment_data(year, 'completions')
            if not df.empty:
                completion_data.append(df)
        
        if completion_data:
            combined_df = pd.concat(completion_data, ignore_index=True)
            
            # Aggregate by year, degree level, and field of study
            if 'cip2' in combined_df.columns and 'award_level' in combined_df.columns:
                summary = combined_df.groupby(['data_year', 'award_level', 'cip2']).agg({
                    'awards': 'sum'
                }).reset_index()
                
                return summary
            else:
                return combined_df
        else:
            return pd.DataFrame()
    
    def fetch_synthetic_enrollment_data(self, start_year: int = 2000,
                                       end_year: int = 2024) -> pd.DataFrame:
        """
        Generate synthetic enrollment data for development/testing purposes.
        This method creates realistic-looking data when API is unavailable.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            DataFrame with synthetic enrollment data
        """
        import numpy as np
        
        years = list(range(start_year, end_year + 1))
        
        # Base enrollment with trend
        base_enrollment = 18_000_000  # ~18M total enrollment in 2020
        growth_rate = 0.01  # 1% annual growth
        
        data = []
        for i, year in enumerate(years):
            # Add some realistic variation
            trend_factor = (1 + growth_rate) ** i
            seasonal_factor = 1 + 0.05 * np.sin(2 * np.pi * i / 4)  # 4-year cycle
            random_factor = 1 + np.random.normal(0, 0.02)  # 2% random variation
            
            total_enrollment = int(base_enrollment * trend_factor * seasonal_factor * random_factor)
            
            # Break down by institution level
            data.append({
                'year': year,
                'total_enrollment': total_enrollment,
                'undergraduate': int(total_enrollment * 0.78),  # ~78% undergraduate
                'graduate': int(total_enrollment * 0.18),       # ~18% graduate
                'professional': int(total_enrollment * 0.04),   # ~4% professional
                'public_institutions': int(total_enrollment * 0.72),  # ~72% public
                'private_institutions': int(total_enrollment * 0.28), # ~28% private
                'full_time': int(total_enrollment * 0.65),      # ~65% full-time
                'part_time': int(total_enrollment * 0.35),      # ~35% part-time
                'data_source': 'synthetic'
            })
        
        return pd.DataFrame(data)


def fetch_enrollment_data(years: Union[range, List[int]], 
                         api_key: Optional[str] = None,
                         use_synthetic: bool = False) -> pd.DataFrame:
    """
    Convenience function to fetch enrollment data.
    
    Args:
        years: Range or list of years to fetch
        api_key: NCES API key
        use_synthetic: Whether to use synthetic data for development
        
    Returns:
        DataFrame with enrollment data
    """
    if isinstance(years, range):
        start_year, end_year = years.start, years.stop - 1
    else:
        start_year, end_year = min(years), max(years)
    
    collector = NCESCollector(api_key)
    
    if use_synthetic:
        return collector.fetch_synthetic_enrollment_data(start_year, end_year)
    else:
        try:
            return collector.get_total_enrollment_trends(start_year, end_year)
        except Exception as e:
            logger.warning(f"Failed to fetch real data, using synthetic: {e}")
            return collector.fetch_synthetic_enrollment_data(start_year, end_year)