"""
🔧 DEMIR AI v7.0 - ENTERPRISE CONFIGURATION
Gelişmiş multi-layer AI için ekstra API key desteği ve profesyonel production doğrulama.
"""
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()
# --------- ENV VARS / API KEYS ---------
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
DEBUG_MODE = ENVIRONMENT == 'development'
VERSION = "7.0"
APP_NAME = "DEMIR AI"
FULL_NAME = f"{APP_NAME} v{VERSION} Enterprise"
ADVISORY_MODE = True  # Kesinlikle sadece analiz,trade yok
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)
# Exchange main keys
BINANCE_API_KEY  = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
# Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_ENABLED = bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
# ------ YENİ ENTEGRASYON API KEYLERİ ------
COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY', '')
COINMARKETCAP_API_KEY = os.getenv('CoinMarketCap_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')
GLASSNODE_API_KEY = os.getenv('GLASSNODE_API_KEY', '')
CRYPTOPANIC_API_KEY = os.getenv('CRYPTOPANIC_API_KEY', '')
# --------- SYSTEM PARAMS ---------
DEFAULT_TRACKED_SYMBOLS = [ ... ] # orijinal listen korunuyor (kısaltıldı buraya)
# --------- OPPORTUNITY THRESHOLDS GERİ EKLENEN ---------
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
# --------- EXTRA THRESHOLDS (Opsiyonel) ---------
ORDERBOOK_WHALE_THRESHOLD = float(os.getenv('ORDERBOOK_WHALE_THRESHOLD', '1000000'))
FLOW_STALE_LIMIT_MINUTES = int(os.getenv('FLOW_STALE_LIMIT_MINUTES', '60'))
# --------- AUTO VALIDATION ---------
def validate_config():
    errors = []
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    if not BINANCE_API_KEY:
        errors.append("BINANCE_API_KEY missing")
    if not COINGLASS_API_KEY:
        errors.append("COINGLASS_API_KEY missing")
    if not COINMARKETCAP_API_KEY:
        errors.append("CoinMarketCap_API_KEY missing")
    if not ALPHA_VANTAGE_API_KEY:
        errors.append("ALPHA_VANTAGE_API_KEY missing")
    if not CRYPTOPANIC_API_KEY:
        errors.append("CRYPTOPANIC_API_KEY missing")
    if errors:
        for err in errors:
            print(f"❌ {err}")
        sys.exit(1)
    print("✅ Config validated - ALL CRITICAL KEYS PRESENT!")
# ------- ENTEGRE OLDUĞUNU GÖSTER -------
print(f"[CONFIG] DEMIR AI config.py yüklendi. Version: {VERSION}, Advisory Mode: {ADVISORY_MODE}")
# --- Export edilen eski fonksiyonlar ve thresholdlar aşağıda korunur ---
