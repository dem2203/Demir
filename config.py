# config.py - Configuration Management

import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class APIConfig:
    """API Configuration"""
    
    # Primary Exchange
    binance_key = os.getenv('BINANCE_API_KEY')
    binance_secret = os.getenv('BINANCE_API_SECRET')
    
    # Fallback Exchanges
    coinbase_key = os.getenv('COINBASE_API_KEY')
    coinbase_secret = os.getenv('COINBASE_API_SECRET')
    bybit_key = os.getenv('BYBIT_API_KEY')
    bybit_secret = os.getenv('BYBIT_API_SECRET')
    
    # Data Sources
    cmc_key = os.getenv('CMC_API_KEY')
    coinglass_key = os.getenv('COINGLASS_API_KEY')
    alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')
    fred_key = os.getenv('FRED_API_KEY')
    news_api_key = os.getenv('NEWSAPI_KEY')


@dataclass
class TelegramConfig:
    """Telegram Configuration"""
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = int(os.getenv('TELEGRAM_CHAT_ID', 0))


@dataclass
class DatabaseConfig:
    """Database Configuration"""
    url = os.getenv('DATABASE_URL', 'sqlite:///demir_ai.db')
    echo = False
    pool_size = 20
    max_overflow = 40


@dataclass
class CacheConfig:
    """Redis Cache Configuration"""
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    db = int(os.getenv('REDIS_DB', 0))


class Config:
    """Master Configuration"""
    
    API = APIConfig()
    TELEGRAM = TelegramConfig()
    DATABASE = DatabaseConfig()
    CACHE = CacheConfig()
    
    # Trading Config
    TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT']
    TRADING_INTERVAL = 300  # 5 minutes
    MAX_POSITION_SIZE = 0.05  # 5% per trade
    
    # Risk Management
    DEFAULT_TP_PERCENT = 1.5
    DEFAULT_SL_PERCENT = 1.0
    TRAILING_TP_PERCENT = 0.5
    
    # Quality Thresholds
    MIN_CONFIDENCE = 60.0  # % confidence required
    MIN_LAYER_AGREEMENT = 0.6  # 60% layer consensus
    MIN_QUALITY_SCORE = 75.0  # Quality score 0-100


CONFIG = Config()
