```python
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from scipy.stats import gaussian_kde
import logging

logger = logging.getLogger(__name__)

class AdvancedRegimeDetector:
    """
    Professional market regime detection using GMM
    Multi-dimensional analysis of market states
    """
    
    def __init__(self, n_regimes: int = 5):
        self.n_regimes = n_regimes
        self.gmm = None
        self.pca = None
        self.regime_names = [
            'EXTREME_BULL',
            'BULL',
            'NEUTRAL',
            'BEAR',
            'EXTREME_BEAR'
        ]
    
    def fit(self, market_data: np.ndarray):
        """Fit GMM to market data"""
        # Feature engineering
        features = self._extract_advanced_features(market_data)
        
        # Dimensionality reduction
        self.pca = PCA(n_components=min(3, features.shape[1]))
        features_reduced = self.pca.fit_transform(features)
        
        # Fit Gaussian Mixture Model
        self.gmm = GaussianMixture(
            n_components=self.n_regimes,
            covariance_type='full',
            max_iter=200
        )
        self.gmm.fit(features_reduced)
        
        logger.info(f"✅ Fitted {self.n_regimes} market regimes")
    
    def _extract_advanced_features(self, data: np.ndarray) -> np.ndarray:
        """Extract professional-grade features"""
        features = []
        
        # Volatility features
        returns = np.diff(data) / data[:-1]
        rolling_vol = pd.Series(returns).rolling(20).std()
        features.append(rolling_vol.values)
        
        # Skewness and Kurtosis
        rolling_skew = pd.Series(returns).rolling(20).skew()
        rolling_kurtosis = pd.Series(returns).rolling(20).kurt()
        features.append(rolling_skew.values[1:])
        features.append(rolling_kurtosis.values[1:])
        
        # Autocorrelation
        acf_values = np.array([np.corrcoef(returns[:-i], returns[i:])[0, 1] 
                              for i in range(1, 6)])
        features.append(np.tile(acf_values, (len(data)-1, 1))[:, 0])
        
        return np.column_stack(features)
    
    def predict_regime(self, market_data: np.ndarray) -> dict:
        """Predict current market regime"""
        features = self._extract_advanced_features(market_data[-100:])
        features_reduced = self.pca.transform(features[-1:])
        
        probabilities = self.gmm.predict_proba(features_reduced)[0]
        regime_idx = np.argmax(probabilities)
        
        return {
            'regime': self.regime_names[regime_idx],
            'probability': float(probabilities[regime_idx]),
            'all_probabilities': {
                self.regime_names[i]: float(p) 
                for i, p in enumerate(probabilities)
            }
        }

class HiddenMarkovModelTrading:
    """
    HMM for market sequence modeling
    Professional implementation for state transitions
    """
    
    def __init__(self, n_hidden_states: int = 5):
        from hmmlearn.hmm import GaussianHMM
        self.hmm = GaussianHMM(
            n_components=n_hidden_states,
            covariance_type='full',
            n_iter=1000
        )
    
    def fit(self, returns: np.ndarray):
        """Fit HMM to returns"""
        self.hmm.fit(returns.reshape(-1, 1))
        logger.info("✅ HMM fitted")
    
    def get_hidden_states(self, returns: np.ndarray) -> np.ndarray:
        """Get hidden states for returns"""
        return self.hmm.predict(returns.reshape(-1, 1))
