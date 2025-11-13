"""
LSTM NEURAL LAYER - v2.0
Deep learning LSTM predictions
⚠️ Real price data training only
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    HAS_TF = True
except ImportError:
    HAS_TF = False


class LSTMNeuralLayer(BaseLayer):
    """LSTM Neural Network Layer"""
    
    def __init__(self, lookback=60):
        """Initialize"""
        super().__init__('LSTM_Layer')
        self.lookback = lookback
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.is_trained = False
    
    async def get_signal(self, prices):
        """Get LSTM prediction"""
        return await self.execute_with_retry(
            self._predict_lstm,
            prices
        )
    
    async def _predict_lstm(self, prices):
        """LSTM prediction on REAL prices"""
        
        if not HAS_TF:
            raise ValueError("TensorFlow not installed")
        
        if not self.is_trained:
            raise ValueError("LSTM model not trained")
        
        try:
            if len(prices) < self.lookback:
                raise ValueError("Insufficient price history")
            
            # Normalize REAL prices
            scaled = self.scaler.fit_transform(np.array(prices).reshape(-1, 1))
            
            # Prepare input
            X = scaled[-self.lookback:].reshape(1, self.lookback, 1)
            
            # Predict
            pred = self.model.predict(X, verbose=0)
            predicted_price = self.scaler.inverse_transform([[pred]])
            current_price = prices[-1]
            
            # Signal
            if predicted_price > current_price * 1.01:
                signal = 'LONG'
                score = 70.0
            elif predicted_price < current_price * 0.99:
                signal = 'SHORT'
                score = 30.0
            else:
                signal = 'NEUTRAL'
                score = 50.0
            
            return {
                'signal': signal,
                'score': score,
                'predicted_price': float(predicted_price),
                'current_price': float(current_price),
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"LSTM error: {e}")
            raise ValueError(f"LSTM error: {e}")
