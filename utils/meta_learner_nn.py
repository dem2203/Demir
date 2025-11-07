"""
🧠 PHASE 8.2 - NEURAL META-LEARNER
====================================

Path: utils/meta_learner_nn.py
Date: 7 Kasım 2025, 15:42 CET

Neural network-based meta-learner that learns optimal layer weights.
3-layer architecture: 15 inputs → 32 hidden → 3 outputs (signal class)
"""

import numpy as np
from typing import Dict, Tuple, List

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class SimpleLearner:
    """Fallback learner when TensorFlow not available"""
    
    @staticmethod
    def predict(layer_scores: Dict[str, float]) -> Dict:
        """
        Simple learned weighting without neural network
        
        Args:
            layer_scores: Dictionary of layer names → scores
        
        Returns:
            Prediction with signal and confidence
        """
        scores = np.array([s for s in layer_scores.values() if s is not None])
        
        if len(scores) == 0:
            return {'signal': 'NEUTRAL', 'confidence': 0.0}
        
        avg_score = np.mean(scores)
        std_score = np.std(scores)
        agreement = max(0, 1 - std_score/50)
        
        # Signal based on average score
        if avg_score >= 65:
            signal = 'LONG'
        elif avg_score <= 35:
            signal = 'SHORT'
        else:
            signal = 'NEUTRAL'
        
        confidence = min(agreement + 0.2, 1.0)
        
        return {
            'signal': signal,
            'confidence': round(confidence, 3),
            'avg_score': round(avg_score, 2)
        }


class NeuralMetaLearner:
    """Advanced neural network meta-learner"""
    
    def __init__(self, input_size=15, hidden_size=32):
        """
        Initialize neural meta-learner
        
        Args:
            input_size: Number of layer inputs (15 layers)
            hidden_size: Size of hidden layer (32)
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.model = None
        self.weights_history = []
        self.training_history = []
        
        if TF_AVAILABLE:
            self._build_model()
    
    def _build_model(self):
        """Build neural network architecture"""
        if not TF_AVAILABLE:
            return
        
        self.model = keras.Sequential([
            # Input layer: 15 layer scores
            layers.Input(shape=(self.input_size,)),
            
            # Hidden layer 1: 32 units with ReLU
            layers.Dense(self.hidden_size, activation='relu', name='hidden_1'),
            layers.Dropout(0.2),
            
            # Hidden layer 2: 16 units with ReLU
            layers.Dense(16, activation='relu', name='hidden_2'),
            layers.Dropout(0.1),
            
            # Output layer: 3 units (LONG, NEUTRAL, SHORT)
            layers.Dense(3, activation='softmax', name='output')
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Neural Meta-Learner model built (15→32→16→3)")
    
    def predict(self, layer_scores: Dict[str, float]) -> Dict:
        """
        Predict optimal signal using neural network
        
        Args:
            layer_scores: Dictionary of layer names → scores
        
        Returns:
            Prediction with signal, confidence, and layer importance
        """
        if self.model is None:
            return SimpleLearner.predict(layer_scores)
        
        try:
            # Prepare input: convert scores to normalized array
            scores = np.array([
                layer_scores.get(name, 50.0) 
                for name in sorted(layer_scores.keys())
            ])
            
            # Normalize scores to 0-1 range
            scores_normalized = scores / 100.0
            
            # Get neural network prediction
            prediction = self.model.predict(scores_normalized.reshape(1, -1), verbose=0)
            
            # Extract probabilities
            prob_long = float(prediction[0][0])
            prob_neutral = float(prediction[0][1])
            prob_short = float(prediction[0][2])
            
            # Determine signal (highest probability)
            probs = {'LONG': prob_long, 'NEUTRAL': prob_neutral, 'SHORT': prob_short}
            signal = max(probs, key=probs.get)
            confidence = max(probs.values())
            
            return {
                'signal': signal,
                'confidence': round(confidence, 3),
                'probabilities': {
                    'LONG': round(prob_long, 3),
                    'NEUTRAL': round(prob_neutral, 3),
                    'SHORT': round(prob_short, 3)
                }
            }
        
        except Exception as e:
            print(f"Neural prediction error: {e}")
            return SimpleLearner.predict(layer_scores)
    
    def get_layer_importance(self) -> Dict[str, float]:
        """
        Extract learned layer importance weights from first layer
        
        Returns:
            Dictionary of layer names → importance weights
        """
        if self.model is None or not TF_AVAILABLE:
            return {f'layer_{i}': 1/15 for i in range(15)}
        
        try:
            # Get weights from first hidden layer
            first_layer = self.model.get_layer('hidden_1')
            weights = first_layer.get_weights()[0]  # Shape: (15, 32)
            
            # Calculate importance as sum of absolute weights
            importance = np.sum(np.abs(weights), axis=1)
            importance = importance / np.sum(importance)  # Normalize
            
            layer_names = [
                'strategy', 'kelly', 'macro', 'gold', 'cross_asset',
                'vix', 'monte_carlo', 'news', 'trad_markets', 'black_scholes',
                'kalman', 'fractal', 'fourier', 'copula', 'rates'
            ]
            
            return {
                name: round(float(imp), 4)
                for name, imp in zip(layer_names, importance)
            }
        except Exception as e:
            print(f"Error extracting importance: {e}")
            return {f'layer_{i}': 1/15 for i in range(15)}
    
    def train_on_history(self, history: List[Dict], epochs=10):
        """
        Train neural network on historical trade data
        
        Args:
            history: List of past analyses with outcomes
            epochs: Number of training epochs
        """
        if self.model is None or len(history) < 10:
            print("⚠️ Insufficient data for neural network training")
            return
        
        try:
            X_train = []
            y_train = []
            
            for record in history:
                scores = np.array([
                    record.get(name, 50.0)
                    for name in sorted(record.keys())
                    if name != 'result'
                ]) / 100.0
                
                result = record.get('result', 'NEUTRAL')
                if result == 'LONG':
                    label = [1, 0, 0]
                elif result == 'SHORT':
                    label = [0, 0, 1]
                else:
                    label = [0, 1, 0]
                
                X_train.append(scores)
                y_train.append(label)
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Train with quiet output
            self.model.fit(X_train, y_train, epochs=epochs, verbose=0)
            print(f"✅ Neural network trained on {len(history)} records")
            
        except Exception as e:
            print(f"Training error: {e}")


def get_meta_learner_prediction(layer_scores: Dict[str, float]) -> Dict:
    """
    Get prediction from meta-learner (wrapper function)
    
    Args:
        layer_scores: Dictionary of layer scores
    
    Returns:
        Prediction with signal and confidence
    """
    if TF_AVAILABLE:
        learner = NeuralMetaLearner()
        return learner.predict(layer_scores)
    else:
        return SimpleLearner.predict(layer_scores)


# Example usage
if __name__ == "__main__":
    # Test with sample layer scores
    test_scores = {
        'strategy': 62,
        'kelly': 58,
        'macro': 55,
        'gold': 60,
        'cross_asset': 65,
        'vix': 52,
        'monte_carlo': 68,
        'news': 61,
        'trad_markets': 59,
        'black_scholes': 64,
        'kalman': 56,
        'fractal': 70,
        'fourier': 63,
        'copula': 58,
        'rates': 54
    }
    
    print("Testing Meta-Learner...")
    result = get_meta_learner_prediction(test_scores)
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']}")
