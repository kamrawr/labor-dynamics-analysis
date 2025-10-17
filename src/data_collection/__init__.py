"""
Data Collection Module for Labor Dynamics Analysis

This module provides interfaces to collect data from various government APIs
including BLS, Census Bureau, NCES, and FRED.
"""

from .bls_collector import BLSCollector, fetch_employment_data
from .nces_collector import NCESCollector, fetch_enrollment_data
from .census_collector import CensusCollector, fetch_demographic_data
from .fred_collector import FREDCollector, fetch_economic_data
from .data_processor import DataProcessor, process_and_merge

__all__ = [
    'BLSCollector',
    'NCESCollector', 
    'CensusCollector',
    'FREDCollector',
    'DataProcessor',
    'fetch_employment_data',
    'fetch_enrollment_data', 
    'fetch_demographic_data',
    'fetch_economic_data',
    'process_and_merge'
]