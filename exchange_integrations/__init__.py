"""
exchange_integrations/__init__.py
Safely load exchange connectors only if API keys exist
"""

import os
import logging

logger = logging.getLogger(__name__)


def get_bybit_connector():
    """Load Bybit connector only if API key exists"""
    bybit_key = os.getenv("BYBIT_API_KEY")
    
    if not bybit_key or bybit_key == "":
        logger.warning("⚠️ BYBIT_API_KEY not configured - Bybit disabled")
        return None
    
    try:
        from .bybit_connector import BybitConnector
        return BybitConnector()
    except Exception as e:
        logger.error(f"❌ Error loading Bybit connector: {e}")
        return None


def get_okx_connector():
    """Load OKX connector only if API key exists"""
    okx_key = os.getenv("OKX_API_KEY")
    
    if not okx_key or okx_key == "":
        logger.warning("⚠️ OKX_API_KEY not configured - OKX disabled")
        return None
    
    try:
        from .okx_connector import OKXConnector
        return OKXConnector()
    except Exception as e:
        logger.error(f"❌ Error loading OKX connector: {e}")
        return None


def get_coinbase_connector():
    """Load Coinbase connector only if API key exists"""
    coinbase_key = os.getenv("COINBASE_API_KEY")
    
    if not coinbase_key or coinbase_key == "":
        logger.warning("⚠️ COINBASE_API_KEY not configured - Coinbase disabled")
        return None
    
    try:
        from .coinbase_connector import CoinbaseConnector
        return CoinbaseConnector()
    except Exception as e:
        logger.error(f"❌ Error loading Coinbase connector: {e}")
        return None


def get_connector(exchange_name: str):
    """
    Unified method to get any exchange connector
    
    Usage:
        connector = get_connector('bybit')
        if connector:
            data = await connector.get_futures_data('BTCUSDT')
    """
    
    if exchange_name.lower() == "bybit":
        return get_bybit_connector()
    
    elif exchange_name.lower() == "okx":
        return get_okx_connector()
    
    elif exchange_name.lower() == "coinbase":
        return get_coinbase_connector()
    
    else:
        logger.error(f"❌ Unknown exchange: {exchange_name}")
        return None


# Auto-load on import
bybit = get_bybit_connector()
okx = get_okx_connector()
coinbase = get_coinbase_connector()

__all__ = [
    'get_connector',
    'get_bybit_connector',
    'get_okx_connector',
    'get_coinbase_connector',
    'bybit',
    'okx',
    'coinbase'
]

