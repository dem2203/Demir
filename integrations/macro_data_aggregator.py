"""
Macro Data Aggregation
FRED + Alpha Vantage + Twelve Data
REAL macro indicators - 100% Policy
"""

import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FREDIntegration:
    """Federal Reserve Economic Data"""
    
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY', '')
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_fed_funds_rate(self):
        """REAL Fed Funds Rate"""
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
                    rate = float(data['observations'][-1]['value'])
                    logger.info(f"✅ Fed Rate: {rate}%")
                    return rate
            return None
        except Exception as e:
            logger.error(f"FRED error: {e}")
            return None
    
    def get_inflation(self):
        """REAL inflation data"""
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
                obs = data.get('observations', [])
                if len(obs) >= 2:
                    inflation = float(obs[-1]['value']) - float(obs[-2]['value'])
                    logger.info(f"✅ Inflation: {inflation:.2f}%")
                    return inflation
            return None
        except Exception as e:
            logger.error(f"Inflation error: {e}")
            return None
    
    def get_unemployment(self):
        """REAL unemployment"""
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
                    rate = float(data['observations'][-1]['value'])
                    logger.info(f"✅ Unemployment: {rate}%")
                    return rate
            return None
        except Exception as e:
            logger.error(f"Unemployment error: {e}")
            return None

class AlphaVantageIntegration:
    """Alpha Vantage - Stock & Forex"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_intraday(self, symbol, interval='5min'):
        """REAL intraday data"""
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

class TwelveDataIntegration:
    """Twelve Data - Real-time prices"""
    
    def __init__(self):
        self.api_key = os.getenv('TWELVE_DATA_API_KEY', '')
        self.base_url = "https://api.twelvedata.com"
    
    def get_price(self, symbol):
        """REAL price from Twelve Data"""
        try:
            params = {'symbol': symbol, 'apikey': self.api_key}
            response = requests.get(f"{self.base_url}/price", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = float(data['price'])
                    logger.info(f"✅ Twelve Data {symbol}: ${price}")
                    return price
            return None
        except Exception as e:
            logger.error(f"Twelve Data error: {e}")
            return None

class MacroAggregator:
    """Aggregate all macro data"""
    
    def __init__(self):
        self.fred = FREDIntegration()
        self.alpha = AlphaVantageIntegration()
        self.twelve = TwelveDataIntegration()
    
    def get_context(self):
        """REAL macro context"""
        return {
            'fed_rate': self.fred.get_fed_funds_rate(),
            'inflation': self.fred.get_inflation(),
            'unemployment': self.fred.get_unemployment(),
            'timestamp': datetime.now()
        }

