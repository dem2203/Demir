"""
=============================================================================
DEMIR AI - MULTI-SOURCE API DATA MANAGER (High-Frequency)
=============================================================================
Purpose: Binance, CoinGecko, Glassnode, OnChain, News paralel veri çekimi
Location: /data/ klasörü
=============================================================================
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Veri kaynağı"""
    name: str
    url: str
    api_key: str = None
    update_interval: int = 5  # seconds
    last_update: float = 0
    status: str = "UNKNOWN"


class MultiSourceDataManager:
    """
    Çoklu Kaynak Veri Yöneticisi
    
    Features:
    - Parallel data fetching
    - High-frequency updates (sub-second)
    - API key management
    - Fallback & caching
    - Rate limiting
    """
    
    def __init__(self):
        self.sources = {
            "binance_spot": DataSource("Binance Spot", "https://api.binance.com"),
            "binance_futures": DataSource("Binance Futures", "https://fapi.binance.com"),
            "coingecko": DataSource("CoinGecko", "https://api.coingecko.com"),
            "glassnode": DataSource("Glassnode", "https://api.glassnode.com", api_key="YOUR_KEY"),
            "nansen": DataSource("Nansen", "https://api.nansen.ai", api_key="YOUR_KEY"),
            "santiment": DataSource("Santiment", "https://api.santiment.net", api_key="YOUR_KEY"),
        }
        
        self.cache = {}
        self.rate_limits = {}
    
    async def fetch_all_sources(self, symbols: List[str]) -> Dict:
        """Tüm kaynaklardan paralel veri çek"""
        logger.info(f"🔄 Fetching data from {len(self.sources)} sources...")
        
        start_time = time.time()
        
        # Create tasks for all sources
        tasks = []
        
        for source_name, source in self.sources.items():
            task = self._fetch_from_source(source_name, source, symbols)
            tasks.append(task)
        
        # Run in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        
        data = {name: result for name, result in zip(self.sources.keys(), results)}
        
        logger.info(f"✅ Data fetch completed in {elapsed:.2f}s")
        return data
    
    async def _fetch_from_source(self, source_name: str, source: DataSource, 
                                 symbols: List[str]) -> Dict:
        """Bir kaynaktan veri çek"""
        try:
            # Check rate limit
            if not self._check_rate_limit(source_name):
                logger.warning(f"⏱️ Rate limited: {source_name}")
                return {"status": "RATE_LIMITED"}
            
            # Check cache
            cache_key = f"{source_name}_{str(symbols)}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if time.time() - cached_data['timestamp'] < source.update_interval:
                    logger.debug(f"📦 Using cache for {source_name}")
                    return cached_data['data']
            
            # Fetch data (mock)
            data = {
                "source": source_name,
                "symbols": symbols,
                "prices": {sym: 50000 + hash(sym) % 1000 for sym in symbols},
                "timestamp": datetime.now().isoformat(),
                "status": "OK"
            }
            
            # Cache it
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            
            logger.info(f"✅ {source_name}: OK ({len(symbols)} symbols)")
            return data
        
        except Exception as e:
            logger.error(f"❌ {source_name} error: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    def _check_rate_limit(self, source_name: str) -> bool:
        """Rate limit kontrol et"""
        now = time.time()
        
        if source_name not in self.rate_limits:
            self.rate_limits[source_name] = now
            return True
        
        elapsed = now - self.rate_limits[source_name]
        
        # Different rate limits per source
        limits = {
            "binance_spot": 0.1,      # 100ms
            "binance_futures": 0.1,
            "coingecko": 1.0,         # 1sec (free tier)
            "glassnode": 2.0,         # 2sec
            "nansen": 5.0,            # 5sec
            "santiment": 2.0          # 2sec
        }
        
        limit = limits.get(source_name, 1.0)
        
        if elapsed >= limit:
            self.rate_limits[source_name] = now
            return True
        
        return False
    
    def get_aggregated_price(self, symbol: str, data: Dict) -> Optional[float]:
        """Tüm kaynaklardan aggregated fiyat al"""
        prices = []
        
        for source_name, source_data in data.items():
            if isinstance(source_data, dict) and source_data.get('status') == 'OK':
                if 'prices' in source_data and symbol in source_data['prices']:
                    prices.append(source_data['prices'][symbol])
        
        if prices:
            avg_price = sum(prices) / len(prices)
            logger.info(f"📊 Aggregated {symbol}: ${avg_price:.2f} (from {len(prices)} sources)")
            return avg_price
        
        return None
    
    def set_api_key(self, source_name: str, api_key: str):
        """API key ayarla"""
        if source_name in self.sources:
            self.sources[source_name].api_key = api_key
            logger.info(f"✅ API key set for {source_name}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    async def main():
        manager = MultiSourceDataManager()
        
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        # Fetch from all sources
        data = await manager.fetch_all_sources(symbols)
        
        # Get aggregated prices
        for symbol in symbols:
            price = manager.get_aggregated_price(symbol, data)
    
    asyncio.run(main())
