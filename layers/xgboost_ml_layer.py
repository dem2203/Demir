"""
PHASE 4.3: XGBOOST ML LAYER
Advanced machine learning predictions using XGBoost

Folder: layers/xgboost_ml_layer.py
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """Machine learning prediction result"""
    symbol: str
    direction: str  # "BUY", "SELL", "HOLD"
    confidence: float
    score: float
    features_used: List[str]
    timestamp: str


class XGBoostMLLayer:
    """
    XGBoost-based machine learning layer for price prediction
    
    Features:
    - Automatic feature engineering
    - Model training and validation
    - Real-time predictions
    - Feature importance analysis
    """
    
    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1):
        """
        Initialize XGBoost ML Layer
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Learning rate for training
        """
        self.model: Optional[xgb.XGBClassifier] = None
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.is_trained = False
        
    def extract_features(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from price data
        
        Args:
            price_data: DataFrame with OHLCV columns
            
        Returns:
            DataFrame with engineered features
        """
        df = price_data.copy()
        
        # Technical indicators as features
        df['sma_10'] = df['close'].rolling(10).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['rsi'] = self._calculate_rsi(df['close'])
        df['macd'] = self._calculate_macd(df['close'])
        df['atr'] = self._calculate_atr(df)
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['price_change'].rolling(20).std()
        
        # Drop NaN values
        df = df.dropna()
        
        self.feature_names = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices: pd.Series) -> pd.Series:
        """Calculate MACD"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        return macd
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift()),
                abs(df['low'] - df['close'].shift())
            )
        )
        atr = df['tr'].rolling(period).mean()
        return atr
    
    def prepare_training_data(self, price_data: pd.DataFrame, lookahead: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data with target labels
        
        Args:
            price_data: Historical price data
            lookahead: Days ahead to predict
            
        Returns:
            X (features), y (labels)
        """
        df = self.extract_features(price_data)
        
        # Create target: 1 if price goes up, 0 if down
        df['target'] = (df['close'].shift(-lookahead) > df['close']).astype(int)
        
        # Remove rows with NaN
        df = df.dropna()
        
        X = df[self.feature_names].values
        y = df['target'].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, val_split: float = 0.2) -> Dict[str, float]:
        """
        Train XGBoost model
        
        Args:
            X: Training features
            y: Training labels
            val_split: Validation split ratio
            
        Returns:
            Training metrics
        """
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=val_split, random_state=42)
        
        self.model = xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=6,
            random_state=42
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=10,
            verbose=False
        )
        
        train_score = self.model.score(X_train, y_train)
        val_score = self.model.score(X_val, y_val)
        
        self.is_trained = True
        
        return {
            'train_accuracy': train_score,
            'validation_accuracy': val_score,
            'best_iteration': self.model.best_iteration
        }
    
    def predict(self, price_data: pd.DataFrame, symbol: str = "UNKNOWN") -> Optional[MLPrediction]:
        """
        Make prediction on new data
        
        Args:
            price_data: Recent price data
            symbol: Trading pair symbol
            
        Returns:
            MLPrediction object or None if not trained
        """
        if not self.is_trained or self.model is None:
            logger.warning("Model not trained yet")
            return None
        
        try:
            df = self.extract_features(price_data)
            
            if len(df) == 0:
                return None
            
            # Get latest row
            X = df[self.feature_names].values[-1:, ]
            X = self.scaler.transform(X)
            
            # Predict
            pred = self.model.predict(X)[0]
            prob = self.model.predict_proba(X)[0]
            
            confidence = max(prob)
            direction = "BUY" if pred == 1 else "SELL"
            score = float(prob[1])  # Probability of upward movement
            
            return MLPrediction(
                symbol=symbol,
                direction=direction,
                confidence=confidence,
                score=score,
                features_used=self.feature_names,
                timestamp=str(pd.Timestamp.now())
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if self.model is None:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    layer = XGBoostMLLayer()
    print("XGBoost ML Layer initialized successfully")
