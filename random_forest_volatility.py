"""
🔱 DEMIR AI TRADING BOT - Random Forest Volatility Predictor (Phase 4.3)
=========================================================================
Date: 2 Kasım 2025, 20:25 CET
Version: 1.0 - ML Volatility Forecasting

PURPOSE:
--------
Random Forest model to predict next period volatility
Used for position sizing and risk management

MODEL:
------
• Algorithm: Random Forest Regression
• Target: Next 10-period volatility (std of returns)
• Features: Historical volatility, ATR, BB width
• Training: Rolling window (last 1000 candles)
• Output: Volatility forecast (0.5% - 5% range)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not installed: pip install scikit-learn")

try:
    from ml_feature_engineer import MLFeatureEngineer
    FEATURE_ENGINEER_AVAILABLE = True
except:
    FEATURE_ENGINEER_AVAILABLE = False
    print("⚠️ ML Feature Engineer not available")


class RandomForestVolatilityPredictor:
    """
    Random Forest-based volatility forecasting
    Predicts next period volatility for risk management
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Random Forest hyperparameters
        self.params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'random_state': 42,
            'n_jobs': -1
        }
    
    def predict_volatility(
        self,
        symbol: str = 'BTC/USDT',
        timeframe: str = '1h',
        lookback: int = 1000
    ) -> Dict[str, Any]:
        """
        Predict next period volatility
        
        Args:
            symbol: Trading pair
            timeframe: Candlestick interval
            lookback: Training data size
        
        Returns:
            Volatility forecast with risk level
        """
        
        if not SKLEARN_AVAILABLE or not FEATURE_ENGINEER_AVAILABLE:
            return self._generate_fallback_prediction()
        
        print(f"\n{'='*70}")
        print(f"🌪️  RANDOM FOREST VOLATILITY PREDICTOR - {symbol}")
        print(f"{'='*70}")
        
        # Extract features
        engineer = MLFeatureEngineer()
        df = engineer.extract_features(symbol, timeframe, lookback)
        
        if df is None or len(df) < 100:
            print("❌ Insufficient data for training")
            return self._generate_fallback_prediction()
        
        # Prepare training data
        X_train, y_train, X_test = self._prepare_volatility_data(df)
        
        # Train model
        self._train_model(X_train, y_train)
        
        # Predict
        prediction = self._predict_volatility(X_test, y_train)
        
        return prediction
    
    def _prepare_volatility_data(self, df: pd.DataFrame):
        """
        Prepare data for volatility prediction
        
        Target: Next 10-period rolling standard deviation
        """
        
        # Calculate forward volatility (next 10 periods)
        df['forward_volatility'] = df['return_1'].rolling(10).std().shift(-10)
        
        # Volatility features
        vol_features = [
            'volatility_10', 'volatility_20', 'atr_14', 'bb_width',
            'volume_ratio', 'return_1', 'return_5', 'return_10'
        ]
        
        # Remove NaN
        df = df.dropna()
        
        # Split: Train (80%), Test (latest 20%)
        split_idx = int(len(df) * 0.8)
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df[vol_features]
        y_train = train_df['forward_volatility']
        
        X_test = test_df[vol_features].iloc[-1:]  # Latest row
        
        self.feature_names = vol_features
        
        print(f"✅ Training data: {len(X_train)} samples")
        print(f"   Mean volatility: {y_train.mean()*100:.2f}%")
        
        return X_train, y_train, X_test
    
    def _train_model(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train Random Forest model"""
        
        print(f"\n🔧 Training Random Forest model...")
        
        self.model = RandomForestRegressor(**self.params)
        self.model.fit(X_train, y_train)
        
        self.is_trained = True
        
        # Training R² score
        train_pred = self.model.predict(X_train)
        r2 = 1 - np.sum((y_train - train_pred)**2) / np.sum((y_train - y_train.mean())**2)
        
        print(f"✅ Model trained | R² Score: {r2:.3f}")
    
    def _predict_volatility(self, X_test: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Predict next period volatility"""
        
        # Forecast
        vol_forecast = self.model.predict(X_test)[0]
        
        # Historical volatility stats
        hist_mean = y_train.mean()
        hist_std = y_train.std()
        
        # Normalize to percentile
        z_score = (vol_forecast - hist_mean) / hist_std
        
        # Determine risk level
        if z_score > 1.5:
            risk_level = 'EXTREME'
            risk_score = 90
        elif z_score > 1.0:
            risk_level = 'HIGH'
            risk_score = 75
        elif z_score > 0.5:
            risk_level = 'ELEVATED'
            risk_score = 60
        elif z_score > -0.5:
            risk_level = 'NORMAL'
            risk_score = 50
        else:
            risk_level = 'LOW'
            risk_score = 30
        
        # Position sizing adjustment
        if risk_level == 'EXTREME':
            position_multiplier = 0.5  # Cut position by 50%
        elif risk_level == 'HIGH':
            position_multiplier = 0.7  # Cut position by 30%
        elif risk_level == 'ELEVATED':
            position_multiplier = 0.85
        else:
            position_multiplier = 1.0
        
        result = {
            'volatility_forecast': round(vol_forecast * 100, 2),  # As percentage
            'risk_level': risk_level,
            'risk_score': risk_score,
            'position_multiplier': position_multiplier,
            'historical_mean': round(hist_mean * 100, 2),
            'z_score': round(z_score, 2),
            'model': 'RandomForest',
            'timestamp': datetime.now().isoformat(),
            'version': 'v1.0-phase4.3'
        }
        
        print(f"\n{'='*70}")
        print(f"🌪️  VOLATILITY FORECAST")
        print(f"{'='*70}")
        print(f"Predicted Volatility: {vol_forecast*100:.2f}%")
        print(f"Risk Level: {risk_level}")
        print(f"Position Multiplier: {position_multiplier:.2f}x")
        print(f"Z-Score: {z_score:.2f} (vs historical)")
        print(f"{'='*70}\n")
        
        return result
    
    def _generate_fallback_prediction(self) -> Dict[str, Any]:
        """Fallback when Random Forest unavailable"""
        return {
            'volatility_forecast': 2.0,
            'risk_level': 'NORMAL',
            'risk_score': 50,
            'position_multiplier': 1.0,
            'historical_mean': 2.0,
            'z_score': 0.0,
            'model': 'RandomForest-fallback',
            'timestamp': datetime.now().isoformat(),
            'error': 'RandomForest not available'
        }


# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":
    print("🔱 Random Forest Volatility Predictor - Standalone Test")
    print("=" * 70)
    
    predictor = RandomForestVolatilityPredictor()
    
    result = predictor.predict_volatility(
        symbol='BTC/USDT',
        timeframe='1h',
        lookback=1000
    )
    
    print(f"\n📊 Final Result:")
    print(f"Volatility Forecast: {result['volatility_forecast']}%")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Position Multiplier: {result['position_multiplier']}x")
    
    print("\n✅ Random Forest Volatility test complete!")
