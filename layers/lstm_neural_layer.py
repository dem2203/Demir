import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os
from binance.client import Client
from datetime import datetime, timedelta

class LSTMNeuralLayer:
    """LSTM Neural Network for time-series price prediction"""
    
    def __init__(self):
        self.model = None
        self.lookback = 60
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        
    def get_real_data(self, symbol='BTCUSDT', interval='1h', limit=500):
        """Fetch REAL data from Binance"""
        try:
            klines = self.client.get_historical_klines(symbol, interval, limit=limit)
            closes = np.array([float(k[4]) for k in klines])
            return closes
        except Exception as e:
            print(f"LSTM: Binance API error: {e}")
            return None
    
    def normalize_data(self, data):
        """Normalize prices to 0-1 range"""
        min_val = np.min(data)
        max_val = np.max(data)
        normalized = (data - min_val) / (max_val - min_val)
        return normalized, min_val, max_val
    
    def prepare_sequences(self, data):
        """Create sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.lookback):
            X.append(data[i:i + self.lookback])
            y.append(data[i + self.lookback])
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        self.model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return self.model
    
    def analyze(self, symbol='BTCUSDT'):
        """Analyze price with LSTM prediction"""
        try:
            # Get REAL data
            data = self.get_real_data(symbol)
            if data is None:
                return {'signal': 'NEUTRAL', 'confidence': 0.0, 'prediction': 'Unknown'}
            
            # Normalize
            normalized, min_val, max_val = self.normalize_data(data)
            
            # Prepare sequences
            X, y = self.prepare_sequences(normalized)
            
            # Build model
            self.build_model((self.lookback, 1))
            
            # Train on data
            X_train = X[:int(len(X) * 0.8)]
            y_train = y[:int(len(y) * 0.8)]
            self.model.fit(X_train.reshape(-1, self.lookback, 1), y_train, 
                          epochs=10, batch_size=32, verbose=0)
            
            # Predict next candle
            last_sequence = normalized[-self.lookback:]
            next_price_normalized = self.model.predict(
                last_sequence.reshape(1, self.lookback, 1), verbose=0
            )[0][0]
            
            # Denormalize
            next_price = next_price_normalized * (max_val - min_val) + min_val
            current_price = data[-1]
            
            # Generate signal
            if next_price > current_price * 1.01:  # 1% threshold
                signal = 'BULLISH'
                confidence = min((next_price - current_price) / current_price, 1.0)
            elif next_price < current_price * 0.99:
                signal = 'BEARISH'
                confidence = min((current_price - next_price) / current_price, 1.0)
            else:
                signal = 'NEUTRAL'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': float(confidence),
                'current_price': float(current_price),
                'predicted_price': float(next_price),
                'prediction': f"Next: ${next_price:.2f}"
            }
            
        except Exception as e:
            print(f"LSTM analysis error: {e}")
            return {'signal': 'NEUTRAL', 'confidence': 0.0, 'prediction': f'Error: {str(e)[:50]}'}

# Global instance
lstm_layer = LSTMNeuralLayer()
```
