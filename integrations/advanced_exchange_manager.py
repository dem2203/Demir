"""
Advanced Exchange Manager - WebSocket & REST API Lifecycle Management
DEMIR AI v6.0 - Phase 4 Production Grade

Binance, Bybit, Coinbase arası geçişi yönetiyor
WebSocket yaşam döngüsü, callback sistemi, failover handling
Gerçek veri doğrulaması ile mock data tespiti yapıyor
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass, field, asdict
from enum import Enum
import traceback

# Real-time data verification
from utils.real_data_verifier_pro import RealDataVerifier, MockDataDetector


logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """Desteklenen borsalar"""
    BINANCE = "binance"
    BYBIT = "bybit"
    COINBASE = "coinbase"


class ConnectionStatus(Enum):
    """Bağlantı durumları"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ExchangeConfig:
    """Borsa konfigürasyonu"""
    exchange_type: ExchangeType
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None  # Coinbase için
    testnet: bool = False
    timeout: int = 30
    max_retries: int = 5
    retry_delay: float = 1.0


@dataclass
class StreamData:
    """WebSocket stream veri yapısı"""
    exchange: str
    symbol: str
    timestamp: float
    price: float
    quantity: float
    bid: float
    ask: float
    bid_qty: float
    ask_qty: float
    volume_24h: float
    percent_change_24h: float
    high_24h: float
    low_24h: float
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Dict'e dönüştür"""
        return asdict(self)
    
    def validate(self) -> bool:
        """Veri doğrulaması"""
        if not isinstance(self.price, (int, float)) or self.price <= 0:
            return False
        if not isinstance(self.quantity, (int, float)) or self.quantity < 0:
            return False
        if self.bid >= self.ask:
            return False
        return True


class RealDataValidator:
    """Gerçek veri doğrulaması - Fake/Mock data tespiti"""
    
    def __init__(self, verifier: RealDataVerifier):
        """
        Args:
            verifier: RealDataVerifier instance
        """
        self.verifier = verifier
        self.detector = MockDataDetector()
        self.last_price_cache: Dict[str, float] = {}
        self.last_timestamp_cache: Dict[str, float] = {}
    
    def validate_stream(self, data: StreamData) -> Tuple[bool, str]:
        """
        Stream veri doğrulaması
        
        Returns:
            (is_valid, message)
        """
        symbol = data.symbol
        
        # Mock/fake data tespiti
        if self.detector.is_suspicious(data.to_dict()):
            return False, "Mock/fake data detected"
        
        # Fiyat doğrulaması
        if symbol in self.last_price_cache:
            last_price = self.last_price_cache[symbol]
            price_change = abs(data.price - last_price) / last_price
            if price_change > 0.10:  # 10% hızlı değişim şüpheli
                logger.warning(f"Suspicious price change for {symbol}: {price_change*100:.2f}%")
        
        # Zaman damgası doğrulaması
        if symbol in self.last_timestamp_cache:
            last_ts = self.last_timestamp_cache[symbol]
            if data.timestamp <= last_ts:
                return False, "Invalid timestamp - not advancing"
        
        # Bid-Ask spread doğrulaması
        spread = (data.ask - data.bid) / data.bid if data.bid > 0 else 0
        if spread > 0.01:  # 1% spread şüpheli
            logger.warning(f"Large bid-ask spread for {symbol}: {spread*100:.2f}%")
        
        # Gerçek veri doğrulaması
        is_real, msg = self.verifier.verify_price(symbol, data.price)
        if not is_real:
            return False, f"Real data verification failed: {msg}"
        
        # Cache'i güncelle
        self.last_price_cache[symbol] = data.price
        self.last_timestamp_cache[symbol] = data.timestamp
        
        return True, "Valid"


