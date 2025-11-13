"""
XGBOOST ML LAYER - v2.0
Machine Learning predictions with BaseLayer
⚠️ Real training data only, no mock predictions
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class XGBoostMLLayer(BaseLayer):
    """XGBoost ML Layer with real market data"""
    
    def __init__(self, n_estimators=100, learning_rate=0.1):
        """Initialize"""
        super().__init__('XGBoostML_Layer')
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
    
    async def get_signal(self, price_data):
        """Get ML prediction signal"""
        return await self.execute_with_retry(
            self._make_prediction,
            price_data
        )
    
    async def _make_prediction(self, price_data):
        """Make ML prediction on REAL data"""
        
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        try:
            # Extract features from REAL prices
            df = self._extract_features(price_data)
            
            if df is None or len(df) == 0:
                raise ValueError("Feature extraction failed")
            
            # Get latest row
            X = df[self.feature_names].values[-1].reshape(1, -1)
            X = self.scaler.transform(X)
            
            # Predict
            pred = self.model.predict(X)
            proba = self.model.predict_proba(X)
            
            # Get confidence
            confidence = max(proba)
            direction = 'LONG' if pred == 1 else 'SHORT'
            score = float(proba * 100)  # UP probability
            
            return {
                'signal': direction,
                'score': score,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            raise ValueError(f"ML error: {e}")
    
    def _extract_features(self, price_data):
        """Extract features from REAL prices"""
        try:
            if not isinstance(price_data, list) or len(price_data) < 30:
                return None
            
            df = pd.DataFrame({'price': price_data})
            
            # REAL technical features
            df['sma_10'] = df['price'].rolling(10).mean()
            df['sma_30'] = df['price'].rolling(30).mean()
            df['rsi'] = self._calculate_rsi(df['price'])
            df['volatility'] = df['price'].rolling(10).std()
            df['momentum'] = df['price'].diff(5)
            
            self.feature_names = ['sma_10', 'sma_30', 'rsi', 'volatility', 'momentum']
            
            # Create target
            df['target'] = (df['price'].shift(-1) > df['price']).astype(int)
            
            return df.dropna()
        
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return None
    
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
