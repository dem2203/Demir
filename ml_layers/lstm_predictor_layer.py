"""
PHASE 9.1: LSTM PREDICTOR LAYER
File 4 of 10 (ayrı dosyalar)
Folder: ml_layers/lstm_predictor_layer.py

LSTM-based time series prediction
- Sequence modeling
- Multi-step forecasting
- Auto-training
- Real-time predictions
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    logging.warning("TensorFlow not installed. LSTM layer will be limited.")

logger = logging.getLogger(__name__)


class LSTMPredictorLayer:
    """
    LSTM-based time series prediction engine
    
    Features:
    - Sequence-to-sequence predictions
    - Multi-step ahead forecasting
    - Automatic training validation
    - Real-time predictions
    """
    
    def __init__(self, lookback: int = 60, forecast_horizon: int = 5):
        """
        Initialize LSTM predictor
        
        Args:
            lookback: Number of past timesteps
            forecast_horizon: Steps to predict ahead
        """
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.model: Optional[Any] = None
        self.is_trained = False
        
        if not KERAS_AVAILABLE:
            logger.warning("LSTM layer requires TensorFlow/Keras")
        
    def build_model(self, input_shape: Tuple[int, int]) -> Optional[Any]:
        """
        Build LSTM model architecture
        
        Args:
            input_shape: (lookback, features)
            
        Returns:
            Compiled Keras model or None
        """
        if not KERAS_AVAILABLE:
            return None
        
        try:
            model = keras.Sequential([
                keras.layers.LSTM(64, activation='relu', input_shape=input_shape,
                                 return_sequences=True),
                keras.layers.Dropout(0.2),
                keras.layers.LSTM(32, activation='relu', return_sequences=False),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(16, activation='relu'),
                keras.layers.Dense(self.forecast_horizon)
            ])
            
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            self.model = model
            return model
            
        except Exception as e:
            logger.error(f"Model building error: {e}")
            return None
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for training
        
        Args:
            data: Price time series [1D]
            
        Returns:
            X, y arrays
        """
        X, y = [], []
        
        for i in range(len(data) - self.lookback - self.forecast_horizon):
            X.append(data[i:i + self.lookback])
            y.append(data[i + self.lookback:i + self.lookback + self.forecast_horizon])
        
        return np.array(X), np.array(y)
    
    def train(self, data: np.ndarray, epochs: int = 50, 
              batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train LSTM model
        
        Args:
            data: Historical price data
            epochs: Training epochs
            batch_size: Batch size
            validation_split: Train/val split ratio
            
        Returns:
            Training metrics
        """
        if not KERAS_AVAILABLE or self.model is None:
            return {"error": "Model not available"}
        
        try:
            X, y = self.prepare_sequences(data)
            
            # Reshape for LSTM [samples, lookback, features]
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Build if needed
            if self.model is None:
                self.build_model((X.shape[1], X.shape[2]))
            
            # Train
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,
                validation_split=validation_split
            )
            
            self.is_trained = True
            
            return {
                'success': True,
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1]),
                'epochs': epochs
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {"error": str(e)}
    
    def predict(self, recent_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Predict next N steps
        
        Args:
            recent_data: Last lookback prices
            
        Returns:
            Predicted prices or None
        """
        if not self.is_trained or self.model is None or not KERAS_AVAILABLE:
            return None
        
        try:
            X = recent_data[-self.lookback:].reshape(1, self.lookback, 1)
            prediction = self.model.predict(X, verbose=0)
            return prediction[0]
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None


if __name__ == "__main__":
    print("✅ PHASE 9.1: LSTM Predictor Ready")
