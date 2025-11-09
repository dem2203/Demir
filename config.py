import os
from dotenv import load_dotenv

load_dotenv()

# ==================== API KEYS (FROM ENVIRONMENT) ====================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
COINGLASS_API_KEY = os.getenv("COINGLASS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FRED_API_KEY = os.getenv("FRED_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
CMC_API_KEY = os.getenv("CMC_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==================== API ENDPOINTS ====================
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_FUTURES_URL = "https://fapi.binance.com"
COINGLASS_BASE_URL = "https://api.coinglass.com"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co"
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
NEWSAPI_BASE_URL = "https://newsapi.org"

# ==================== UI COLORS ====================
COLOR_SUCCESS = "#00D084"      # Green
COLOR_DANGER = "#FF4757"       # Red
COLOR_WARNING = "#FFA502"      # Orange
COLOR_INFO = "#2196F3"         # Blue
COLOR_NEUTRAL = "#95A3A6"      # Gray
COLOR_DARK_BG = "#111111"
COLOR_CARD_BG = "#1a1a1a"

# ==================== REFRESH RATES ====================
REFRESH_RATES = {
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute": 60,
    "5 minutes": 300
}

# ==================== CACHE SETTINGS ====================
CACHE_TTL = 60  # seconds

# ==================== SUPPORTED COINS ====================
SUPPORTED_COINS = ["BTC", "ETH", "LTC", "XRP", "SOL", "ADA", "DOGE"]
DEFAULT_COINS = ["BTC", "ETH"]

# ==================== TIMEFRAMES ====================
TIMEFRAMES = ["1h", "4h", "1d", "1w"]
DEFAULT_TIMEFRAME = "1h"

# ==================== API LIMITS ====================
BINANCE_API_WEIGHT_LIMIT = 1200  # requests per minute
COINGLASS_API_LIMIT = 100        # requests per day
ALPHA_VANTAGE_API_LIMIT = 5      # requests per minute
FRED_API_LIMIT = 120              # requests per minute

# ==================== TRADING PARAMETERS ====================
DEFAULT_ENTRY_PRICE = 43200
DEFAULT_TP1_PRICE = 44200
DEFAULT_TP2_PRICE = 45300
DEFAULT_TP3_PRICE = 46500
DEFAULT_SL_PRICE = 42100

# ==================== DASHBOARD CONFIGURATION ====================
DASHBOARD_TITLE = "🤖 DEMIR AI v30 Trading Dashboard"
DASHBOARD_DESCRIPTION = "Professional 8-Page Trading Intelligence System"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# ==================== PHASES ====================
TOTAL_PHASES = 26

PHASES = {
    1: {"name": "Binance SPOT Data", "category": "Data Collection"},
    2: {"name": "Binance FUTURES Data", "category": "Data Collection"},
    3: {"name": "Order Book Analysis", "category": "Data Collection"},
    4: {"name": "Technical Indicators", "category": "Data Collection"},
    5: {"name": "Volume Analysis", "category": "Data Collection"},
    6: {"name": "Market Sentiment", "category": "Data Collection"},
    7: {"name": "ML Data Preprocessing", "category": "Data Collection"},
    8: {"name": "Anomaly Detection", "category": "Data Collection"},
    9: {"name": "Data Validation", "category": "Data Collection"},
    10: {"name": "Consciousness Engine (Bayesian)", "category": "Decision Making"},
    11: {"name": "Intelligence Layers (111+ Factors)", "category": "Analysis"},
    12: {"name": "On-Chain Intelligence", "category": "Analysis"},
    13: {"name": "Macro Intelligence", "category": "Analysis"},
    14: {"name": "Sentiment Analysis", "category": "Analysis"},
    15: {"name": "Learning Engine", "category": "Optimization"},
    16: {"name": "Adversarial Testing", "category": "Optimization"},
    17: {"name": "Regulatory Compliance", "category": "Optimization"},
    18: {"name": "Multi-Coin Opportunity Scanner", "category": "Optimization"},
    19: {"name": "Quantum-Enhanced Layers", "category": "Advanced AI"},
    20: {"name": "Reinforcement Learning", "category": "Advanced AI"},
    21: {"name": "Multi-Agent Consensus", "category": "Advanced AI"},
    22: {"name": "Predictive Analytics", "category": "Advanced AI"},
    23: {"name": "Self-Learning System", "category": "Integration"},
    24: {"name": "Backtesting Validation", "category": "Integration"},
    25: {"name": "Recovery & Failover", "category": "Integration"},
    26: {"name": "Final Integration", "category": "Integration"}
}

# ==================== INTELLIGENCE FACTORS ====================
TECHNICAL_FACTORS = 40
ONCHAIN_FACTORS = 25
MACRO_FACTORS = 18
SENTIMENT_FACTORS = 15
GLOBAL_FACTORS = 13
TOTAL_FACTORS = TECHNICAL_FACTORS + ONCHAIN_FACTORS + MACRO_FACTORS + SENTIMENT_FACTORS + GLOBAL_FACTORS

# ==================== TELEGRAM SETTINGS ====================
TELEGRAM_ALERT_INTERVAL = 3600  # 1 hour in seconds
TELEGRAM_MESSAGE_FORMAT = """
🤖 DEMIR AI Market Update - {time}

🟢 SIGNAL: {signal} ({confidence}% confidence)
💰 Entry: {entry} | TP1: {tp1} | TP3: {tp3} | SL: {sl}

📊 {coin}: {price} ({change}%)

🔧 System Status: ✅ All operational

Last update: {timestamp}
"""

# ==================== BAYESIAN PARAMETERS ====================
PRIOR_BULL = 0.35
PRIOR_BEAR = 0.25
PRIOR_SIDEWAYS = 0.40

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== DATABASE (if using) ====================
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/demir_ai")

# ==================== PERFORMANCE ====================
MAX_HISTORICAL_ROWS = 1000
MEMORY_LIMIT_MB = 512
API_TIMEOUT_SECONDS = 30
