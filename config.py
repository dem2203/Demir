"""
CONFIG.PY v3 - REAL DATA CONFIG
==============================
Date: 7 Kasım 2025, 20:50 CET
Version: 3.0 - REEL API Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# EXCHANGE CONFIGS
# ============================================================================

BINANCE_CONFIG = {
    'api_key': os.getenv('BINANCE_API_KEY', ''),
    'api_secret': os.getenv('BINANCE_API_SECRET', ''),
    'use_testnet': os.getenv('BINANCE_USE_TESTNET', 'False').lower() == 'true',
    'default_pair': 'BTCUSDT',
    'default_interval': '1h',
}

# ============================================================================
# API KEYS - REEL DATA SOURCES
# ============================================================================

EXTERNAL_APIS = {
    # Alternative.me - Fear & Greed (FREE, NO KEY)
    'ALTERNATIVE_ME': {
        'endpoint': 'https://api.alternative.me/fng/?limit=1',
        'timeout': 10,
        'enabled': True
    },
    
    # CoinGecko - Bitcoin Dominance (FREE, NO KEY)
    'COINGECKO': {
        'endpoint': 'https://api.coingecko.com/api/v3/',
        'timeout': 10,
        'enabled': True,
        'api_key': os.getenv('COINGECKO_API_KEY', ''),
    },
    
    # Yahoo Finance - VIX, Treasury Yields (FREE, NO KEY)
    'YAHOO_FINANCE': {
        'timeout': 20,
        'enabled': True,
    },
    
    # Twelve Data - VIX, Premium Data (OPTIONAL)
    'TWELVE_DATA': {
        'api_key': os.getenv('TWELVE_DATA_API_KEY', ''),
        'endpoint': 'https://api.twelvedata.com/',
        'timeout': 15,
        'enabled': bool(os.getenv('TWELVE_DATA_API_KEY')),
    },
    
    # NewsAPI - News & Sentiment (OPTIONAL)
    'NEWSAPI': {
        'api_key': os.getenv('NEWSAPI_KEY', ''),
        'endpoint': 'https://newsapi.org/v2/',
        'timeout': 10,
        'enabled': bool(os.getenv('NEWSAPI_KEY')),
    },
    
    # Binance - Live Data & Funding Rates (FREE)
    'BINANCE_API': {
        'endpoint': 'https://api.binance.com',
        'endpoint_futures': 'https://fapi.binance.com',
        'timeout': 15,
        'enabled': True,
    }
}

# ============================================================================
# TELEGRAM ALERTS
# ============================================================================

TELEGRAM_CONFIG = {
    'token': os.getenv('TELEGRAM_TOKEN', ''),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'enabled': bool(os.getenv('TELEGRAM_TOKEN') and os.getenv('TELEGRAM_CHAT_ID')),
    'timeout': 10,
}

# ============================================================================
# DATABASE
# ============================================================================

DATABASE_CONFIG = {
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'path': 'phase_9/data/demir.db',
    'echo': False,  # Set to True for SQL logging
}

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

TRADING_CONFIG = {
    'default_risk_level': 0.5,  # 0.1 - 1.0
    'default_position_size': 10,  # %
    'min_confidence': 0.60,  # Min confidence to trade
    'min_score': 55,  # Min score to trade
    'max_score': 45,  # Max score (reverse) for SHORT
}

# ============================================================================
# ANALYSIS LAYERS
# ============================================================================

LAYERS_CONFIG = {
    'enabled_layers': [
        'external_data',      # Fear & Greed, Funding, BTC Dom
        'interest_rates',     # Treasury yields
        'vix',               # VIX fear index
        'strategy',          # Strategy engine
        'macro_correlation', # Macro data
        'cross_asset',       # Cross-asset correlation
        'traditional_markets', # Stock/Bond markets
        'kelly_enhanced',    # Kelly criterion
        'monte_carlo',       # Monte Carlo simulation
        'news_sentiment',    # News sentiment analysis
    ],
    'cache_timeout': 300,  # 5 minutes
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'phase_9/logs/demir.log',
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5,
}

# ============================================================================
# RENDER SPECIFIC
# ============================================================================

RENDER_CONFIG = {
    'use_render': os.getenv('RENDER', 'False').lower() == 'true',
    'timeout_multiplier': 2,  # Double timeouts on Render
    'max_retries': 3,
    'retry_delay': 3,
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    'use_real_data': True,  # Use REAL_DATA layers
    'use_telegram': TELEGRAM_CONFIG['enabled'],
    'use_database': True,
    'use_cache': True,
    'debug_mode': os.getenv('DEBUG', 'False').lower() == 'true',
}

# ============================================================================
# VALIDATE CONFIG
# ============================================================================

def validate_config():
    """Validate critical config values"""
    errors = []
    
    # Check if at least one API is enabled
    api_enabled = any(v.get('enabled', False) for v in EXTERNAL_APIS.values())
    if not api_enabled:
        errors.append("❌ No external APIs enabled!")
    
    # Warn if Telegram not configured
    if not TELEGRAM_CONFIG['enabled']:
        print("⚠️ WARNING: Telegram not configured. Alerts will be disabled.")
    
    # Warn if Binance API not configured for trading
    if not BINANCE_CONFIG['api_key']:
        print("⚠️ WARNING: Binance API not configured. Trading will be disabled.")
    
    return errors

# Run validation
config_errors = validate_config()
if config_errors:
    for error in config_errors:
        print(error)
