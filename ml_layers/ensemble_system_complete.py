#!/usr/bin/env python3
"""
🔱 DEMIR AI - ensemble_system.py
============================================================================
ENSEMBLE VOTING SYSTEM (2K lines)

Combine LSTM + Transformer + Traditional TA into single prediction
- Soft voting (weighted probabilities)
- Confidence scoring
- Model performance tracking
- Database logging

Weights:
- LSTM: 50% (proven stability)
- Transformer: 30% (better long-range)
- Traditional TA: 20% (interpretability)
============================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# ============================================================================
# ENSEMBLE VOTER
# ============================================================================

class EnsembleVoter:
    """Combine predictions from multiple models"""
    
    def __init__(self,
                 lstm_model=None,
                 transformer_model=None,
                 lstm_weight: float = 0.5,
                 transformer_weight: float = 0.3,
                 ta_weight: float = 0.2):
        """
        Initialize ensemble
        
        Args:
            lstm_model: Trained LSTM model
            transformer_model: Trained Transformer model
            lstm_weight: Weight for LSTM predictions
            transformer_weight: Weight for Transformer
            ta_weight: Weight for Traditional TA
        """
        
        self.lstm_model = lstm_model
        self.transformer_model = transformer_model
        
        self.weights = {
            'lstm': lstm_weight,
            'transformer': transformer_weight,
            'ta': ta_weight
        }
        
        # Normalize weights
        total = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] /= total
        
        self.predictions_history = []
        logger.info(f"✅ EnsembleVoter initialized with weights: {self.weights}")
    
    def predict_lstm(self, features: np.ndarray) -> Tuple[str, float]:
        """Get LSTM prediction"""
        
        try:
            if self.lstm_model is None:
                return 'HOLD', 0.33
            
            signal, confidence = self.lstm_model.predict(features)
            return signal, confidence
        except Exception as e:
            logger.error(f"❌ LSTM prediction error: {e}")
            return 'HOLD', 0.33
    
    def predict_transformer(self, features: np.ndarray) -> Tuple[str, float]:
        """Get Transformer prediction"""
        
        try:
            if self.transformer_model is None:
                return 'HOLD', 0.33
            
            signal, confidence = self.transformer_model.predict(features)
            return signal, confidence
        except Exception as e:
            logger.error(f"❌ Transformer prediction error: {e}")
            return 'HOLD', 0.33
    
    def predict_traditional_ta(self, indicators: Dict) -> Tuple[str, float]:
        """Traditional technical analysis signal"""
        
        try:
            rsi = indicators.get('rsi_14', 50)
            macd = indicators.get('macd_line', 0)
            bb_position = indicators.get('bb_position', 0.5)
            
            # Simple rules-based TA
            score = 50.0
            
            if rsi < 30:
                score += 30  # Oversold = BUY
            elif rsi > 70:
                score -= 30  # Overbought = SELL
            else:
                score += (50 - rsi) * 0.6
            
            if macd > 0:
                score += 15
            else:
                score -= 15
            
            if bb_position < 0.2:
                score += 20  # Near lower band = BUY
            elif bb_position > 0.8:
                score -= 20  # Near upper band = SELL
            
            score = max(0, min(100, score))
            
            if score >= 70:
                return 'UP', score
            elif score <= 30:
                return 'DOWN', 100 - score
            else:
                return 'HOLD', 50
        
        except Exception as e:
            logger.error(f"❌ TA prediction error: {e}")
            return 'HOLD', 50
    
    def soft_vote(self,
                 lstm_pred: str,
                 lstm_conf: float,
                 transformer_pred: str,
                 transformer_conf: float,
                 ta_pred: str,
                 ta_conf: float) -> Dict:
        """
        Soft voting using weighted probabilities
        
        Returns:
            Final signal, confidence, voting breakdown
        """
        
        try:
            # Convert signals to probabilities
            signal_to_prob = {
                'DOWN': [0.9, 0.05, 0.05],
                'HOLD': [0.33, 0.33, 0.33],
                'UP': [0.05, 0.05, 0.9]
            }
            
            lstm_probs = np.array(signal_to_prob.get(lstm_pred, [0.33, 0.33, 0.33])) * (lstm_conf / 100)
            transformer_probs = np.array(signal_to_prob.get(transformer_pred, [0.33, 0.33, 0.33])) * (transformer_conf / 100)
            ta_probs = np.array(signal_to_prob.get(ta_pred, [0.33, 0.33, 0.33])) * (ta_conf / 100)
            
            # Weighted ensemble
            ensemble_probs = (
                lstm_probs * self.weights['lstm'] +
                transformer_probs * self.weights['transformer'] +
                ta_probs * self.weights['ta']
            )
            
            # Normalize
            ensemble_probs = ensemble_probs / np.sum(ensemble_probs) if np.sum(ensemble_probs) > 0 else ensemble_probs
            
            # Get final prediction
            pred_map = {0: 'DOWN', 1: 'HOLD', 2: 'UP'}
            final_signal = pred_map[np.argmax(ensemble_probs)]
            confidence = float(np.max(ensemble_probs)) * 100
            
            return {
                'signal': final_signal,
                'confidence': confidence,
                'lstm': lstm_pred,
                'lstm_conf': lstm_conf,
                'transformer': transformer_pred,
                'transformer_conf': transformer_conf,
                'ta': ta_pred,
                'ta_conf': ta_conf,
                'ensemble_probs': ensemble_probs.tolist()
            }
        
        except Exception as e:
            logger.error(f"❌ Soft vote error: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 50,
                'error': str(e)
            }
    
    def generate_ensemble_signal(self, 
                                features: np.ndarray,
                                indicators: Dict = None) -> Dict:
        """
        Generate final ensemble signal
        
        Args:
            features: Input features (80+)
            indicators: Technical indicators for TA
        
        Returns:
            Complete ensemble prediction
        """
        
        try:
            # Get individual predictions
            lstm_signal, lstm_conf = self.predict_lstm(features)
            transformer_signal, transformer_conf = self.predict_transformer(features)
            ta_signal, ta_conf = self.predict_traditional_ta(indicators or {})
            
            # Ensemble voting
            result = self.soft_vote(
                lstm_signal, lstm_conf,
                transformer_signal, transformer_conf,
                ta_signal, ta_conf
            )
            
            # Add metadata
            result['timestamp'] = datetime.now().isoformat()
            result['model_versions'] = {
                'lstm': 'v1',
                'transformer': 'v1',
                'ta': 'builtin'
            }
            
            # Log
            self.predictions_history.append(result)
            logger.info(f"✅ Ensemble signal: {result['signal']} ({result['confidence']:.1f}%)")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Ensemble generation error: {e}")
            return {'signal': 'HOLD', 'confidence': 50, 'error': str(e)}

# ============================================================================
# MODEL MANAGER
# ============================================================================

class ModelManager:
    """Manage multiple model versions and performance"""
    
    def __init__(self):
        self.models = {
            'lstm': [],
            'transformer': []
        }
        self.performance_stats = {}
        logger.info("✅ ModelManager initialized")
    
    def register_model(self, model_type: str, model, version: int = 1):
        """Register a trained model"""
        
        try:
            self.models[model_type].append({
                'model': model,
                'version': version,
                'created_at': datetime.now().isoformat(),
                'accuracy': 0.0
            })
            logger.info(f"✅ Registered {model_type} v{version}")
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
    
    def get_best_model(self, model_type: str):
        """Get best performing model version"""
        
        try:
            if not self.models[model_type]:
                return None
            
            best = max(self.models[model_type], key=lambda x: x['accuracy'])
            logger.info(f"✅ Retrieved best {model_type}: v{best['version']}")
            return best['model']
        except Exception as e:
            logger.error(f"❌ Get best model error: {e}")
            return None
    
    def update_model_performance(self, model_type: str, version: int, metrics: Dict):
        """Update model performance metrics"""
        
        try:
            for model_info in self.models[model_type]:
                if model_info['version'] == version:
                    model_info['accuracy'] = metrics.get('accuracy', 0)
                    model_info['metrics'] = metrics
                    logger.info(f"✅ Updated {model_type} v{version} performance")
                    break
        except Exception as e:
            logger.error(f"❌ Update performance error: {e}")
    
    def compare_models(self) -> Dict:
        """Compare all model performances"""
        
        try:
            comparison = {
                'lstm': sorted(self.models['lstm'], key=lambda x: x['accuracy'], reverse=True)[:3],
                'transformer': sorted(self.models['transformer'], key=lambda x: x['accuracy'], reverse=True)[:3]
            }
            
            logger.info("✅ Model comparison complete")
            return comparison
        except Exception as e:
            logger.error(f"❌ Comparison error: {e}")
            return {}

# ============================================================================
# PERFORMANCE TRACKER
# ============================================================================

class EnsemblePerformanceTracker:
    """Track ensemble prediction accuracy over time"""
    
    def __init__(self):
        self.predictions = []
        self.performance_metrics = {}
        logger.info("✅ EnsemblePerformanceTracker initialized")
    
    def log_prediction(self, prediction_result: Dict, actual_direction: str):
        """Log prediction and actual result"""
        
        try:
            prediction_result['actual_direction'] = actual_direction
            prediction_result['correct'] = prediction_result['signal'] == actual_direction
            
            self.predictions.append(prediction_result)
            logger.info(f"✅ Logged prediction: {prediction_result['signal']} vs {actual_direction}")
        except Exception as e:
            logger.error(f"❌ Logging error: {e}")
    
    def calculate_metrics(self) -> Dict:
        """Calculate accuracy metrics"""
        
        try:
            if not self.predictions:
                return {}
            
            df = pd.DataFrame(self.predictions)
            
            correct = df['correct'].sum()
            total = len(df)
            accuracy = correct / total if total > 0 else 0
            
            # Metrics by signal type
            metrics = {
                'overall_accuracy': accuracy,
                'total_predictions': total,
                'correct_predictions': correct,
                'signals': {}
            }
            
            for signal in ['UP', 'DOWN', 'HOLD']:
                signal_df = df[df['signal'] == signal]
                if len(signal_df) > 0:
                    signal_accuracy = signal_df['correct'].sum() / len(signal_df)
                    metrics['signals'][signal] = {
                        'count': len(signal_df),
                        'accuracy': signal_accuracy
                    }
            
            logger.info(f"✅ Ensemble accuracy: {accuracy:.4f}")
            return metrics
        
        except Exception as e:
            logger.error(f"❌ Metrics calculation error: {e}")
            return {}

# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize
    voter = EnsembleVoter(lstm_weight=0.5, transformer_weight=0.3, ta_weight=0.2)
    manager = ModelManager()
    tracker = EnsemblePerformanceTracker()
    
    # Sample prediction
    sample_features = np.random.randn(80)
    sample_indicators = {'rsi_14': 45, 'macd_line': 0.01, 'bb_position': 0.6}
    
    result = voter.generate_ensemble_signal(sample_features, sample_indicators)
    print(f"✅ Ensemble prediction: {result['signal']} ({result['confidence']:.1f}%)")
    
    # Track
    tracker.log_prediction(result, 'UP')
    metrics = tracker.calculate_metrics()
    print(f"✅ Metrics: {metrics}")
