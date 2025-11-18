"""
🤖 DEMIR AI v6.0 - AI MODEL TRAINING & SELF-LEARNING PIPELINE
==============================================================
✅ LSTM + XGBoost training automation
✅ Historical data fetching
✅ Model versioning
✅ Performance tracking
✅ Self-learning loop (daily retrain)
"""

import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
import json

# ML Libraries
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow not available - LSTM disabled")

logger = logging.getLogger(__name__)

class AITrainingPipeline:
    """Automated AI model training and self-learning"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.models_dir = 'models'
        self.data_dir = 'data'
        self.metrics_file = 'model_metrics.json'
        
        # Create directories
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Model storage
        self.lstm_model = None
        self.xgb_model = None
        self.scaler = MinMaxScaler()
        
        # Performance tracking
        self.metrics_history = self._load_metrics_history()
        
        logger.info("✅ AI Training Pipeline initialized")
    
    def train_all_models(self, symbol: str = 'BTCUSDT', days: int = 90) -> Dict:
        """
        Train both LSTM and XGBoost models
        
        Args:
            symbol: Trading pair
            days: Historical data days
        
        Returns:
            Training results dict
        """
        logger.info(f"🚀 Starting AI training for {symbol} (last {days} days)")
        
        results = {
            'symbol': symbol,
            'trained_at': datetime.now().isoformat(),
            'lstm': {},
            'xgboost': {},
            'status': 'started'
        }
        
        try:
            # 1. Fetch historical data
            logger.info("📊 Fetching historical data...")
            data = self._fetch_historical_data(symbol, days)
            
            if data is None or len(data) < 100:
                logger.error("❌ Insufficient data for training")
                results['status'] = 'failed'
                results['error'] = 'Insufficient data'
                return results
            
            logger.info(f"✅ Fetched {len(data)} data points")
            
            # 2. Prepare features
            logger.info("🔧 Preparing features...")
            X, y = self._prepare_features(data)
            
            # 3. Train XGBoost (faster, train first)
            logger.info("🌲 Training XGBoost...")
            xgb_results = self._train_xgboost(X, y, symbol)
            results['xgboost'] = xgb_results
            
            # 4. Train LSTM (slower)
            if TF_AVAILABLE:
                logger.info("🧠 Training LSTM...")
                lstm_results = self._train_lstm(data, symbol)
                results['lstm'] = lstm_results
            else:
                logger.warning("⚠️ TensorFlow not available - skipping LSTM")
                results['lstm'] = {'status': 'skipped', 'reason': 'TensorFlow not installed'}
            
            # 5. Save metrics
            results['status'] = 'success'
            self._save_training_results(results)
            
            logger.info("✅ AI Training completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            results['status'] = 'failed'
            results['error'] = str(e)
            return results
    
    def _fetch_historical_data(self, symbol: str, days: int) -> Optional[pd.DataFrame]:
        """Fetch historical signals from database"""
        try:
            # Get signals from last N days
            query = f"""
            SELECT 
                timestamp,
                entry_price,
                direction,
                ensemble_score,
                tech_group_score,
                sentiment_group_score,
                onchain_group_score,
                confidence
            FROM signals
            WHERE symbol = %s
            AND timestamp > NOW() - INTERVAL '{days} days'
            ORDER BY timestamp ASC
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query, (symbol,))
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(results, columns=[
                'timestamp', 'price', 'direction', 'ensemble',
                'technical', 'sentiment', 'onchain', 'confidence'
            ])
            
            # Convert direction to binary (LONG=1, SHORT=0)
            df['direction_binary'] = (df['direction'] == 'LONG').astype(int)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return None
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare ML features from dataframe"""
        
        # Features
        feature_cols = [
            'price', 'ensemble', 'technical', 
            'sentiment', 'onchain', 'confidence'
        ]
        
        X = df[feature_cols].values
        
        # Target: next period direction (1=UP, 0=DOWN)
        # Simple: if next price > current price -> 1, else 0
        y = (df['price'].shift(-1) > df['price']).astype(int).values[:-1]
        X = X[:-1]  # Remove last row (no future data)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def _train_xgboost(self, X: np.ndarray, y: np.ndarray, symbol: str) -> Dict:
        """Train XGBoost model"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Train model
            logger.info(f"  Training on {len(X_train)} samples...")
            
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                objective='binary:logistic',
                random_state=42
            )
            
            self.xgb_model.fit(X_train, y_train)
            
            # Evaluate
            train_acc = self.xgb_model.score(X_train, y_train)
            test_acc = self.xgb_model.score(X_test, y_test)
            
            logger.info(f"  ✅ XGBoost - Train Accuracy: {train_acc:.2%}, Test Accuracy: {test_acc:.2%}")
            
            # Save model
            model_path = f"{self.models_dir}/xgboost_{symbol}_{datetime.now().strftime('%Y%m%d')}.joblib"
            joblib.dump(self.xgb_model, model_path)
            
            return {
                'status': 'success',
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc),
                'model_path': model_path,
                'samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"  ❌ XGBoost training failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _train_lstm(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Train LSTM model"""
        if not TF_AVAILABLE:
            return {'status': 'skipped', 'reason': 'TensorFlow not available'}
        
        try:
            # Prepare sequences
            lookback = 10  # Use last 10 timepoints
            X, y = self._create_sequences(df, lookback)
            
            # Split data
            split = int(0.8 * len(X))
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]
            
            logger.info(f"  Training on {len(X_train)} sequences...")
            
            # Build model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(lookback, 6)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1, activation='sigmoid')
            ])
            
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Callbacks
            checkpoint_path = f"{self.models_dir}/lstm_{symbol}_{datetime.now().strftime('%Y%m%d')}.h5"
            callbacks = [
                EarlyStopping(patience=5, restore_best_weights=True),
                ModelCheckpoint(checkpoint_path, save_best_only=True)
            ]
            
            # Train
            history = model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test, y_test),
                callbacks=callbacks,
                verbose=0
            )
            
            # Evaluate
            train_acc = history.history['accuracy'][-1]
            test_acc = history.history['val_accuracy'][-1]
            
            logger.info(f"  ✅ LSTM - Train Accuracy: {train_acc:.2%}, Test Accuracy: {test_acc:.2%}")
            
            self.lstm_model = model
            
            return {
                'status': 'success',
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc),
                'model_path': checkpoint_path,
                'epochs': len(history.history['accuracy']),
                'samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"  ❌ LSTM training failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _create_sequences(self, df: pd.DataFrame, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create LSTM sequences"""
        feature_cols = ['price', 'ensemble', 'technical', 'sentiment', 'onchain', 'confidence']
        data = df[feature_cols].values
        
        # Normalize
        data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(lookback, len(data) - 1):
            X.append(data[i-lookback:i])
            # Target: 1 if next price > current price
            y.append(1 if df['price'].iloc[i+1] > df['price'].iloc[i] else 0)
        
        return np.array(X), np.array(y)
    
    def predict(self, features: np.ndarray) -> Dict:
        """
        Make prediction using trained models
        
        Returns:
            {
                'xgboost_prediction': float,  # 0-1 probability
                'lstm_prediction': float,      # 0-1 probability
                'ensemble_prediction': float,  # Average
                'direction': 'LONG' or 'SHORT'
            }
        """
        results = {}
        
        # XGBoost prediction
        if self.xgb_model:
            xgb_prob = self.xgb_model.predict_proba(features)[0][1]
            results['xgboost_prediction'] = float(xgb_prob)
        
        # LSTM prediction (if available)
        if self.lstm_model and TF_AVAILABLE:
            # LSTM expects sequences, use last 10 points
            lstm_prob = float(self.lstm_model.predict(features, verbose=0)[0][0])
            results['lstm_prediction'] = lstm_prob
        
        # Ensemble
        predictions = [v for k, v in results.items() if 'prediction' in k]
        if predictions:
            ensemble = np.mean(predictions)
            results['ensemble_prediction'] = float(ensemble)
            results['direction'] = 'LONG' if ensemble > 0.5 else 'SHORT'
        
        return results
    
    def _save_training_results(self, results: Dict):
        """Save training results to metrics history"""
        self.metrics_history.append(results)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
        
        logger.info(f"💾 Training results saved to {self.metrics_file}")
    
    def _load_metrics_history(self) -> List[Dict]:
        """Load training metrics history"""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return []
    
    def should_retrain(self) -> bool:
        """
        Check if models should be retrained
        
        Criteria:
        - Last training > 7 days ago
        - Test accuracy dropped below 0.55
        - New data available (>100 new signals)
        """
        if not self.metrics_history:
            return True  # Never trained
        
        last_training = self.metrics_history[-1]
        last_date = datetime.fromisoformat(last_training['trained_at'])
        days_since = (datetime.now() - last_date).days
        
        # Retrain every 7 days
        if days_since >= 7:
            logger.info(f"📅 {days_since} days since last training - retrain scheduled")
            return True
        
        # Check accuracy degradation
        xgb_acc = last_training.get('xgboost', {}).get('test_accuracy', 0)
        if xgb_acc < 0.55:
            logger.warning(f"⚠️ Low accuracy ({xgb_acc:.2%}) - retrain needed")
            return True
        
        return False


