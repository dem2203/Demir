# advanced_ai/__init__.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 DEMIR AI v7.0 - ADVANCED AI MODULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CENTRALIZED IMPORTS FOR BACKWARD COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SIGNAL GENERATION & ORCHESTRATION
# ============================================================================

try:
    from .signal_engine_integration import SignalGroupOrchestrator
    logger.debug("✅ SignalGroupOrchestrator imported")
except ImportError as e:
    logger.warning(f"⚠️  SignalGroupOrchestrator import failed: {e}")
    SignalGroupOrchestrator = None

# ============================================================================
# ADVISOR CORE
# ============================================================================

try:
    from .advisor_core import DemirAIAdvisor, AdvisorConfig
    AdvisorCore = DemirAIAdvisor  # Alias
    logger.debug("✅ AdvisorCore imported")
except ImportError as e:
    logger.warning(f"⚠️  AdvisorCore import failed: {e}")
    DemirAIAdvisor = None
    AdvisorCore = None
    AdvisorConfig = None

# ============================================================================
# MARKET REGIME DETECTION
# ============================================================================

try:
    from .regime_detector import RegimeDetector
    MarketRegimeDetector = RegimeDetector  # Alias
    logger.debug("✅ MarketRegimeDetector imported")
except ImportError as e:
    logger.warning(f"⚠️  MarketRegimeDetector import failed: {e}")
    RegimeDetector = None
    MarketRegimeDetector = None

# ============================================================================
# OPPORTUNITY ENGINE
# ============================================================================

try:
    from .opportunity_engine import OpportunityEngine, TradePlan
    logger.debug("✅ OpportunityEngine imported")
except ImportError as e:
    logger.warning(f"⚠️  OpportunityEngine import failed: {e}")
    OpportunityEngine = None
    TradePlan = None

# ============================================================================
# OPTIONAL MODULES (Allow failures)
# ============================================================================

# Causality
try:
    from .causality_inference import CausalInference
    logger.debug("✅ CausalInference imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  CausalInference import failed: {e}")
    CausalInference = None

# LSTM Trainer
try:
    from .lstm_trainer import LSTMTrainer
    logger.debug("✅ LSTMTrainer imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  LSTMTrainer import failed: {e}")
    LSTMTrainer = None

# Layer Optimizer
try:
    from .layer_optimizer import LayerOptimizer
    logger.debug("✅ LayerOptimizer imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  LayerOptimizer import failed: {e}")
    LayerOptimizer = None

# Intelligent Layer Optimizer
try:
    from .layer_optimizer_intelligent import IntelligentLayerOptimizer
    logger.debug("✅ IntelligentLayerOptimizer imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  IntelligentLayerOptimizer import failed: {e}")
    IntelligentLayerOptimizer = None

# Market Regime Analyzer - DISABLED (Syntax error)
MarketRegimeAnalyzer = None
logger.warning("⚠️  MarketRegimeAnalyzer disabled due to syntax error in file")

# ML Training Optimizer
try:
    from .ml_training_optimizer_advanced import MLTrainingOptimizerAdvanced
    logger.debug("✅ MLTrainingOptimizerAdvanced imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  MLTrainingOptimizerAdvanced import failed: {e}")
    MLTrainingOptimizerAdvanced = None

# Deep Learning Models
try:
    from .deep_learning_models import DeepLearningModels
    logger.debug("✅ DeepLearningModels imported")
except (ImportError, SyntaxError) as e:
    logger.warning(f"⚠️  DeepLearningModels import failed: {e}")
    DeepLearningModels = None

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'SignalGroupOrchestrator',
    'AdvisorCore',
    'DemirAIAdvisor',
    'AdvisorConfig',
    'MarketRegimeDetector',
    'RegimeDetector',
    'OpportunityEngine',
    'TradePlan',
    'CausalInference',
    'LSTMTrainer',
    'LayerOptimizer',
    'IntelligentLayerOptimizer',
    'MLTrainingOptimizerAdvanced',
    'DeepLearningModels',
]

logger.info("✅ advanced_ai module initialized")
