#!/usr/bin/env python3
"""
🔱 DEMIR AI - ensemble_system_v2.py
============================================================================
ENSEMBLE VOTING SYSTEM - PRODUCTION READY - STRICT VALIDATION

Combine LSTM + Transformer + Traditional TA signals
Rules:
✅ Fail if models missing
✅ Validate all predictions
✅ Confidence must be 0-100
✅ Signal must be UP/DOWN/HOLD
✅ All errors raised, no swallowing
============================================================================
"""

import logging
import traceback
from typing import Dict, Tuple, Optional
from datetime import datetime

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ============================================================================
# ENSEMBLE VOTER - PRODUCTION GRADE
# ============================================================================

class EnsembleVoter:
    """Ensemble prediction voter - STRICT VALIDATION"""
    
    def __init__(self,
                 lstm_model=None,
                 transformer_model=None,
                 lstm_weight: float = 0.5,
                 transformer_weight: float = 0.3,
                 ta_weight: float = 0.2):
        """
        Initialize ensemble
        
        Args:
            lstm_model: Trained LSTM model (required)
            transformer_model: Trained Transformer model (required)
            lstm_weight: Weight for LSTM
            transformer_weight: Weight for Transformer
            ta_weight: Weight for Traditional TA
        
        Raises:
            ValueError: If models missing or weights invalid
        """
        
        if lstm_model is None:
            raise ValueError("❌ LSTM model is required!")
        
        if transformer_model is None:
            raise ValueError("❌ Transformer model is required!")
        
        # Validate weights
        total_weight = lstm_weight + transformer_weight + ta_weight
        if total_weight <= 0:
            raise ValueError(f"❌ Invalid weights: sum is {total_weight}")
        
        self.lstm_model = lstm_model
        self.transformer_model = transformer_model
        
        # Normalize weights
        self.weights = {
            'lstm': lstm_weight / total_weight,
            'transformer': transformer_weight / total_weight,
            'ta': ta_weight / total_weight
        }
        
        self.predictions_history = []
        logger.info(
            f"✅ EnsembleVoter initialized with weights: "
            f"LSTM={self.weights['lstm']:.2f}, "
            f"Transformer={self.weights['transformer']:.2f}, "
            f"TA={self.weights['ta']:.2f}"
        )
    
    def predict_lstm(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Get LSTM prediction - STRICT
        
        Args:
            features: Input features
        
        Returns:
            (signal, confidence)
        
        Raises:
            ValueError: If prediction invalid
        """
        
        try:
            if self.lstm_model is None:
                raise ValueError("❌ LSTM model not loaded")
            
            signal, confidence = self.lstm_model.predict(features)
            
            if signal not in ['UP', 'DOWN', 'HOLD']:
                raise ValueError(f"❌ Invalid LSTM signal: {signal}")
            
            if not 0 <= confidence <= 100:
                raise ValueError(f"❌ Invalid LSTM confidence: {confidence}")
            
            logger.debug(f"✅ LSTM prediction: {signal} ({confidence:.1f}%)")
            return signal, confidence
        
        except Exception as e:
            logger.error(f"❌ LSTM prediction failed: {e}")
            raise
    
    def predict_transformer(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Get Transformer prediction - STRICT
        
        Args:
            features: Input features
        
        Returns:
            (signal, confidence)
        
        Raises:
            ValueError: If prediction invalid
        """
        
        try:
            if self.transformer_model is None:
                raise ValueError("❌ Transformer model not loaded")
            
            signal, confidence = self.transformer_model.predict(features)
            
            if signal not in ['UP', 'DOWN', 'HOLD']:
                raise ValueError(f"❌ Invalid Transformer signal: {signal}")
            
            if not 0 <= confidence <= 100:
                raise ValueError(f"❌ Invalid Transformer confidence: {confidence}")
            
            logger.debug(f"✅ Transformer prediction: {signal} ({confidence:.1f}%)")
            return signal, confidence
        
        except Exception as e:
            logger.error(f"❌ Transformer prediction failed: {e}")
            raise
    
    def predict_traditional_ta(self, indicators: Dict) -> Tuple[str, float]:
        """
        Traditional TA prediction - STRICT
        
        Args:
            indicators: Technical indicators dict
        
        Returns:
            (signal, confidence)
        
        Raises:
            ValueError: If indicators invalid
        """
        
        try:
            if not indicators:
                raise ValueError("❌ Indicators dict is empty")
            
            # Extract indicators
            rsi = indicators.get('rsi_14', 50)
            macd = indicators.get('macd_line', 0)
            bb_position = indicators.get('bb_position', 0.5)
            atr = indicators.get('atr_14', 0)
            
            # Validate
            if not 0 <= rsi <= 100:
                raise ValueError(f"❌ Invalid RSI: {rsi}")
            
            if not 0 <= bb_position <= 1:
                raise ValueError(f"❌ Invalid BB position: {bb_position}")
            
            # Score-based TA signal
            score = 50.0
            
            # RSI signals
            if rsi < 30:
                score += 25  # Oversold = BUY
            elif rsi > 70:
                score -= 25  # Overbought = SELL
            else:
                score += (50 - rsi) * 0.3
            
            # MACD signals
            if macd > 0:
                score += 15
            else:
                score -= 15
            
            # Bollinger Bands signals
            if bb_position < 0.2:
                score += 20  # Near lower band = BUY
            elif bb_position > 0.8:
                score -= 20  # Near upper band = SELL
            
            # ATR volatility adjustment
            if atr > 0:
                atr_factor = min(atr / 100, 0.1)  # Cap effect
                if score > 50:
                    score += atr_factor * 10
                else:
                    score -= atr_factor * 10
            
            # Clamp score
            score = np.clip(score, 0, 100)
            
            # Determine signal
            if score >= 70:
                signal = 'UP'
                confidence = score
            elif score <= 30:
                signal = 'DOWN'
                confidence = 100 - score
            else:
                signal = 'HOLD'
                confidence = 50 + (abs(score - 50) * 0.5)
            
            # Validate confidence
            if not 0 <= confidence <= 100:
                raise ValueError(f"❌ Invalid TA confidence: {confidence}")
            
            logger.debug(f"✅ TA prediction: {signal} ({confidence:.1f}%)")
            return signal, confidence
        
        except Exception as e:
            logger.error(f"❌ TA prediction failed: {e}")
            raise
    
    def soft_vote(self,
                 lstm_signal: str,
                 lstm_conf: float,
                 transformer_signal: str,
                 transformer_conf: float,
                 ta_signal: str,
                 ta_conf: float) -> Dict:
        """
        Soft voting using weighted probabilities - STRICT
        
        Args:
            lstm_signal: LSTM signal
            lstm_conf: LSTM confidence
            transformer_signal: Transformer signal
            transformer_conf: Transformer confidence
            ta_signal: TA signal
            ta_conf: TA confidence
        
        Returns:
            Ensemble result with final signal and confidence
        
        Raises:
            ValueError: If voting fails
        """
        
        try:
            # Validate inputs
            for sig in [lstm_signal, transformer_signal, ta_signal]:
                if sig not in ['UP', 'DOWN', 'HOLD']:
                    raise ValueError(f"❌ Invalid signal: {sig}")
            
            for conf in [lstm_conf, transformer_conf, ta_conf]:
                if not 0 <= conf <= 100:
                    raise ValueError(f"❌ Invalid confidence: {conf}")
            
            # Convert signals to probability distributions
            signal_to_probs = {
                'DOWN': np.array([0.85, 0.10, 0.05]),
                'HOLD': np.array([0.33, 0.34, 0.33]),
                'UP': np.array([0.05, 0.10, 0.85])
            }
            
            # Get probabilities weighted by confidence
            lstm_probs = signal_to_probs[lstm_signal] * (lstm_conf / 100)
            transformer_probs = signal_to_probs[transformer_signal] * (transformer_conf / 100)
            ta_probs = signal_to_probs[ta_signal] * (ta_conf / 100)
            
            # Ensemble: weighted sum
            ensemble_probs = (
                lstm_probs * self.weights['lstm'] +
                transformer_probs * self.weights['transformer'] +
                ta_probs * self.weights['ta']
            )
            
            # Normalize
            if np.sum(ensemble_probs) > 0:
                ensemble_probs = ensemble_probs / np.sum(ensemble_probs)
            else:
                raise ValueError("❌ Ensemble probabilities sum to 0")
            
            # Get final prediction
            pred_map = {0: 'DOWN', 1: 'HOLD', 2: 'UP'}
            final_signal = pred_map[np.argmax(ensemble_probs)]
            final_confidence = float(np.max(ensemble_probs)) * 100
            
            # Validate output
            if final_signal not in ['UP', 'DOWN', 'HOLD']:
                raise ValueError(f"❌ Invalid ensemble signal: {final_signal}")
            
            if not 0 <= final_confidence <= 100:
                raise ValueError(f"❌ Invalid ensemble confidence: {final_confidence}")
            
            logger.debug(f"✅ Ensemble result: {final_signal} ({final_confidence:.1f}%)")
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'ensemble_probs': ensemble_probs.tolist(),
                'lstm_signal': lstm_signal,
                'lstm_confidence': lstm_conf,
                'transformer_signal': transformer_signal,
                'transformer_confidence': transformer_conf,
                'ta_signal': ta_signal,
                'ta_confidence': ta_conf
            }
        
        except Exception as e:
            logger.critical(f"❌ SOFT VOTE FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def generate_ensemble_signal(self,
                                features: np.ndarray,
                                indicators: Dict = None) -> Dict:
        """
        Generate final ensemble signal - STRICT
        
        Args:
            features: Input features (80+)
            indicators: Technical indicators for TA
        
        Returns:
            Complete ensemble prediction
        
        Raises:
            ValueError: If any component fails
        """
        
        try:
            logger.info("🔄 Generating ensemble signal...")
            
            # Get individual predictions (NO try/except - let them fail!)
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
                'lstm': 'v2',
                'transformer': 'v2',
                'ensemble': 'v2'
            }
            
            # Log to history
            self.predictions_history.append(result)
            
            logger.info(
                f"✅ ENSEMBLE SIGNAL: {result['signal']} "
                f"({result['confidence']:.1f}%)"
            )
            
            return result
        
        except Exception as e:
            logger.critical(f"❌ ENSEMBLE SIGNAL GENERATION FAILED: {e}")
            logger.critical(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    def get_performance_stats(self) -> Dict:
        """Get ensemble performance statistics"""
        
        try:
            if not self.predictions_history:
                raise ValueError("❌ No predictions in history")
            
            df = pd.DataFrame(self.predictions_history)
            
            up_preds = len(df[df['signal'] == 'UP'])
            down_preds = len(df[df['signal'] == 'DOWN'])
            hold_preds = len(df[df['signal'] == 'HOLD'])
            
            avg_confidence = df['confidence'].mean()
            
            return {
                'total_predictions': len(df),
                'up_signals': up_preds,
                'down_signals': down_preds,
                'hold_signals': hold_preds,
                'average_confidence': float(avg_confidence)
            }
        
        except Exception as e:
            logger.error(f"❌ Performance stats failed: {e}")
            raise

# ============================================================================
# MODEL MANAGER
# ============================================================================

class ModelManager:
    """Manage model versions and performance - STRICT"""
    
    def __init__(self):
        self.models = {
            'lstm': [],
            'transformer': []
        }
        self.performance_stats = {}
        logger.info("✅ ModelManager initialized")
    
    def register_model(self, model_type: str, model, version: int = 1):
        """Register a model - STRICT"""
        
        try:
            if model_type not in self.models:
                raise ValueError(f"❌ Invalid model type: {model_type}")
            
            if model is None:
                raise ValueError(f"❌ Model is None")
            
            self.models[model_type].append({
                'model': model,
                'version': version,
                'created_at': datetime.now().isoformat(),
                'accuracy': 0.0
            })
            
            logger.info(f"✅ Registered {model_type} v{version}")
        
        except Exception as e:
            logger.error(f"❌ Model registration failed: {e}")
            raise
    
    def get_best_model(self, model_type: str):
        """Get best model by accuracy - STRICT"""
        
        try:
            if model_type not in self.models:
                raise ValueError(f"❌ Invalid model type: {model_type}")
            
            if not self.models[model_type]:
                raise ValueError(f"❌ No {model_type} models registered")
            
            best = max(self.models[model_type], key=lambda x: x['accuracy'])
            logger.info(f"✅ Retrieved best {model_type}: v{best['version']}")
            return best['model']
        
        except Exception as e:
            logger.error(f"❌ Get best model failed: {e}")
            raise
    
    def update_model_performance(self, model_type: str, version: int, metrics: Dict):
        """Update model performance - STRICT"""
        
        try:
            for model_info in self.models.get(model_type, []):
                if model_info['version'] == version:
                    model_info['accuracy'] = metrics.get('accuracy', 0)
                    model_info['metrics'] = metrics
                    logger.info(f"✅ Updated {model_type} v{version} performance")
                    return
            
            logger.warning(f"⚠️ Model {model_type} v{version} not found")
        
        except Exception as e:
            logger.error(f"❌ Performance update failed: {e}")
            raise

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    logger.info("=" * 80)
    logger.info("🔱 DEMIR AI - Ensemble System v2 - PRODUCTION READY")
    logger.info("=" * 80)
    
    logger.info("✅ Ensemble System ready (requires LSTM + Transformer models)")
