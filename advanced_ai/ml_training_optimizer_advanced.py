import logging
from typing import Tuple, List, Dict, Any
import numpy as np
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

logger = logging.getLogger(__name__)


class MLTrainingOptimizer:
    """Optimize ML model training with real data."""

    def __init__(self):
        """Initialize trainer."""
        self.model = None
        self.scaler = StandardScaler()
        self.best_params = {}

    def validate_training_data(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[bool, List[str]]:
        """Validate training data."""
        errors = []

        if len(X) < 1000:
            errors.append(f"Need minimum 1000 samples, got {len(X)}")

        if len(X) != len(y):
            errors.append(f"X and y size mismatch: {len(X)} vs {len(y)}")

        if np.isnan(X).any() or np.isnan(y).any():
            errors.append("Data contains NaN values")

        if np.isinf(X).any() or np.isinf(y).any():
            errors.append("Data contains infinite values")

        return len(errors) == 0, errors

    def train_xgboost_optimized(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train XGBoost with hyperparameter optimization.

        Args:
            X_train: Training features (1000+ samples)
            y_train: Training labels
            cv_folds: Cross-validation folds

        Returns:
            Trained model and metrics
        """

        # Validate data
        valid, errors = self.validate_training_data(X_train, y_train)
        if not valid:
            logger.error(f"Data validation failed: {errors}")
            return {}

        logger.info(f"Training XGBoost with {len(X_train)} samples, {cv_folds}-fold CV")

        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        # Hyperparameter grid
        param_grid = {
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'n_estimators': [50, 100, 200],
            'subsample': [0.7, 0.9, 1.0],
            'colsample_bytree': [0.7, 0.9, 1.0]
        }

        # Base model
        base_model = xgb.XGBClassifier(
            objective='binary:logistic',
            random_state=42,
            n_jobs=-1
        )

        # Grid search
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv_folds,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )

        grid_search.fit(X_scaled, y_train)

        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_

        logger.info(f"Best CV accuracy: {grid_search.best_score_:.4f}")
        logger.info(f"Best params: {self.best_params}")

        return {
            'model': self.model,
            'best_params': self.best_params,
            'cv_score': grid_search.best_score_,
            'feature_importance': self.model.feature_importances_.tolist()
        }

    def calculate_cross_validation_metrics(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5
    ) -> Dict[str, float]:
        """Calculate cross-validation metrics."""

        if self.model is None:
            logger.warning("No model trained yet")
            return {}

        X_scaled = self.scaler.transform(X)

        scores = cross_val_score(
            self.model,
            X_scaled,
            y,
            cv=cv,
            scoring='accuracy'
        )

        return {
            'cv_mean': scores.mean(),
            'cv_std': scores.std(),
            'cv_min': scores.min(),
            'cv_max': scores.max(),
            'fold_scores': scores.tolist()
        }

    def get_model_performance(self) -> Dict[str, Any]:
        """Get trained model performance summary."""
        if self.model is None:
            return {}

        return {
            'model_type': type(self.model).__name__,
            'best_params': self.best_params,
            'ready_for_deployment': True
        }
