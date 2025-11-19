# config.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 DEMIR AI v7.0 - ENTERPRISE CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Central configuration management
- Environment variables
- API credentials
- System parameters
- Trading settings
- Thresholds and limits

SECURITY: All sensitive data from environment variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# ENVIRONMENT
# ============================================================================

ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
DEBUG_MODE = ENVIRONMENT == 'development'

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================

VERSION = "7.0"
APP_NAME = "DEMIR AI"
FULL_NAME = f"{APP_NAME} v{VERSION} Enterprise"

# ============================================================================
# ADVISORY MODE (CRITICAL)
# ============================================================================

# Advisory mode - Bot NEVER executes trades automatically
# Only provides analysis and recommendations
ADVISORY_MODE = True  # ⚠️ ALWAYS TRUE - Safety first

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("Please set DATABASE_URL in your environment or .env file")
    sys.exit(1)

# Fix Railway PostgreSQL URL format (postgres:// → postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Database pool settings
DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', '5'))
DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', '20'))
DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))

# ============================================================================
# REDIS CONFIGURATION (Optional)
# ============================================================================

REDIS_URL = os.getenv('REDIS_URL', None)
REDIS_ENABLED = bool(REDIS_URL)

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60        # 1 minute
CACHE_TTL_MEDIUM = 300      # 5 minutes
CACHE_TTL_LONG = 3600       # 1 hour

# ============================================================================
# BINANCE API CREDENTIALS
# ============================================================================

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

if not BINANCE_API_KEY or not BINANCE_API_SECRET:
    print("⚠️  WARNING: Binance API credentials not configured")
    print("   Some features will be limited to public endpoints only")

BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_WS_URL = "wss://stream.binance.com:9443"
BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'false').lower() == 'true'

if BINANCE_TESTNET:
    BINANCE_BASE_URL = "https://testnet.binance.vision"
    BINANCE_WS_URL = "wss://testnet.binance.vision/ws"
    print("⚠️  WARNING: Using Binance TESTNET")

# ============================================================================
# BYBIT API CREDENTIALS
# ============================================================================

BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')

BYBIT_BASE_URL = "https://api.bybit.com"
BYBIT_TESTNET = os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'

if BYBIT_TESTNET:
    BYBIT_BASE_URL = "https://api-testnet.bybit.com"

# ============================================================================
# COINBASE API CREDENTIALS
# ============================================================================

COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')

COINBASE_BASE_URL = "https://api.pro.coinbase.com"

# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

TELEGRAM_ENABLED = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)

if not TELEGRAM_ENABLED:
    print("⚠️  WARNING: Telegram notifications not configured")

# ============================================================================
# TRACKED SYMBOLS (Default)
# ============================================================================

# Primary symbols - major cryptocurrencies
DEFAULT_TRACKED_SYMBOLS = [
    'BTCUSDT',   # Bitcoin
    'ETHUSDT',   # Ethereum
    'BNBUSDT',   # Binance Coin
    'SOLUSDT',   # Solana
    'XRPUSDT',   # Ripple
    'ADAUSDT',   # Cardano
    'DOGEUSDT',  # Dogecoin
    'DOTUSDT',   # Polkadot
    'MATICUSDT', # Polygon
    'AVAXUSDT',  # Avalanche
]

# Extended symbols (can be enabled)
EXTENDED_TRACKED_SYMBOLS = [
    'LINKUSDT',  # Chainlink
    'ATOMUSDT',  # Cosmos
    'LTCUSDT',   # Litecoin
    'UNIUSDT',   # Uniswap
    'ETCUSDT',   # Ethereum Classic
    'XLMUSDT',   # Stellar
    'ALGOUSDT',  # Algorand
    'VETUSDT',   # VeChain
    'ICPUSDT',   # Internet Computer
    'FILUSDT',   # Filecoin
]

# Use extended list if enabled
USE_EXTENDED_SYMBOLS = os.getenv('USE_EXTENDED_SYMBOLS', 'false').lower() == 'true'

if USE_EXTENDED_SYMBOLS:
    DEFAULT_TRACKED_SYMBOLS += EXTENDED_TRACKED_SYMBOLS

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Position sizing (as percentage of capital)
DEFAULT_POSITION_SIZE_PCT = float(os.getenv('POSITION_SIZE_PCT', '2.0'))  # 2% per trade
MAX_POSITION_SIZE_PCT = float(os.getenv('MAX_POSITION_SIZE_PCT', '10.0'))  # 10% max

