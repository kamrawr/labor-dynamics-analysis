"""
Bureau of Labor Statistics (BLS) Data Collector

Handles fetching employment, unemployment, and labor force data from the BLS API.
"""

import requests
import pandas as pd
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class BLSCollector:
    """Collector for Bureau of Labor Statistics data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS collector.
        
        Args:
            api_key: BLS API key (optional but recommended for higher rate limits)
        """
        self.api_key = api_key
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        self.headers = {'Content-type': 'application/json'}
        
        # Common BLS series IDs
        self.series_ids = {
            'civilian_labor_force': 'LNS11300000',
            'employment_level': 'LNS12300000',
            'unemployment_level': 'LNS13000000',
            'unemployment_rate': 'LNS14000000',
            'labor_force_participation': 'LNS11300012',
            'employment_pop_ratio': 'LNS12300012',
        }
        
        # Youth employment series (16-24 years)
        self.youth_series = {
            'youth_labor_force': 'LNS11300012',
            'youth_employment': 'LNS12300012',
            'youth_unemployment_rate': 'LNS14000012',
        }
    
    def fetch_series_data(self, series_ids: List[str], start_year: int, 
                         end_year: int) -> pd.DataFrame:
        """
        Fetch data for specific BLS series.
        
        Args:
            series_ids: List of BLS series IDs
            start_year: Starting year for data
            end_year: Ending year for data
            
        Returns:
            DataFrame with BLS data
        """
        data_frames = []
        
        # BLS API limits to 50 series per request
        chunk_size = 50
        for i in range(0, len(series_ids), chunk_size):
            chunk_ids = series_ids[i:i + chunk_size]
            
            payload = {
                'seriesid': chunk_ids,
                'startyear': str(start_year),
                'endyear': str(end_year)
            }
            
            if self.api_key:
                payload['registrationkey'] = self.api_key
            
            try:
                response = requests.post(
                    self.base_url, 
                    json=payload, 
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data['status'] != 'REQUEST_SUCCEEDED':
                    logger.warning(f"BLS API warning: {data.get('message', 'Unknown error')}")
                
                # Process series data
                for series in data['Results']['series']:
                    series_id = series['seriesID']
                    series_data = []
                    
                    for item in series['data']:
                        series_data.append({
                            'series_id': series_id,
                            'year': int(item['year']),
                            'period': item['period'],
                            'value': float(item['value']) if item['value'] != '' else None,
                            'date': self._parse_bls_date(item['year'], item['period'])
                        })
                    
                    if series_data:
                        df = pd.DataFrame(series_data)
                        data_frames.append(df)
                
                # Rate limiting for API
                time.sleep(0.5)
                
            except requests.RequestException as e:
                logger.error(f"Error fetching BLS data: {e}")
                continue
        
        if data_frames:
            return pd.concat(data_frames, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def _parse_bls_date(self, year: str, period: str) -> pd.Timestamp:
        """Parse BLS year/period format to datetime."""
        try:
            if period.startswith('M'):
                month = int(period[1:])
                return pd.Timestamp(year=int(year), month=month, day=1)
            elif period.startswith('Q'):
                quarter = int(period[1:])
                month = (quarter - 1) * 3 + 1
                return pd.Timestamp(year=int(year), month=month, day=1)
            else:
                # Annual data
                return pd.Timestamp(year=int(year), month=1, day=1)
        except ValueError:
            return pd.NaT
    
    def get_employment_data(self, start_year: int = 2000, 
                           end_year: int = 2024) -> pd.DataFrame:
        """
        Get comprehensive employment data.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            DataFrame with employment metrics
        """
        series_list = list(self.series_ids.values())
        df = self.fetch_series_data(series_list, start_year, end_year)
        
        if df.empty:
            return df
        
        # Pivot to wide format
        df_pivot = df.pivot_table(
            index=['year', 'period', 'date'], 
            columns='series_id', 
            values='value'
        ).reset_index()
        
        # Rename columns with meaningful names
        reverse_mapping = {v: k for k, v in self.series_ids.items()}
        df_pivot = df_pivot.rename(columns=reverse_mapping)
        
        return df_pivot
    
    def get_youth_employment_data(self, start_year: int = 2000, 
                                 end_year: int = 2024) -> pd.DataFrame:
        """
        Get youth (16-24) employment data.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            DataFrame with youth employment metrics
        """
        series_list = list(self.youth_series.values())
        df = self.fetch_series_data(series_list, start_year, end_year)
        
        if df.empty:
            return df
        
        df_pivot = df.pivot_table(
            index=['year', 'period', 'date'], 
            columns='series_id', 
            values='value'
        ).reset_index()
        
        reverse_mapping = {v: k for k, v in self.youth_series.items()}
        df_pivot = df_pivot.rename(columns=reverse_mapping)
        
        return df_pivot


def fetch_employment_data(years: Union[range, List[int]], 
                         api_key: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to fetch employment data.
    
    Args:
        years: Range or list of years to fetch
        api_key: BLS API key
        
    Returns:
        DataFrame with employment data
    """
    if isinstance(years, range):
        start_year, end_year = years.start, years.stop - 1
    else:
        start_year, end_year = min(years), max(years)
    
    collector = BLSCollector(api_key)
    return collector.get_employment_data(start_year, end_year)