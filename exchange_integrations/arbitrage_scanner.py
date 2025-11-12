"""
FILE 13: arbitrage_scanner.py
PHASE 5.4 - ARBITRAGE SCANNER
700 lines
"""

import aiohttp
import logging
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

class ArbitrageScanner:
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3',
            'bybit': 'https://api.bybit.com/v5',
            'okx': 'https://www.okx.com/api/v5'
        }
    
    async def scan_arbitrage(self, symbol: str) -> Dict:
        """
        Scan for arbitrage opportunities across exchanges
        Returns: opportunity, spread%, buy_exchange, sell_exchange, profit_potential
        """
        try:
            # Get prices from multiple exchanges
            prices = {}
            
            # Binance
            url = f"{self.exchanges['binance']}/ticker/price?symbol={symbol}USDT"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        prices['binance'] = float(data['price'])
            
            # Bybit
            url = f"{self.exchanges['bybit']}/market/tickers?category=linear&symbol={symbol}USDT"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('result', {}).get('list'):
                            prices['bybit'] = float(data['result']['list'][0]['lastPrice'])
            
            # OKX
            url = f"{self.exchanges['okx']}/market/tickers?instType=SWAP&instId={symbol}-USDT"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data'):
                            prices['okx'] = float(data['data'][0]['last'])
            
            # Calculate spread
            valid_prices = [p for p in prices.values() if p]
            if len(valid_prices) < 2:
                return {'opportunity': False, 'prices': prices}
            
            max_price = max(valid_prices)
            min_price = min(valid_prices)
            spread = ((max_price - min_price) / min_price * 100)
            
            # Find exchanges
            buy_exchange = [k for k, v in prices.items() if v == min_price][0]
            sell_exchange = [k for k, v in prices.items() if v == max_price][0]
            
            # Profit potential (minus 0.5% fees)
            profit_potential = spread - 0.5
            
            if profit_potential > 0.5:
                return {
                    'opportunity': True,
                    'spread': spread,
                    'buy_exchange': buy_exchange,
                    'sell_exchange': sell_exchange,
                    'profit_potential': profit_potential,
                    'prices': prices
                }
            
            return {'opportunity': False, 'prices': prices}
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    print("✅ ArbitrageScanner initialized")
