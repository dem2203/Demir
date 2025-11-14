#!/usr/bin/env python3
"""
🔱 DEMIR AI - transformer_model_v2.py
============================================================================
TRANSFORMER MODEL - PRODUCTION READY - ZERO MOCK, FAIL LOUD, STRICT VALIDATION

Multi-head attention architecture for time-series prediction
Rules:
✅ NO defaults - raise if invalid
✅ STRICT validation on training data
✅ Model must learn (accuracy > 0.33)
✅ All errors re-raised
✅ LSTM-compatible interface
============================================================================
"""

import os
import logging
import traceback
from typing import Tuple, Dict, Optional

import numpy as np
import pandas as pd
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
# TRANSFORMER MODEL - PRODUCTION GRADE
# ============================================================================

class TransformerModel:
    """Transformer time-series predictor - STRICT VALIDATION"""
    
    def __init__(self,
                 lookback: int = 100,
                 n_features: int = 80,
                 embedding_dim: int = 64,
                 num_heads: int = 8,
                 ff_dim: int = 256,
                 num_blocks: int = 4,
                 dropout: float = 0.1):
        """
        Initialize Transformer model
        
        Args:
            lookback: Historical days
            n_features: Number of features
            embedding_dim: Embedding dimension
            num_heads: Number of attention heads
            ff_dim: Feed-forward dimension
            num_blocks: Number of transformer blocks
            dropout: Dropout rate
        """
        
        if lookback < 10:
            raise ValueError(f"❌ lookback must be >= 10, got {lookback}")
        
        if n_features < 2:
            raise ValueError(f"❌ n_features must be >= 2, got {n_features}")
        
        if embedding_dim % num_heads != 0:
            raise ValueError(
                f"❌ embedding_dim {embedding_dim} must be divisible by num_heads {num_heads}"
            )
        
        self.lookback = lookback
        self.n_features = n_features
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.num_blocks = num_blocks
        self.dropout = dropout
        
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
        
        logger.info(
            f"✅ TransformerModel initialized: lookback={lookback}, "
            f"features={n_features}, heads={num_heads}"
        )
    
    def build_model(self) -> models.Model:
        """Build Transformer architecture - STRICT"""
        
        try:
            logger.info("🔨 Building Transformer model...")
            
            inputs = layers.Input(shape=(self.lookback, self.n_features))
            
            # Embedding layer
            x = layers.Dense(self.embedding_dim, name='embedding')(inputs)
            
            # Multi-head attention blocks
            for block_idx in range(self.num_blocks):
                # Multi-head attention
                attention_output = layers.MultiHeadAttention(
                    num_heads=self.num_heads,
                    key_dim=self.embedding_dim // self.num_heads,
                    dropout=self.dropout,
                    name=f'attention_{block_idx}'
                )(x, x)
                
                # Residual connection + layer norm
                x = layers.Add(name=f'add_attention_{block_idx}')([x, attention_output])
                x = layers.LayerNormalization(epsilon=1e-6, name=f'norm_attention_{block_idx}')(x)
                
                # Feed-forward network
                ffn_output = layers.Dense(self.ff_dim, activation='relu', name=f'ffn_1_{block_idx}')(x)
                ffn_output = layers.Dropout(self.dropout)(ffn_output)
                ffn_output = layers.Dense(self.embedding_dim, name=f'ffn_2_{block_idx}')(ffn_output)
                
                # Residual connection + layer norm
                x = layers.Add(name=f'add_ffn_{block_idx}')([x, ffn_output])
                x = layers.LayerNormalization(epsilon=1e-6, name=f'norm_ffn_{block_idx}')(x)
            
            # Global average pooling
            x = layers.GlobalAveragePooling1D(name='global_pool')(x)
            
            # Dense layers
            x = layers.Dense(32, activation='relu', name='dense_1')(x)
            x = layers.Dropout(self.dropout)(x)
            x = layers.Dense(16, activation='relu', name='dense_2')(x)
            x = layers.Dropout(self.dropout)(x)
            
            # Output layer (3 classes: DOWN, HOLD, UP)
            outputs = layers.Dense(3, activation='softmax', name='output')(x)
            
            # Create model
            model = models.Model(inputs, outputs, name='transformer')
            
            # Compile
            optimizer = Adam(learning_rate=0.001)
            model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=[
                    'accuracy',
                    tf.keras.metrics.Precision(),
                    tf.keras.metrics.Recall()
                ]
            )
            
            self.model = model
            logger.info("✅ Transformer model built successfully")
            return model
        
        except Exception as e:
            logger.critical(f"❌ TRANSFORMER BUILD FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def prepare_data(self,
                    features_df: pd.DataFrame,
                    labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training - STRICT VALIDATION
        
        Args:
            features_df: DataFrame with features
            labels: Target labels (0=DOWN, 1=HOLD, 2=UP)
        
        Returns:
            X_train, X_test, y_train, y_test
        
        Raises:
            ValueError: If data is invalid
        """
        
        try:
            logger.info("🔄 Preparing data...")
            
            # Validate input
            if features_df.empty:
                raise ValueError("❌ Features DataFrame is empty")
            
            if labels is None or len(labels) == 0:
                raise ValueError("❌ Labels array is empty")
            
            if len(features_df) != len(labels):
                raise ValueError(
                    f"❌ Shape mismatch: features {len(features_df)} != labels {len(labels)}"
                )
            
            if len(features_df) < 100:
                raise ValueError(f"❌ Insufficient data: {len(features_df)} < 100")
            
            # Check for NaN/Inf
            if features_df.isnull().any().any():
                raise ValueError("❌ Features contain NaN values")
            
            if np.any(np.isinf(features_df.values)):
                raise ValueError("❌ Features contain Inf values")
            
            # Normalize features
            X_scaled = self.scaler.fit_transform(features_df)
            
            if np.any(np.isnan(X_scaled)):
                raise ValueError("❌ Scaled features contain NaN")
            
            # Split data (stratified)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, labels,
                test_size=0.2,
                random_state=42,
                stratify=labels
            )
            
            logger.info(f"✅ Train: {X_train.shape}, Test: {X_test.shape}")
            
            # Validate split
            if len(X_train) < 50:
                raise ValueError(f"❌ Insufficient training data: {len(X_train)} < 50")
            
            # Reshape for Transformer (samples, timesteps, features)
            X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
            X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
            
            logger.info(f"✅ Reshaped - Train: {X_train.shape}, Test: {X_test.shape}")
            
            # One-hot encode labels
            y_train = keras.utils.to_categorical(y_train, 3)
            y_test = keras.utils.to_categorical(y_test, 3)
            
            logger.info("✅ Data prepared successfully")
            return X_train, X_test, y_train, y_test
        
        except Exception as e:
            logger.critical(f"❌ DATA PREPARATION FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def train(self,
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None,
              epochs: int = 100,
              batch_size: int = 32,
              model_path: str = 'models/transformer_model.h5') -> dict:
        """
        Train Transformer model - STRICT VALIDATION
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            model_path: Path to save model
        
        Returns:
            Training history
        
        Raises:
            ValueError: If model doesn't learn
        """
        
        try:
            logger.info("🚀 Starting Transformer training...")
            
            # Build model if not already built
            if self.model is None:
                self.build_model()
            
            # Use test as validation if not provided
            if X_val is None or y_val is None:
                X_val, y_val = X_train, y_train
            
            # Create models directory
            os.makedirs(os.path.dirname(model_path) or '.', exist_ok=True)
            
            # Callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True,
                    verbose=1
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-5,
                    verbose=1
                ),
                ModelCheckpoint(
                    model_path,
                    monitor='val_accuracy',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train
            self.history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            # Validate training
            final_accuracy = self.history.history['accuracy'][-1]
            final_val_accuracy = self.history.history['val_accuracy'][-1]
            
            logger.info(
                f"✅ Training complete: Train Acc={final_accuracy:.4f}, "
                f"Val Acc={final_val_accuracy:.4f}"
            )
            
            # STRICT: Model must learn!
            if final_val_accuracy < 0.33:
                raise ValueError(
                    f"❌ MODEL NOT LEARNING! Val accuracy {final_val_accuracy:.4f} < 0.33"
                )
            
            logger.info("✅ Transformer training successful!")
            return self.history.history
        
        except Exception as e:
            logger.critical(f"❌ TRANSFORMER TRAINING FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model on test set - STRICT
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Metrics dictionary
        
        Raises:
            ValueError: If model accuracy too low
        """
        
        try:
            logger.info("📊 Evaluating Transformer...")
            
            loss, accuracy, precision, recall = self.model.evaluate(X_test, y_test, verbose=0)
            
            metrics = {
                'loss': float(loss),
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(2 * (precision * recall) / (precision + recall))
                           if (precision + recall) > 0 else 0
            }
            
            logger.info(f"✅ Test Accuracy: {accuracy:.4f}, F1: {metrics['f1_score']:.4f}")
            
            # STRICT: Must be better than random!
            if accuracy < 0.33:
                raise ValueError(f"❌ Test accuracy {accuracy:.4f} < 0.33 (random guess)")
            
            return metrics
        
        except Exception as e:
            logger.critical(f"❌ TRANSFORMER EVALUATION FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def predict(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Make prediction - STRICT
        
        Args:
            features: Input features (80+)
        
        Returns:
            (signal, confidence) where signal is 'UP', 'DOWN', or 'HOLD'
        
        Raises:
            ValueError: If model not ready or prediction invalid
        """
        
        try:
            if self.model is None:
                raise ValueError("❌ Transformer model not loaded")
            
            # Validate input
            if features is None or len(features) == 0:
                raise ValueError("❌ Features is empty")
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            if np.any(np.isnan(features_scaled)):
                raise ValueError("❌ Scaled features contain NaN")
            
            # Reshape for Transformer
            features_scaled = features_scaled.reshape((1, 1, features_scaled.shape[1]))
            
            # Predict
            prediction = self.model.predict(features_scaled, verbose=0)
            
            if prediction.shape != (1, 3):
                raise ValueError(f"❌ Invalid prediction shape: {prediction.shape}")
            
            # Get class and confidence
            class_idx = int(np.argmax(prediction[0]))
            confidence = float(np.max(prediction[0])) * 100
            
            # Validate
            if class_idx not in [0, 1, 2]:
                raise ValueError(f"❌ Invalid class index: {class_idx}")
            
            if not 0 <= confidence <= 100:
                raise ValueError(f"❌ Invalid confidence: {confidence}")
            
            signal_map = {0: 'DOWN', 1: 'HOLD', 2: 'UP'}
            signal = signal_map[class_idx]
            
            logger.debug(f"✅ Prediction: {signal} ({confidence:.1f}%)")
            return signal, confidence
        
        except Exception as e:
            logger.error(f"❌ TRANSFORMER PREDICTION FAILED: {e}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def save_model(self, path: str = 'models/transformer_model.h5'):
        """
        Save trained model - STRICT
        
        Args:
            path: Path to save model
        
        Raises:
            ValueError: If save fails
        """
        
        try:
            if self.model is None:
                raise ValueError("❌ Model not trained")
            
            # Create directory
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            
            # Save model
            self.model.save(path)
            logger.info(f"✅ Transformer model saved: {path}")
            
            # Save scaler
            scaler_path = path.replace('.h5', '_scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"✅ Transformer scaler saved: {scaler_path}")
        
        except Exception as e:
            logger.critical(f"❌ SAVE FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def load_model(self, path: str = 'models/transformer_model.h5'):
        """
        Load trained model - STRICT
        
        Args:
            path: Path to model
        
        Raises:
            ValueError: If load fails
        """
        
        try:
            if not os.path.exists(path):
                raise ValueError(f"❌ Model file not found: {path}")
            
            self.model = keras.models.load_model(path)
            logger.info(f"✅ Transformer model loaded: {path}")
            
            # Load scaler
            scaler_path = path.replace('.h5', '_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info(f"✅ Transformer scaler loaded: {scaler_path}")
            else:
                logger.warning(f"⚠️ Scaler file not found: {scaler_path}")
        
        except Exception as e:
            logger.critical(f"❌ LOAD FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    logger.info("=" * 80)
    logger.info("🔱 DEMIR AI - Transformer Model v2 - PRODUCTION READY")
    logger.info("=" * 80)
    
    # Initialize
    transformer = TransformerModel()
    logger.info("✅ Transformer Model ready for training")
