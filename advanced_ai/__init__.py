# advanced_ai/__init__.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 DEMIR AI v7.0 - ADVANCED AI MODULE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CENTRALIZED IMPORTS FOR BACKWARD COMPATIBILITY

All class names and imports are managed here to prevent name mismatches
between main.py expectations and actual class definitions.

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
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
# ADVISOR CORE (Main orchestrator)
# ============================================================================

try:
    from .advisor_core import DemirAIAdvisor, AdvisorCore, AdvisorConfig
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
    from .regime_detector import RegimeDetector, MarketRegimeDetector
    logger.debug("✅ MarketRegimeDetector imported")
except ImportError as e:
    logger.warning(f"⚠️  MarketRegimeDetector import failed: {e}")
    RegimeDetector = None
    MarketRegimeDetector = None

# ============================================================================
# CAUSALITY & INFERENCE
# ============================================================================

try:
    from .causality_inference import CausalInference
    logger.debug("✅ CausalInference imported")
except ImportError as e:
    logger.warning(f"⚠️  CausalInference import failed: {e}")
    CausalInference = None

# ============================================================================
# LSTM TRAINING
# ============================================================================

try:
    from .lstm_trainer import LSTMTrainer
    logger.debug("✅ LSTMTrainer imported")
except ImportError as e:
    logger.warning(f"⚠️  LSTMTrainer import failed: {e}")
    LSTMTrainer = None

# ============================================================================
# LAYER OPTIMIZATION
# ============================================================================

try:
    from .layer_optimizer import LayerOptimizer
    logger.debug("✅ LayerOptimizer imported")
except ImportError as e:
    logger.warning(f"⚠️  LayerOptimizer import failed: {e}")
    LayerOptimizer = None

try:
    from .layer_optimizer_intelligent import IntelligentLayerOptimizer
    logger.debug("✅ IntelligentLayerOptimizer imported")
except ImportError as e:
    logger.warning(f"⚠️  IntelligentLayerOptimizer import failed: {e}")
    IntelligentLayerOptimizer = None

# ============================================================================
# MARKET REGIME ANALYSIS
# ============================================================================

try:
    from .market_regime_analysis import MarketRegimeAnalyzer
    logger.debug("✅ MarketRegimeAnalyzer imported")
except ImportError as e:
    logger.warning(f"⚠️  MarketRegimeAnalyzer import failed: {e}")
    MarketRegimeAnalyzer = None

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
# ADVISOR CORE
# ============================================================================

try:
    from .advisor_core import DemirAIAdvisor as AdvisorCore_Class
    AdvisorCore = AdvisorCore_Class
    logger.debug("✅ AdvisorCore aliased")
except ImportError as e:
    logger.warning(f"⚠️  AdvisorCore alias failed: {e}")

# ============================================================================
# ML TRAINING OPTIMIZER
# ============================================================================

try:
    from .ml_training_optimizer_advanced import MLTrainingOptimizerAdvanced
    logger.debug("✅ MLTrainingOptimizerAdvanced imported")
except ImportError as e:
    logger.warning(f"⚠️  MLTrainingOptimizerAdvanced import failed: {e}")
    MLTrainingOptimizerAdvanced = None

# ============================================================================
# DEEP LEARNING MODELS
# ============================================================================

try:
    from .deep_learning_models import DeepLearningModels
    logger.debug("✅ DeepLearningModels imported")
except ImportError as e:
    logger.warning(f"⚠️  DeepLearningModels import failed: {e}")
    DeepLearningModels = None

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Signal generation
    'SignalGroupOrchestrator',
    
    # Advisor core
    'AdvisorCore',
    'DemirAIAdvisor',
    'AdvisorConfig',
    
    # Market regime
    'MarketRegimeDetector',
    'RegimeDetector',
    'MarketRegimeAnalyzer',
    
    # Causality & inference
    'CausalInference',
    
    # Training & optimization
    'LSTMTrainer',
    'LayerOptimizer',
    'IntelligentLayerOptimizer',
    'MLTrainingOptimizerAdvanced',
    
    # Opportunities
    'OpportunityEngine',
    'TradePlan',
    
    # Deep learning
    'DeepLearningModels',
]

logger.info("✅ advanced_ai module initialized with centralized imports")
