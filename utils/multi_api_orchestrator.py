"""
MULTI-API ORCHESTRATOR
Tüm fallback'leri yönet
Binance → Coinbase → CMC (REAL data chain)
"""

import logging
from typing import Dict, List, Optional
from utils.exchange_fallback_manager import ExchangeFallbackManager
from utils.futures_fallback_manager import FuturesFallbackManager

logger = logging.getLogger(__name__)


class MultiAPIOrchestrator:
    """
    Tüm API'leri yönet ve fallback zincirini kontrol et
    REAL DATA ONLY - NO MOCK
    """
    
    def __init__(self):
        self.spot_manager = ExchangeFallbackManager()
        self.futures_manager = FuturesFallbackManager()
    
    async def get_price(self, symbol: str, futures: bool = False) -> Dict:
        """
        Get price (spot veya futures)
        
        Args:
            symbol: 'BTC', 'ETH', etc.
            futures: True = futures price, False = spot price
        
        Returns:
            Real price or error
        """
        
        if futures:
            return await self.futures_manager.get_futures_price(symbol)
        else:
            return await self.spot_manager.get_spot_price(symbol)
    
    async def verify_data_quality(self, price_data: Dict) -> bool:
        """
        Veri kalitesini kontrol et
        
        ⚠️ Eğer price_data invalid ise, sistem trading yapmaz!
        """
        
        if not price_data.get('valid'):
            logger.error(f"❌ Invalid data: {price_data.get('error')}")
            return False
        
        if price_data.get('price') is None:
            logger.error("❌ Price is None (mock data döndürülmedi!)")
            return False
        
        if price_data.get('price') <= 0:
            logger.error(f"❌ Invalid price: {price_data.get('price')}")
            return False
        
        logger.info(f"✅ Data quality OK: {price_data['source']} = ${price_data['price']}")
        return True
    
    async def get_portfolio_prices(self, symbols: List[str]) -> Dict:
        """Get prices for portfolio symbols"""
        
        portfolio = {}
        
        for symbol in symbols:
            price_data = await self.get_price(symbol, futures=False)
            
            # Verify quality
            if await self.verify_data_quality(price_data):
                portfolio[symbol] = price_data
            else:
                # SKIP invalid data (don't use mock!)
                logger.warning(f"⚠️ Skipping {symbol} - no valid data available")
        
        return portfolio
