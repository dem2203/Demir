"""
PHASE 9.2: TRANSFORMER ATTENTION LAYER
File 5 of 10 (ayrı dosyalar)
Folder: ml_layers/transformer_attention_layer.py

Transformer-based prediction with attention
- Multi-head attention
- Positional encoding
- Context-aware predictions
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    logging.warning("TensorFlow not installed. Transformer layer will be limited.")

logger = logging.getLogger(__name__)


class TransformerAttentionLayer:
    """
    Transformer-based prediction with attention mechanism
    
    Features:
    - Multi-head self-attention
    - Positional encoding
    - Parallel processing
    - Context-aware predictions
    """
    
    def __init__(self, num_heads: int = 4, hidden_dim: int = 64,
                 num_layers: int = 2):
        """
        Initialize Transformer
        
        Args:
            num_heads: Number of attention heads
            hidden_dim: Hidden dimension
            num_layers: Number of transformer blocks
        """
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.model: Optional[Any] = None
        self.is_trained = False
        
        if not KERAS_AVAILABLE:
            logger.warning("Transformer requires TensorFlow/Keras")
    
    def positional_encoding(self, seq_len: int, d_model: int) -> np.ndarray:
        """
        Generate positional encoding
        
        Args:
            seq_len: Sequence length
            d_model: Model dimension
            
        Returns:
            Positional encoding matrix
        """
        pos = np.arange(seq_len)[:, np.newaxis]
        i = np.arange(d_model)[np.newaxis, :]
        angle_rates = 1 / (10000 ** (2 * (i // 2) / d_model))
        
        pe = pos * angle_rates
        pe[:, 0::2] = np.sin(pe[:, 0::2])
        pe[:, 1::2] = np.cos(pe[:, 1::2])
        
        return pe[np.newaxis, ...]
    
    def build_model(self, seq_len: int, features: int) -> Optional[Any]:
        """
        Build Transformer model
        
        Args:
            seq_len: Sequence length
            features: Number of features
            
        Returns:
            Compiled model or None
        """
        if not KERAS_AVAILABLE:
            return None
        
        try:
            inputs = keras.Input(shape=(seq_len, features))
            
            x = inputs
            
            # Multi-head attention layers
            for _ in range(self.num_layers):
                # Self-attention
                attention_output = keras.layers.MultiHeadAttention(
                    num_heads=self.num_heads,
                    key_dim=self.hidden_dim,
                    dropout=0.1
                )(x, x)
                
                x = keras.layers.Add()([inputs, attention_output])
                x = keras.layers.LayerNormalization(epsilon=1e-6)(x)
                
                # Feed forward
                ff_output = keras.layers.Dense(self.hidden_dim * 2, 
                                               activation='relu')(x)
                ff_output = keras.layers.Dense(features)(ff_output)
                x = keras.layers.Add()([x, ff_output])
                x = keras.layers.LayerNormalization(epsilon=1e-6)(x)
            
            # Output
            x = keras.layers.GlobalAveragePooling1D()(x)
            x = keras.layers.Dense(32, activation='relu')(x)
            outputs = keras.layers.Dense(1)(x)
            
            model = keras.Model(inputs, outputs)
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            self.model = model
            return model
            
        except Exception as e:
            logger.error(f"Model building error: {e}")
            return None
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 50,
              batch_size: int = 32, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train Transformer model
        
        Args:
            X: Training features [samples, seq_len, features]
            y: Training targets
            epochs: Number of epochs
            batch_size: Batch size
            validation_split: Train/val split
            
        Returns:
            Training metrics
        """
        if not KERAS_AVAILABLE or self.model is None:
            return {"error": "Model not available"}
        
        try:
            self.build_model(X.shape[1], X.shape[2])
            
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,
                validation_split=validation_split
            )
            
            self.is_trained = True
            
            return {
                'success': True,
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1])
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {"error": str(e)}
    
    def predict(self, X: np.ndarray) -> Optional[np.ndarray]:
        """
        Make predictions
        
        Args:
            X: Input data [1, seq_len, features]
            
        Returns:
            Predictions or None
        """
        if not self.is_trained or self.model is None or not KERAS_AVAILABLE:
            return None
        
        try:
            predictions = self.model.predict(X, verbose=0)
            return predictions
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None


if __name__ == "__main__":
    print("✅ PHASE 9.2: Transformer Attention Ready")
