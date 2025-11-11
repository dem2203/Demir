import numpy as np
import pandas as pd
import os
from binance.client import Client
from datetime import datetime, timedelta

class LSTMNeuralLayer:
    """LSTM Neural Layer for time-series price prediction (NumPy-based)"""
    
    def __init__(self):
        self.lookback = 60
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = Client(self.api_key, self.api_secret)
    
    def get_real_data(self, symbol="BTCUSDT", interval="1h", limit=500):
        """Fetch REAL data from Binance"""
        try:
            klines = self.client.get_historical_klines(symbol, interval, limit=limit)
            closes = np.array([float(k[4]) for k in klines])
            return closes
        except Exception as e:
            print(f"LSTM Binance API error: {e}")
            return None
    
    def normalize_data(self, data):
        """Normalize prices to 0-1 range"""
        min_val = np.min(data)
        max_val = np.max(data)
        normalized = (data - min_val) / (max_val - min_val + 1e-8)
        return normalized, min_val, max_val
    
    def prepare_sequences(self, data):
        """Create sequences for LSTM-like analysis"""
        X, y = [], []
        for i in range(len(data) - self.lookback):
            X.append(data[i:i+self.lookback])
            y.append(data[i+self.lookback])
        return np.array(X), np.array(y)
    
    def analyze(self, symbol="BTCUSDT"):
        """Analyze price with NumPy-based LSTM prediction"""
        try:
            # Get REAL data from Binance
            data = self.get_real_data(symbol)
            if data is None:
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0.0,
                    "prediction": "No data"
                }
            
            # Normalize data
            normalized, min_val, max_val = self.normalize_data(data)
            
            # Simple trend analysis (replacing LSTM)
            recent_prices = normalized[-self.lookback:]
            
            # Calculate trend using linear regression
            x = np.arange(len(recent_prices))
            z = np.polyfit(x, recent_prices, 1)
            trend = z[0]
            
            # Predict next value
            next_value = z[0] * len(recent_prices) + z[1]
            current_price = data[-1]
            
            # Denormalize
            predicted_price = next_value * (max_val - min_val) + min_val
            
            # Generate signal
            if predicted_price > current_price * 1.01:
                signal = "LONG"
                confidence = min((predicted_price - current_price) / current_price, 1.0)
            elif predicted_price < current_price * 0.99:
                signal = "SHORT"
                confidence = min((current_price - predicted_price) / current_price, 1.0)
            else:
                signal = "NEUTRAL"
                confidence = 0.5
            
            return {
                "signal": signal,
                "confidence": round(float(confidence), 3),
                "current_price": float(current_price),
                "predicted_price": float(predicted_price),
                "trend": round(float(trend), 4)
            }
        
        except Exception as e:
            print(f"LSTM analysis error: {e}")
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "prediction": f"Error: {str(e)}"
            }

# Global instance
lstm_layer = LSTMNeuralLayer()
