# ============================================================================
# DEMIR AI - Layers Package
# ============================================================================

# EXISTING LAYERS (from advanced_layers.py)
from .advanced_layers import (
    StrategyLayer,
    FibonacciLayer,
    VWAPLayer,
    VolumeProfileLayer,
    PivotPointsLayer,
    GARCHVolatilityLayer,
    HistoricalVolatilityLayer,
    MarkovRegimeLayer,
    MonteCarloLayer,
    KellyEnhancedLayer,
    NewsSentimentLayer,
    EnhancedMacroLayer,
    EnhancedGoldLayer,
    EnhancedDominanceLayer,
    EnhancedVIXLayer,
    EnhancedRatesLayer,
    LAYERS,
)

# PHASE 3E - ML LAYERS (NEW IMPORTS)
from .lstm_neural_layer import lstm_layer
from .transformer_layer import transformer_layer
from .risk_management_layer import risk_layer
from .portfolio_optimizer_layer import portfolio_layer
from .quantum_algorithm_layer import quantum_layer
from .meta_learning_layer import meta_layer

# PHASE 3F - REAL-TIME CRYPTO LAYERS (NEW IMPORTS)
from .realtime_price_stream_layer import realtime_stream
from .telegram_alert_layer import telegram_layer
from .live_order_execution_layer import execution_layer
from .portfolio_monitoring_layer import portfolio_monitoring_layer
from .bitcoin_dominance_layer import bitcoin_dominance_layer
from .altcoin_season_layer import altcoin_season_layer
from .exchange_flow_layer import exchange_flow_layer
from .onchain_metrics_layer import onchain_metrics_layer
from .smart_contract_layer import smart_contract_layer
from .liquidity_layer import liquidity_layer
from .whale_alert_layer import whale_alert_layer
from .news_aggregator_layer import news_aggregator_layer
from .integration_engine_layer import integration_engine_layer

__all__ = [
    # Existing layers
    'StrategyLayer',
    'FibonacciLayer',
    'VWAPLayer',
    'VolumeProfileLayer',
    'PivotPointsLayer',
    'GARCHVolatilityLayer',
    'HistoricalVolatilityLayer',
    'MarkovRegimeLayer',
    'MonteCarloLayer',
    'KellyEnhancedLayer',
    'NewsSentimentLayer',
    'EnhancedMacroLayer',
    'EnhancedGoldLayer',
    'EnhancedDominanceLayer',
    'EnhancedVIXLayer',
    'EnhancedRatesLayer',
    'LAYERS',
    # Phase 3E - ML Layers
    'lstm_layer',
    'transformer_layer',
    'risk_layer',
    'portfolio_layer',
    'quantum_layer',
    'meta_layer',
    # Phase 3F - Real-time Crypto Layers
    'realtime_stream',
    'telegram_layer',
    'execution_layer',
    'portfolio_monitoring_layer',
    'bitcoin_dominance_layer',
    'altcoin_season_layer',
    'exchange_flow_layer',
    'onchain_metrics_layer',
    'smart_contract_layer',
    'liquidity_layer',
    'whale_alert_layer',
    'news_aggregator_layer',
    'integration_engine_layer',
]
