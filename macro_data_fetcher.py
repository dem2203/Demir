#!/usr/bin/env python3
"""
🔱 DEMIR AI - Macro Data Fetcher v1.0
HAFTA 3-5: Macro Economic Data + Market Sentiment

KURALLAR:
✅ FRED API - Interest rates, inflation, employment
✅ VIX, SPX, DXY - Market indicators
✅ Gold, Oil prices
✅ Real-time data only
✅ Error loud - all errors logged
✅ Database storage (macro_indicators table)
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
FRED_API_KEY = os.getenv('FRED_API_KEY')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')

# FRED Series IDs
FRED_SERIES = {
    'UNRATE': 'Unemployment Rate',
    'CPIAUCSL': 'CPI',
    'DFF': 'Federal Funds Rate',
    'DEXUSEU': 'USD/EUR',
    'DEXCHUS': 'USD/CNY',
    'DCOILWTICO': 'WTI Oil',
    'GOLDAMDONUSD': 'Gold Price'
}

# ============================================================================
# VALIDATION
# ============================================================================

def validate_environment():
    """Validate API keys"""
    logger.info("🔍 Validating environment...")
    
    if not FRED_API_KEY:
        logger.critical("❌ FRED_API_KEY not set")
        raise ValueError("FRED_API_KEY required")
    
    if not ALPHA_VANTAGE_KEY:
        logger.critical("❌ ALPHA_VANTAGE_KEY not set")
        raise ValueError("ALPHA_VANTAGE_KEY required")
    
    logger.info("✅ API keys validated")

# ============================================================================
# FRED DATA FETCHER
# ============================================================================

class FREDDataFetcher:
    """Fetch Federal Reserve Economic Data"""
    
    def __init__(self):
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    def fetch_series(self, series_id: str) -> Optional[float]:
        """Fetch latest value for series"""
        try:
            params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' in data and len(data['observations']) > 0:
                value = data['observations'][0]['value']
                if value and value != '.':
                    logger.info(f"✅ {series_id}: {value}")
                    return float(value)
            
            logger.warning(f"⚠️ No data for {series_id}")
            return None
        
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout fetching {series_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {series_id}: {e}")
            return None
    
    def fetch_all(self) -> Dict[str, float]:
        """Fetch all FRED series"""
        logger.info("📊 Fetching FRED data...")
        
        data = {}
        for series_id, name in FRED_SERIES.items():
            value = self.fetch_series(series_id)
            if value is not None:
                data[series_id] = value
        
        logger.info(f"✅ Fetched {len(data)} FRED series")
        return data

# ============================================================================
# ALPHA VANTAGE DATA FETCHER
# ============================================================================

class AlphaVantageDataFetcher:
    """Fetch market indices (VIX, SPX, DXY)"""
    
    def __init__(self):
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_intraday(self, symbol: str) -> Optional[Dict]:
        """Fetch intraday price data"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_KEY
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                quote = data['Global Quote']
                
                result = {
                    'symbol': symbol,
                    'price': float(quote['05. price']),
                    'change': float(quote['09. change']),
                    'change_percent': float(quote['10. change percent'].replace('%', '')),
                    'timestamp': datetime.now()
                }
                
                logger.info(f"✅ {symbol}: ${result['price']} ({result['change_percent']:.2f}%)")
                return result
            
            logger.warning(f"⚠️ No quote for {symbol}")
            return None
        
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout fetching {symbol}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
            return None
    
    def fetch_indices(self) -> Dict:
        """Fetch all market indices"""
        logger.info("📈 Fetching market indices...")
        
        indices = {}
        for symbol in ['^VIX', '^GSPC', 'DXY=F']:
            data = self.fetch_intraday(symbol)
            if data:
                indices[symbol] = data
        
        logger.info(f"✅ Fetched {len(indices)} indices")
        return indices

# ============================================================================
# CRYPTO MARKET FETCHER
# ============================================================================

