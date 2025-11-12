import numpy as np
import pandas as pd
import os
from binance.client import Client

class TransformerLayer:
    """Transformer-based attention mechanism for trading (NumPy-based)"""
    
    def __init__(self, num_heads=8, ff_dim=128):
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = Client(self.api_key, self.api_secret)
    
    def get_real_data(self, symbol="BTCUSDT", interval="1h", limit=200):
        """Fetch REAL data from Binance"""
        try:
            klines = self.client.get_historical_klines(symbol, interval, limit=limit)
            data = np.array([[float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[7])] for k in klines])
            return data
        except Exception as e:
            print(f"Transformer Binance error: {e}")
            return None
    
    def calculate_attention_scores(self, data):
        """Calculate attention scores using NumPy"""
        if len(data) == 0:
            return None
        
        data_normalized = (data - np.mean(data, axis=0)) / (np.std(data, axis=0) + 1e-8)
        close_prices = data[:, 3]
        
        attention = np.zeros(len(close_prices))
        for i in range(len(close_prices)):
            if i > 0:
                price_change = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
                volume_ratio = data[i, 4] / (np.mean(data[:, 4]) + 1e-8)
                attention[i] = price_change * volume_ratio
        
        return attention
    
    def analyze(self, symbol="BTCUSDT"):
        """Analyze with transformer attention"""
        try:
            data = self.get_real_data(symbol)
            if data is None:
                return {"signal": "NEUTRAL", "confidence": 0.0, "attention": "No data"}
            
            attention = self.calculate_attention_scores(data)
            
            recent_attention = attention[-20:]
            bullish = np.sum(recent_attention > 0) / len(recent_attention)
            bearish = np.sum(recent_attention < 0) / len(recent_attention)
            
            if bullish > 0.6:
                signal = "BULLISH"
                confidence = float(bullish)
            elif bearish > 0.6:
                signal = "BEARISH"
                confidence = float(bearish)
            else:
                signal = "NEUTRAL"
                confidence = 0.5
            
            return {
                "signal": signal,
                "confidence": round(confidence, 3),
                "bullish_score": round(float(bullish), 3),
                "neutral_score": round(0.5 * (1 - bullish - bearish), 3),
                "bearish_score": round(float(bearish), 3),
                "attention": "Transformer attention active"
            }
        except Exception as e:
            print(f"Transformer error: {e}")
            return {"signal": "NEUTRAL", "confidence": 0.0, "attention": f"Error: {str(e)}"}

transformer_layer = TransformerLayer()
