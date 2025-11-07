"""FAZ 12 - DOSYA 1: learning_engine.py - AI Kendini Öğrenir"""

import numpy as np, pandas as pd, pickle
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LearningEngine:
    """Her trade'den öğrenme - Factor ağırlıklarını update eder"""
    
    def __init__(self):
        self.trade_history = []
        self.factor_weights = {}
        self.daily_learning = {}
        self.learning_rate = 0.01
        self.momentum = 0.9
        self.velocity = {}
    
    def log_trade(self, trade: Dict[str, Any]):
        """Her trade'i kaydet"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'entry_price': trade.get('entry_price'),
            'exit_price': trade.get('exit_price'),
            'pnl': trade.get('pnl', 0),
            'factors': trade.get('factors', {}),
            'prediction': trade.get('prediction', None),
            'actual': trade.get('actual', None),
            'correct': trade.get('pnl', 0) > 0
        })
    
    def update_factor_weights(self, factors: Dict[str, float], result: bool, pnl: float):
        """Bayesian learning: Başarılı faktörlerin ağırlığını artır"""
        adjustment = self.learning_rate * pnl if pnl != 0 else 0
        
        for factor_name, value in factors.items():
            if factor_name not in self.factor_weights:
                self.factor_weights[factor_name] = 0.5
                self.velocity[factor_name] = 0
            
            # Signal: factor bullish ise 1, bearish ise -1
            signal = 1.0 if value > 0.5 else -1.0
            
            # Momentum-based update
            gradient = signal * adjustment * (1.0 if result else -1.0)
            self.velocity[factor_name] = self.momentum * self.velocity[factor_name] + gradient
            
            # Update weight (keep in 0-1)
            new_weight = self.factor_weights[factor_name] + self.velocity[factor_name]
            self.factor_weights[factor_name] = max(0, min(1, new_weight))
            
            logger.debug(f"Updated {factor_name}: {self.factor_weights[factor_name]:.4f}")
    
    def calculate_factor_correlation_to_profit(self) -> Dict[str, float]:
        """Her faktörün trade sonucuyla korelasyonunu hesapla"""
        if len(self.trade_history) < 10:
            return {}
        
        correlations = {}
        trades_df = pd.DataFrame(self.trade_history)
        
        for factor_name in self.factor_weights.keys():
            values = []
            pnls = []
            
            for trade in self.trade_history[-100:]:
                if factor_name in trade.get('factors', {}):
                    values.append(trade['factors'][factor_name])
                    pnls.append(1 if trade['pnl'] > 0 else 0)
            
            if len(values) > 5:
                corr = np.corrcoef(values, pnls)[0, 1]
                correlations[factor_name] = float(np.nan_to_num(corr, 0))
        
        return correlations
    
    def get_top_predictive_factors(self, top_n: int = 10) -> List[tuple]:
        """En iyi tahmin eden faktörleri bul"""
        correlations = self.calculate_factor_correlation_to_profit()
        
        sorted_factors = sorted(
            correlations.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return sorted_factors[:top_n]
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Öğrenme özetini ver"""
        if not self.trade_history:
            return {}
        
        trades_df = pd.DataFrame(self.trade_history)
        
        return {
            'total_trades': len(self.trade_history),
            'winning_trades': sum(1 for t in self.trade_history if t['correct']),
            'accuracy': sum(1 for t in self.trade_history if t['correct']) / len(self.trade_history) if self.trade_history else 0,
            'total_pnl': sum(t['pnl'] for t in self.trade_history),
            'avg_pnl': np.mean([t['pnl'] for t in self.trade_history]),
            'top_factors': self.get_top_predictive_factors(5),
            'factor_weights': self.factor_weights.copy()
        }
    
    def export_weights(self, filepath: str = "learned_weights.pkl"):
        """Öğrenilen ağırlıkları kaydet"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'weights': self.factor_weights,
                'velocity': self.velocity,
                'timestamp': datetime.now()
            }, f)
        logger.info(f"Weights saved to {filepath}")
    
    def import_weights(self, filepath: str = "learned_weights.pkl"):
        """Öğrenilen ağırlıkları yükle"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.factor_weights = data['weights']
            self.velocity = data['velocity']
        logger.info(f"Weights loaded from {filepath}")
