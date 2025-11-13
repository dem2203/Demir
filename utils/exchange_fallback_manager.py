"""
EXCHANGE FALLBACK MANAGER
Binance fail → Coinbase → CMC (all REAL data)

⚠️ NO MOCK DATA:
- Binance fail → Coinbase'ten real fiyat
- Coinbase fail → CMC'den real fiyat
- Both fail → ERROR (never fake price)
"""

import aiohttp
import logging
import os
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExchangeFallbackManager:
    """
    Multi-exchange price fallback
    REAL data only - no mock/fake prices
    """
    
    def __init__(self):
        self.binance_api = "https://api.binance.com/api/v3"
        self.coinbase_api = "https://api.coinbase.com/v2"
        self.cmc_api = "https://pro-api.coinmarketcap.com/v1"
        
        # API Keys
        self.coinbase_key = os.getenv('COINBASE_API_KEY')
        self.coinbase_secret = os.getenv('COINBASE_API_SECRET')
        self.cmc_key = os.getenv('CMC_API_KEY')
        
        # Symbol mapping
        self.symbol_map = {
            'BTC': {'binance': 'BTCUSDT', 'coinbase': 'BTC-USD', 'cmc': 'BTC'},
            'ETH': {'binance': 'ETHUSDT', 'coinbase': 'ETH-USD', 'cmc': 'ETH'},
            'SOL': {'binance': 'SOLUSDT', 'coinbase': 'SOL-USD', 'cmc': 'SOL'},
            'ADA': {'binance': 'ADAUSDT', 'coinbase': 'ADA-USD', 'cmc': 'ADA'},
            'XRP': {'binance': 'XRPUSDT', 'coinbase': 'XRP-USD', 'cmc': 'XRP'},
            'DOGE': {'binance': 'DOGEUSDT', 'coinbase': 'DOGE-USD', 'cmc': 'DOGE'},
            'MATIC': {'binance': 'MATICUSDT', 'coinbase': 'MATIC-USD', 'cmc': 'MATIC'},
            'AVAX': {'binance': 'AVAXUSDT', 'coinbase': 'AVAX-USD', 'cmc': 'AVAX'},
            'LINK': {'binance': 'LINKUSDT', 'coinbase': 'LINK-USD', 'cmc': 'LINK'},
            'ARB': {'binance': 'ARBUSDT', 'coinbase': 'ARB-USD', 'cmc': 'ARB'},
            'OP': {'binance': 'OPUSDT', 'coinbase': 'OP-USD', 'cmc': 'OP'},
            'UNI': {'binance': 'UNIUSDT', 'coinbase': 'UNI-USD', 'cmc': 'UNI'},
            'AAVE': {'binance': 'AAVEUSDT', 'coinbase': 'AAVE-USD', 'cmc': 'AAVE'},
        }
    
    async def get_spot_price(self, symbol: str) -> Dict:
        """
        Get REAL spot price with fallback
        
        Priority:
        1. BINANCE (Primary) → Most reliable
        2. COINBASE (Secondary) → REAL data
        3. CMC (Tertiary) → REAL data
        4. ERROR if all fail (NO MOCK!)
        
        Args:
            symbol: 'BTC', 'ETH', 'SOL', etc.
        
        Returns:
            {
                'price': 45000.50,
                'source': 'BINANCE',
                'timestamp': '2025-11-13T13:27:00',
                'valid': True
            }
            OR
            {
                'price': None,
                'source': 'NONE',
                'error': 'All real sources failed',
                'valid': False
            }
        """
        
        symbol_upper = symbol.upper()
        
        if symbol_upper not in self.symbol_map:
            logger.error(f"❌ Symbol {symbol} not in mapping")
            return {
                'price': None,
                'source': 'NONE',
                'error': f'Symbol {symbol} not supported',
                'valid': False
            }
        
        symbols = self.symbol_map[symbol_upper]
        
        # ========== TIER 1: BINANCE (PRIMARY) ==========
        logger.info(f"📊 Getting {symbol} price from Binance...")
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.binance_api}/ticker/price"
                params = {'symbol': symbols['binance']}
                
                async with session.get(url, params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        price = float(data['price'])
                        
                        logger.info(f"✅ BINANCE: {symbol} = ${price:.2f}")
                        
                        return {
                            'price': price,
                            'source': 'BINANCE',
                            'timestamp': datetime.now().isoformat(),
                            'valid': True
                        }
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Binance timeout for {symbol}")
        except Exception as e:
            logger.warning(f"⚠️ Binance error: {e}")
        
        # ========== TIER 2: COINBASE (SECONDARY) ==========
        logger.info(f"⚠️ Binance failed, trying Coinbase for {symbol}...")
        
        if not self.coinbase_key:
            logger.warning("⚠️ COINBASE_API_KEY not configured")
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    # Coinbase Pro API
                    url = f"{self.coinbase_api}/prices/{symbols['coinbase']}/spot"
                    
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            price = float(data['data']['amount'])
                            
                            logger.info(f"✅ COINBASE: {symbol} = ${price:.2f}")
                            
                            return {
                                'price': price,
                                'source': 'COINBASE',
                                'timestamp': datetime.now().isoformat(),
                                'valid': True
                            }
            except Exception as e:
                logger.warning(f"⚠️ Coinbase error: {e}")
        
        # ========== TIER 3: COINMARKETCAP (TERTIARY) ==========
        logger.info(f"⚠️ Coinbase failed, trying CMC for {symbol}...")
        
        if not self.cmc_key:
            logger.warning("⚠️ CMC_API_KEY not configured")
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.cmc_api}/cryptocurrency/quotes/latest"
                    params = {
                        'symbol': symbols['cmc'],
                        'convert': 'USD'
                    }
                    headers = {
                        'X-CMC_PRO_API_KEY': self.cmc_key
                    }
                    
                    async with session.get(url, params=params, headers=headers, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            price = data['data'][symbols['cmc']]['quote']['USD']['price']
                            
                            logger.info(f"✅ CMC: {symbol} = ${price:.2f}")
                            
                            return {
                                'price': price,
                                'source': 'CMC',
                                'timestamp': datetime.now().isoformat(),
                                'valid': True
                            }
            except Exception as e:
                logger.warning(f"⚠️ CMC error: {e}")
        
        # ========== ALL FAILED - RETURN ERROR (NOT MOCK!) ==========
        logger.critical(f"🚨 ALL real sources failed for {symbol}")
        
        return {
            'price': None,
            'source': 'NONE',
            'error': 'All real data sources unavailable (Binance, Coinbase, CMC)',
            'valid': False
        }
    
    async def get_multiple_prices(self, symbols: list) -> Dict:
        """Get prices for multiple symbols"""
        
        prices = {}
        
        for symbol in symbols:
            price_data = await self.get_spot_price(symbol)
            prices[symbol] = price_data
        
        return prices
