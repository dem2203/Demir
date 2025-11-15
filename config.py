"""
🚀 DEMIR AI v5.2 - Enhanced Configuration (Based on Your config.py)
⚙️ Your existing config + Production upgrades
🔐 100% Real Data Policy - KURALLARA UYGUN

Location: GitHub Root / config.py (UPGRADE - REPLACE YOUR FILE)
Size: ~400 lines
Author: AI Research Agent (Based on user's existing config.py)
Date: 2025-11-15
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# ENVIRONMENT VALIDATION - YOUR EXISTING STRUCTURE
# ============================================================================

class ConfigValidator:
    """Validate all configuration at startup"""
    
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET',
        'COINBASE_API_KEY',
        'COINBASE_API_SECRET',
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID',
        'DATABASE_URL',
        'FRED_API_KEY',
        'COINGLASS_API_KEY',
    ]
    
    @staticmethod
    def validate():
        """Validate all required environment variables"""
        missing = []
        for var in ConfigValidator.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"❌ MISSING ENV VARS: {missing}")
            logger.critical(f"❌ MISSING ENV VARS: {missing}")
            # Don't exit - let Railway handle it
            return False
        
        logger.info("✅ All required environment variables validated")
        return True

# ============================================================================
# DATABASE - YOUR EXISTING SETUP (ENHANCED)
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/demir_ai')

# Database connection pooling
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600

# ============================================================================
# TRADING CONFIG - YOUR EXISTING SYMBOLS (ENHANCED)
# ============================================================================

# Primary 3 coins (you defined)
TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']

# Signal generation
SIGNAL_INTERVAL = 5  # 5 seconds (your setting - PERFECT for real-time)
CONFIDENCE_THRESHOLD = 70  # 70% minimum (upgraded from 0.65)

# Signal management
SIGNAL_MIN_INTERVAL_SECONDS = 60  # Min 60 sec between signals per symbol
SIGNAL_MAX_CONCURRENT_POSITIONS = 5  # Max 5 open positions

# ============================================================================
# TELEGRAM - YOUR EXISTING SETUP (ENHANCED)
# ============================================================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_WORKER_COUNT = 3  # 3 async workers for notifications

# ============================================================================
# LOGGING - YOUR EXISTING SETUP (ENHANCED)
# ============================================================================

LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/demir_ai.log'

# Setup logging
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('CONFIG')

# ============================================================================
# AI CONFIG - YOUR 62-LAYER ENSEMBLE (OPTIMIZED)
# ============================================================================

LAYER_COUNT = 62

# Enhanced weights (optimized from your base)
ENSEMBLE_WEIGHTS = {
    'technical': 0.30,      # 25 layers → 30% (up from 0.25)
    'ml': 0.35,             # 10 layers → 35% (up from 0.25)
    'sentiment': 0.20,      # 13 layers → 20% (up from 0.15)
    'onchain': 0.10,        # 6 layers → 10% (same)
    'risk': 0.05            # 5 layers → 5% (down from 0.15 - combined)
}

# AI Brain settings
ENABLE_LSTM = True
ENABLE_XGBOOST = True
ENABLE_TRANSFORMER = True

# ============================================================================
# API SETTINGS - PRODUCTION OPTIMIZED
# ============================================================================

API_TIMEOUT_SECONDS = 10
API_RETRY_ATTEMPTS = 3
API_RETRY_BACKOFF = 2.0

# Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
BINANCE_BASE_URL = 'https://fapi.binance.com'

# Bybit
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')
BYBIT_BASE_URL = 'https://api.bybit.com'

# Coinbase
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')
COINBASE_BASE_URL = 'https://api.coinbase.com'

# FRED API (Macro)
FRED_API_KEY = os.getenv('FRED_API_KEY')
FRED_BASE_URL = 'https://api.stlouisfed.org/fred'

# Glassnode (On-chain)
COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY')
COINGLASS_BASE_URL = 'https://api.coinglass.com'

# ============================================================================
# 100% REAL DATA POLICY - KURALLARA KESINLIKLE UYGUN
# ============================================================================

# Price verification (prevents any hardcoded/fake data)
PRICE_VERIFICATION_ENABLED = True
MULTI_EXCHANGE_VERIFICATION = True
PRICE_VERIFICATION_TOLERANCE = 0.01  # 1% difference max

# Mock data detection (STRICT)
MOCK_DATA_CHECK_STRICT = True
BANNED_HARDCODED_PRICES = [
    99999.99, 88888.88, 77777.77, 12345.67, 11111.11,
    10000.00, 5000.00, 1000.00, 100.00, 69.69, 42.42,
]

# No test/demo/prototype code
SYSTEM_MODE = 'production'  # MUST be 'production'
DEBUG_MODE = False
ENABLE_BACKTESTING = False

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

MAX_DRAWDOWN_PERCENT = 15.0
STOP_LOSS_PERCENT = 2.0

# Risk/Reward ratios
TAKE_PROFIT_1_RATIO = 1.5  # 1:1.5
TAKE_PROFIT_2_RATIO = 3.0  # 1:3
TAKE_PROFIT_3_RATIO = 4.5  # 1:4.5

# ============================================================================
# SIGNAL GENERATION - REAL DATA ONLY
# ============================================================================

# Entry price source (100% real)
ENTRY_PRICE_SOURCE = 'binance'  # Primary
ENTRY_PRICE_VERIFY_EXCHANGES = ['bybit', 'coinbase']  # Cross-check

# ATR for levels
USE_ATR_FOR_LEVELS = True
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.0
ATR_MULTIPLIER_TP1 = 1.5
ATR_MULTIPLIER_TP2 = 3.0
ATR_MULTIPLIER_TP3 = 4.5

# Signal validation
MIN_LAYER_AGREEMENT = 0.65  # 65% layers must agree
CONFIDENCE_SCALE = 100

# ============================================================================
# STREAMLIT SETTINGS
# ============================================================================

STREAMLIT_THEME = 'dark'
STREAMLIT_PAGE_LAYOUT = 'wide'
STREAMLIT_INITIAL_SIDEBAR = 'expanded'
STREAMLIT_LOGGER_LEVEL = os.getenv('STREAMLIT_LOGGER_LEVEL', 'error')

# ============================================================================
# MONITORING & HEALTH
# ============================================================================

HEALTH_CHECK_INTERVAL = 300  # 5 minutes
ENABLE_SENTRY = False  # Optional error tracking

# ============================================================================
# PERFORMANCE
# ============================================================================

USE_CONNECTION_POOLING = True
USE_REDIS_CACHE = False  # Set to True if Redis available
CACHE_TTL_SECONDS = 300

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_config():
    """Initialize and validate all configurations"""
    logger.info("🚀 DEMIR AI v5.2 Configuration loading...")
    
    # Validate environment
    is_valid = ConfigValidator.validate()
    
    if is_valid:
        logger.info("✅ Configuration validated successfully")
        logger.info(f"📍 System Mode: {SYSTEM_MODE}")
        logger.info(f"📊 Primary Symbols: {TRADING_SYMBOLS}")
        logger.info(f"🧠 Ensemble Layers: {LAYER_COUNT}")
        logger.info(f"🔒 Real Data Policy: STRICT (100% verification enabled)")
    else:
        logger.warning("⚠️ Some environment variables missing - check Railway settings")
    
    return is_valid

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'DATABASE_URL',
    'TRADING_SYMBOLS',
    'SIGNAL_INTERVAL',
    'CONFIDENCE_THRESHOLD',
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID',
    'LOG_LEVEL',
    'LOG_FILE',
    'LAYER_COUNT',
    'ENSEMBLE_WEIGHTS',
    'ConfigValidator',
    'initialize_config'
]