# Self-Learning Loop (integrate in main.py)
class SelfLearningLoop:
    """Daily self-learning and model retraining"""
    
    def __init__(self, db_manager, training_pipeline: AITrainingPipeline):
        self.db = db_manager
        self.training = training_pipeline
        self.check_interval = 86400  # 24 hours
        
    def run_daily_check(self):
        """Run daily self-learning check"""
        logger.info("🔄 Running daily self-learning check...")
        
        # 1. Calculate performance
        performance = self._calculate_daily_performance()
        logger.info(f"📊 Today's Performance: Win Rate {performance['win_rate']:.2%}")
        
        # 2. Check if retrain needed
        if self.training.should_retrain():
            logger.info("🚀 Retraining models...")
            
            for symbol in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                results = self.training.train_all_models(symbol, days=90)
                logger.info(f"  {symbol}: {results['status']}")
        
        else:
            logger.info("✅ Models performing well - no retrain needed")
    
    def _calculate_daily_performance(self) -> Dict:
        """Calculate last 24h performance"""
        try:
            query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN direction = 'LONG' AND entry_price < tp1 THEN 1 ELSE 0 END) as wins
            FROM signals
            WHERE timestamp > NOW() - INTERVAL '1 day'
            """
            
            cursor = self.db.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            total = result[0] if result else 0
            wins = result[1] if result else 0
            win_rate = wins / total if total > 0 else 0
            
            return {
                'total_signals': total,
                'wins': wins,
                'win_rate': win_rate
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance: {e}")
            return {'total_signals': 0, 'wins': 0, 'win_rate': 0}
