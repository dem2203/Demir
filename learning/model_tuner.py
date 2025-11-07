"""FAZ 12 - DOSYA 3: model_tuner.py - Model Parametrelerini Fine-Tune Et"""

import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelTuner:
    """Regressor parametrelerini otomatik tune et"""
    
    def __init__(self):
        self.hyperparameters = {
            'learning_rate': 0.01,
            'momentum': 0.9,
            'batch_size': 32,
            'epochs': 100,
            'dropout_rate': 0.2,
            'regularization': 0.001
        }
        self.tuning_history = []
    
    def tune_learning_rate(self, train_loss_history: list) -> float:
        """Learning rate'i optimize et"""
        if len(train_loss_history) < 10:
            return 0.01
        
        recent_loss = np.mean(train_loss_history[-10:])
        previous_loss = np.mean(train_loss_history[-20:-10])
        
        improvement_rate = (previous_loss - recent_loss) / (previous_loss + 1e-10)
        
        if improvement_rate > 0.05:
            new_lr = min(self.hyperparameters['learning_rate'] * 1.1, 0.1)
        elif improvement_rate < 0.01:
            new_lr = max(self.hyperparameters['learning_rate'] * 0.9, 0.001)
        else:
            new_lr = self.hyperparameters['learning_rate']
        
        logger.info(f"Learning rate tuned: {self.hyperparameters['learning_rate']:.4f} -> {new_lr:.4f}")
        self.hyperparameters['learning_rate'] = new_lr
        return new_lr
    
    def tune_batch_size(self, available_memory: float, sample_count: int) -> int:
        """Batch size'ı belleğe göre tune et"""
        max_batch = min(256, sample_count)
        
        if available_memory < 1000:
            new_batch = 16
        elif available_memory < 5000:
            new_batch = 32
        else:
            new_batch = 64
        
        self.hyperparameters['batch_size'] = new_batch
        logger.info(f"Batch size set to {new_batch}")
        return new_batch
    
    def tune_regularization(self, validation_accuracy: float, train_accuracy: float) -> float:
        """Overfitting kontrol için regularization tune et"""
        overfit_ratio = train_accuracy / (validation_accuracy + 1e-10)
        
        if overfit_ratio > 1.3:
            new_reg = min(self.hyperparameters['regularization'] * 1.5, 0.01)
        elif overfit_ratio < 1.05:
            new_reg = max(self.hyperparameters['regularization'] * 0.8, 0.0001)
        else:
            new_reg = self.hyperparameters['regularization']
        
        self.hyperparameters['regularization'] = new_reg
        logger.info(f"Regularization tuned: {new_reg:.6f}")
        return new_reg
    
    def tune_all_hyperparameters(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Tüm hyperparametreleri tune et"""
        
        # Learning rate tune
        if 'train_loss_history' in metrics:
            self.tune_learning_rate(metrics['train_loss_history'])
        
        # Batch size tune
        if 'available_memory' in metrics and 'sample_count' in metrics:
            self.tune_batch_size(metrics['available_memory'], metrics['sample_count'])
        
        # Regularization tune
        if 'val_accuracy' in metrics and 'train_accuracy' in metrics:
            self.tune_regularization(metrics['val_accuracy'], metrics['train_accuracy'])
        
        # Momentum tune
        if metrics.get('oscillation_rate', 0) > 0.05:
            self.hyperparameters['momentum'] = min(0.99, self.hyperparameters['momentum'] + 0.01)
        
        # Dropout tune
        if metrics.get('overfitting_detected', False):
            self.hyperparameters['dropout_rate'] = min(0.5, self.hyperparameters['dropout_rate'] + 0.05)
        
        self.tuning_history.append({
            'timestamp': np.datetime64('now'),
            'hyperparameters': self.hyperparameters.copy()
        })
        
        return self.hyperparameters
    
    def get_recommended_config(self, model_type: str = 'lstm') -> Dict[str, Any]:
        """Model tipine göre önerilen config'i ver"""
        
        configs = {
            'lstm': {
                'learning_rate': 0.001,
                'momentum': 0.95,
                'batch_size': 32,
                'epochs': 100,
                'dropout_rate': 0.3,
                'regularization': 0.001
            },
            'transformer': {
                'learning_rate': 0.0001,
                'momentum': 0.9,
                'batch_size': 64,
                'epochs': 50,
                'dropout_rate': 0.2,
                'regularization': 0.0005
            },
            'xgboost': {
                'learning_rate': 0.1,
                'max_depth': 5,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8
            }
        }
        
        return configs.get(model_type, configs['lstm'])
    
    def get_tuning_summary(self) -> Dict[str, Any]:
        """Tuning özetini ver"""
        return {
            'current_hyperparameters': self.hyperparameters.copy(),
            'tuning_history_length': len(self.tuning_history),
            'last_tuning': self.tuning_history[-1] if self.tuning_history else None
        }
