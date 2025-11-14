#!/usr/bin/env python3
"""
🔱 DEMIR AI - training_pipeline.py (HAFTA 3-7)
============================================================================
LSTM + TRANSFORMER TRAINING - ORCHESTRATOR
Zero mock, fail loud, strict validation
============================================================================
"""

import logging
import traceback
import os
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
import numpy as np
import psycopg2
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class TrainingPipeline:
    """Train LSTM + Transformer ensemble - PRODUCTION READY"""
    
    def __init__(self, db_url: str):
        if not db_url:
            raise ValueError("❌ Missing database URL")
        
        self.db_url = db_url
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT']
        self.models_dir = 'models'
        
        os.makedirs(self.models_dir, exist_ok=True)
        logger.info("✅ TrainingPipeline initialized")
    
    def fetch_features_from_db(self, symbol: str) -> Tuple[np.ndarray, np.ndarray]:
        """Fetch features from database - STRICT"""
        try:
            logger.info(f"📊 Fetching features for {symbol}...")
            
            conn = psycopg2.connect(self.db_url)
            
            query = f"""
                SELECT * FROM feature_store 
                WHERE symbol = '{symbol}' 
                ORDER BY timestamp ASC
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            if df.empty:
                raise ValueError(f"❌ No features found for {symbol}")
            
            if len(df) < 100:
                raise ValueError(f"❌ Insufficient features: {len(df)} < 100")
            
            # Extract features (skip symbol, timestamp, price columns)
            feature_cols = [c for c in df.columns if c not in [
                'id', 'symbol', 'timestamp', 'price', 'label', 'created_at'
            ]]
            
            X = df[feature_cols].values
            y = df['label'].values
            
            # Validate
            if np.any(np.isnan(X)):
                raise ValueError(f"❌ NaN in features for {symbol}")
            
            if np.any(np.isinf(X)):
                raise ValueError(f"❌ Inf in features for {symbol}")
            
            logger.info(f"✅ {symbol}: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y
        
        except Exception as e:
            logger.critical(f"❌ Feature fetch failed: {e}")
            raise
    
    def prepare_training_data(self, X: np.ndarray, y: np.ndarray, 
                             lookback: int = 100) -> Tuple:
        """Prepare sliding windows - STRICT"""
        try:
            if X.shape[0] < lookback:
                raise ValueError(f"❌ Insufficient samples: {X.shape[0]} < {lookback}")
            
            X_windows = []
            y_windows = []
            
            for i in range(len(X) - lookback):
                X_windows.append(X[i:i+lookback])
                y_windows.append(y[i+lookback])
            
            X_windows = np.array(X_windows)
            y_windows = np.array(y_windows)
            
            if len(X_windows) == 0:
                raise ValueError("❌ No training windows created")
            
            logger.info(f"✅ Created {len(X_windows)} training windows")
            return X_windows, y_windows
        
        except Exception as e:
            logger.critical(f"❌ Data preparation failed: {e}")
            raise
    
    def split_data(self, X: np.ndarray, y: np.ndarray
                  ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, 
                            np.ndarray, np.ndarray]:
        """Train/Val/Test split - STRICT"""
        try:
            from sklearn.model_selection import train_test_split
            
            # 70/30 split
            X_train_val, X_test, y_train_val, y_test = train_test_split(
                X, y, test_size=0.15, random_state=42, stratify=y
            )
            
            # 70/30 of train_val
            X_train, X_val, y_train, y_val = train_test_split(
                X_train_val, y_train_val, test_size=0.176, 
                random_state=42, stratify=y_train_val
            )
            
            if len(X_train) < 50 or len(X_val) < 20 or len(X_test) < 20:
                raise ValueError("❌ Split resulted in too few samples")
            
            logger.info(f"✅ Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
            return X_train, X_val, X_test, y_train, y_val, y_test
        
        except Exception as e:
            logger.critical(f"❌ Data split failed: {e}")
            raise
    
    def train_lstm(self, symbol: str, X_train: np.ndarray, y_train: np.ndarray,
                  X_val: np.ndarray, y_val: np.ndarray,
                  X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Train LSTM - STRICT"""
        try:
            from ml_layers.lstm_model import LSTMModel
            
            logger.info(f"🚀 Training LSTM for {symbol}...")
            
            lstm = LSTMModel(lookback=100, n_features=X_train.shape[2])
            lstm.build_model()
            
            # Train
            history = lstm.train(X_train, y_train, X_val, y_val, epochs=100)
            
            # Evaluate
            metrics = lstm.evaluate(X_test, y_test)
            
            if metrics['accuracy'] < 0.33:
                raise ValueError(f"❌ LSTM accuracy too low: {metrics['accuracy']}")
            
            # Save
            model_path = f"{self.models_dir}/lstm_{symbol}.h5"
            lstm.save_model(model_path)
            
            logger.info(f"✅ {symbol} LSTM: Acc={metrics['accuracy']:.4f}, F1={metrics['f1_score']:.4f}")
            
            return {
                'symbol': symbol,
                'model': 'lstm',
                'accuracy': metrics['accuracy'],
                'f1_score': metrics['f1_score'],
                'loss': metrics['loss'],
                'model_path': model_path
            }
        
        except Exception as e:
            logger.critical(f"❌ LSTM training failed for {symbol}: {e}")
            raise
    
    def train_transformer(self, symbol: str, X_train: np.ndarray, y_train: np.ndarray,
                         X_val: np.ndarray, y_val: np.ndarray,
                         X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Train Transformer - STRICT"""
        try:
            from ml_layers.transformer_model import TransformerModel
            
            logger.info(f"🚀 Training Transformer for {symbol}...")
            
            transformer = TransformerModel(lookback=100, n_features=X_train.shape[2])
            transformer.build_model()
            
            # Train
            history = transformer.train(X_train, y_train, X_val, y_val, epochs=100)
            
            # Evaluate
            metrics = transformer.evaluate(X_test, y_test)
            
            if metrics['accuracy'] < 0.33:
                raise ValueError(f"❌ Transformer accuracy too low: {metrics['accuracy']}")
            
            # Save
            model_path = f"{self.models_dir}/transformer_{symbol}.h5"
            transformer.save_model(model_path)
            
            logger.info(f"✅ {symbol} Transformer: Acc={metrics['accuracy']:.4f}, F1={metrics['f1_score']:.4f}")
            
            return {
                'symbol': symbol,
                'model': 'transformer',
                'accuracy': metrics['accuracy'],
                'f1_score': metrics['f1_score'],
                'loss': metrics['loss'],
                'model_path': model_path
            }
        
        except Exception as e:
            logger.critical(f"❌ Transformer training failed for {symbol}: {e}")
            raise
    
    def test_ensemble(self, symbol: str, X_test: np.ndarray, y_test: np.ndarray,
                     lstm_path: str, transformer_path: str) -> Dict:
        """Test ensemble - STRICT"""
        try:
            from ml_layers.lstm_model import LSTMModel
            from ml_layers.transformer_model import TransformerModel
            from ml_layers.ensemble_system import EnsembleVoter
            
            logger.info(f"🧪 Testing Ensemble for {symbol}...")
            
            # Load models
            lstm = LSTMModel()
            lstm.load_model(lstm_path)
            
            transformer = TransformerModel()
            transformer.load_model(transformer_path)
            
            # Create ensemble
            ensemble = EnsembleVoter(lstm, transformer)
            
            # Test
            correct = 0
            for i, (features, true_label) in enumerate(zip(X_test, y_test)):
                try:
                    signal, conf = ensemble.generate_ensemble_signal(features)
                    
                    # Map signal to label
                    signal_to_label = {'DOWN': 0, 'HOLD': 1, 'UP': 2}
                    pred_label = signal_to_label.get(signal, 1)
                    
                    if pred_label == true_label:
                        correct += 1
                
                except Exception as e:
                    logger.warning(f"⚠️ Prediction failed at {i}: {e}")
                    continue
            
            accuracy = correct / len(X_test) if X_test.shape[0] > 0 else 0
            
            if accuracy < 0.33:
                raise ValueError(f"❌ Ensemble accuracy too low: {accuracy}")
            
            logger.info(f"✅ {symbol} Ensemble: Acc={accuracy:.4f}")
            
            return {
                'symbol': symbol,
                'model': 'ensemble',
                'accuracy': accuracy,
                'correct': correct,
                'total': len(X_test)
            }
        
        except Exception as e:
            logger.critical(f"❌ Ensemble test failed for {symbol}: {e}")
            raise
    
    def run_full_pipeline(self):
        """Full training pipeline - STRICT"""
        try:
            logger.info("="*80)
            logger.info("🚀 STARTING FULL TRAINING PIPELINE (LSTM + TRANSFORMER)")
            logger.info("="*80)
            
            results = {
                'lstm': [],
                'transformer': [],
                'ensemble': []
            }
            
            for symbol in self.symbols:
                logger.info(f"\n{'='*80}")
                logger.info(f"Processing {symbol}")
                logger.info(f"{'='*80}")
                
                # Fetch features
                X, y = self.fetch_features_from_db(symbol)
                
                # Prepare data
                X_windows, y_windows = self.prepare_training_data(X, y)
                
                # Split
                X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(
                    X_windows, y_windows
                )
                
                # Train LSTM
                lstm_result = self.train_lstm(
                    symbol, X_train, y_train, X_val, y_val, X_test, y_test
                )
                results['lstm'].append(lstm_result)
                
                # Train Transformer
                transformer_result = self.train_transformer(
                    symbol, X_train, y_train, X_val, y_val, X_test, y_test
                )
                results['transformer'].append(transformer_result)
                
                # Test Ensemble
                ensemble_result = self.test_ensemble(
                    symbol, X_test, y_test, 
                    lstm_result['model_path'],
                    transformer_result['model_path']
                )
                results['ensemble'].append(ensemble_result)
            
            # Summary
            logger.info(f"\n{'='*80}")
            logger.info("📊 TRAINING SUMMARY")
            logger.info(f"{'='*80}")
            
            for model_type in ['lstm', 'transformer', 'ensemble']:
                accuracies = [r['accuracy'] for r in results[model_type]]
                avg_acc = np.mean(accuracies)
                min_acc = np.min(accuracies)
                max_acc = np.max(accuracies)
                
                logger.info(f"\n{model_type.upper()}:")
                logger.info(f"  Average Accuracy: {avg_acc:.4f}")
                logger.info(f"  Min Accuracy: {min_acc:.4f}")
                logger.info(f"  Max Accuracy: {max_acc:.4f}")
            
            logger.info(f"\n{'='*80}")
            logger.info("✅ TRAINING PIPELINE COMPLETE!")
            logger.info(f"{'='*80}\n")
            
            return results
        
        except Exception as e:
            logger.critical(f"❌ TRAINING PIPELINE FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        pipeline = TrainingPipeline(
            db_url=os.getenv('DATABASE_URL')
        )
        
        results = pipeline.run_full_pipeline()
        
        logger.info("✅ All models trained and tested!")
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise
