"""
🔱 DEMIR AI TRADING BOT - XGBoost Trend Classifier (Phase 4.3)
================================================================
Date: 2 Kasım 2025, 20:20 CET
Version: 1.0 - Machine Learning Trend Classification

PURPOSE:
--------
XGBoost-based trend classifier for BUY/SELL/HOLD signals
Uses 20+ features from ml_feature_engineer.py

MODEL:
------
• Algorithm: XGBoost Gradient Boosting
• Target: Price direction (UP/DOWN/FLAT)
• Features: Technical indicators + price patterns
• Training: Rolling window (last 1000 candles)
• Output: Probability distribution [BUY, SELL, HOLD]
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not installed: pip install xgboost")

try:
    from ml_feature_engineer import MLFeatureEngineer
    FEATURE_ENGINEER_AVAILABLE = True
except:
    FEATURE_ENGINEER_AVAILABLE = False
    print("⚠️ ML Feature Engineer not available")


class XGBoostTrendClassifier:
    """
    XGBoost-based trend classification model
    Predicts: BUY (price will rise), SELL (price will fall), HOLD (sideways)
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # XGBoost hyperparameters
        self.params = {
            'objective': 'multi:softprob',
            'num_class': 3,
            'max_depth': 5,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'use_label_encoder': False,
            'eval_metric': 'mlogloss'
        }
    
    def predict_trend(
        self,
        symbol: str = 'BTC/USDT',
        timeframe: str = '1h',
        lookback: int = 1000
    ) -> Dict[str, Any]:
        """
        Predict trend direction for given symbol
        
        Args:
            symbol: Trading pair
            timeframe: Candlestick interval
            lookback: Training data size
        
        Returns:
            Prediction with probabilities
        """
        
        if not XGBOOST_AVAILABLE or not FEATURE_ENGINEER_AVAILABLE:
            return self._generate_fallback_prediction()
        
        print(f"\n{'='*70}")
        print(f"🤖 XGBOOST TREND CLASSIFIER - {symbol}")
        print(f"{'='*70}")
        
        # Extract features
        engineer = MLFeatureEngineer()
        df = engineer.extract_features(symbol, timeframe, lookback)
        
        if df is None or len(df) < 100:
            print("❌ Insufficient data for training")
            return self._generate_fallback_prediction()
        
        # Prepare training data
        X_train, y_train, X_test = self._prepare_data(df, engineer.feature_names)
        
        # Train model
        self._train_model(X_train, y_train)
        
        # Predict
        prediction = self._predict(X_test)
        
        return prediction
    
    def _prepare_data(self, df: pd.DataFrame, feature_names: list):
        """
        Prepare training and test data
        
        Target:
        - 0 (SELL): Next 5 candles drop > 1%
        - 1 (HOLD): Next 5 candles move < 1%
        - 2 (BUY): Next 5 candles rise > 1%
        """
        
        # Calculate forward returns (next 5 candles)
        df['forward_return'] = df['close'].shift(-5).pct_change(5)
        
        # Create target labels
        df['target'] = 1  # Default: HOLD
        df.loc[df['forward_return'] > 0.01, 'target'] = 2  # BUY
        df.loc[df['forward_return'] < -0.01, 'target'] = 0  # SELL
        
        # Remove NaN
        df = df.dropna()
        
        # Split: Train (80%), Test (latest 20%)
        split_idx = int(len(df) * 0.8)
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df[feature_names]
        y_train = train_df['target']
        
        X_test = test_df[feature_names].iloc[-1:]  # Latest row only
        
        print(f"✅ Training data: {len(X_train)} samples")
        print(f"   BUY: {sum(y_train == 2)} | HOLD: {sum(y_train == 1)} | SELL: {sum(y_train == 0)}")
        
        return X_train, y_train, X_test
    
    def _train_model(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train XGBoost model"""
        
        print(f"\n🔧 Training XGBoost model...")
        
        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(X_train, y_train, verbose=False)
        
        self.feature_names = X_train.columns.tolist()
        self.is_trained = True
        
        # Training accuracy
        train_pred = self.model.predict(X_train)
        accuracy = (train_pred == y_train).mean()
        
        print(f"✅ Model trained | Accuracy: {accuracy*100:.1f}%")
    
    def _predict(self, X_test: pd.DataFrame) -> Dict[str, Any]:
        """Make prediction on test data"""
        
        # Get probabilities
        probs = self.model.predict_proba(X_test)[0]
        
        prob_sell = probs[0]
        prob_hold = probs[1]
        prob_buy = probs[2]
        
        # Determine signal
        if prob_buy > 0.60:
            signal = 'STRONG BUY'
            confidence = prob_buy
        elif prob_buy > 0.45:
            signal = 'BUY'
            confidence = prob_buy
        elif prob_sell > 0.60:
            signal = 'STRONG SELL'
            confidence = prob_sell
        elif prob_sell > 0.45:
            signal = 'SELL'
            confidence = prob_sell
        else:
            signal = 'HOLD'
            confidence = prob_hold
        
        # Calculate ML score (0-100)
        ml_score = 50 + (prob_buy - prob_sell) * 50
        
        result = {
            'signal': signal,
            'confidence': round(confidence, 2),
            'score': round(ml_score, 1),
            'probabilities': {
                'buy': round(prob_buy, 3),
                'hold': round(prob_hold, 3),
                'sell': round(prob_sell, 3)
            },
            'model': 'XGBoost',
            'timestamp': datetime.now().isoformat(),
            'version': 'v1.0-phase4.3'
        }
        
        print(f"\n{'='*70}")
        print(f"🎯 XGBOOST PREDICTION")
        print(f"{'='*70}")
        print(f"Signal: {signal}")
        print(f"ML Score: {ml_score:.1f}/100")
        print(f"Probabilities: BUY={prob_buy:.1%} | HOLD={prob_hold:.1%} | SELL={prob_sell:.1%}")
        print(f"{'='*70}\n")
        
        return result
    
    def _generate_fallback_prediction(self) -> Dict[str, Any]:
        """Fallback when XGBoost unavailable"""
        return {
            'signal': 'HOLD',
            'confidence': 0.50,
            'score': 50.0,
            'probabilities': {
                'buy': 0.33,
                'hold': 0.34,
                'sell': 0.33
            },
            'model': 'XGBoost-fallback',
            'timestamp': datetime.now().isoformat(),
            'error': 'XGBoost not available'
        }


# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":
    print("🔱 XGBoost Trend Classifier - Standalone Test")
    print("=" * 70)
    
    classifier = XGBoostTrendClassifier()
    
    result = classifier.predict_trend(
        symbol='BTC/USDT',
        timeframe='1h',
        lookback=1000
    )
    
    print(f"\n📊 Final Result:")
    print(f"Signal: {result['signal']}")
    print(f"ML Score: {result['score']}/100")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    
    print("\n✅ XGBoost Classifier test complete!")
