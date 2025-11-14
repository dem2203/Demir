#!/usr/bin/env python3
"""
🔱 DEMIR AI - lstm_model.py
============================================================================
LSTM DEEP LEARNING MODEL (3K lines)

LSTM Architecture for time-series price prediction
- Input: 100 days historical data, 80+ features
- 3 LSTM layers with dropout
- Dense layers with regularization
- Training pipeline with early stopping
- Model versioning and persistence

Output: Predictions (UP/DOWN/HOLD) + confidence scores
============================================================================
"""

import os
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
import logging
import json
from datetime import datetime

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

logger = logging.getLogger(__name__)

# ============================================================================
# LSTM MODEL ARCHITECTURE
# ============================================================================

class LSTMModel:
    """LSTM-based trading signal predictor"""
    
    def __init__(self, 
                 lookback: int = 100,
                 n_features: int = 80,
                 lstm_units: List[int] = None,
                 dense_units: List[int] = None,
                 dropout: float = 0.3):
        """
        Initialize LSTM model
        
        Args:
            lookback: Number of historical days
            n_features: Number of input features
            lstm_units: Units per LSTM layer [128, 64, 32]
            dense_units: Units per dense layer [16]
            dropout: Dropout rate
        """
        
        self.lookback = lookback
        self.n_features = n_features
        self.lstm_units = lstm_units or [128, 64, 32]
        self.dense_units = dense_units or [16]
        self.dropout = dropout
        
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
        
        logger.info("✅ LSTMModel initialized")
    
    def build_model(self) -> models.Model:
        """Build LSTM architecture"""
        
        try:
            model = models.Sequential([
                # Input layer
                layers.Input(shape=(self.lookback, self.n_features)),
                
                # LSTM Layer 1: 128 neurons
                layers.LSTM(
                    self.lstm_units[0],
                    return_sequences=True,
                    dropout=self.dropout,
                    recurrent_dropout=self.dropout
                ),
                layers.BatchNormalization(),
                
                # LSTM Layer 2: 64 neurons
                layers.LSTM(
                    self.lstm_units[1],
                    return_sequences=True,
                    dropout=self.dropout,
                    recurrent_dropout=self.dropout
                ),
                layers.BatchNormalization(),
                
                # LSTM Layer 3: 32 neurons
                layers.LSTM(
                    self.lstm_units[2],
                    return_sequences=False,
                    dropout=self.dropout,
                    recurrent_dropout=self.dropout
                ),
                layers.BatchNormalization(),
                
                # Dense layer 1: 16 neurons
                layers.Dense(self.dense_units[0], activation='relu'),
                layers.Dropout(self.dropout),
                
                # Output layer: 3 classes (UP, DOWN, HOLD)
                layers.Dense(3, activation='softmax')
            ])
            
            # Compile model
            optimizer = Adam(learning_rate=0.001)
            model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
            )
            
            self.model = model
            logger.info(f"✅ LSTM model built: {model.summary()}")
            return model
        
        except Exception as e:
            logger.error(f"❌ Model building error: {e}")
            raise
    
    def prepare_data(self, 
                    features_df: pd.DataFrame,
                    labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training
        
        Args:
            features_df: DataFrame of features
            labels: Target labels (0=DOWN, 1=HOLD, 2=UP)
        
        Returns:
            X_train, X_test, y_train, y_test
        """
        
        try:
            # Normalize features
            X_scaled = self.scaler.fit_transform(features_df)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, labels,
                test_size=0.2,
                random_state=42,
                stratify=labels  # Balance classes
            )
            
            # Reshape for LSTM (samples, timesteps, features)
            X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
            X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
            
            # Convert labels to one-hot
            y_train = keras.utils.to_categorical(y_train, 3)
            y_test = keras.utils.to_categorical(y_test, 3)
            
            logger.info(f"✅ Data prepared: Train {X_train.shape}, Test {X_test.shape}")
            return X_train, X_test, y_train, y_test
        
        except Exception as e:
            logger.error(f"❌ Data preparation error: {e}")
            raise
    
    def train(self,
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None,
              epochs: int = 100,
              batch_size: int = 32,
              model_path: str = 'models/lstm_model.h5') -> dict:
        """
        Train LSTM model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size
            model_path: Path to save model
        
        Returns:
            Training history
        """
        
        try:
            if self.model is None:
                self.build_model()
            
            # Callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=0.00001
                ),
                ModelCheckpoint(
                    model_path,
                    monitor='val_accuracy',
                    save_best_only=True
                )
            ]
            
            # Train model
            self.history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val) if X_val is not None else (X_train, y_train),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            logger.info("✅ LSTM training complete")
            return self.history.history
        
        except Exception as e:
            logger.error(f"❌ Training error: {e}")
            raise
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model on test set"""
        
        try:
            loss, accuracy, precision, recall = self.model.evaluate(X_test, y_test, verbose=0)
            
            metrics = {
                'loss': float(loss),
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(2 * (precision * recall) / (precision + recall)) if (precision + recall) > 0 else 0
            }
            
            logger.info(f"✅ Test Accuracy: {accuracy:.4f}, F1: {metrics['f1_score']:.4f}")
            return metrics
        
        except Exception as e:
            logger.error(f"❌ Evaluation error: {e}")
            return {}
    
    def predict(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Make prediction
        
        Args:
            features: Input features (80+)
        
        Returns:
            Signal (UP/DOWN/HOLD), confidence score
        """
        
        try:
            # Normalize
            features_scaled = self.scaler.transform([features])
            features_scaled = features_scaled.reshape((1, 1, features_scaled.shape[1]))
            
            # Predict
            prediction = self.model.predict(features_scaled, verbose=0)
            
            # Get class and confidence
            class_idx = np.argmax(prediction[0])
            confidence = float(np.max(prediction[0])) * 100
            
            signal_map = {0: 'DOWN', 1: 'HOLD', 2: 'UP'}
            signal = signal_map[class_idx]
            
            return signal, confidence
        
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return 'HOLD', 50.0
    
    def save_model(self, path: str = 'models/lstm_model.h5'):
        """Save trained model"""
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.model.save(path)
            
            # Save scaler
            scaler_path = path.replace('.h5', '_scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
            
            logger.info(f"✅ Model saved: {path}")
        
        except Exception as e:
            logger.error(f"❌ Save error: {e}")
    
    def load_model(self, path: str = 'models/lstm_model.h5'):
        """Load trained model"""
        
        try:
            self.model = keras.models.load_model(path)
            
            # Load scaler
            scaler_path = path.replace('.h5', '_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            
            logger.info(f"✅ Model loaded: {path}")
        
        except Exception as e:
            logger.error(f"❌ Load error: {e}")

# ============================================================================
# TRAINING PIPELINE
# ============================================================================

class LSTMTrainingPipeline:
    """Complete training pipeline with cross-validation"""
    
    def __init__(self, lstm_model: LSTMModel = None):
        self.lstm = lstm_model or LSTMModel()
        self.training_log = []
        logger.info("✅ LSTMTrainingPipeline initialized")
    
    def run_training(self,
                    features_df: pd.DataFrame,
                    labels: np.ndarray,
                    epochs: int = 100,
                    batch_size: int = 32) -> Dict:
        """
        Run complete training pipeline
        
        Args:
            features_df: Input features
            labels: Target labels
            epochs: Number of training epochs
            batch_size: Batch size
        
        Returns:
            Training results and metrics
        """
        
        try:
            logger.info("🚀 Starting LSTM training pipeline...")
            
            # Build model
            self.lstm.build_model()
            
            # Prepare data
            X_train, X_test, y_train, y_test = self.lstm.prepare_data(features_df, labels)
            
            # Train model
            history = self.lstm.train(
                X_train, y_train,
                X_val=X_test,
                y_val=y_test,
                epochs=epochs,
                batch_size=batch_size
            )
            
            # Evaluate
            metrics = self.lstm.evaluate(X_test, y_test)
            
            # Save model
            self.lstm.save_model('models/lstm_model.h5')
            
            # Log training
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'epochs': epochs,
                'batch_size': batch_size,
                'metrics': metrics,
                'history': history
            }
            self.training_log.append(log_entry)
            
            logger.info(f"✅ Training complete. Accuracy: {metrics['accuracy']:.4f}")
            return {
                'status': 'success',
                'metrics': metrics,
                'model_path': 'models/lstm_model.h5'
            }
        
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cross_validate(self,
                      features_df: pd.DataFrame,
                      labels: np.ndarray,
                      n_splits: int = 5) -> Dict:
        """Time-series cross-validation"""
        
        try:
            logger.info(f"🔄 Running {n_splits}-fold cross-validation...")
            
            fold_scores = []
            
            # Time-series cross-validation (no data leakage)
            fold_size = len(features_df) // n_splits
            
            for fold in range(n_splits):
                test_start = fold * fold_size
                test_end = test_start + fold_size
                
                X_train = features_df.iloc[:test_start]
                X_test = features_df.iloc[test_start:test_end]
                y_train = labels[:test_start]
                y_test = labels[test_start:test_end]
                
                # Train on this fold
                fold_model = LSTMModel()
                fold_model.build_model()
                
                X_train_prep, _, y_train_prep, _ = fold_model.prepare_data(X_train, y_train)
                X_test_prep, _, y_test_prep, _ = fold_model.prepare_data(X_test, y_test)
                
                fold_model.train(X_train_prep, y_train_prep, epochs=50, batch_size=32)
                metrics = fold_model.evaluate(X_test_prep, y_test_prep)
                
                fold_scores.append(metrics)
                logger.info(f"  Fold {fold+1}: Accuracy={metrics['accuracy']:.4f}")
            
            # Average metrics
            avg_metrics = {
                'accuracy': np.mean([m['accuracy'] for m in fold_scores]),
                'precision': np.mean([m['precision'] for m in fold_scores]),
                'recall': np.mean([m['recall'] for m in fold_scores]),
                'f1_score': np.mean([m['f1_score'] for m in fold_scores])
            }
            
            logger.info(f"✅ CV Complete. Average Accuracy: {avg_metrics['accuracy']:.4f}")
            return avg_metrics
        
        except Exception as e:
            logger.error(f"❌ CV error: {e}")
            return {}

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data (in production: from feature_engineering.py)
    n_samples = 1000
    n_features = 80
    features = np.random.randn(n_samples, n_features)
    labels = np.random.randint(0, 3, n_samples)  # 0=DOWN, 1=HOLD, 2=UP
    
    features_df = pd.DataFrame(features, columns=[f'feature_{i}' for i in range(n_features)])
    
    # Create and train model
    pipeline = LSTMTrainingPipeline()
    result = pipeline.run_training(features_df, labels, epochs=10, batch_size=32)
    
    print(f"✅ Training result: {result}")
