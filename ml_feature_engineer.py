"""
🔱 DEMIR AI TRADING BOT - ML Feature Engineer (Phase 4.3)
==========================================================
Date: 2 Kasım 2025, 20:20 CET
Version: 1.0 - Feature Engineering for ML Models

PURPOSE:
--------
Extract 20+ technical features from price data
Feed into XGBoost and Random Forest models

FEATURES EXTRACTED:
-------------------
• Price-based: Returns, log returns, momentum
• Volatility: Rolling std, ATR, Bollinger width
• Volume: Volume MA, OBV, volume ratio
• Trend: SMA crossovers, EMA slopes, ADX
• Oscillators: RSI, MACD, Stochastic
• Pattern: Higher highs, lower lows, consolidation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import ccxt
    CCXT_AVAILABLE = True
except:
    CCXT_AVAILABLE = False


class MLFeatureEngineer:
    """
    Extract technical features for machine learning models
    """
    
    def __init__(self):
        self.feature_names = []
    
    def extract_features(
        self, 
        symbol: str = 'BTC/USDT',
        timeframe: str = '1h',
        lookback: int = 200
    ) -> Optional[pd.DataFrame]:
        """
        Extract all features from price data
        
        Args:
            symbol: Trading pair
            timeframe: Candlestick interval
            lookback: Number of candles
        
        Returns:
            DataFrame with all features
        """
        
        # Fetch OHLCV data
        df = self._fetch_data(symbol, timeframe, lookback)
        
        if df is None or df.empty:
            print(f"❌ ML Feature Engineer: No data for {symbol}")
            return None
        
        print(f"✅ ML Feature Engineer: Processing {len(df)} candles")
        
        # Extract all features
        df = self._add_price_features(df)
        df = self._add_volatility_features(df)
        df = self._add_volume_features(df)
        df = self._add_trend_features(df)
        df = self._add_oscillator_features(df)
        df = self._add_pattern_features(df)
        
        # Drop NaN rows
        df = df.dropna()
        
        print(f"✅ ML Feature Engineer: {len(df.columns)} features extracted")
        self.feature_names = [col for col in df.columns if col not in ['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def _fetch_data(self, symbol: str, timeframe: str, lookback: int) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from Binance"""
        
        if not CCXT_AVAILABLE:
            print("⚠️ ccxt not available - using mock data")
            return self._generate_mock_data(lookback)
        
        try:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=lookback)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"⚠️ Binance fetch error: {e} - using mock data")
            return self._generate_mock_data(lookback)
    
    def _generate_mock_data(self, lookback: int) -> pd.DataFrame:
        """Generate mock OHLCV data for testing"""
        
        base_price = 69000
        dates = pd.date_range(end=datetime.now(), periods=lookback, freq='1H')
        
        # Simulate realistic price movement
        returns = np.random.normal(0, 0.02, lookback)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * (1 + np.random.uniform(-0.005, 0.005, lookback)),
            'high': prices * (1 + np.random.uniform(0, 0.01, lookback)),
            'low': prices * (1 - np.random.uniform(0, 0.01, lookback)),
            'close': prices,
            'volume': np.random.uniform(100, 1000, lookback)
        })
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Price-based features"""
        
        # Returns
        df['return_1'] = df['close'].pct_change(1)
        df['return_5'] = df['close'].pct_change(5)
        df['return_10'] = df['close'].pct_change(10)
        
        # Log returns
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # Momentum
        df['momentum_10'] = df['close'] - df['close'].shift(10)
        df['momentum_20'] = df['close'] - df['close'].shift(20)
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volatility features"""
        
        # Rolling standard deviation
        df['volatility_10'] = df['return_1'].rolling(10).std()
        df['volatility_20'] = df['return_1'].rolling(20).std()
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr_14'] = tr.rolling(14).mean()
        
        # Bollinger Band Width
        sma_20 = df['close'].rolling(20).mean()
        std_20 = df['close'].rolling(20).std()
        df['bb_width'] = (std_20 / sma_20) * 100
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volume features"""
        
        # Volume moving averages
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        df['volume_ma_20'] = df['volume'].rolling(20).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']
        
        # OBV (On-Balance Volume)
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        df['obv'] = obv
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trend indicators"""
        
        # SMAs
        df['sma_10'] = df['close'].rolling(10).mean()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        
        # SMA crossovers
        df['sma_10_20_cross'] = df['sma_10'] - df['sma_20']
        df['sma_20_50_cross'] = df['sma_20'] - df['sma_50']
        
        # EMA slopes
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['ema_slope'] = ema_12 - ema_26
        
        return df
    
    def _add_oscillator_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Oscillator indicators"""
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Stochastic
        low_14 = df['low'].rolling(14).min()
        high_14 = df['high'].rolling(14).max()
        df['stoch_k'] = ((df['close'] - low_14) / (high_14 - low_14)) * 100
        df['stoch_d'] = df['stoch_k'].rolling(3).mean()
        
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pattern recognition features"""
        
        # Higher highs / Lower lows
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
        
        # Consolidation (low volatility)
        df['consolidation'] = (df['volatility_10'] < df['volatility_10'].rolling(20).mean()).astype(int)
        
        return df


# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":
    print("🔱 ML Feature Engineer - Standalone Test")
    print("=" * 70)
    
    engineer = MLFeatureEngineer()
    
    features = engineer.extract_features(
        symbol='BTC/USDT',
        timeframe='1h',
        lookback=200
    )
    
    if features is not None:
        print(f"\n📊 Features extracted: {len(engineer.feature_names)}")
        print(f"Data shape: {features.shape}")
        print(f"\nFeature list:")
        for i, name in enumerate(engineer.feature_names, 1):
            print(f"{i}. {name}")
        
        print(f"\n✅ ML Feature Engineer test complete!")
    else:
        print(f"\n❌ Feature extraction failed!")