class CryptoMarketFetcher:
    """Fetch crypto market metrics"""
    
    @staticmethod
    def fetch_bitcoin_dominance() -> Optional[float]:
        """Fetch Bitcoin dominance percentage"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            btc_dominance = data['data']['btc_dominance']
            
            logger.info(f"✅ Bitcoin dominance: {btc_dominance:.2f}%")
            return btc_dominance
        
        except Exception as e:
            logger.error(f"❌ BTC dominance fetch failed: {e}")
            return None
    
    @staticmethod
    def fetch_altcoin_volume() -> Optional[float]:
        """Fetch altcoin trading volume"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            total_volume = data['data']['total_volume']['usd']
            
            logger.info(f"✅ Total crypto volume: ${total_volume/1e9:.2f}B")
            return total_volume
        
        except Exception as e:
            logger.error(f"❌ Altcoin volume fetch failed: {e}")
            return None
    
    @staticmethod
    def fetch_fear_greed_index() -> Optional[int]:
        """Fetch Crypto Fear & Greed Index"""
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fgi = int(data['data'][0]['value'])
            
            logger.info(f"✅ Fear & Greed Index: {fgi}")
            return fgi
        
        except Exception as e:
            logger.error(f"❌ Fear & Greed fetch failed: {e}")
            return None

# ============================================================================
# DATABASE STORAGE
# ============================================================================

class MacroIndicatorStorage:
    """Store macro data"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def save_fred_data(self, data: Dict):
        """Save FRED data"""
        try:
            cur = self.db_conn.cursor()
            
            for series_id, value in data.items():
                insert_query = """
                    INSERT INTO macro_indicators 
                    (timestamp, indicator_type, indicator_name, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (indicator_type, indicator_name) DO UPDATE SET
                    value = EXCLUDED.value,
                    timestamp = EXCLUDED.timestamp
                """
                
                indicator_name = FRED_SERIES.get(series_id, series_id)
                
                cur.execute(insert_query, (
                    datetime.now(),
                    'FRED',
                    indicator_name,
                    value
                ))
            
            self.db_conn.commit()
            logger.info(f"💾 Saved {len(data)} FRED indicators")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save FRED data: {e}")
    
    def save_market_indices(self, data: Dict):
        """Save market indices"""
        try:
            cur = self.db_conn.cursor()
            
            for symbol, quote in data.items():
                insert_query = """
                    INSERT INTO macro_indicators 
                    (timestamp, indicator_type, indicator_name, value, change_percent)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                cur.execute(insert_query, (
                    quote['timestamp'],
                    'MARKET_INDEX',
                    symbol,
                    quote['price'],
                    quote['change_percent']
                ))
            
            self.db_conn.commit()
            logger.info(f"💾 Saved {len(data)} market indices")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save market indices: {e}")
    
    def save_crypto_metrics(self, metrics: Dict):
        """Save crypto metrics"""
        try:
            cur = self.db_conn.cursor()
            
            for metric_name, value in metrics.items():
                if value is not None:
                    insert_query = """
                        INSERT INTO macro_indicators 
                        (timestamp, indicator_type, indicator_name, value)
                        VALUES (%s, %s, %s, %s)
                    """
                    
                    cur.execute(insert_query, (
                        datetime.now(),
                        'CRYPTO_METRIC',
                        metric_name,
                        value
                    ))
            
            self.db_conn.commit()
            logger.info(f"💾 Saved {len(metrics)} crypto metrics")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to save crypto metrics: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - MACRO DATA FETCHER (HAFTA 3-5)")
        logger.info("=" * 80)
        
        validate_environment()
        
        db_conn = psycopg2.connect(DATABASE_URL)
        storage = MacroIndicatorStorage(db_conn)
        
        # Fetch FRED data
        logger.info("\n📊 Fetching FRED data...")
        fred_fetcher = FREDDataFetcher()
        fred_data = fred_fetcher.fetch_all()
        storage.save_fred_data(fred_data)
        
        # Fetch market indices
        logger.info("\n📈 Fetching market indices...")
        av_fetcher = AlphaVantageDataFetcher()
        indices = av_fetcher.fetch_indices()
        storage.save_market_indices(indices)
        
        # Fetch crypto metrics
        logger.info("\n🪙 Fetching crypto metrics...")
        crypto_fetcher = CryptoMarketFetcher()
        crypto_metrics = {
            'BTC_Dominance': crypto_fetcher.fetch_bitcoin_dominance(),
            'Total_Crypto_Volume': crypto_fetcher.fetch_altcoin_volume(),
            'Fear_Greed_Index': crypto_fetcher.fetch_fear_greed_index()
        }
        storage.save_crypto_metrics(crypto_metrics)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ MACRO DATA FETCHING COMPLETED")
        logger.info("=" * 80)
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
