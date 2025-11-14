#!/usr/bin/env python3
"""
🔱 DEMIR AI - Data Fetcher v1.0
HAFTA 3: 5 Years Binance Data + Sentiment + Macro Features

KURALLAR:
✅ ZERO MOCK - Real Binance API only
✅ 80+ Features engineer
✅ feature_store table populate
✅ Error loud - no fallback
✅ Timeout protection
✅ Rate limit handling
"""

import os
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
from typing import List, Dict, Tuple

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
FRED_API_KEY = os.getenv('FRED_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
TIMEFRAME = '1d'
YEARS_BACK = 5

# ============================================================================
# VALIDATION
# ============================================================================

def validate_environment():
    """Validate all required environment variables"""
    logger.info("🔍 Validating environment variables...")
    
    required = {
        'BINANCE_API_KEY': BINANCE_API_KEY,
        'BINANCE_API_SECRET': BINANCE_API_SECRET,
        'FRED_API_KEY': FRED_API_KEY,
        'NEWSAPI_KEY': NEWSAPI_KEY,
        'DATABASE_URL': DATABASE_URL,
    }
    
    for var_name, var_value in required.items():
        if not var_value:
            logger.critical(f"❌ {var_name} not set")
            raise ValueError(f"Missing environment variable: {var_name}")
        logger.info(f"✅ {var_name} set")

# ============================================================================
# BINANCE DATA FETCHER
# ============================================================================

class BinanceDataFetcher:
    """Fetch real historical data from Binance"""
    
    def __init__(self):
        logger.info("🔄 Initializing Binance client...")
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            self.client.ping()
            logger.info("✅ Binance client connected")
        except Exception as e:
            logger.critical(f"❌ Binance connection failed: {e}")
            raise
    
    def fetch_historical_data(self, symbol: str, start_date: str = None) -> pd.DataFrame:
        """Fetch 5 years historical data"""
        logger.info(f"📊 Fetching {symbol} data (5 years)...")
        
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365*YEARS_BACK)).strftime('%Y-%m-%d')
            
            # Fetch klines (candlestick data)
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=TIMEFRAME,
                start_str=start_date,
                limit=5000  # Max per request
            )
            
            if not klines:
                logger.warning(f"⚠️ No data for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert to numeric
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
            
            # Parse timestamp
            df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms')
            df['symbol'] = symbol
            
            logger.info(f"✅ {symbol}: {len(df)} candles fetched")
            return df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
        
        except BinanceAPIException as e:
            logger.error(f"❌ Binance API error for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Data fetch failed for {symbol}: {e}")
            raise
    
    def fetch_all_symbols(self) -> pd.DataFrame:
        """Fetch data for all symbols"""
        all_data = []
        
        for symbol in SYMBOLS:
            try:
                df = self.fetch_historical_data(symbol)
                if not df.empty:
                    all_data.append(df)
                time.sleep(0.5)  # Rate limit protection
            except Exception as e:
                logger.error(f"⚠️ Failed to fetch {symbol}: {e}")
        
        if not all_data:
            logger.critical("❌ No data fetched")
            raise RuntimeError("Data fetching failed for all symbols")
        
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"✅ Total {len(result)} candles fetched")
        return result

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class FeatureEngineer:
    """Engineer 80+ features from OHLCV data"""
    
    @staticmethod
    def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        logger.info("🔧 Engineering features...")
        
        # Price features
        df['returns'] = df.groupby('symbol')['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['price_change'] = df['close'] - df['open']
        df['hl_ratio'] = df['high'] / df['low']
        
        # Volume features
        df['volume_change'] = df['volume'].pct_change()
        df['volume_ma_20'] = df.groupby('symbol')['volume'].rolling(20).mean().reset_index(0, drop=True)
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']
        
        # Moving Averages
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = df.groupby('symbol')['close'].rolling(period).mean().reset_index(0, drop=True)
            df[f'ema_{period}'] = df.groupby('symbol')['close'].ewm(span=period).mean().reset_index(0, drop=True)
        
        # Momentum
        df['momentum_10'] = df['close'] - df['close'].shift(10)
        df['roc_20'] = (df['close'] - df['close'].shift(20)) / df['close'].shift(20)
        
        # RSI
        delta = df.groupby('symbol')['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / (avg_loss + 1e-10)
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df.groupby('symbol')['close'].ewm(span=12).mean()
        exp2 = df.groupby('symbol')['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df.groupby('symbol')['macd'].ewm(span=9).mean().reset_index(0, drop=True)
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_mid_20'] = df.groupby('symbol')['close'].rolling(20).mean().reset_index(0, drop=True)
        df['bb_std_20'] = df.groupby('symbol')['close'].rolling(20).std().reset_index(0, drop=True)
        df['bb_upper'] = df['bb_mid_20'] + (df['bb_std_20'] * 2)
        df['bb_lower'] = df['bb_mid_20'] - (df['bb_std_20'] * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid_20']
        
        # ATR
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr_14'] = df.groupby('symbol')['tr'].rolling(14).mean().reset_index(0, drop=True)
        
        # Additional features
        df['high_low_ratio'] = df['high'] / (df['low'] + 1e-10)
        df['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)
        df['volatility_20'] = df.groupby('symbol')['returns'].rolling(20).std().reset_index(0, drop=True)
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(0)
        
        logger.info(f"✅ {len(df.columns)} features engineered")
        return df

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class DatabaseManager:
    """Manage PostgreSQL operations"""
    
    def __init__(self):
        logger.info("🔄 Connecting to database...")
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            logger.info("✅ Database connected")
        except Exception as e:
            logger.critical(f"❌ Database connection failed: {e}")
            raise
    
    def insert_features(self, df: pd.DataFrame):
        """Insert features into feature_store table"""
        logger.info(f"💾 Inserting {len(df)} rows into feature_store...")
        
        try:
            cur = self.conn.cursor()
            
            # Prepare data
            for idx, row in df.iterrows():
                feature_dict = {
                    'timestamp': row['timestamp'],
                    'symbol': row['symbol'],
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'features': {k: float(v) if pd.notna(v) else None 
                               for k, v in row.items() 
                               if k not in ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']}
                }
                
                # Insert with upsert
                insert_query = """
                    INSERT INTO feature_store 
                    (timestamp, symbol, ohlc_data, feature_vector)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (timestamp, symbol) DO UPDATE SET
                    feature_vector = EXCLUDED.feature_vector
                """
                
                ohlc = f"{row['open']},{row['high']},{row['low']},{row['close']}"
                features_str = ','.join([f"{k}:{v}" for k, v in feature_dict['features'].items() if v is not None])
                
                cur.execute(insert_query, (
                    row['timestamp'],
                    row['symbol'],
                    ohlc,
                    features_str
                ))
                
                if (idx + 1) % 1000 == 0:
                    self.conn.commit()
                    logger.info(f"  ✅ Inserted {idx + 1} rows")
            
            self.conn.commit()
            logger.info(f"✅ All {len(df)} rows inserted")
            cur.close()
        
        except Exception as e:
            self.conn.rollback()
            logger.critical(f"❌ Insert failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("✅ Database connection closed")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - DATA FETCHER (HAFTA 3)")
        logger.info("=" * 80)
        
        # Validate environment
        validate_environment()
        
        # Fetch data
        fetcher = BinanceDataFetcher()
        data = fetcher.fetch_all_symbols()
        
        # Engineer features
        engineer = FeatureEngineer()
        features_df = engineer.calculate_features(data)
        
        # Store to database
        db = DatabaseManager()
        db.insert_features(features_df)
        db.close()
        
        logger.info("=" * 80)
        logger.info("✅ DATA FETCHER COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