class ExchangeConnector:
    """Borsa bağlantısı - WebSocket & REST"""
    
    def __init__(self, config: ExchangeConfig):
        """
        Args:
            config: ExchangeConfig
        """
        self.config = config
        self.status = ConnectionStatus.DISCONNECTED
        self.websocket = None
        self.session = None
        self.data_validator = RealDataValidator(RealDataVerifier())
        
        self.callbacks: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.reconnect_attempts = 0
        self.last_heartbeat = time.time()
    
    async def connect(self) -> bool:
        """Bağlan"""
        try:
            self.status = ConnectionStatus.CONNECTING
            
            if self.config.exchange_type == ExchangeType.BINANCE:
                await self._connect_binance()
            elif self.config.exchange_type == ExchangeType.BYBIT:
                await self._connect_bybit()
            elif self.config.exchange_type == ExchangeType.COINBASE:
                await self._connect_coinbase()
            
            self.status = ConnectionStatus.CONNECTED
            self.reconnect_attempts = 0
            logger.info(f"Connected to {self.config.exchange_type.value}")
            return True
        
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.status = ConnectionStatus.FAILED
            return False
    
    async def _connect_binance(self):
        """Binance WebSocket bağlantısı"""
        import websockets
        
        url = "wss://stream.binance.com:9443/ws"
        self.websocket = await websockets.connect(url)
        
        # Stream subscribe
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": ["btcusdt@trade", "ethusdt@trade", "ltcusdt@trade"],
            "id": 1
        }
        await self.websocket.send(json.dumps(subscribe_msg))
        
        # Mesaj dinleme döngüsü
        asyncio.create_task(self._binance_stream_handler())
    
    async def _connect_bybit(self):
        """Bybit WebSocket bağlantısı"""
        import websockets
        
        url = "wss://stream.bybit.com/v5/public/linear"
        self.websocket = await websockets.connect(url)
        
        subscribe_msg = {
            "op": "subscribe",
            "args": ["tickers.BTCUSDT", "tickers.ETHUSDT", "tickers.LTCUSDT"]
        }
        await self.websocket.send(json.dumps(subscribe_msg))
        
        asyncio.create_task(self._bybit_stream_handler())
    
    async def _connect_coinbase(self):
        """Coinbase WebSocket bağlantısı"""
        import websockets
        
        url = "wss://ws-feed.exchange.coinbase.com"
        self.websocket = await websockets.connect(url)
        
        subscribe_msg = {
            "type": "subscribe",
            "product_ids": ["BTC-USD", "ETH-USD", "LTC-USD"],
            "channels": ["ticker"]
        }
        await self.websocket.send(json.dumps(subscribe_msg))
        
        asyncio.create_task(self._coinbase_stream_handler())
    
    async def _binance_stream_handler(self):
        """Binance mesaj işlemesi"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if "e" in data and data["e"] == "trade":
                    stream_data = StreamData(
                        exchange="binance",
                        symbol=data["s"],
                        timestamp=data["T"] / 1000,
                        price=float(data["p"]),
                        quantity=float(data["q"]),
                        bid=float(data.get("b", data["p"])),
                        ask=float(data.get("a", data["p"])),
                        bid_qty=float(data.get("B", 0)),
                        ask_qty=float(data.get("A", 0)),
                        volume_24h=float(data.get("v", 0)),
                        percent_change_24h=float(data.get("P", 0)),
                        high_24h=float(data.get("h", 0)),
                        low_24h=float(data.get("l", 0)),
                        metadata={"trade_id": data.get("t")}
                    )
                    
                    # Doğrulama
                    is_valid, msg = self.data_validator.validate_stream(stream_data)
                    if is_valid:
                        await self.message_queue.put(stream_data)
                        await self._trigger_callbacks("data", stream_data)
                    else:
                        logger.warning(f"Invalid stream data: {msg}")
        
        except Exception as e:
            logger.error(f"Binance stream handler error: {e}")
            await self.reconnect()
    
    async def _bybit_stream_handler(self):
        """Bybit mesaj işlemesi"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if "data" in data and "tickers" in data["data"]:
                    for ticker in data["data"]["tickers"]:
                        stream_data = StreamData(
                            exchange="bybit",
                            symbol=ticker["symbol"],
                            timestamp=time.time(),
                            price=float(ticker["lastPrice"]),
                            quantity=float(ticker["volume24h"]),
                            bid=float(ticker["bid1Price"]),
                            ask=float(ticker["ask1Price"]),
                            bid_qty=float(ticker["bid1Size"]),
                            ask_qty=float(ticker["ask1Size"]),
                            volume_24h=float(ticker["volume24h"]),
                            percent_change_24h=float(ticker["price24hPcnt"]),
                            high_24h=float(ticker["highPrice24h"]),
                            low_24h=float(ticker["lowPrice24h"]),
                            metadata={"turnover_24h": ticker.get("turnover24h")}
                        )
                        
                        is_valid, msg = self.data_validator.validate_stream(stream_data)
                        if is_valid:
                            await self.message_queue.put(stream_data)
                            await self._trigger_callbacks("data", stream_data)
                        else:
                            logger.warning(f"Invalid stream data: {msg}")
        
        except Exception as e:
            logger.error(f"Bybit stream handler error: {e}")
            await self.reconnect()
    
    async def _coinbase_stream_handler(self):
        """Coinbase mesaj işlemesi"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get("type") == "ticker":
                    stream_data = StreamData(
                        exchange="coinbase",
                        symbol=data["product_id"],
                        timestamp=datetime.fromisoformat(data["time"].replace("Z", "+00:00")).timestamp(),
                        price=float(data["price"]),
                        quantity=float(data["last_size"]),
                        bid=float(data["best_bid"]),
                        ask=float(data["best_ask"]),
                        bid_qty=float(data.get("best_bid_size", 0)),
                        ask_qty=float(data.get("best_ask_size", 0)),
                        volume_24h=float(data.get("volume", 0)),
                        percent_change_24h=float(data.get("percent_change", 0)),
                        high_24h=float(data.get("high_24h", 0)),
                        low_24h=float(data.get("low_24h", 0)),
                        metadata={"sequence": data.get("sequence")}
                    )
                    
                    is_valid, msg = self.data_validator.validate_stream(stream_data)
                    if is_valid:
                        await self.message_queue.put(stream_data)
                        await self._trigger_callbacks("data", stream_data)
                    else:
                        logger.warning(f"Invalid stream data: {msg}")
        
        except Exception as e:
            logger.error(f"Coinbase stream handler error: {e}")
            await self.reconnect()
    
    def register_callback(self, event: str, callback: Callable):
        """Callback kaydı"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    async def _trigger_callbacks(self, event: str, *args):
        """Callback çalıştır"""
        if event in self.callbacks:
            tasks = [
                asyncio.create_task(callback(*args))
                if asyncio.iscoroutinefunction(callback)
                else callback(*args)
                for callback in self.callbacks[event]
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def reconnect(self):
        """Yeniden bağlan"""
        self.status = ConnectionStatus.RECONNECTING
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > self.config.max_retries:
            self.status = ConnectionStatus.FAILED
            logger.error(f"Max reconnection attempts reached for {self.config.exchange_type.value}")
            return
        
        delay = self.config.retry_delay * (2 ** self.reconnect_attempts)
        logger.info(f"Reconnecting to {self.config.exchange_type.value} in {delay}s (attempt {self.reconnect_attempts})")
        await asyncio.sleep(delay)
        
        if self.websocket:
            await self.websocket.close()
        
        await self.connect()
    
    async def get_data(self, timeout: Optional[float] = None) -> Optional[StreamData]:
        """Veri oku"""
        try:
            return await asyncio.wait_for(self.message_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    async def close(self):
        """Kapat"""
        self.status = ConnectionStatus.DISCONNECTED
        if self.websocket:
            await self.websocket.close()
        logger.info(f"Closed connection to {self.config.exchange_type.value}")


class AdvancedExchangeManager:
    """İleri Borsa Yöneticisi - Multi-exchange failover"""
    
    def __init__(self):
        """Başlat"""
        self.connectors: Dict[ExchangeType, ExchangeConnector] = {}
        self.active_exchange: Optional[ExchangeType] = None
        self.config_list: List[ExchangeConfig] = []
        self.health_check_interval = 30  # saniye
        self.last_data_time: Dict[ExchangeType, float] = {}
    
    def add_exchange(self, config: ExchangeConfig):
        """Borsa ekle"""
        self.config_list.append(config)
    
    async def initialize(self) -> bool:
        """Başlangıç - Birinci borsaya bağlan"""
        for config in self.config_list:
            connector = ExchangeConnector(config)
            
            if await connector.connect():
                self.connectors[config.exchange_type] = connector
                self.active_exchange = config.exchange_type
                logger.info(f"Initialized with {config.exchange_type.value}")
                
                # Health check döngü başlat
                asyncio.create_task(self._health_check_loop())
                return True
        
        logger.error("Failed to initialize any exchange")
        return False
    
    async def _health_check_loop(self):
        """Sistem sağlık kontrolü"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                if self.active_exchange:
                    connector = self.connectors.get(self.active_exchange)
                    if connector and connector.status != ConnectionStatus.CONNECTED:
                        logger.warning(f"Active exchange {self.active_exchange.value} is not connected")
                        await self._failover()
            
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _failover(self):
        """Yedek borsaya geç"""
        logger.warning("Initiating failover to backup exchange")
        
        for exchange_type, connector in self.connectors.items():
            if exchange_type != self.active_exchange:
                if connector.status == ConnectionStatus.CONNECTED:
                    self.active_exchange = exchange_type
                    logger.info(f"Failed over to {exchange_type.value}")
                    return
        
        logger.error("No backup exchanges available")
    
    async def get_live_data(self) -> Optional[StreamData]:
        """Canlı veri al"""
        if not self.active_exchange:
            return None
        
        connector = self.connectors.get(self.active_exchange)
        if not connector:
            return None
        
        return await connector.get_data(timeout=5.0)
    
    async def close_all(self):
        """Tümünü kapat"""
        for connector in self.connectors.values():
            await connector.close()


# Kullanım örneği
async def main():
    """Test"""
    manager = AdvancedExchangeManager()
    
    # Binance config
    binance_config = ExchangeConfig(
        exchange_type=ExchangeType.BINANCE,
        api_key="your_binance_key",
        api_secret="your_binance_secret",
        testnet=False
    )
    
    manager.add_exchange(binance_config)
    
    if await manager.initialize():
        # 10 veri oku
        for _ in range(10):
            data = await manager.get_live_data()
            if data:
                print(f"{data.exchange} - {data.symbol}: ${data.price}")
    
    await manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