# Risk management
DEFAULT_STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', '2.0'))  # 2% stop loss
DEFAULT_TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', '4.0'))  # 4% take profit

# Minimum risk/reward ratio
MIN_RISK_REWARD_RATIO = float(os.getenv('MIN_RR_RATIO', '2.0'))  # 1:2 minimum

# ============================================================================
# SIGNAL GENERATION THRESHOLDS
# ============================================================================

# Minimum confidence for signal generation
MIN_SIGNAL_CONFIDENCE = float(os.getenv('MIN_SIGNAL_CONFIDENCE', '0.60'))  # 60%

# Minimum ensemble score (average of all groups)
MIN_ENSEMBLE_SCORE = float(os.getenv('MIN_ENSEMBLE_SCORE', '0.55'))  # 55%

# Minimum layer agreement (how many layers must agree)
MIN_LAYER_AGREEMENT = int(os.getenv('MIN_LAYER_AGREEMENT', '3'))  # At least 3 layers

# Signal generation interval (seconds)
SIGNAL_GENERATION_INTERVAL = int(os.getenv('SIGNAL_INTERVAL', '300'))  # 5 minutes

# ============================================================================
# OPPORTUNITY THRESHOLDS
# ============================================================================

OPPORTUNITY_THRESHOLDS = {
    # Confidence thresholds
    'min_confidence': float(os.getenv('OPP_MIN_CONFIDENCE', '0.75')),  # 75%
    'high_confidence': float(os.getenv('OPP_HIGH_CONFIDENCE', '0.85')),  # 85%
    
    # Risk/Reward thresholds
    'min_rr_ratio': float(os.getenv('OPP_MIN_RR', '2.0')),  # 1:2
    'excellent_rr_ratio': float(os.getenv('OPP_EXCELLENT_RR', '3.0')),  # 1:3
    
    # Maximum drawdown allowed
    'max_drawdown_pct': float(os.getenv('OPP_MAX_DRAWDOWN', '15.0')),  # 15%
    
    # Minimum trading volume (USDT)
    'min_volume_24h': float(os.getenv('OPP_MIN_VOLUME', '10000000')),  # 10M USDT
    
    # Maximum position exposure
    'max_exposure_pct': float(os.getenv('OPP_MAX_EXPOSURE', '25.0')),  # 25%
}

# ============================================================================
# AI MODEL PARAMETERS
# ============================================================================

# LSTM parameters
LSTM_PARAMS = {
    'sequence_length': int(os.getenv('LSTM_SEQUENCE_LENGTH', '60')),
    'units': int(os.getenv('LSTM_UNITS', '128')),
    'dropout': float(os.getenv('LSTM_DROPOUT', '0.2')),
    'epochs': int(os.getenv('LSTM_EPOCHS', '50')),
    'batch_size': int(os.getenv('LSTM_BATCH_SIZE', '32'))
}

# XGBoost parameters
XGBOOST_PARAMS = {
    'n_estimators': int(os.getenv('XGB_N_ESTIMATORS', '100')),
    'max_depth': int(os.getenv('XGB_MAX_DEPTH', '5')),
    'learning_rate': float(os.getenv('XGB_LEARNING_RATE', '0.1')),
    'subsample': float(os.getenv('XGB_SUBSAMPLE', '0.8'))
}

# Random Forest parameters
RF_PARAMS = {
    'n_estimators': int(os.getenv('RF_N_ESTIMATORS', '100')),
    'max_depth': int(os.getenv('RF_MAX_DEPTH', '10')),
    'min_samples_split': int(os.getenv('RF_MIN_SAMPLES_SPLIT', '5')),
    'min_samples_leaf': int(os.getenv('RF_MIN_SAMPLES_LEAF', '2'))
}

# ============================================================================
# TECHNICAL INDICATORS PARAMETERS
# ============================================================================

INDICATOR_PARAMS = {
    # RSI
    'rsi_period': int(os.getenv('RSI_PERIOD', '14')),
    'rsi_overbought': float(os.getenv('RSI_OVERBOUGHT', '70')),
    'rsi_oversold': float(os.getenv('RSI_OVERSOLD', '30')),
    
    # MACD
    'macd_fast': int(os.getenv('MACD_FAST', '12')),
    'macd_slow': int(os.getenv('MACD_SLOW', '26')),
    'macd_signal': int(os.getenv('MACD_SIGNAL', '9')),
    
    # Bollinger Bands
    'bb_period': int(os.getenv('BB_PERIOD', '20')),
    'bb_std': float(os.getenv('BB_STD', '2.0')),
    
    # Moving Averages
    'ma_fast': int(os.getenv('MA_FAST', '50')),
    'ma_slow': int(os.getenv('MA_SLOW', '200')),
    
    # ATR
    'atr_period': int(os.getenv('ATR_PERIOD', '14')),
    
    # Stochastic
    'stoch_k': int(os.getenv('STOCH_K', '14')),
    'stoch_d': int(os.getenv('STOCH_D', '3')),
}

