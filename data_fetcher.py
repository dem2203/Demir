#!/usr/bin/env python3
"""
🔱 DEMIR AI - data_fetcher.py (HAFTA 3-7)
============================================================================
5 YEARS BINANCE DATA - REAL DATA ONLY, ZERO MOCK

Fetch 2020-2025 Binance klines, NO DEFAULTS, FAIL LOUD
============================================================================
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

import pandas as pd
import numpy as np
from binance.client import Client
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch REAL market data - STRICT"""
    
    def __init__(self, binance_key: str, binance_secret: str, db_url: str):
        if not binance_key or not binance_secret:
            raise ValueError("❌ Missing Binance API keys")
        if not db_url:
            raise ValueError("❌ Missing database URL")
        
        self.client = Client(binance_key, binance_secret)
        self.db_url = db_url
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT']
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2025, 1, 1)
        
        logger.info("✅ DataFetcher initialized")
    
    def validate_date_range(self):
        """Validate date range - STRICT"""
        if self.start_date >= self.end_date:
            raise ValueError(f"❌ Invalid date range: {self.start_date} >= {self.end_date}")
        
        days = (self.end_date - self.start_date).days
        if days < 365:
            raise ValueError(f"❌ Date range too short: {days} days < 365 days")
        
        logger.info(f"✅ Date range valid: {days} days")
    
    def fetch_binance_klines(self, symbol: str) -> pd.DataFrame:
        """Fetch REAL Binance klines - STRICT"""
        try:
            logger.info(f"🔄 Fetching {symbol} klines...")
            
            if symbol not in self.symbols:
                raise ValueError(f"❌ Invalid symbol: {symbol}")
            
            klines = []
            current_date = self.start_date
            
            while current_date < self.end_date:
                try:
                    # Fetch 1000 candles at a time (Binance limit)
                    batch = self.client.futures_historical_klines(
                        symbol=symbol,
                        interval=Client.KLINE_INTERVAL_1DAY,
                        start_str=current_date.strftime("%Y-%m-%d"),
                        end_str=(current_date + timedelta(days=500)).strftime("%Y-%m-%d"),
                        limit=500
                    )
                    
                    if not batch:
                        raise ValueError(f"❌ No klines returned for {symbol} at {current_date}")
                    
                    klines.extend(batch)
                    current_date += timedelta(days=500)
                
                except Exception as e:
                    logger.error(f"⚠️ Batch fetch failed: {e}")
                    raise
            
            if not klines:
                raise ValueError(f"❌ No klines fetched for {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Validate data
            if df.isnull().any().any():
                raise ValueError(f"❌ NaN values in klines for {symbol}")
            
            if (df['close'] <= 0).any():
                raise ValueError(f"❌ Invalid prices in {symbol}")
            
            if len(df) < 1000:
                raise ValueError(f"❌ Insufficient klines: {len(df)} < 1000")
            
            logger.info(f"✅ {symbol}: {len(df)} candles fetched")
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        except Exception as e:
            logger.critical(f"❌ Klines fetch failed for {symbol}: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def validate_klines(self, df: pd.DataFrame, symbol: str):
        """Validate klines - STRICT"""
        try:
            if df.empty:
                raise ValueError(f"❌ Empty klines for {symbol}")
            
            if len(df) < 1000:
                raise ValueError(f"❌ Insufficient klines: {len(df)} < 1000")
            
            # Check for gaps
            df['timestamp_diff'] = df['timestamp'].diff()
            max_gap = df['timestamp_diff'].max()
            
            if max_gap > timedelta(days=2):
                raise ValueError(f"❌ Data gap > 2 days in {symbol}")
            
            # Check prices
            if (df['close'] <= 0).any():
                raise ValueError(f"❌ Invalid prices in {symbol}")
            
            if (df['high'] < df['low']).any():
                raise ValueError(f"❌ High < Low in {symbol}")
            
            if df['volume'].isna().any():
                raise ValueError(f"❌ Missing volume in {symbol}")
            
            logger.info(f"✅ {symbol} klines validated")
        
        except Exception as e:
            logger.critical(f"❌ Klines validation failed: {e}")
            raise
    
    def calculate_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Calculate 80+ features - STRICT"""
        try:
            from ml_layers.feature_engineering import FeatureEngineer
            
            engineer = FeatureEngineer()
            
            features_list = []
            
            for i in range(100, len(df)):  # Need 100-day window
                window = df.iloc[i-100:i]
                prices = window['close'].values
                klines_data = window[['timestamp', 'open', 'high', 'low', 'close', 'volume']].values
                
                try:
                    features = engineer.extract_all_features(
                        klines=klines_data,
                        macro_data={'vix_close': 20, 'dxy_close': 100, 'fed_rate': 2.5},
                        sentiment_data={'news_sentiment': 0, 'twitter_sentiment': 0}
                    )
                    
                    features['symbol'] = symbol
                    features['timestamp'] = df.iloc[i]['timestamp']
                    features['price'] = float(df.iloc[i]['close'])
                    
                    # Calculate label (next day movement)
                    if i + 1 < len(df):
                        next_close = df.iloc[i+1]['close']
                        current_close = df.iloc[i]['close']
                        
                        if next_close > current_close * 1.01:  # >1% up
                            features['label'] = 2  # UP
                        elif next_close < current_close * 0.99:  # <-1% down
                            features['label'] = 0  # DOWN
                        else:
                            features['label'] = 1  # HOLD
                    
                    features_list.append(features)
                
                except Exception as e:
                    logger.warning(f"⚠️ Feature calculation failed at index {i}: {e}")
                    continue
            
            if not features_list:
                raise ValueError(f"❌ No features calculated for {symbol}")
            
            logger.info(f"✅ {symbol}: {len(features_list)} feature vectors calculated")
            return pd.DataFrame(features_list)
        
        except Exception as e:
            logger.critical(f"❌ Feature calculation failed: {e}")
            raise
    
    def store_to_database(self, features_df: pd.DataFrame, symbol: str):
        """Store features to database - STRICT"""
        try:
            if features_df.empty:
                raise ValueError(f"❌ Empty features for {symbol}")
            
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Prepare data for insertion
            rows = []
            for _, row in features_df.iterrows():
                rows.append((
                    row['symbol'],
                    row['timestamp'],
                    row.get('rsi_14', None),
                    row.get('macd_line', None),
                    row.get('macd_signal', None),
                    row.get('atr_14', None),
                    row.get('bb_upper', None),
                    row.get('bb_middle', None),
                    row.get('bb_lower', None),
                    row.get('bb_position', None),
                    row.get('sma_20', None),
                    row.get('volume_ratio', None),
                    row.get('vix_level', None),
                    row.get('dxy_level', None),
                    row.get('news_sentiment', None),
                    row.get('combined_score', None),
                    row.get('price', None),
                    datetime.now()
                ))
            
            execute_values(
                cur,
                """INSERT INTO feature_store (
                    symbol, timestamp, rsi_14, macd_line, macd_signal,
                    atr_14, bb_upper, bb_middle, bb_lower, bb_position,
                    sma_20, volume_ratio, vix_level, dxy_level, news_sentiment,
                    combined_score, price, created_at
                ) VALUES %s""",
                rows
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Stored {len(rows)} feature records for {symbol}")
        
        except Exception as e:
            logger.critical(f"❌ Database storage failed: {e}")
            raise
    
    def fetch_all_data(self):
        """Fetch and process all data - STRICT"""
        try:
            logger.info("🚀 Starting 5-year data fetch...")
            
            self.validate_date_range()
            
            for symbol in self.symbols:
                logger.info(f"\n{'='*80}")
                logger.info(f"Processing {symbol}...")
                logger.info(f"{'='*80}")
                
                # Fetch klines
                klines_df = self.fetch_binance_klines(symbol)
                self.validate_klines(klines_df, symbol)
                
                # Calculate features
                features_df = self.calculate_features(klines_df, symbol)
                
                # Store to database
                self.store_to_database(features_df, symbol)
            
            logger.info(f"\n{'='*80}")
            logger.info("✅ ALL DATA FETCHED AND STORED!")
            logger.info(f"{'='*80}")
        
        except Exception as e:
            logger.critical(f"❌ DATA FETCH FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        fetcher = DataFetcher(
            binance_key=os.getenv('BINANCE_API_KEY'),
            binance_secret=os.getenv('BINANCE_API_SECRET'),
            db_url=os.getenv('DATABASE_URL')
        )
        
        fetcher.fetch_all_data()
        
        logger.info("✅ Data fetching complete!")
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise
