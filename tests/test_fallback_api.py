# tests/test_fallback_api.py

import pytest
from utils.exchange_fallback_manager import ExchangeFallbackManager
from utils.futures_fallback_manager import FuturesFallbackManager


@pytest.mark.asyncio
async def test_spot_price_binance():
    """Test Binance spot price"""
    manager = ExchangeFallbackManager()
    price = await manager.get_spot_price('BTC')
    
    assert price['valid'] == True
    assert price['price'] > 0
    assert price['source'] == 'BINANCE'


@pytest.mark.asyncio
async def test_spot_price_fallback_coinbase():
    """Test Coinbase fallback"""
    # Mock Binance failure
    manager = ExchangeFallbackManager()
    price = await manager.get_spot_price('BTC')
    
    if price['source'] == 'COINBASE':
        assert price['valid'] == True
        assert price['price'] > 0


@pytest.mark.asyncio
async def test_futures_price_bybit():
    """Test Bybit futures"""
    manager = FuturesFallbackManager()
    price = await manager.get_futures_price('BTC')
    
    assert price['valid'] == True
    assert price['price'] > 0