# ============================================================================
# LAYER WEIGHTS (50+ Layers)
# ============================================================================

LAYER_WEIGHTS = {
    # Technical Analysis Group (30% weight)
    'technical': {
        'RSI': 0.10,
        'MACD': 0.10,
        'BollingerBands': 0.08,
        'MovingAverages': 0.08,
        'Stochastic': 0.07,
        'ATR': 0.06,
        'ADX': 0.07,
        'CCI': 0.06,
        'Ichimoku': 0.06,
        'FibonacciRetracements': 0.07,
        'CandlestickPatterns': 0.08,
        'HarmonicPatterns': 0.08,
        'VolumeProfile': 0.09,
    },
    
    # Sentiment Analysis Group (20% weight)
    'sentiment': {
        'NewsSentiment': 0.25,
        'FearGreedIndex': 0.20,
        'TwitterSentiment': 0.15,
        'RedditSentiment': 0.10,
        'SocialVolume': 0.15,
        'GoogleTrends': 0.15,
    },
    
    # Machine Learning Group (25% weight)
    'ml': {
        'LSTM': 0.20,
        'XGBoost': 0.18,
        'RandomForest': 0.15,
        'GradientBoosting': 0.15,
        'NeuralNetwork': 0.17,
        'SVM': 0.08,
        'AdaBoost': 0.07,
    },
    
    # On-Chain Analysis Group (15% weight)
    'onchain': {
        'WhaleActivity': 0.20,
        'ExchangeFlows': 0.20,
        'NetworkValue': 0.15,
        'ActiveAddresses': 0.15,
        'TransactionVolume': 0.15,
        'MinerRevenue': 0.15,
    },
    
    # Macro & Risk Group (10% weight)
    'macro_risk': {
        'BTCCorrelation': 0.15,
        'VIXIndex': 0.15,
        'DXYIndex': 0.15,
        'SP500Correlation': 0.15,
        'FundingRates': 0.20,
        'LongShortRatio': 0.20,
    }
}

# ============================================================================
# MULTI-TIMEFRAME SETTINGS
# ============================================================================

TIMEFRAMES = {
    '1m': {'weight': 0.05, 'enabled': False},   # Disabled by default (too noisy)
    '5m': {'weight': 0.10, 'enabled': True},
    '15m': {'weight': 0.15, 'enabled': True},
    '1h': {'weight': 0.25, 'enabled': True},
    '4h': {'weight': 0.25, 'enabled': True},
    '1d': {'weight': 0.20, 'enabled': True},
}

# ============================================================================
# API RATE LIMITS
# ============================================================================

RATE_LIMITS = {
    'binance': {
        'requests_per_minute': 1200,
        'weight_per_minute': 6000,
        'orders_per_second': 10,
        'orders_per_day': 200000,
    },
    'bybit': {
        'requests_per_minute': 600,
    },
    'coinbase': {
        'requests_per_second': 10,
    }
}

# ============================================================================
# WEBSOCKET SETTINGS
# ============================================================================

WS_PING_INTERVAL = 30  # seconds
WS_PONG_TIMEOUT = 10   # seconds
WS_RECONNECT_DELAY = 5  # seconds
WS_MAX_RECONNECT_ATTEMPTS = 10

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 10
LOG_ROTATION_INTERVAL = 'midnight'
LOG_RETENTION_DAYS = 30

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

# Thread pool sizes
MAX_WORKERS_DATA_FETCH = int(os.getenv('MAX_WORKERS_FETCH', '10'))
MAX_WORKERS_SIGNAL_GEN = int(os.getenv('MAX_WORKERS_SIGNAL', '5'))

# Timeouts (seconds)
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
DATABASE_TIMEOUT = int(os.getenv('DB_TIMEOUT', '30'))

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv('CIRCUIT_THRESHOLD', '5'))
CIRCUIT_BREAKER_TIMEOUT = int(os.getenv('CIRCUIT_TIMEOUT', '60'))

# ============================================================================
# BACKTEST SETTINGS
# ============================================================================

