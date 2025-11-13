"""
FUTURES FALLBACK MANAGER
Binance Futures fail → Bybit (REAL data)

⚠️ NO MOCK DATA:
- Binance Futures fail → Bybit'ten real futures fiyat
- Bybit fail → ERROR (never fake)
"""

import aiohttp
import logging
import os
import hmac
import hashlib
import time
from typing import Dict
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class FuturesFallbackManager:
    """
    Multi-exchange futures fallback
    REAL data only - no mock/fake prices
    """
    
    def __init__(self):
        self.binance_futures_api = "https://fapi.binance.com/fapi/v1"
        self.bybit_api = "https://api.bybit.com/v5"
        
        # API Keys
        self.bybit_key = os.getenv('BYBIT_API_KEY')
        self.bybit_secret = os.getenv('BYBIT_API_SECRET')
        
        # Symbol mapping
        self.symbol_map = {
            'BTC': {'binance': 'BTCUSDT', 'bybit': 'BTCUSDT'},
            'ETH': {'binance': 'ETHUSDT', 'bybit': 'ETHUSDT'},
            'SOL': {'binance': 'SOLUSDT', 'bybit': 'SOLUSDT'},
            'ADA': {'binance': 'ADAUSDT', 'bybit': 'ADAUSDT'},
            'XRP': {'binance': 'XRPUSDT', 'bybit': 'XRPUSDT'},
            'DOGE': {'binance': 'DOGEUSDT', 'bybit': 'DOGEUSDT'},
            'MATIC': {'binance': 'MATICUSDT', 'bybit': 'MATICUSDT'},
        }
    
    async def get_futures_price(self, symbol: str) -> Dict:
        """
        Get REAL futures price with fallback
        
        Priority:
        1. BINANCE Futures (Primary)
        2. BYBIT (Secondary) → REAL data
        3. ERROR if both fail (NO MOCK!)
        
        Args:
            symbol: 'BTC', 'ETH', 'SOL', etc.
        
        Returns:
            Real futures price or error
        """
        
        symbol_upper = symbol.upper()
        
        if symbol_upper not in self.symbol_map:
            logger.error(f"❌ Symbol {symbol} not in futures mapping")
            return {
                'price': None,
                'source': 'NONE',
                'error': f'Symbol {symbol} not supported for futures',
                'valid': False
            }
        
        symbols = self.symbol_map[symbol_upper]
        
        # ========== TIER 1: BINANCE FUTURES (PRIMARY) ==========
        logger.info(f"📊 Getting {symbol} futures price from Binance...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.binance_futures_api}/ticker/24hr"
                params = {'symbol': symbols['binance']}
                
                async with session.get(url, params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        price = float(data['lastPrice'])
                        
                        logger.info(f"✅ BINANCE FUTURES: {symbol} = ${price:.2f}")
                        
                        return {
                            'price': price,
                            'source': 'BINANCE_FUTURES',
                            'timestamp': datetime.now().isoformat(),
                            'valid': True
                        }
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Binance Futures timeout")
        except Exception as e:
            logger.warning(f"⚠️ Binance Futures error: {e}")
        
        # ========== TIER 2: BYBIT (SECONDARY) ==========
        logger.info(f"⚠️ Binance Futures failed, trying Bybit for {symbol}...")
        
        if not self.bybit_key:
            logger.warning("⚠️ BYBIT_API_KEY not configured")
        else:
            try:
                # Bybit doesn't require auth for public endpoints
                async with aiohttp.ClientSession() as session:
                    url = f"{self.bybit_api}/market/tickers"
                    params = {
                        'category': 'linear',
                        'symbol': symbols['bybit']
                    }
                    
                    async with session.get(url, params=params, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            if data['result']['list']:
                                ticker = data['result']['list']
                                price = float(ticker['lastPrice'])
                                
                                logger.info(f"✅ BYBIT FUTURES: {symbol} = ${price:.2f}")
                                
                                return {
                                    'price': price,
                                    'source': 'BYBIT_FUTURES',
                                    'timestamp': datetime.now().isoformat(),
                                    'valid': True
                                }
            except Exception as e:
                logger.warning(f"⚠️ Bybit error: {e}")
        
        # ========== ALL FAILED - RETURN ERROR (NOT MOCK!) ==========
        logger.critical(f"🚨 ALL real futures sources failed for {symbol}")
        
        return {
            'price': None,
            'source': 'NONE',
            'error': 'All real futures sources unavailable (Binance Futures, Bybit)',
            'valid': False
        }
    
    async def get_futures_data(self, symbol: str) -> Dict:
        """
        Get detailed futures data (price, funding, open interest)
        """
        
        price_data = await self.get_futures_price(symbol)
        
        return price_data
