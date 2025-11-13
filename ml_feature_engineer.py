"""
ML FEATURE ENGINEER - v2.0 FIXED
⚠️ REAL Binance data ONLY
NO MOCK DATA - Real prices or Error
"""

import os
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import asyncio
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

try:
    from binance.client import Client
    HAS_BINANCE = True
except ImportError:
    HAS_BINANCE = False


class MLFeatureEngineer:
    """ML Feature Engineering - REAL data only"""
    
    def __init__(self):
        """Initialize"""
        self.binance_key = os.getenv('BINANCE_API_KEY')
        self.binance_secret = os.getenv('BINANCE_API_SECRET')
        
        if HAS_BINANCE and self.binance_key:
            self.client = Client(self.binance_key, self.binance_secret)
        else:
            self.client = None
            logger.warning("Binance not configured - ML features will fail")
        
        self.scaler = None
        self.is_trained = False
    
    async def fetch_real_data(
        self, 
        symbol: str, 
        timeframe: str = '1h', 
        lookback: int = 500
    ) -> Optional[pd.DataFrame]:
        """Fetch REAL Binance data - NO MOCK
        
        Args:
            symbol: 'BTCUSDT'
            timeframe: '1h', '4h', '1d'
            lookback: Number of candles
        
        Returns:
            Real OHLCV data from BINANCE or ERROR
        """
        
        if not self.client:
            logger.error("Binance client not initialized")
            return None
        
        try:
            # Get REAL klines from Binance
            klines = self.client.get_historical_klines(
                symbol,
                timeframe,
                limit=lookback
            )
            
            if not klines:
                logger.error(f"No data from Binance for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric (REAL data)
            df['close'] = pd.to_numeric(df['close'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['open'] = pd.to_numeric(df['open'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Validate REAL data
            if df.isnull().sum().sum() > 0:
                logger.warning("NULL values in real data")
            
            if (df['close'] <= 0).any():
                logger.error("Invalid prices in real data")
                return None
            
            logger.info(f"✅ Fetched {len(df)} real candles for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Binance fetch error: {e}")
            return None
    
    def extract_features(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract ML features from REAL price data
        
        Features:
        - RSI: Relative Strength Index
        - MACD: Moving Average Convergence
        - Bollinger: Volatility bands
        - Volume: Trading volume
        - Momentum: Rate of change
        """
        
        if df is None or len(df) < 50:
            logger.error("Insufficient real data for feature extraction")
            return None
        
        try:
            df = df.copy()
            
            # 1. RSI (Real Strength Index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss if loss.iloc[-1] != 0 else np.inf
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 2. MACD (Moving Average Convergence Divergence)
            ema_12 = df['close'].ewm(span=12, adjust=False).mean()
            ema_26 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            # 3. Bollinger Bands
            sma_20 = df['close'].rolling(20).mean()
            std_20 = df['close'].rolling(20).std()
            df['bb_upper'] = sma_20 + (std_20 * 2)
            df['bb_lower'] = sma_20 - (std_20 * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # 4. Volume
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # 5. Momentum
            df['momentum'] = df['close'].diff(12)
            
            # 6. Price changes
            df['pct_change'] = df['close'].pct_change()
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
            
            # Drop NaN
            df = df.dropna()
            
            logger.info(f"✅ Extracted {len(df)} feature rows from real data")
            return df
        
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return None
    
    async def get_ml_features(
        self,
        symbol: str,
        timeframe: str = '1h',
        lookback: int = 500
    ) -> Optional[pd.DataFrame]:
        """Get ML features from REAL Binance data
        
        Returns:
            Features or None (never mock!)
        """
        
        # Step 1: Get REAL data
        df = await asyncio.to_thread(
            self.fetch_real_data,
            symbol,
            timeframe,
            lookback
        )
        
        if df is None:
            logger.error(f"Failed to get real data for {symbol}")
            return None
        
        # Step 2: Extract features
        features = self.extract_features(df)
        
        if features is None:
            logger.error(f"Failed to extract features for {symbol}")
            return None
        
        return features