BACKTEST_INITIAL_CAPITAL = float(os.getenv('BACKTEST_CAPITAL', '10000'))  # $10,000
BACKTEST_COMMISSION = float(os.getenv('BACKTEST_COMMISSION', '0.001'))  # 0.1%
BACKTEST_SLIPPAGE = float(os.getenv('BACKTEST_SLIPPAGE', '0.0005'))  # 0.05%

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'demir-ai-ultra-secret-2025-change-in-production')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour

# API rate limiting
API_RATE_LIMIT_PER_HOUR = int(os.getenv('API_RATE_HOUR', '200'))
API_RATE_LIMIT_PER_MINUTE = int(os.getenv('API_RATE_MINUTE', '50'))

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration parameters"""
    errors = []
    warnings = []
    
    # Critical validations
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if not BINANCE_API_KEY and not BINANCE_API_SECRET:
        warnings.append("Binance API credentials not configured - limited functionality")
    
    if not TELEGRAM_ENABLED:
        warnings.append("Telegram notifications disabled")
    
    if MIN_RISK_REWARD_RATIO < 1.0:
        errors.append(f"MIN_RISK_REWARD_RATIO must be >= 1.0 (current: {MIN_RISK_REWARD_RATIO})")
    
    if MIN_SIGNAL_CONFIDENCE < 0.5 or MIN_SIGNAL_CONFIDENCE > 1.0:
        errors.append(f"MIN_SIGNAL_CONFIDENCE must be between 0.5 and 1.0 (current: {MIN_SIGNAL_CONFIDENCE})")
    
    # Print errors
    if errors:
        print("\n❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    # Print warnings
    if warnings:
        print("\n⚠️  CONFIGURATION WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("✅ Configuration validated successfully")
    return True

# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================

def print_config_summary():
    """Print configuration summary"""
    print("\n" + "="*80)
    print("📋 CONFIGURATION SUMMARY")
    print("="*80)
    print(f"Version:              {FULL_NAME}")
    print(f"Environment:          {ENVIRONMENT.upper()}")
    print(f"Advisory Mode:        {'ENABLED ✅' if ADVISORY_MODE else 'DISABLED ⚠️'}")
    print(f"Database:             {'Connected ✅' if DATABASE_URL else 'Not configured ❌'}")
    print(f"Redis Cache:          {'Enabled ✅' if REDIS_ENABLED else 'Disabled'}")
    print(f"Telegram:             {'Enabled ✅' if TELEGRAM_ENABLED else 'Disabled'}")
    print(f"Tracked Symbols:      {len(DEFAULT_TRACKED_SYMBOLS)} pairs")
    print(f"Min Confidence:       {MIN_SIGNAL_CONFIDENCE*100:.0f}%")
    print(f"Min R:R Ratio:        1:{MIN_RISK_REWARD_RATIO:.1f}")
    print(f"Signal Interval:      {SIGNAL_GENERATION_INTERVAL}s")
    print("="*80 + "\n")

# ============================================================================
# AUTO-VALIDATE ON IMPORT
# ============================================================================

if __name__ != "__main__":
    validate_config()

# ============================================================================
# EXPORT SUMMARY
# ============================================================================

__all__ = [
    # Environment
    'ENVIRONMENT',
    'DEBUG_MODE',
    'VERSION',
    'APP_NAME',
    'FULL_NAME',
    
    # Core settings
    'ADVISORY_MODE',
    'DATABASE_URL',
    'REDIS_URL',
    
    # API credentials
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'BYBIT_API_KEY',
    'BYBIT_API_SECRET',
    'COINBASE_API_KEY',
    'COINBASE_API_SECRET',
    
    # Telegram
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID',
    'TELEGRAM_ENABLED',
    
    # Trading
    'DEFAULT_TRACKED_SYMBOLS',
    'DEFAULT_POSITION_SIZE_PCT',
    'MAX_POSITION_SIZE_PCT',
    'MIN_RISK_REWARD_RATIO',
    
    # Thresholds
    'MIN_SIGNAL_CONFIDENCE',
    'MIN_ENSEMBLE_SCORE',
    'MIN_LAYER_AGREEMENT',
    'OPPORTUNITY_THRESHOLDS',
    
    # Parameters
    'INDICATOR_PARAMS',
    'LAYER_WEIGHTS',
    'TIMEFRAMES',
    'LSTM_PARAMS',
    'XGBOOST_PARAMS',
    'RF_PARAMS',
    
    # Functions
    'validate_config',
    'print_config_summary',
]
