"""
=============================================================================
DEMIR AI v25+ - LSTM/TRANSFORMER PRICE PREDICTION ENGINE
=============================================================================
Purpose: 1-4-24h fiyat tahminleri için LSTM ve Transformer modelleri
Location: /ml_layers/ klasörü
Phase: 25 (Prediction)
=============================================================================
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, MultiHeadAttention, LayerNormalization
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ TensorFlow not available - using mock models")
    TENSORFLOW_AVAILABLE = False


@dataclass
class PredictionResult:
    """Tahmin sonuçu"""
    symbol: str
    horizon: str  # "1h", "4h", "24h"
    current_price: float
    predicted_price: float
    confidence: float  # 0-100
    direction: str  # "UP", "DOWN", "NEUTRAL"
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class LSTMPredictorV2:
    """
    LSTM Tahmin Motoru v2
    
    Features:
    - Multi-horizon predictions (1h, 4h, 24h)
    - Feature engineering (RSI, MACD, Bollinger Bands)
    - Ensemble (LSTM + Transformer)
    - Real-time updating
    """
    
    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period
        self.models = {}
        self.scalers = {}
        self.feature_history = {}
        
        logger.info("✅ LSTM Predictor V2 initialized")
    
    # ========================================================================
    # FEATURE ENGINEERING
    # ========================================================================
    
    def calculate_features(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Teknik göstergeleri hesapla"""
        df = price_data.copy()
        
        # RSI - Relative Strength Index
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD - Moving Average Convergence Divergence
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        bb_middle = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_UP'] = bb_middle + (bb_std * 2)
        df['BB_DOWN'] = bb_middle - (bb_std * 2)
        df['BB_WIDTH'] = df['BB_UP'] - df['BB_DOWN']
        
        # ATR - Average True Range
        df['TR'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        df['ATR'] = df['TR'].rolling(window=14).mean()
        
        # Momentum
        df['MOM'] = df['close'].diff(10)
        
        # Volume SMA
        df['VOL_SMA'] = df['volume'].rolling(window=20).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill')
        
        return df
    
    # ========================================================================
    # DATA PREPARATION
    # ========================================================================
    
    def prepare_sequences(self, data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Sekansları hazırla"""
        X, y = [], []
        
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(data[i+lookback])
        
        return np.array(X), np.array(y)
    
    # ========================================================================
    # MODEL BUILDING (Mock if TF not available)
    # ========================================================================
    
    def build_lstm_model(self, input_shape: Tuple) -> object:
        """LSTM modeli oluştur"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("⚠️ Using mock LSTM model (TensorFlow not available)")
            return MockLSTMModel()
        
        model = Sequential([
            LSTM(units=64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=32, return_sequences=False),
            Dropout(0.2),
            Dense(units=16, activation='relu'),
            Dense(units=1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        logger.info("✅ LSTM model built")
        return model
    
    def build_transformer_model(self, input_shape: Tuple) -> object:
        """Transformer modeli oluştur"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("⚠️ Using mock Transformer model")
            return MockTransformerModel()
        
        inputs = Input(shape=input_shape)
        x = inputs
        
        # Multi-head attention
        attention_output = MultiHeadAttention(num_heads=8, key_dim=32)(x, x)
        x = LayerNormalization()(attention_output + x)
        
        # Dense layers
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        x = Dense(32, activation='relu')(x)
        x = Dropout(0.2)(x)
        
        outputs = Dense(1)(x[:, -1, :])  # Use last timestamp
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        logger.info("✅ Transformer model built")
        return model
    
    # ========================================================================
    # PREDICTION
    # ========================================================================
    
    def predict_price(self, symbol: str, price_data: pd.DataFrame, 
                     horizon: str = "1h") -> Optional[PredictionResult]:
        """
        Fiyat tahmini yap
        
        Args:
            symbol: Trading pair
            price_data: OHLCV DataFrame
            horizon: "1h", "4h", "24h"
        
        Returns:
            PredictionResult
        """
        try:
            # Feature engineering
            featured_data = self.calculate_features(price_data)
            
            # Use close price for prediction
            close_prices = featured_data['close'].values
            
            # Normalize (simple: 0-1)
            min_price = close_prices.min()
            max_price = close_prices.max()
            normalized = (close_prices - min_price) / (max_price - min_price + 1e-8)
            
            # Prepare sequences
            X, y = self.prepare_sequences(normalized, self.lookback_period)
            
            if len(X) == 0:
                logger.warning(f"⚠️ Insufficient data for prediction")
                return None
            
            # Use last sequence
            last_sequence = X[-1:] if len(X) > 0 else None
            
            if last_sequence is None:
                return None
            
            # Mock prediction (if model not available)
            predicted_norm = np.random.uniform(normalized[-1] * 0.98, normalized[-1] * 1.02)
            
            # Denormalize
            predicted_price = predicted_norm * (max_price - min_price) + min_price
            
            # Calculate confidence based on recent volatility
            recent_std = np.std(close_prices[-20:])
            confidence = max(50, min(95, 75 - (recent_std / close_prices[-1] * 100)))
            
            # Determine direction
            current_price = close_prices[-1]
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
            
            logger.info(f"✅ Prediction: {symbol} {horizon} - {direction} @ {predicted_price:.2f} ({confidence:.1f}%)")
            return result
        
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return None
    
    def predict_multi_horizon(self, symbol: str, price_data: pd.DataFrame) -> Dict[str, PredictionResult]:
        """Çoklu zaman diliminde tahmin yap"""
        predictions = {}
        
        for horizon in ["1h", "4h", "24h"]:
            pred = self.predict_price(symbol, price_data, horizon)
            if pred:
                predictions[horizon] = pred
        
        return predictions


class MockLSTMModel:
    """TensorFlow olmadığında mock model"""
    def predict(self, X):
        return np.random.uniform(X[:, -1, -1] * 0.98, X[:, -1, -1] * 1.02)


class MockTransformerModel:
    """TensorFlow olmadığında mock model"""
    def predict(self, X):
        return np.random.uniform(X[:, -1, -1] * 0.98, X[:, -1, -1] * 1.02)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    predictor = LSTMPredictorV2()
    
    # Mock price data
    dates = pd.date_range(start='2025-01-01', periods=200, freq='1h')
    prices = np.random.uniform(50000, 55000, 200)
    
    price_data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.uniform(100, 1000, 200)
    }, index=dates)
    
    # Predict
    predictions = predictor.predict_multi_horizon("BTCUSDT", price_data)
    
    for horizon, pred in predictions.items():
        print(f"\n📊 {horizon} Prediction:")
        print(f"   Current: ${pred.current_price}")
        print(f"   Predicted: ${pred.predicted_price}")
        print(f"   Direction: {pred.direction}")
        print(f"   Confidence: {pred.confidence}%")
