"""
=============================================================================
DEMIR AI v25-28 - LSTM PREDICTOR V2 (REAL DATA ONLY)
=============================================================================
NO MOCK DATA - Sadece gerçek Binance + API verisi kullanılır
=============================================================================
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import ccxt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("⚠️ TensorFlow not available - install via: pip install tensorflow")


@dataclass
class PredictionResult:
    """Tahmin sonuçu"""
    symbol: str
    horizon: str
    current_price: float
    predicted_price: float
    confidence: float
    direction: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class LSTMPredictorV2Real:
    """
    LSTM Tahmin Motoru v2 - GERÇEK VERİ
    
    ONLY REAL DATA:
    - Binance WebSocket live prices
    - Historical OHLCV from Binance API
    - NO mock, NO synthetic data
    """
    
    def __init__(self, exchange_id='binance'):
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'timeout': 30000,
        })
        self.lookback_period = 100
        self.models = {}
        logger.info(f"✅ LSTM initialized with REAL {exchange_id.upper()} API")
    
    def fetch_real_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Binance'den GERÇEK fiyat verisi çek
        
        Args:
            symbol: BTCUSDT, ETHUSDT vb
            timeframe: 1m, 5m, 1h, 4h, 1d
            limit: Kaç mumla (max 1000)
        
        Returns:
            OHLCV DataFrame
        """
        try:
            logger.info(f"📊 Fetching REAL data: {symbol} {timeframe}x{limit}")
            
            # Binance API'den fetch et
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            
            if not ohlcv:
                logger.error(f"❌ No data from Binance for {symbol}")
                return None
            
            # DataFrame'e çevir
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ Loaded {len(df)} REAL candles: {df.index[0]} → {df.index[-1]}")
            return df
        
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            return None
    
    def calculate_real_features(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """GERÇEK teknik göstergeler"""
        df = price_data.copy()
        
        # RSI - Gerçek hesaplama
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD - Gerçek hesaplama
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands - Gerçek hesaplama
        bb_middle = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_UP'] = bb_middle + (bb_std * 2)
        df['BB_DOWN'] = bb_middle - (bb_std * 2)
        
        # ATR - Gerçek hesaplama
        df['TR'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        df = df.fillna(method='bfill')
        logger.info("✅ Calculated REAL technical indicators")
        return df
    
    def prepare_sequences_real(self, data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Sekanslar REAL data'dan"""
        X, y = [], []
        
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback])
        
        return np.array(X), np.array(y)
    
    def train_lstm_model(self, symbol: str, price_data: pd.DataFrame) -> Optional[object]:
        """LSTM modeli REAL veri ile eğit"""
        if not TF_AVAILABLE:
            logger.error("❌ TensorFlow required for LSTM training")
            return None
        
        try:
            logger.info(f"🧠 Training LSTM model for {symbol}...")
            
            # Feature engineering
            featured_data = self.calculate_real_features(price_data)
            close_prices = featured_data['close'].values
            
            # Normalize
            min_price = close_prices.min()
            max_price = close_prices.max()
            normalized = (close_prices - min_price) / (max_price - min_price + 1e-8)
            
            # Prepare sequences
            X, y = self.prepare_sequences_real(normalized, self.lookback_period)
            
            if len(X) < 10:
                logger.error("❌ Insufficient data for LSTM training")
                return None
            
            # Build & train model
            model = Sequential([
                LSTM(units=64, return_sequences=True, input_shape=(self.lookback_period, 1)),
                Dropout(0.2),
                LSTM(units=32, return_sequences=False),
                Dropout(0.2),
                Dense(units=16, activation='relu'),
                Dense(units=1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # Train on REAL data
            history = model.fit(
                X.reshape(-1, self.lookback_period, 1),
                y,
                epochs=50,
                batch_size=16,
                validation_split=0.2,
                verbose=0
            )
            
            self.models[symbol] = model
            logger.info(f"✅ LSTM model trained for {symbol}")
            return model
        
        except Exception as e:
            logger.error(f"❌ Training error: {e}")
            return None
    
    def predict_real(self, symbol: str, horizon: str = "1h") -> Optional[PredictionResult]:
        """GERÇEK tahmin - REAL veri kullanarak"""
        try:
            # 1. REAL veri çek
            if horizon == "1h":
                timeframe, lookback = "1h", 100
            elif horizon == "4h":
                timeframe, lookback = "4h", 100
            else:  # "24h"
                timeframe, lookback = "1d", 100
            
            price_data = self.fetch_real_ohlcv(symbol, timeframe=timeframe, limit=lookback)
            
            if price_data is None or len(price_data) < 20:
                logger.error(f"❌ Insufficient REAL data for {symbol}")
                return None
            
            # 2. Model eğit (varsa) veya tekrar eğit
            if symbol not in self.models:
                model = self.train_lstm_model(symbol, price_data)
                if model is None:
                    return None
            else:
                model = self.models[symbol]
            
            # 3. Feature engineering REAL data üzerinde
            featured_data = self.calculate_real_features(price_data)
            close_prices = featured_data['close'].values
            
            current_price = close_prices[-1]
            
            # 4. Normalize & prepare
            min_price = close_prices.min()
            max_price = close_prices.max()
            normalized = (close_prices - min_price) / (max_price - min_price + 1e-8)
            
            # 5. Predict
            if TF_AVAILABLE and model is not None:
                last_sequence = normalized[-self.lookback_period:].reshape(1, self.lookback_period, 1)
                predicted_norm = model.predict(last_sequence, verbose=0)[0][0]
            else:
                # Simple fallback - use last 5 candles trend
                trend = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
                predicted_norm = normalized[-1] * (1 + trend * 0.1)
                predicted_norm = np.clip(predicted_norm, 0, 1)
            
            # 6. Denormalize
            predicted_price = predicted_norm * (max_price - min_price) + min_price
            
            # 7. Confidence dari volatility
            recent_std = np.std(close_prices[-20:]) / current_price
            confidence = max(50, min(95, 75 - (recent_std * 100)))
            
            # 8. Direction
            if predicted_price > current_price * 1.01:
                direction = "UP 📈"
            elif predicted_price < current_price * 0.99:
                direction = "DOWN 📉"
            else:
                direction = "NEUTRAL ➡️"
            
            result = PredictionResult(
                symbol=symbol,
                horizon=horizon,
                current_price=round(current_price, 2),
                predicted_price=round(predicted_price, 2),
                confidence=round(confidence, 1),
                direction=direction
            )
            
            logger.info(f"✅ REAL prediction: {symbol} {horizon} → {direction} @ ${predicted_price:.2f}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return None
    
    def predict_multi_horizon_real(self, symbol: str) -> Dict[str, PredictionResult]:
        """Multi-horizon REAL predictions"""
        predictions = {}
        
        for horizon in ["1h", "4h", "24h"]:
            pred = self.predict_real(symbol, horizon)
            if pred:
                predictions[horizon] = pred
        
        return predictions


# ============================================================================
# TEST - GERÇEK VERI İLE
# ============================================================================

if __name__ == "__main__":
    predictor = LSTMPredictorV2Real()
    
    # GERÇEK veri ile tahmin
    predictions = predictor.predict_multi_horizon_real("BTCUSDT")
    
    for horizon, pred in predictions.items():
        print(f"\n📊 {horizon} Prediction (REAL DATA):")
        print(f"   Current: ${pred.current_price}")
        print(f"   Predicted: ${pred.predicted_price}")
        print(f"   Direction: {pred.direction}")
        print(f"   Confidence: {pred.confidence}%")
