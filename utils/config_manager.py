"""
DEMIR AI BOT - Configuration Manager
Railway environment variables type-safe manager
Production-ready configuration with validation
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ExchangeConfig:
    """Exchange API configuration with validation."""
    
    binance_api_key: str
    binance_api_secret: str
    bybit_api_key: str
    bybit_api_secret: str
    coinbase_api_key: str
    coinbase_api_secret: str
    
    def __post_init__(self):
        """Validate that all required keys are present."""
        required = [
            self.binance_api_key, self.binance_api_secret,
            self.bybit_api_key, self.bybit_api_secret,
            self.coinbase_api_key, self.coinbase_api_secret
        ]
        if any(not key or key == "railwayde tanimli calisiyor" for key in required):
            logger.warning("Some exchange keys may not be fully configured in Railway")


@dataclass
class DataSourceConfig:
    """Data source API configuration."""
    
    alpha_vantage_key: str
    coinglass_key: str
    coinmarketcap_key: str
    dexcheck_key: str
    finnhub_key: str
    fred_key: str
    newsapi_key: str
    opensea_key: str
    twelve_data_key: str
    twitter_key: str
    twitter_secret: str
    twitter_bearer: str
    cryptoalert_key: str


@dataclass
class DatabaseConfig:
    """Database configuration for PostgreSQL."""
    
    database_url: str
    
    def __post_init__(self):
        """Validate database URL format."""
        if not self.database_url or self.database_url == "railwayde tanimli calisiyor":
            raise ValueError("DATABASE_URL not properly configured in Railway")
        if not self.database_url.startswith(("postgresql://", "postgres://")):
            logger.warning("DATABASE_URL may not be a valid PostgreSQL connection string")


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    
    bot_token: str
    chat_id: str
    
    def __post_init__(self):
        """Validate Telegram credentials."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram configuration incomplete")


@dataclass
class StreamlitConfig:
    """Streamlit configuration settings."""
    
    watermark_enabled: bool = False
    logger_level: str = "error"
    xsrf_protection: bool = False
    headless_mode: bool = True
    serve_templates: bool = True


class ConfigManager:
    """Central configuration manager for Railway environment."""
    
    def __init__(self):
        """Initialize and load all configurations."""
        self.exchange = self._load_exchange_config()
        self.data_sources = self._load_data_source_config()
        self.database = self._load_database_config()
        self.telegram = self._load_telegram_config()
        self.streamlit = self._load_streamlit_config()
        self.api_url = os.getenv("API_URL", "http://api-server:5000")
        self.python_version = os.getenv("PYTHON_VERSION", "3.11.9")
        
        logger.info("Configuration loaded successfully from Railway environment")
    
    @staticmethod
    def _load_exchange_config() -> ExchangeConfig:
        """Load exchange API configuration."""
        return ExchangeConfig(
            binance_api_key=os.getenv("BINANCE_API_KEY", ""),
            binance_api_secret=os.getenv("BINANCE_API_SECRET", ""),
            bybit_api_key=os.getenv("BYBIT_API_KEY", ""),
            bybit_api_secret=os.getenv("BYBIT_API_SECRET", ""),
            coinbase_api_key=os.getenv("COINBASE_API_KEY", ""),
            coinbase_api_secret=os.getenv("COINBASE_API_SECRET", "")
        )
    
    @staticmethod
    def _load_data_source_config() -> DataSourceConfig:
        """Load data source API configuration."""
        return DataSourceConfig(
            alpha_vantage_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            coinglass_key=os.getenv("COINGLASS_API_KEY", ""),
            coinmarketcap_key=os.getenv("CoinMarketCap_API_KEY", ""),
            dexcheck_key=os.getenv("DEXCHECK_API_KEY", ""),
            finnhub_key=os.getenv("Finnhub_API_KEY", ""),
            fred_key=os.getenv("FRED_API_KEY", ""),
            newsapi_key=os.getenv("NEWSAPI_KEY", ""),
            opensea_key=os.getenv("OPENSEA_API_KEY", ""),
            twelve_data_key=os.getenv("TWELVE_DATA_API_KEY", ""),
            twitter_key=os.getenv("TWITTER_API_KEY", ""),
            twitter_secret=os.getenv("TWITTER_API_SECRET", ""),
            twitter_bearer=os.getenv("TWITTER_BEARER_TOKEN", ""),
            cryptoalert_key=os.getenv("CRYPTOALERT_API_KEY", "")
        )
    
    @staticmethod
    def _load_database_config() -> DatabaseConfig:
        """Load database configuration."""
        return DatabaseConfig(
            database_url=os.getenv("DATABASE_URL", "")
        )
    
    @staticmethod
    def _load_telegram_config() -> TelegramConfig:
        """Load Telegram configuration."""
        return TelegramConfig(
            bot_token=os.getenv("TELEGRAM_TOKEN", ""),
            chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
        )
    
    @staticmethod
    def _load_streamlit_config() -> StreamlitConfig:
        """Load Streamlit configuration."""
        return StreamlitConfig(
            watermark_enabled=os.getenv("STREAMLIT_CLIENT_SHOWSTREAMLITWATERMARK", "false").lower() == "true",
            logger_level=os.getenv("STREAMLIT_LOGGER_LEVEL", "error"),
            xsrf_protection=os.getenv("STREAMLIT_SERVER_ENABLEXSRFPROTECTION", "false").lower() == "true",
            headless_mode=os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true",
            serve_templates=os.getenv("SERVE_TEMPLATES", "true").lower() == "true"
        )
    
    def get_exchange_credentials(self, exchange: str) -> Dict[str, str]:
        """Get credentials for specific exchange."""
        exchange_lower = exchange.lower()
        
        if exchange_lower == "binance":
            return {
                "api_key": self.exchange.binance_api_key,
                "api_secret": self.exchange.binance_api_secret
            }
        elif exchange_lower == "bybit":
            return {
                "api_key": self.exchange.bybit_api_key,
                "api_secret": self.exchange.bybit_api_secret
            }
        elif exchange_lower == "coinbase":
            return {
                "api_key": self.exchange.coinbase_api_key,
                "api_secret": self.exchange.coinbase_api_secret
            }
        else:
            raise ValueError(f"Unknown exchange: {exchange}")
    
    def validate_all(self) -> bool:
        """Validate all configurations."""
        try:
            assert self.exchange.binance_api_key, "Binance API key missing"
            assert self.database.database_url, "Database URL missing"
            assert self.telegram.bot_token, "Telegram token missing"
            logger.info("All configurations validated successfully")
            return True
        except AssertionError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (sensitive data masked)."""
        return {
            "exchange": {
                "binance": "***",
                "bybit": "***",
                "coinbase": "***"
            },
            "database": "***",
            "telegram": "***",
            "api_url": self.api_url,
            "python_version": self.python_version,
            "streamlit": {
                "watermark_enabled": self.streamlit.watermark_enabled,
                "logger_level": self.streamlit.logger_level,
                "headless_mode": self.streamlit.headless_mode
            }
        }


# Global config instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get or create global config instance (singleton)."""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


if __name__ == "__main__":
    config = get_config()
    print("Configuration loaded successfully")
    print(f"Config: {config.to_dict()}")
