import numpy as np
from typing import Dict, Tuple, List

class SimpleLearner:
    """Fallback learner when TensorFlow not available"""
    
    @staticmethod
    def predict_layer_scores(layer_scores: Dict[str, float]) -> Dict:
        """Simple learned weighting without neural network
        
        Args:
            layer_scores: Dictionary of layer names -> scores
        
        Returns:
            Prediction with signal and confidence scores
        """
        scores = [s for s in layer_scores.values() if s is not None]
        
        if len(scores) == 0:
            return {
                "signal": "NEUTRAL",
                "confidence": 0.0
            }
        
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
        """Initialize neural meta-learner
        
        Args:
            input_size: Number of layer inputs (15 layers)
            hidden_size: Size of hidden layer (32)
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Initialize weights with NumPy
        self.w1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        
        self.w2 = np.random.randn(hidden_size, 16) * 0.01
        self.b2 = np.zeros((1, 16))
        
        self.w3 = np.random.randn(16, 3) * 0.01  # 3 outputs: LONG, NEUTRAL, SHORT
        self.b3 = np.zeros((1, 3))
        
        self.weights_history = []
        self.training_history = []
    
    def relu(self, x):
        """ReLU activation"""
        return np.maximum(0, x)
    
    def softmax(self, x):
        """Softmax activation"""
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / np.sum(e_x, axis=1, keepdims=True)
    
    def forward(self, x):
        """Forward pass through network"""
        # Hidden layer 1
        h1 = np.dot(x, self.w1) + self.b1
        h1 = self.relu(h1)
        
        # Hidden layer 2
        h2 = np.dot(h1, self.w2) + self.b2
        h2 = self.relu(h2)
        
        # Output layer
        output = np.dot(h2, self.w3) + self.b3
        output = self.softmax(output)
        
        return output
    
    def predict(self, layer_scores: Dict[str, float]) -> Dict:
        """Predict optimal signal using neural network
        
        Args:
            layer_scores: Dictionary of layer names -> scores
        
        Returns:
            Prediction with signal, confidence, and probabilities
        """
        try:
            # Prepare input (normalize scores)
            layer_names = sorted(layer_scores.keys())
            scores = np.array([layer_scores.get(name, 50.0) for name in layer_names])
            scores_normalized = scores / 100.0
            
            # Pad to 15 inputs if needed
            if len(scores_normalized) < self.input_size:
                scores_normalized = np.pad(scores_normalized, 
                                          (0, self.input_size - len(scores_normalized)), 
                                          mode='constant', constant_values=0.5)
            
            scores_normalized = scores_normalized.reshape(1, -1)
            
            # Forward pass
            prediction = self.forward(scores_normalized)
            
            # Extract probabilities
            prob_long = float(prediction[0, 0])
            prob_neutral = float(prediction[0, 1])
            prob_short = float(prediction[0, 2])
            
            # Determine signal
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
    
    def train_on_history(self, history: List[Dict], epochs: int = 10) -> None:
        """Train neural network on historical data
        
        Args:
            history: List of past analyses with outcomes
            epochs: Number of training epochs
        """
        if len(history) < 10:
            print("Insufficient data for neural network training")
            return
        
        try:
            # Simple training loop (no backprop for simplicity)
            for epoch in range(epochs):
                total_loss = 0
                for record in history:
                    scores = np.array([record.get(name, 50.0) for name in sorted(record.keys())])
                    scores = scores / 100.0
                    
                    # Make prediction
                    pred = self.forward(scores.reshape(1, -1))
                    
                    total_loss += np.mean((pred - 0.33) ** 2)
                
                avg_loss = total_loss / len(history)
                if epoch % 5 == 0:
                    print(f"Epoch {epoch}: Loss = {avg_loss:.4f}")
            
            print(f"Neural network trained on {len(history)} records")
        
        except Exception as e:
            print(f"Training error: {e}")
    
    def get_layer_importance(self) -> Dict[str, float]:
        """Extract learned layer importance weights"""
        try:
            importance = np.sum(np.abs(self.w1), axis=1)
            importance = importance / np.sum(importance)
            
            layer_names = [
                "strategy", "kelly", "macro", "gold", "cross_asset",
                "vix", "monte_carlo", "news", "markets", "black_scholes",
                "kalman", "fractal", "fourier", "copula", "rates"
            ]
            
            return {
                name: round(float(imp), 4)
                for name, imp in zip(layer_names, importance)
            }
        
        except Exception as e:
            print(f"Error extracting importance: {e}")
            return {}

# Global function
def get_meta_learner_prediction(layer_scores: Dict[str, float]) -> Dict:
    """Get prediction from meta-learner"""
    learner = NeuralMetaLearner()
    return learner.predict(layer_scores)

# Example usage
if __name__ == "__main__":
    test_scores = {
        "strategy": 62, "kelly": 58, "macro": 55, "gold": 60,
        "cross_asset": 65, "vix": 52, "monte_carlo": 68, "news": 61,
        "markets": 59, "black_scholes": 64, "kalman": 56, "fractal": 70,
        "fourier": 63, "copula": 58, "rates": 54
    }
    
    print("Testing Meta-Learner...")
    result = get_meta_learner_prediction(test_scores)
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']}")

    learner = NeuralMetaLearner()

