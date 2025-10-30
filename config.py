"""
DEMIR - Configuration
API Keys, Parameters, Settings
"""

import os
from typing import Dict, Any

# ============================================
# API KEYS (Environment Variables)
# ============================================

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ============================================
# TRADING PARAMETERS
# ============================================

TRADING_CONFIG = {
    # Risk yönetimi
    'max_position_size': 0.1,  # Bakiyenin %10'u
    'stop_loss_pct': 2.0,      # %2 stop loss
    'take_profit_pct': 5.0,    # %5 take profit
    
    # Sinyal parametreleri
    'min_confidence': 60,      # Minimum güven skoru (0-100)
    'signal_cooldown': 3600,   # Sinyaller arası bekleme (saniye)
    
    # Timeframes
    'default_timeframe': '1h',
    'supported_timeframes': ['15m', '1h', '4h', '1d'],
    
    # Symbols
    'default_symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    'max_concurrent_positions': 3
}

# ============================================
# TECHNICAL ANALYSIS PARAMETERS
# ============================================

TA_CONFIG = {
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    
    'bollinger_period': 20,
    'bollinger_std': 2,
    
    'ema_periods': [9, 21, 50, 200],
    
    'volume_profile_bins': 20,
    'fibonacci_lookback': 100
}

# ============================================
# DATABASE SETTINGS
# ============================================

DB_CONFIG = {
    'type': 'sqlite',  # sqlite veya postgresql
    'sqlite_path': 'demir_trading.db',
    
    # PostgreSQL için (production)
    'postgres_host': os.getenv('DB_HOST', 'localhost'),
    'postgres_port': os.getenv('DB_PORT', '5432'),
    'postgres_db': os.getenv('DB_NAME', 'demir_db'),
    'postgres_user': os.getenv('DB_USER', 'postgres'),
    'postgres_password': os.getenv('DB_PASSWORD', '')
}

# ============================================
# LOGGING
# ============================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'demir.log'
}

# ============================================
# STREAMLIT UI SETTINGS
# ============================================

UI_CONFIG = {
    'page_title': 'DEMIR Trading Bot',
    'page_icon': '🤖',
    'layout': 'wide',
    'refresh_interval': 5,  # saniye
    'chart_height': 500
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_config(section: str = None) -> Dict[str, Any]:
    """Konfigürasyon verilerini döndür"""
    configs = {
        'trading': TRADING_CONFIG,
        'ta': TA_CONFIG,
        'db': DB_CONFIG,
        'logging': LOGGING_CONFIG,
        'ui': UI_CONFIG
    }
    
    if section:
        return configs.get(section, {})
    return configs


def validate_config() -> bool:
    """Zorunlu ayarları kontrol et"""
    # Kritik ayarlar kontrolü
    required_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            print(f"Uyarı: {key} environment variable tanımlanmamış")
    
    return True
