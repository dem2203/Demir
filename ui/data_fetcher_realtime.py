"""
Real-time Data Fetcher - Canlı Veri Alma ve Önbellekleme
DEMIR AI v6.0 - Phase 4 Production Grade

Binance/Bybit/Coinbase'den canlı OHLCV verisi
Multi-timeframe destekleme, veri validation, caching
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import json
import aiohttp
from collections import defaultdict, deque
import hashlib
import time

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Veri kaynağı"""
    BINANCE = "binance"
    BYBIT = "bybit"
    COINBASE = "coinbase"


@dataclass
class Candle:
    """Mum verisi"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return asdict(self)
    
    def hash(self) -> str:
        """Veri tutarlılığı hash'i"""
        data_str = f"{self.timestamp}{self.open}{self.high}{self.low}{self.close}{self.volume}"
        return hashlib.md5(data_str.encode()).hexdigest()


class CandleCache:
    """Mum verisi cache'i"""
    
    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: Maksimum cache boyutu
        """
        self.cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_size))
        self.last_update: Dict[str, float] = {}
        self.checksums: Dict[str, str] = {}
    
    def add(self, key: str, candle: Candle) -> bool:
        """Mum ekle"""
        
        try:
            self.cache[key].append(candle)
            self.last_update[key] = time.time()
            return True
        except Exception as e:
            logger.error(f"Error adding candle to cache: {e}")
            return False
    
    def get_recent(self, key: str, count: int = 100) -> List[Candle]:
        """En son mumleri al"""
        
        if key not in self.cache:
            return []
        
        candles = list(self.cache[key])
        return candles[-count:]
    
    def get_all(self, key: str) -> List[Candle]:
        """Tüm mumleri al"""
        
        if key not in self.cache:
            return []
        
        return list(self.cache[key])
    
    def get_by_time(
        self,
        key: str,
        start_time: float,
        end_time: float
    ) -> List[Candle]:
        """Zaman aralığında mumleri al"""
        
        if key not in self.cache:
            return []
        
        return [c for c in self.cache[key] 
                if start_time <= c.timestamp <= end_time]
    
    def clear(self, key: str):
        """Cache'i temizle"""
        
        if key in self.cache:
            self.cache[key].clear()


