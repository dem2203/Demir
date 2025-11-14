# macro_data_aggregator.py - Real Macro Data Integration

import requests
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FREDData:
    """Federal Reserve Economic Data - REAL macro indicators"""
    
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY', '')
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_fed_funds_rate(self):
        """Get REAL Fed Funds Rate"""
        try:
            params = {
                'series_id': 'FEDFUNDS',
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 1
            }
            
            response = requests.get(f"{self.base_url}/series/observations", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('observations'):
                    latest = data['observations'][-1]
                    rate = float(latest['value'])
                    logger.info(f"✅ FRED Fed Funds Rate: {rate}%")
                    return rate
            
            return None
        except Exception as e:
            logger.error(f"FRED error: {e}")
            return None
    
    def get_inflation_cpi(self):
        """Get REAL CPI inflation data"""
        try:
            params = {
                'series_id': 'CPIAUCSL',
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 2
            }
            
            response = requests.get(f"{self.base_url}/series/observations", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('observations') and len(data['observations']) >= 2:
                    latest = float(data['observations'][-1]['value'])
                    previous = float(data['observations'][-2]['value'])
                    
                    inflation = ((latest - previous) / previous * 100)
                    logger.info(f"✅ FRED CPI Inflation: {inflation:.2f}%")
                    return inflation
            
            return None
        except Exception as e:
            logger.error(f"CPI error: {e}")
            return None
    
    def get_unemployment_rate(self):
        """Get REAL unemployment rate"""
        try:
            params = {
                'series_id': 'UNRATE',
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 1
            }
            
            response = requests.get(f"{self.base_url}/series/observations", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('observations'):
                    latest = data['observations'][-1]
                    rate = float(latest['value'])
                    logger.info(f"✅ FRED Unemployment: {rate}%")
                    return rate
            
            return None
        except Exception as e:
            logger.error(f"Unemployment error: {e}")
            return None

class AlphaVantageData:
    """Alpha Vantage - Stock & Forex data"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_intraday_data(self, symbol, interval='5min'):
        """Get REAL intraday data"""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Alpha Vantage {symbol}: Got data")
                return data
            
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

class TwelveDataAPI:
    """Twelve Data - Real-time market data"""
    
    def __init__(self):
        self.api_key = os.getenv('TWELVE_DATA_API_KEY', '')
        self.base_url = "https://api.twelvedata.com"
    
    def get_real_time_price(self, symbol):
        """Get REAL real-time price"""
        try:
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/price", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    logger.info(f"✅ Twelve Data {symbol}: ${data['price']}")
                    return float(data['price'])
            
            return None
        except Exception as e:
            logger.error(f"Twelve Data error: {e}")
            return None

class MacroAggregator:
    """Aggregate macro data from all sources"""
    
    def __init__(self):
        self.fred = FREDData()
        self.alpha = AlphaVantageData()
        self.twelve = TwelveDataAPI()
    
    def get_macro_context(self):
        """Get REAL comprehensive macro context"""
        return {
            'fed_funds_rate': self.fred.get_fed_funds_rate(),
            'inflation_rate': self.fred.get_inflation_cpi(),
            'unemployment': self.fred.get_unemployment_rate(),
            'timestamp': datetime.now()
        }
