# utils/__init__.py
# PHASE 8 COMPLETE - All utilities integrated

from .market_regime_analyzer import get_regime_weights, detect_market_regime
from .layer_performance_cache import get_performance_weights, record_analysis
from .meta_learner_nn import get_meta_learner_prediction, NeuralMetaLearner
from .cross_layer_analyzer import analyze_cross_layer_correlations
from .streaming_cache import execute_layers_async, get_cache_stats
from .backtesting_framework import run_full_backtest, PerformanceMetrics, BacktestReport

__all__ = [
    # 8.1: Market Regime & Performance
    'get_regime_weights',
    'detect_market_regime',
    'get_performance_weights',
    'record_analysis',
    
    # 8.2: Neural Meta-Learner
    'get_meta_learner_prediction',
    'NeuralMetaLearner',
    
    # 8.3: Cross-Layer Analysis
    'analyze_cross_layer_correlations',
    
    # 8.4: Streaming & Optimization
    'execute_layers_async',
    'get_cache_stats',
    
    # 8.5: Backtesting Framework
    'run_full_backtest',
    'PerformanceMetrics',
    'BacktestReport',
]

__version__ = '8.0.0'
__phase__ = 'Phase 8 Complete'