class RealtimeDataFetcher:
    """Canlı Veri Fetcher"""
    
    def __init__(self, source: DataSource = DataSource.BINANCE):
        """
        Args:
            source: Veri kaynağı
        """
        self.source = source
        self.cache = CandleCache(max_size=5000)
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Source-specific URLs
        self.base_urls = {
            DataSource.BINANCE: "https://api.binance.com/api/v3",
            DataSource.BYBIT: "https://api.bybit.com/v5/market",
            DataSource.COINBASE: "https://api.exchange.coinbase.com"
        }
        
        # Timeframe mappings
        self.timeframe_map = {
            "15m": {"binance": "15m", "bybit": "15", "coinbase": "900"},
            "1h": {"binance": "1h", "bybit": "60", "coinbase": "3600"},
            "4h": {"binance": "4h", "bybit": "240", "coinbase": "14400"},
            "1d": {"binance": "1d", "bybit": "D", "coinbase": "86400"}
        }
        
        self.rate_limit_remaining: Dict[str, int] = {}
        self.last_request_time: Dict[str, float] = {}
    
    async def initialize(self) -> bool:
        """Başlat"""
        
        try:
            self.session = aiohttp.ClientSession()
            logger.info(f"Initialized RealtimeDataFetcher with source: {self.source.value}")
            return True
        except Exception as e:
            logger.error(f"Error initializing fetcher: {e}")
            return False
    
    async def close(self):
        """Kapat"""
        
        if self.session:
            await self.session.close()
    
    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100
    ) -> Optional[List[Candle]]:
        """
        Mumleri al
        
        Args:
            symbol: "BTCUSDT"
            timeframe: "15m", "1h", "4h", "1d"
            limit: Kaç mum
        
        Returns:
            Mum listesi veya None
        """
        
        if not self.session:
            logger.error("Session not initialized")
            return None
        
        try:
            cache_key = f"{symbol}_{timeframe}"
            
            # Source'e göre fetch yap
            if self.source == DataSource.BINANCE:
                candles = await self._fetch_binance(symbol, timeframe, limit)
            elif self.source == DataSource.BYBIT:
                candles = await self._fetch_bybit(symbol, timeframe, limit)
            elif self.source == DataSource.COINBASE:
                candles = await self._fetch_coinbase(symbol, timeframe, limit)
            else:
                return None
            
            # Cache'e ekle
            if candles:
                for candle in candles:
                    self.cache.add(cache_key, candle)
            
            return candles
        
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return None
    
    async def _fetch_binance(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> Optional[List[Candle]]:
        """Binance'den fetch yap"""
        
        try:
            url = f"{self.base_urls[DataSource.BINANCE]}/klines"
            
            params = {
                "symbol": symbol,
                "interval": self.timeframe_map[timeframe]["binance"],
                "limit": limit
            }
            
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"Binance API error: {resp.status}")
                    return None
                
                data = await resp.json()
                
                candles = []
                for kline in data:
                    candle = Candle(
                        timestamp=kline[0] / 1000,  # Milliseconds to seconds
                        open=float(kline[1]),
                        high=float(kline[2]),
                        low=float(kline[3]),
                        close=float(kline[4]),
                        volume=float(kline[7])
                    )
                    candles.append(candle)
                
                logger.debug(f"Fetched {len(candles)} candles from Binance for {symbol}")
                return candles
        
        except Exception as e:
            logger.error(f"Error fetching from Binance: {e}")
            return None
    
    async def _fetch_bybit(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> Optional[List[Candle]]:
        """Bybit'ten fetch yap"""
        
        try:
            url = f"{self.base_urls[DataSource.BYBIT]}/kline"
            
            # Bybit symbol formatting
            bybit_symbol = symbol.replace("USDT", "") + "USDT"
            
            params = {
                "category": "linear",
                "symbol": bybit_symbol,
                "interval": self.timeframe_map[timeframe]["bybit"],
                "limit": limit
            }
            
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"Bybit API error: {resp.status}")
                    return None
                
                data = await resp.json()
                
                candles = []
                for kline in data.get("result", {}).get("list", []):
                    candle = Candle(
                        timestamp=float(kline[0]) / 1000,
                        open=float(kline[1]),
                        high=float(kline[2]),
                        low=float(kline[3]),
                        close=float(kline[4]),
                        volume=float(kline[7])
                    )
                    candles.append(candle)
                
                logger.debug(f"Fetched {len(candles)} candles from Bybit for {symbol}")
                return candles
        
        except Exception as e:
            logger.error(f"Error fetching from Bybit: {e}")
            return None
    
    async def _fetch_coinbase(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> Optional[List[Candle]]:
        """Coinbase'ten fetch yap"""
        
        try:
            # Coinbase formatting
            cb_symbol = symbol.replace("USDT", "-USD")
            
            url = f"{self.base_urls[DataSource.COINBASE]}/products/{cb_symbol}/candles"
            
            params = {
                "granularity": self.timeframe_map[timeframe]["coinbase"]
            }
            
            async with self.session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"Coinbase API error: {resp.status}")
                    return None
                
                data = await resp.json()
                
                candles = []
                for kline in data:
                    candle = Candle(
                        timestamp=kline[0],
                        open=float(kline[3]),
                        high=float(kline[2]),
                        low=float(kline[1]),
                        close=float(kline[4]),
                        volume=float(kline[5])
                    )
                    candles.append(candle)
                
                logger.debug(f"Fetched {len(candles)} candles from Coinbase for {symbol}")
                return candles
        
        except Exception as e:
            logger.error(f"Error fetching from Coinbase: {e}")
            return None
    
    def get_cached_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 100
    ) -> List[Candle]:
        """Önbellekten mumleri al"""
        
        cache_key = f"{symbol}_{timeframe}"
        return self.cache.get_recent(cache_key, count)
    
    async def stream_candles(
        self,
        symbol: str,
        timeframe: str,
        interval_seconds: int = 60
    ):
        """
        Mumleri stream et (Generator)
        
        Args:
            symbol: Trading pair
            timeframe: Zaman dilimi
            interval_seconds: Kaç saniyede bir fetch yap
        
        Yields:
            Mum listesi
        """
        
        while True:
            try:
                candles = await self.fetch_candles(symbol, timeframe, limit=100)
                if candles:
                    yield candles
                
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"Error in stream: {e}")
                await asyncio.sleep(interval_seconds)


# Kullanım örneği
async def main():
    """Test"""
    
    fetcher = RealtimeDataFetcher(source=DataSource.BINANCE)
    
    if await fetcher.initialize():
        # Mumleri al
        candles = await fetcher.fetch_candles("BTCUSDT", "1h", limit=100)
        
        if candles:
            print(f"Fetched {len(candles)} candles")
            for candle in candles[-5:]:
                print(f"  {datetime.fromtimestamp(candle.timestamp)}: O={candle.open} C={candle.close}")
        
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())
