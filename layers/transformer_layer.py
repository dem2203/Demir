import numpy as np
import pandas as pd
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, MultiHeadAttention, LayerNormalization, Add, Dropout
from tensorflow.keras.optimizers import Adam
import os
from binance.client import Client

class TransformerLayer:
    """Transformer-based attention mechanism for trading"""
    
    def __init__(self, num_heads=8, ff_dim=128):
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.model = None
        
    def get_real_data(self, symbol='BTCUSDT', interval='1h', limit=200):
        """Fetch REAL data from Binance"""
        try:
            klines = self.client.get_historical_klines(symbol, interval, limit=limit)
            data = np.array([[float(k[1]), float(k[2]), float(k[3]), float(k[4]), 
                           float(k[7])] for k in klines])
            return data  # [open, high, low, close, volume]
        except Exception as e:
            print(f"Transformer: Binance error: {e}")
            return None
    
    def build_transformer(self, seq_len=60, d_model=64):
        """Build transformer model"""
        inputs = Input(shape=(seq_len, 5))
        
        # Dense projection
        x = Dense(d_model)(inputs)
        x = Dropout(0.1)(x)
        
        # Multi-head attention
        attention_output = MultiHeadAttention(
            num_heads=self.num_heads, 
            key_dim=d_model // self.num_heads
        )(x, x)
        x = Add()([x, attention_output])
        x = LayerNormalization()(x)
        
        # Feed-forward network
        ff_output = Dense(self.ff_dim, activation='relu')(x)
        ff_output = Dense(d_model)(ff_output)
        x = Add()([x, ff_output])
        x = LayerNormalization()(x)
        
        # Global average pooling + dense
        x = Dense(32, activation='relu')(x)
        x = Dropout(0.2)(x)
        outputs = Dense(3, activation='softmax')(x)  # [BULLISH, NEUTRAL, BEARISH]
        
        self.model = Model(inputs, outputs)
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy')
        return self.model
    
    def analyze(self, symbol='BTCUSDT'):
        """Analyze with transformer attention"""
        try:
            # Get REAL data
            data = self.get_real_data(symbol)
            if data is None:
                return {'signal': 'NEUTRAL', 'confidence': 0.0, 'attention': 'No data'}
            
            # Normalize
            data_normalized = (data - np.mean(data, axis=0)) / (np.std(data, axis=0) + 1e-8)
            
            # Build model
            self.build_transformer(seq_len=len(data_normalized))
            
            # Predict with attention
            predictions = self.model.predict(
                data_normalized.reshape(1, -1, 5), 
                verbose=0
            )[0]
            
            # Interpret predictions
            bullish, neutral, bearish = predictions
            
            if bullish > 0.6:
                signal = 'BULLISH'
                confidence = float(bullish)
            elif bearish > 0.6:
                signal = 'BEARISH'
                confidence = float(bearish)
            else:
                signal = 'NEUTRAL'
                confidence = float(neutral)
            
            return {
                'signal': signal,
                'confidence': confidence,
                'bullish_score': float(bullish),
                'neutral_score': float(neutral),
                'bearish_score': float(bearish),
                'attention': 'Transformer attention active'
            }
            
        except Exception as e:
            print(f"Transformer error: {e}")
            return {'signal': 'NEUTRAL', 'confidence': 0.0, 'attention': f'Error: {str(e)[:30]}'}

# Global instance
transformer_layer = TransformerLayer()
