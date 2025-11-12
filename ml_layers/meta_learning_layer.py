import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class MetaLearningLayer:
    """Meta-learner for adaptive layer weighting"""
    
    def __init__(self, num_layers: int = 15, hidden_dim: int = 32):
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        
        self.w1 = np.random.randn(num_layers, hidden_dim) * 0.01
        self.b1 = np.zeros((1, hidden_dim))
        
        self.w2 = np.random.randn(hidden_dim, hidden_dim // 2) * 0.01
        self.b2 = np.zeros((1, hidden_dim // 2))
        
        self.w3 = np.random.randn(hidden_dim // 2, num_layers) * 0.01
        self.b3 = np.zeros((1, num_layers))
        
        self.learning_rate = 0.001
        self.training_steps = 0
        logger.info("MetaLearningLayer initialized (NumPy-based)")
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def softmax(self, x):
        if x.ndim == 1:
            x = x.reshape(1, -1)
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / (np.sum(e_x, axis=1, keepdims=True) + 1e-8)
    
    def forward(self, layer_scores: np.ndarray) -> np.ndarray:
        if layer_scores.ndim == 1:
            layer_scores = layer_scores.reshape(1, -1)
        
        h1 = np.dot(layer_scores, self.w1) + self.b1
        h1_activated = self.relu(h1)
        
        h2 = np.dot(h1_activated, self.w2) + self.b2
        h2_activated = self.relu(h2)
        
        output = np.dot(h2_activated, self.w3) + self.b3
        output = self.softmax(output)
        
        return output.flatten()
    
    def predict_layer_weights(self, layer_scores: Dict[str, float]) -> Dict[str, float]:
        try:
            layer_names = sorted(layer_scores.keys())
            scores = np.array([layer_scores.get(name, 50.0) for name in layer_names])
            
            scores_normalized = scores / 100.0
            
            if len(scores_normalized) < self.num_layers:
                scores_normalized = np.pad(scores_normalized, (0, self.num_layers - len(scores_normalized)), mode='constant', constant_values=0.5)
            elif len(scores_normalized) > self.num_layers:
                scores_normalized = scores_normalized[:self.num_layers]
            
            weights = self.forward(scores_normalized)
            
            result = {}
            for i, name in enumerate(layer_names[:self.num_layers]):
                result[name] = float(weights[i])
            
            return result
        except Exception as e:
            logger.error(f"Error in predict_layer_weights: {e}")
            return {name: 1.0 / len(layer_scores) for name in layer_scores.keys()}
    
    def analyze(self, layer_scores: Dict[str, float]) -> Dict:
        try:
            weights = self.predict_layer_weights(layer_scores)
            
            total_score = 0
            total_weight = 0
            for layer_name, score in layer_scores.items():
                weight = weights.get(layer_name, 1.0)
                total_score += score * weight
                total_weight += weight
            
            weighted_avg = total_score / (total_weight + 1e-8)
            
            if weighted_avg > 65:
                signal = "LONG"
                confidence = (weighted_avg - 65) / 35
            elif weighted_avg < 35:
                signal = "SHORT"
                confidence = (35 - weighted_avg) / 35
            else:
                signal = "NEUTRAL"
                confidence = 1 - abs(weighted_avg - 50) / 50
            
            return {
                "signal": signal,
                "confidence": min(float(confidence), 1.0),
                "weighted_score": float(weighted_avg),
                "layer_weights": {k: float(v) for k, v in weights.items()},
                "dominant_layer": max(weights, key=weights.get) if weights else None
            }
        except Exception as e:
            logger.error(f"Error in analyze: {e}")
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "weighted_score": 50.0,
                "error": str(e)
            }

# Global instance
meta_layer = MetaLearningLayer()
