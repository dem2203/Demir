"""
🔧 DEMIR AI v8.0 - ENTERPRISE CONFIGURATION
Gelişmiş multi-layer AI için ekstra API key desteği ve profesyonel production doğrulama.
"""
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ========================================================================
# ENV VARS / API KEYS
# ========================================================================

ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
DEBUG_MODE = ENVIRONMENT == 'development'

VERSION = "8.0"
APP_NAME = "DEMIR AI"
FULL_NAME = f"{APP_NAME} v{VERSION} Enterprise"

ADVISORY_MODE = True  # Kesinlikle sadece analiz, trade yok

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

# Exchange main keys
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')

COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')

# Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_ENABLED = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)

# ========================================================================
# YENİ ENTEGRASYON API KEYLERİ
# ========================================================================

COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY', '')
COINMARKETCAP_API_KEY = os.getenv('CoinMarketCap_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')
GLASSNODE_API_KEY = os.getenv('GLASSNODE_API_KEY', '')
CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY', '')

# Alternative News & Sentiment APIs (v8.0)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')  # newsapi.org
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

# ========================================================================
# SYSTEM PARAMETERS (MAIN.PY İÇİN EKSİK OLANLAR EKLENДİ)
# ========================================================================

# Threading & Processing
MAX_THREADS = int(os.getenv('MAX_THREADS', '20'))
MAX_PROCESSES = int(os.getenv('MAX_PROCESSES', '4'))

# Caching
CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes default

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# ========================================================================
# TRACKED SYMBOLS - v8.0 UPDATE: PERPETUAL FUTURES ONLY
# User can dynamically add/remove symbols via dashboard
# ========================================================================

# Default symbols - PERPETUAL FUTURES (changed per user request)
# Users will manually add additional symbols via dashboard UI
DEFAULT_TRACKED_SYMBOLS = [
    'BTCUSDT.P',   # Bitcoin Perpetual Futures
    'ETHUSDT.P',   # Ethereum Perpetual Futures
    'LTCUSDT.P',   # Litecoin Perpetual Futures
]

# Runtime symbol management - loaded from database or user input
# This list will be dynamically updated when user adds/removes symbols
TRACKED_SYMBOLS = DEFAULT_TRACKED_SYMBOLS.copy()

# Symbol addition/removal functions
def add_symbol(symbol: str) -> bool:
    """
    Add a symbol to tracked list (runtime).
    
    Args:
        symbol: Symbol to add (e.g., 'BTCUSDT.P')
        
    Returns:
        bool: True if added, False if already exists
    """
    symbol = symbol.upper().strip()
    if symbol not in TRACKED_SYMBOLS:
        TRACKED_SYMBOLS.append(symbol)
        print(f"✅ Symbol added: {symbol}")
        return True
    print(f"⚠️  Symbol already tracked: {symbol}")
    return False

def remove_symbol(symbol: str) -> bool:
    """
    Remove a symbol from tracked list (runtime).
    
    Args:
        symbol: Symbol to remove
        
    Returns:
        bool: True if removed, False if not found
    """
    symbol = symbol.upper().strip()
    if symbol in TRACKED_SYMBOLS:
        TRACKED_SYMBOLS.remove(symbol)
        print(f"❌ Symbol removed: {symbol}")
        return True
    print(f"⚠️  Symbol not found: {symbol}")
    return False

def get_tracked_symbols() -> List[str]:
    """
    Get current list of tracked symbols.
    
    Returns:
        List of symbol strings
    """
    return TRACKED_SYMBOLS.copy()

def reset_symbols_to_default():
    """
    Reset tracked symbols to default list.
    """
    global TRACKED_SYMBOLS
    TRACKED_SYMBOLS = DEFAULT_TRACKED_SYMBOLS.copy()
    print(f"♻️ Symbols reset to default: {TRACKED_SYMBOLS}")

# ========================================================================
# OPPORTUNITY THRESHOLDS
# ========================================================================

OPPORTUNITY_THRESHOLDS = {
    'min_confidence': 0.75,
    'high_confidence': 0.85,
    'min_telegram_confidence': 0.80,
    'min_rr': 2.0,
    'excellent_rr_ratio': 3.0,
    'max_drawdown_pct': 15.0,
    'min_volume_24h': 10000000,
    'max_exposure_pct': 25.0,
}

# ========================================================================
# EXTRA THRESHOLDS (Opsiyonel)
# ========================================================================

ORDERBOOK_WHALE_THRESHOLD = float(os.getenv('ORDERBOOK_WHALE_THRESHOLD', '1000000'))
FLOW_STALE_LIMIT_MINUTES = int(os.getenv('FLOW_STALE_LIMIT_MINUTES', '60'))

# ========================================================================
# CONFIGURATION VALIDATION
# ========================================================================

def validate_config():
    """Validate critical configuration parameters"""
    errors = []
    
    # Critical checks
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if not BINANCE_API_KEY:
        errors.append("BINANCE_API_KEY missing")
    
    # Optional API key warnings (non-blocking)
    warnings = []
    if not COINGLASS_API_KEY:
        warnings.append("COINGLASS_API_KEY missing (some features disabled)")
    if not COINMARKETCAP_API_KEY:
        warnings.append("CoinMarketCap_API_KEY missing (some features disabled)")
    if not ALPHA_VANTAGE_API_KEY:
        warnings.append("ALPHA_VANTAGE_API_KEY missing (macro data limited)")
    if not CRYPTOPANIC_API_KEY:
        warnings.append("CRYPTOPANIC_API_KEY missing (sentiment limited)")
    
    # Show warnings
    if warnings:
        for warn in warnings:
            print(f"⚠️  {warn}")
    
    # Critical errors halt
    if errors:
        for err in errors:
            print(f"❌ {err}")
        sys.exit(1)
    
    print("✅ Config validated - Critical keys present")
    return True

# ========================================================================
# AUTO-INIT MESSAGE
# ========================================================================

print(f"[CONFIG] DEMIR AI config.py yüklendi. Version: {VERSION}, Advisory Mode: {ADVISORY_MODE}")
print(f"🥇 Default Tracked Symbols (Perpetual Futures): {DEFAULT_TRACKED_SYMBOLS}")
