# ============================================================================
# DEMIR AI - CONFIGURATION & ENVIRONMENT MANAGEMENT
# ============================================================================
# Date: November 10, 2025
# Purpose: Tüm config değerlerini merkezi olarak yönet
# 
# 🔒 RULES:
# - Tüm API key'leri environment variable'dan al
# - ASLA hard-code değer kullanma
# - Mock data flag'ı KAPALI tutulacak
# - Fallback logic'ler tanımla
# ============================================================================

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class APIConfig:
    """API Yapılandırması (API Configuration)"""
    key: str
    secret: Optional[str] = None
    url: Optional[str] = None
    timeout: int = 10
    enabled: bool = True
    rate_limit: int = 1200  # Per minute

# ============================================================================
# CONFIG LOADER
# ============================================================================

class Config:
    """
    Merkezi yapılandırma sınıfı
    (Central configuration manager)
    """
    
    # ========================================================================
    # ENVIRONMENT VARIABLES - Gerçek API Anahtarları
    # ========================================================================
    
    # Binance Futures
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    BINANCE_FUTURES_URL = 'https://fapi.binance.com'
    BINANCE_SPOT_URL = 'https://api.binance.com'
    
    # CoinMarketCap
    CMC_API_KEY = os.getenv('CMC_API_KEY')
    CMC_URL = 'https://pro-api.coinmarketcap.com/v1'
    
    # Coinglass (On-chain)
    COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY')
    COINGLASS_URL = 'https://api.coinglass.com/v1'
    
    # Alpha Vantage (Traditional Markets)
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'
    
    # FRED (Federal Reserve Economic Data)
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    FRED_URL = 'https://api.stlouisfed.org/fred'
    
    # News API
    NEWS_API_KEY = os.getenv('NEWSAPI_KEY')
    NEWS_API_URL = 'https://newsapi.org/v2'
    
    # Twitter/X API
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_API_URL = 'https://api.twitter.com/2'
    
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'
    
    # Twelve Data
    TWELVE_DATA_KEY = os.getenv('TWELVE_DATA_API_KEY')
    TWELVE_DATA_URL = 'https://api.twelvedata.com'
    
    # ========================================================================
    # STREAMLIT SETTINGS
    # ========================================================================
    
    STREAMLIT_CLIENT_SHOWSTREAMLITWATERMARK = os.getenv(
        'STREAMLIT_CLIENT_SHOWSTREAMLITWATERMARK', 'false'
    ).lower() == 'true'
    
    STREAMLIT_SERVER_HEADLESS = os.getenv(
        'STREAMLIT_SERVER_HEADLESS', 'true'
    ).lower() == 'true'
    
    STREAMLIT_SERVER_ENABLEXSRFPROTECTION = os.getenv(
        'STREAMLIT_SERVER_ENABLEXSRFPROTECTION', 'false'
    ).lower() == 'true'
    
    STREAMLIT_LOGGER_LEVEL = os.getenv('STREAMLIT_LOGGER_LEVEL', 'info')
    
    # ========================================================================
    # DASHBOARD CONFIGURATION
    # ========================================================================
    
    DASHBOARD_CONFIG = {
        'theme': 'perplexity',  # Perplexity tarzı
        'refresh_interval': 60,  # Saniye
        'default_symbol': 'BTCUSDT',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT'],
        'timeframes': ['1h', '4h', '1d'],
        'enable_real_data': True,  # ✅ ASLA False yapma
        'enable_mock_data': False,  # ✅ Kalıcı olarak False
        'data_cache_duration': 60,  # 1 minute
        'max_retries': 3,
        'timeout': 10
    }
    
    # ========================================================================
    # DAEMON CONFIGURATION (7/24)
    # ========================================================================
    
    DAEMON_CONFIG = {
        'enabled': True,
        'auto_start': True,
        'market_monitor_interval': 300,  # 5 dakika
        'hourly_ping_enabled': True,
        'hourly_ping_minute': 0,  # Saat başında
        'telegram_alerts': True,
        'log_file': 'daemon.log',
        'max_log_size': 10 * 1024 * 1024,  # 10 MB
        'watchdog_enabled': True,
        'watchdog_interval': 30  # 30 saniye
    }
    
    # ========================================================================
    # TELEGRAM ALERT CONFIGURATION
    # ========================================================================
    
    TELEGRAM_CONFIG = {
        'enabled': True,
        'hourly_alerts': True,  # Her saat bildirim
        'signal_alerts': True,  # Sinyal uyarıları
        'risk_alerts': True,    # Risk uyarıları
        'funding_alerts': True, # Funding rate uyarıları
        'extreme_volatility_threshold': 10,  # % 10
        'extreme_funding_threshold': 0.1,    # 0.1%
        'high_volume_threshold': 1.5,  # 1.5x average
        'message_format': 'HTML',
        'rate_limit': 30,  # mesaj/dakika
        'batch_size': 10  # Batch notification
    }
    
    # ========================================================================
    # AI BRAIN CONFIGURATION
    # ========================================================================
    
    AI_BRAIN_CONFIG = {
        'ensemble_method': 'weighted_voting',  # Weighted ensemble
        'min_active_layers': 3,  # En az 3 layer aktif olmalı
        'confidence_threshold': 0.5,  # 50% minimum
        'enable_meta_learning': True,  # Adaptive weighting
        'meta_learning_period': 3600,  # 1 saat
        'signal_confirmation_bars': 3  # 3 bar confirmation
    }
    
    # ========================================================================
    # ANALYSIS LAYERS CONFIGURATION
    # ========================================================================
    
    LAYERS_CONFIG = {
        'momentum_layer': {'weight': 1.2, 'enabled': True},
        'volume_layer': {'weight': 1.0, 'enabled': True},
        'funding_rate_layer': {'weight': 1.5, 'enabled': True},
        'fibonacci_layer': {'weight': 1.1, 'enabled': True},
        'vwap_layer': {'weight': 1.3, 'enabled': True},
        'rsi_layer': {'weight': 1.2, 'enabled': True},
        'macro_correlation_layer': {'weight': 1.4, 'enabled': True},
        'onchain_layer': {'weight': 1.5, 'enabled': True},
        'volatility_layer': {'weight': 1.0, 'enabled': True},
        'market_structure_layer': {'weight': 1.3, 'enabled': True},
        'support_resistance_layer': {'weight': 1.2, 'enabled': True},
        'orderbook_imbalance_layer': {'weight': 1.1, 'enabled': True},
        'liquidation_layer': {'weight': 1.4, 'enabled': True},
        'news_sentiment_layer': {'weight': 0.9, 'enabled': True},
        'social_sentiment_layer': {'weight': 0.8, 'enabled': True},
        'whale_movement_layer': {'weight': 1.3, 'enabled': True},
        'market_maker_layer': {'weight': 1.2, 'enabled': True},
    }
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    
    DATABASE_CONFIG = {
        'type': 'sqlite',
        'path': 'data/demir_ai.db',
        'backup_path': 'data/backups/',
        'retention_days': 90,
        'enable_wal': True,
        'cache_size': 10000
    }
    
    # ========================================================================
    # TRADING CONFIGURATION
    # ========================================================================
    
    TRADING_CONFIG = {
        'enable_paper_trading': True,
        'enable_live_trading': False,
        'position_sizing': 'kelly',  # Kelly criterion
        'max_leverage': 5.0,
        'max_position_size': 0.1,  # 10% portfolio
        'stop_loss_pct': 2.0,  # 2%
        'take_profit_targets': [1, 2, 3],  # 1%, 2%, 3%
        'trailing_stop': True,
        'trailing_stop_pct': 0.5
    }
    
    # ========================================================================
    # BACKTESTING CONFIGURATION
    # ========================================================================
    
    BACKTEST_CONFIG = {
        'enabled': True,
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_balance': 10000,  # USDT
        'commission': 0.0004,  # 0.04%
        'slippage': 0.0002,  # 0.02%
        'use_real_historical_data': True
    }
    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'log_dir': 'logs/',
        'max_file_size': 100 * 1024 * 1024,  # 100 MB
        'backup_count': 10,
        'console_enabled': True,
        'file_enabled': True,
    }
    
    # ========================================================================
    # VALIDATION & HEALTH CHECKS
    # ========================================================================
    
    @classmethod
    def validate(cls) -> bool:
        """
        Yapılandırmanın geçerli olup olmadığını kontrol et
        (Validate configuration)
        """
        required_vars = [
            'BINANCE_API_KEY',
            'BINANCE_API_SECRET',
            'TELEGRAM_TOKEN',
            'TELEGRAM_CHAT_ID'
        ]
        
        missing = []
        for var in required_vars:
            value = getattr(cls, var, None)
            if not value:
                missing.append(var)
        
        if missing:
            logger.error(f"❌ Eksik ortam değişkenleri (Missing env vars): {missing}")
            logger.error("   Railway Dashboard → Variables'de ayarla")
            return False
        
        logger.info("✅ Yapılandırma doğru (Config validated)")
        return True
    
    @classmethod
    def get_api_config(cls, api_name: str) -> Dict[str, Any]:
        """Belirli bir API'nin yapılandırmasını al"""
        configs = {
            'binance': {
                'key': cls.BINANCE_API_KEY,
                'secret': cls.BINANCE_API_SECRET,
                'url': cls.BINANCE_FUTURES_URL,
                'timeout': 10
            },
            'cmc': {
                'key': cls.CMC_API_KEY,
                'url': cls.CMC_URL,
                'timeout': 10
            },
            'coinglass': {
                'key': cls.COINGLASS_API_KEY,
                'url': cls.COINGLASS_URL,
                'timeout': 10
            },
            'telegram': {
                'token': cls.TELEGRAM_TOKEN,
                'chat_id': cls.TELEGRAM_CHAT_ID,
                'url': cls.TELEGRAM_API_URL,
                'timeout': 5
            }
        }
        
        return configs.get(api_name.lower(), {})
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Yapılandırma durumunu al (Get config status)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'dashboard_enabled': cls.DASHBOARD_CONFIG['enable_real_data'],
            'mock_data_disabled': not cls.DASHBOARD_CONFIG['enable_mock_data'],
            'daemon_enabled': cls.DAEMON_CONFIG['enabled'],
            'telegram_enabled': cls.TELEGRAM_CONFIG['enabled'],
            'trading_mode': 'paper' if cls.TRADING_CONFIG['enable_paper_trading'] else 'live'
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['Config']

# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Validate config
    if Config.validate():
        print("\n✅ Configuration Status:")
        print(f"   Dashboard: {Config.DASHBOARD_CONFIG['theme'].upper()}")
        print(f"   Real Data: {Config.DASHBOARD_CONFIG['enable_real_data']}")
        print(f"   Mock Data: {Config.DASHBOARD_CONFIG['enable_mock_data']}")
        print(f"   Daemon: {Config.DAEMON_CONFIG['enabled']}")
        print(f"   Telegram: {Config.TELEGRAM_CONFIG['enabled']}")
        print(f"   Trading Mode: {'Paper' if Config.TRADING_CONFIG['enable_paper_trading'] else 'Live'}")
        print(f"\n   Status: {Config.get_status()}")
    else:
        print("\n❌ Configuration validation failed")
