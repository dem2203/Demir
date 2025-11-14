import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)

class MultiExchangeFailover:
    """
    Multi-exchange failover - if Binance down, use Bybit/Coinbase
    Ensures 99.99% uptime
    """
    
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com',
            'bybit': 'https://api.bybit.com',
            'coinbase': 'https://api.coinbase.com'
        }
        self.exchange_health = {ex: True for ex in self.exchanges}
        self.primary_exchange = 'binance'
        
    def get_price(self, symbol: str) -> Optional[float]:
        """Get price from available exchange"""
        # Try primary first
        price = self._get_price_from(self.primary_exchange, symbol)
        if price:
            return price
        
        # Fallback to others
        for exchange in self.exchanges:
            if exchange != self.primary_exchange:
                price = self._get_price_from(exchange, symbol)
                if price:
                    logger.warning(f"⚠️ Fallback to {exchange} for {symbol}")
                    self.primary_exchange = exchange
                    return price
        
        logger.error(f"❌ Could not get price for {symbol} from any exchange")
        return None
    
    def _get_price_from(self, exchange: str, symbol: str) -> Optional[float]:
        """Get price from specific exchange"""
        try:
            if exchange == 'binance':
                url = f"{self.exchanges[exchange]}/api/v3/ticker/price?symbol={symbol}"
            elif exchange == 'bybit':
                url = f"{self.exchanges[exchange]}/v5/market/tickers?category=spot&symbol={symbol}"
            elif exchange == 'coinbase':
                url = f"{self.exchanges[exchange]}/products/{symbol}/ticker"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                if exchange == 'binance':
                    return float(response.json()['price'])
                elif exchange == 'bybit':
                    return float(response.json()['result']['list'][0]['lastPrice'])
                elif exchange == 'coinbase':
                    return float(response.json()['price'])
            
            self.exchange_health[exchange] = False
            return None
        
        except Exception as e:
            logger.error(f"Error fetching from {exchange}: {e}")
            self.exchange_health[exchange] = False
            return None
    
    def get_best_price(self, symbol: str) -> Dict:
        """Get best price across exchanges"""
        prices = {}
        
        for exchange in self.exchanges:
            price = self._get_price_from(exchange, symbol)
            if price:
                prices[exchange] = price
        
        if prices:
            best = max(prices, key=prices.get)
            logger.info(f"📊 Best price for {symbol}: {prices[best]} ({best})")
            return {'price': prices[best], 'exchange': best, 'all_prices': prices}
        
        return None
