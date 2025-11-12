import numpy as np
from typing import Dict, Tuple, List

class SimpleLearner:
    """Fallback learner when TensorFlow not available"""
    
    @staticmethod
    def predict_layer_scores(layer_scores: Dict[str, float]) -> Dict:
        """Simple learned weighting without neural network"""
        scores = [s for s in layer_scores.values() if s is not None]
        
        if len(scores) == 0:
            return {"signal": "NEUTRAL", "confidence": 0.0}
        
        avg_score = np.mean(scores)
        std_score = np.std(scores)
        agreement = max(0, 1 - (std_score / 50))
        
        if avg_score > 65:
            signal = "LONG"
        elif avg_score < 35:
            signal = "SHORT"
        else:
            signal = "NEUTRAL"
        
        confidence = min(agreement * 0.8, 1.0)
        
        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "avg_score": round(avg_score, 2)
        }

class NeuralMetaLearner:
    """NumPy-based meta-learner (no TensorFlow required)"""
    
    def __init__(self, input_size: int = 15, hidden_size: int = 32):
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        self.w1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        
        self.w2 = np.random.randn(hidden_size, 16) * 0.01
        self.b2 = np.zeros((1, 16))
        
        self.w3 = np.random.randn(16, 3) * 0.01
        self.b3 = np.zeros((1, 3))
        
        self.weights_history = []
        self.training_history = []
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / np.sum(e_x, axis=1, keepdims=True)
    
    def forward(self, x):
        h1 = np.dot(x, self.w1) + self.b1
        h1 = self.relu(h1)
        
        h2 = np.dot(h1, self.w2) + self.b2
        h2 = self.relu(h2)
        
        output = np.dot(h2, self.w3) + self.b3
        output = self.softmax(output)
        
        return output
    
    def predict(self, layer_scores: Dict[str, float]) -> Dict:
        """Predict optimal signal using neural network"""
        try:
            layer_names = sorted(layer_scores.keys())
            scores = np.array([layer_scores.get(name, 50.0) for name in layer_names])
            scores_normalized = scores / 100.0
            
            if len(scores_normalized) < self.input_size:
                scores_normalized = np.pad(scores_normalized, (0, self.input_size - len(scores_normalized)), mode='constant', constant_values=0.5)
            
            scores_normalized = scores_normalized.reshape(1, -1)
            
            prediction = self.forward(scores_normalized)
            
            prob_long = float(prediction[0, 0])
            prob_neutral = float(prediction[0, 1])
            prob_short = float(prediction[0, 2])
            
            signal_map = {0: "LONG", 1: "NEUTRAL", 2: "SHORT"}
            signal = signal_map[np.argmax(prediction[0])]
            confidence = float(np.max(prediction[0]))
            
            return {
                "signal": signal,
                "confidence": round(confidence, 3),
                "probabilities": {
                    "LONG": round(prob_long, 3),
                    "NEUTRAL": round(prob_neutral, 3),
                    "SHORT": round(prob_short, 3)
                }
            }
        except Exception as e:
            print(f"Neural prediction error: {e}")
            return SimpleLearner.predict_layer_scores(layer_scores)

def get_meta_learner_prediction(layer_scores: Dict[str, float]) -> Dict:
    """Get prediction from meta-learner"""
    learner = NeuralMetaLearner()
    return learner.predict(layer_scores)

learner = NeuralMetaLearner()
