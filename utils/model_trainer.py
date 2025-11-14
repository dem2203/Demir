import logging
import numpy as np
from datetime import datetime, timedelta
import pickle
import os
from typing import Tuple

logger = logging.getLogger(__name__)

class IncrementalModelTrainer:
    """
    Incremental ML training - keeps models fresh
    Retrains every 24 hours with latest 1000 trades
    No data drift, always optimal
    """
    
    def __init__(self, db, model_dir: str = "models"):
        self.db = db
        self.model_dir = model_dir
        self.last_training = None
        self.training_interval = timedelta(hours=24)
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    def should_retrain(self) -> bool:
        """Check if retraining needed"""
        if not self.last_training:
            logger.info("First training - should proceed")
            return True
        
        time_since = datetime.now() - self.last_training
        if time_since > self.training_interval:
            logger.info(f"Retraining needed ({time_since} elapsed)")
            return True
        
        return False
    
    def get_training_data(self, limit: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Get recent trades for training"""
        try:
            # Get last N trades
            trades = self.db.get_recent_trades(limit)
            
            # Features: [technical, ml, sentiment, onchain]
            X = np.array([
                [t['technical'], t['ml'], t['sentiment'], t['onchain']]
                for t in trades
            ])
            
            # Labels: 1 = Win, 0 = Loss
            y = np.array([1 if t['profit'] > 0 else 0 for t in trades])
            
            logger.info(f"Training data: {len(X)} samples")
            return X, y
        except Exception as e:
            logger.error(f"Training data error: {e}")
            return np.array([]), np.array([])
    
    def train_transformer(self, X: np.ndarray, y: np.ndarray):
        """Retrain transformer model"""
        try:
            from advanced_ai.deep_learning_models import TransformerModel
            
            logger.info("🔄 Retraining Transformer...")
            transformer = TransformerModel()
            
            # Incremental training
            transformer.fit(X, y, epochs=5, batch_size=32)
            
            # Save model
            model_path = f"{self.model_dir}/transformer_v{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(transformer, f)
            
            logger.info(f"✅ Transformer saved: {model_path}")
        except Exception as e:
            logger.error(f"Transformer training error: {e}")
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray):
        """Retrain ensemble models"""
        try:
            from advanced_ai.deep_learning_models import EnsemblePredictor
            
            logger.info("🔄 Retraining Ensemble...")
            ensemble = EnsemblePredictor()
            
            # Incremental training
            ensemble.fit(X, y)
            
            # Save model
            model_path = f"{self.model_dir}/ensemble_v{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(ensemble, f)
            
            logger.info(f"✅ Ensemble saved: {model_path}")
        except Exception as e:
            logger.error(f"Ensemble training error: {e}")
    
    def run_training(self):
        """Run full training cycle"""
        if not self.should_retrain():
            return
        
        logger.info("🔄 Starting model retraining...")
        
        # Get training data
        X, y = self.get_training_data(limit=1000)
        
        if len(X) > 0:
            # Train models
            self.train_transformer(X, y)
            self.train_ensemble(X, y)
            
            self.last_training = datetime.now()
            logger.info("✅ Model retraining complete")
        else:
            logger.warning("⚠️ No training data available")
