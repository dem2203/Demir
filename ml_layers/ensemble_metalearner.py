"""
PHASE 9: ENSEMBLE META-LEARNER
File: ensemble_metalearner.py
Folder: ml_layers/

Advanced meta-learner combining multiple model predictions
- Dynamic weight adjustment
- Performance-based weighting
- Model diversity tracking
- Adaptive ensemble strategy
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Track individual model performance"""
    model_id: str
    predictions: List[float]
    actual_values: List[float]
    mae: float = 0.0
    rmse: float = 0.0
    accuracy: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0


class EnsembleMetaLearner:
    """
    Advanced ensemble meta-learner
    
    Features:
    - Multiple prediction aggregation
    - Dynamic weight adjustment
    - Performance tracking
    - Diversity measurement
    - Risk-adjusted ensemble
    """
    
    def __init__(self, num_models: int = 4, learning_rate: float = 0.01):
        """
        Initialize ensemble meta-learner
        
        Args:
            num_models: Number of models in ensemble
            learning_rate: Weight update learning rate
        """
        self.num_models = num_models
        self.learning_rate = learning_rate
        
        # Initialize equal weights
        self.weights = np.ones(num_models) / num_models
        self.model_weights_history = []
        
        # Track performance
        self.model_performances: Dict[str, ModelPerformance] = {}
        self.ensemble_predictions: List[float] = []
        self.ensemble_errors: List[float] = []
        
        # Diversity tracking
        self.prediction_variance: List[float] = []
        self.correlation_matrix: Optional[np.ndarray] = None
        
    def predict(self, model_predictions: List[np.ndarray]) -> np.ndarray:
        """
        Generate ensemble prediction
        
        Args:
            model_predictions: List of predictions from each model
                              [model1_pred, model2_pred, ...]
            
        Returns:
            Ensemble prediction
        """
        if len(model_predictions) != self.num_models:
            raise ValueError(f"Expected {self.num_models} predictions, got {len(model_predictions)}")
        
        # Stack predictions
        predictions = np.array(model_predictions)
        
        # Calculate variance (diversity metric)
        variance = np.var(predictions, axis=0)
        self.prediction_variance.append(float(np.mean(variance)))
        
        # Weighted average ensemble
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        self.ensemble_predictions.append(ensemble_pred)
        
        return ensemble_pred
    
    def update_weights(self, model_errors: List[float], 
                      method: str = 'inverse_error') -> None:
        """
        Update ensemble weights based on model performance
        
        Args:
            model_errors: Error metrics for each model
            method: Weight update method
                   - 'inverse_error': w ∝ 1/error
                   - 'softmax': softmax of negative errors
                   - 'exponential': exponential decay
        """
        errors = np.array(model_errors)
        
        if method == 'inverse_error':
            # Inverse error weighting
            self.weights = 1.0 / (errors + 1e-6)
            self.weights /= self.weights.sum()
            
        elif method == 'softmax':
            # Softmax of negative errors
            neg_errors = -errors / (np.std(errors) + 1e-6)
            self.weights = np.exp(neg_errors) / np.sum(np.exp(neg_errors))
            
        elif method == 'exponential':
            # Exponential decay
            min_error = np.min(errors)
            decay_errors = np.exp(-(errors - min_error) / (np.std(errors) + 1e-6))
            self.weights = decay_errors / decay_errors.sum()
        
        # Store history
        self.model_weights_history.append(self.weights.copy())
        
        logger.info(f"Weights updated: {self.weights}")
    
    def calculate_diversity(self) -> float:
        """
        Calculate ensemble diversity (correlation metric)
        
        Returns:
            Average pairwise correlation (0-1, lower is better)
        """
        if len(self.ensemble_predictions) < self.num_models:
            return 0.0
        
        # Get recent predictions for all models
        recent_size = min(100, len(self.ensemble_predictions))
        
        # This would need model-specific predictions to compute properly
        # For now, use prediction variance as proxy
        avg_variance = np.mean(self.prediction_variance[-recent_size:])
        
        return float(avg_variance)
    
    def track_model_performance(self, model_id: str, 
                               predictions: List[float],
                               actual_values: List[float]) -> ModelPerformance:
        """
        Track individual model performance
        
        Args:
            model_id: Model identifier
            predictions: Model predictions
            actual_values: Ground truth values
            
        Returns:
            ModelPerformance object
        """
        predictions = np.array(predictions)
        actual = np.array(actual_values)
        
        # Calculate metrics
        errors = predictions - actual
        mae = np.mean(np.abs(errors))
        rmse = np.sqrt(np.mean(errors ** 2))
        
        # Accuracy (for classification)
        accuracy = np.mean((predictions.round() == actual).astype(float))
        
        # Sharpe ratio (for returns)
        if len(errors) > 1:
            returns = errors
            sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Max drawdown (for returns)
        cumulative = np.cumsum(errors)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / (np.abs(running_max) + 1e-6)
        max_dd = float(np.min(drawdown))
        
        perf = ModelPerformance(
            model_id=model_id,
            predictions=list(predictions),
            actual_values=list(actual),
            mae=mae,
            rmse=rmse,
            accuracy=accuracy,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd
        )
        
        self.model_performances[model_id] = perf
        return perf
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics for all tracked models"""
        stats = {}
        
        for model_id, perf in self.model_performances.items():
            stats[model_id] = {
                'mae': perf.mae,
                'rmse': perf.rmse,
                'accuracy': perf.accuracy,
                'sharpe': perf.sharpe_ratio,
                'max_dd': perf.max_drawdown,
                'weight': float(self.weights[int(model_id.split('_')[-1])] 
                               if '_' in model_id else 0.0)
            }
        
        return stats
    
    def get_ensemble_metrics(self) -> Dict[str, float]:
        """Get ensemble-level metrics"""
        if not self.ensemble_errors:
            return {}
        
        errors = np.array(self.ensemble_errors)
        
        return {
            'ensemble_mae': float(np.mean(np.abs(errors))),
            'ensemble_rmse': float(np.sqrt(np.mean(errors ** 2))),
            'avg_diversity': float(np.mean(self.prediction_variance)),
            'diversity_trend': float(np.mean(self.prediction_variance[-10:]) 
                                    if len(self.prediction_variance) > 10 else 0.0)
        }
    
    def recalibrate_weights(self, performance_data: Dict[str, List[float]]) -> None:
        """
        Recalibrate weights based on full performance data
        
        Args:
            performance_data: {model_id: [error_list]}
        """
        errors = []
        
        for model_id in sorted(performance_data.keys()):
            model_errors = performance_data[model_id]
            avg_error = np.mean(model_errors)
            errors.append(avg_error)
        
        self.update_weights(errors, method='inverse_error')
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive ensemble report"""
        return {
            'ensemble_metrics': self.get_ensemble_metrics(),
            'model_statistics': self.get_model_statistics(),
            'weights': self.weights.tolist(),
            'num_predictions': len(self.ensemble_predictions),
            'avg_diversity': float(np.mean(self.prediction_variance)) 
                            if self.prediction_variance else 0.0,
            'weight_history': [w.tolist() for w in self.model_weights_history]
        }


if __name__ == "__main__":
    print("✅ PHASE 9: Ensemble Meta-Learner Ready")
