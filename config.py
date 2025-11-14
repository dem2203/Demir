"""
DEMIR AI v5.0 - Configuration
100% Real Data Policy - No Mock, No Fallback
"""
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE
DATABASE_URL = os.getenv('DATABASE_URL', '')
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set in Railway variables!")

# REAL DATA APIs
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
FRED_API_KEY = os.getenv('FRED_API_KEY')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
CMC_API_KEY = os.getenv('CMC_API_KEY')
TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_API_KEY')

# TELEGRAM (Real Alerts)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("❌ TELEGRAM credentials missing!")

# TRADING CONFIG
SIGNAL_INTERVAL = 5  # Every 5 seconds
CONFIDENCE_THRESHOLD = 0.65
HIGH_CONFIDENCE = 0.75
TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
MAX_POSITION = 0.1
RISK_PER_TRADE = 0.02
STOP_LOSS = 0.05
TAKE_PROFIT = 0.15

# LOGGING
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

print("✅ Config loaded - All systems ready")

