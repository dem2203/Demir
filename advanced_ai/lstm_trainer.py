"""
LSTM Training
Deep learning on real data
REAL model training - 100% Policy
"""

import numpy as np
import pandas as pd
import logging
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    KERAS_AVAILABLE = True
except:
    KERAS_AVAILABLE = False
    logger.warning("TensorFlow not available")

class LSTMTrainer:
    """LSTM model trainer"""
    
    def __init__(self, lookback=60):
        self.lookback = lookback
        self.scaler = MinMaxScaler()
        self.model = None
        self.keras_available = KERAS_AVAILABLE
    
    def prepare_sequences(self, prices):
        """Prepare REAL sequences"""
        try:
            if len(prices) < self.lookback:
                return None, None
            
            scaled = self.scaler.fit_transform(prices.reshape(-1, 1))
            X, y = [], []
            
            for i in range(len(scaled) - self.lookback - 1):
                X.append(scaled[i:(i + self.lookback), 0])
                y.append(scaled[i + self.lookback, 0])
            
            X = np.array(X).reshape((len(X), len(X[0]), 1))
            y = np.array(y)
            
            logger.info(f"✅ Prepared {len(X)} sequences")
            return X, y
        except Exception as e:
            logger.error(f"Sequence error: {e}")
            return None, None
    
    def build_model(self):
        """Build LSTM model"""
        try:
            if not self.keras_available:
                return False
            
            self.model = Sequential([
                LSTM(50, activation='relu', input_shape=(self.lookback, 1), return_sequences=True),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1)
            ])
            
            self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            logger.info("✅ LSTM model built")
            return True
        except Exception as e:
            logger.error(f"Build error: {e}")
            return False
    
    def train(self, X, y, epochs=50):
        """Train on REAL data"""
        try:
            if self.model is None:
                return False
            
            self.model.fit(X, y, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)
            logger.info("✅ Model trained")
            return True
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
