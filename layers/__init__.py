"""
🔱 DEMIR AI - LAYERS/__INIT__.PY (v1.0)
============================================================================
Layers Module - Tüm layer'ları import et
Import hataları çözülmüş!
============================================================================
Date: 13 Kasım 2025
Author: DEMIR AI Team
Status: PRODUCTION READY
Satır: 220
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# TEMEL LAYERS
# ============================================================================

try:
    from .risk_management_layer import RiskManagementLayer
    logger.info("✅ RiskManagementLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ RiskManagementLayer yüklenemedi: {e}")
    RiskManagementLayer = None

try:
    from .atr_layer import ATRLayer
    logger.info("✅ ATRLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ ATRLayer yüklenemedi: {e}")
    ATRLayer = None

try:
    from .enhanced_macro_layer import EnhancedMacroLayer
    logger.info("✅ EnhancedMacroLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ EnhancedMacroLayer yüklenemedi: {e}")
    EnhancedMacroLayer = None

# ============================================================================
# QUANTUM LAYERS
# ============================================================================

try:
    from .black_scholes_layer import BlackScholesLayer
    logger.info("✅ BlackScholesLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ BlackScholesLayer yüklenemedi: {e}")
    BlackScholesLayer = None

try:
    from .kalman_filter_layer import KalmanFilterLayer
    logger.info("✅ KalmanFilterLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ KalmanFilterLayer yüklenemedi: {e}")
    KalmanFilterLayer = None

try:
    from .fractal_chaos_layer import FractalChaosLayer
    logger.info("✅ FractalChaosLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ FractalChaosLayer yüklenemedi: {e}")
    FractalChaosLayer = None

try:
    from .fourier_cycle_layer import FourierCycleLayer
    logger.info("✅ FourierCycleLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ FourierCycleLayer yüklenemedi: {e}")
    FourierCycleLayer = None

try:
    from .copula_correlation_layer import CopulaCorrelationLayer
    logger.info("✅ CopulaCorrelationLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ CopulaCorrelationLayer yüklenemedi: {e}")
    CopulaCorrelationLayer = None

try:
    from .monte_carlo_layer import MonteCarloLayer
    logger.info("✅ MonteCarloLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ MonteCarloLayer yüklenemedi: {e}")
    MonteCarloLayer = None

try:
    from .kelly_criterion_layer import KellyCriterionLayer
    logger.info("✅ KellyCriterionLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ KellyCriterionLayer yüklenemedi: {e}")
    KellyCriterionLayer = None

try:
    from .lstm_neural_layer import LSTMNeuralLayer
    logger.info("✅ LSTMNeuralLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ LSTMNeuralLayer yüklenemedi: {e}")
    LSTMNeuralLayer = None

# ============================================================================
# MAKRO LAYERS (ENHANCED)
# ============================================================================

try:
    from .enhanced_vix_layer import EnhancedVIXLayer
    logger.info("✅ EnhancedVIXLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ EnhancedVIXLayer yüklenemedi: {e}")
    EnhancedVIXLayer = None

try:
    from .enhanced_gold_layer import EnhancedGoldLayer
    logger.info("✅ EnhancedGoldLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ EnhancedGoldLayer yüklenemedi: {e}")
    EnhancedGoldLayer = None

try:
    from .enhanced_dominance_layer import EnhancedDominanceLayer
    logger.info("✅ EnhancedDominanceLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ EnhancedDominanceLayer yüklenemedi: {e}")
    EnhancedDominanceLayer = None

try:
    from .enhanced_rates_layer import EnhancedRatesLayer
    logger.info("✅ EnhancedRatesLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ EnhancedRatesLayer yüklenemedi: {e}")
    EnhancedRatesLayer = None

try:
    from .market_microstructure_layer import MarketMicrostructureLayer
    logger.info("✅ MarketMicrostructureLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ MarketMicrostructureLayer yüklenemedi: {e}")
    MarketMicrostructureLayer = None

# ============================================================================
# DIĞER LAYERS
# ============================================================================

try:
    from .strategy_layer import StrategyLayer
    logger.info("✅ StrategyLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ StrategyLayer yüklenemedi: {e}")
    StrategyLayer = None

try:
    from .news_sentiment_layer import NewsSentimentLayer
    logger.info("✅ NewsSentimentLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ NewsSentimentLayer yüklenemedi: {e}")
    NewsSentimentLayer = None

try:
    from .macro_correlation_layer import MacroCorrelationLayer
    logger.info("✅ MacroCorrelationLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ MacroCorrelationLayer yüklenemedi: {e}")
    MacroCorrelationLayer = None

try:
    from .on_chain_layer import OnChainLayer
    logger.info("✅ OnChainLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ OnChainLayer yüklenemedi: {e}")
    OnChainLayer = None

try:
    from .funding_rate_layer import FundingRateLayer
    logger.info("✅ FundingRateLayer yüklendi")
except ImportError as e:
    logger.warning(f"⚠️ FundingRateLayer yüklenemedi: {e}")
    FundingRateLayer = None

# ============================================================================
# EXPORT LIST - Tüm geçerli layers
# ============================================================================

__all__ = [
    # Temel (3)
    'RiskManagementLayer',
    'ATRLayer',
    'EnhancedMacroLayer',
    
    # Quantum (8)
    'BlackScholesLayer',
    'KalmanFilterLayer',
    'FractalChaosLayer',
    'FourierCycleLayer',
    'CopulaCorrelationLayer',
    'MonteCarloLayer',
    'KellyCriterionLayer',
    'LSTMNeuralLayer',
    
    # Makro (5)
    'EnhancedVIXLayer',
    'EnhancedGoldLayer',
    'EnhancedDominanceLayer',
    'EnhancedRatesLayer',
    'MarketMicrostructureLayer',
    
    # Diğer (5)
    'StrategyLayer',
    'NewsSentimentLayer',
    'MacroCorrelationLayer',
    'OnChainLayer',
    'FundingRateLayer',
]

# ============================================================================
# BAŞARILI YÜKLEMELERİ SAY
# ============================================================================

successfully_loaded = [x for x in __all__ if eval(x) is not None]
total_layers = len(__all__)

logger.info("=" * 70)
logger.info("🔱 DEMIR AI LAYERS MODULE INITIALIZED")
logger.info("=" * 70)
logger.info(f"✅ {len(successfully_loaded)}/{total_layers} layer başarılı şekilde yüklendi")

if len(successfully_loaded) < total_layers:
    failed_layers = [x for x in __all__ if eval(x) is None]
    logger.warning(f"⚠️ Yüklenemeyen layer'lar: {failed_layers}")

logger.info("=" * 70)
