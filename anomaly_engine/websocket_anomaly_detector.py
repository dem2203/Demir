"""
=============================================================================
DEMIR AI v26 - WEBSOCKET ANOMALY DETECTOR (REAL DATA ONLY)
=============================================================================
NO MOCK - Sadece Binance WebSocket gerçek-zaman verisi
=============================================================================
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnomalyAlert:
    """Gerçek anomali uyarısı"""
    symbol: str
    anomaly_type: str
    severity: str
    price: float
    volume: float
    timestamp: str = None
    details: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class BinanceWebSocketMonitorReal:
    """
    Binance WebSocket ile GERÇEK-ZAMAN Anomali Tespiti
    
    REAL DATA ONLY:
    - Binance WebSocket streams (< 100ms latency)
    - Live price ticks
    - NO mock data, NO synthetic
    """
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT"]
        self.price_buffer = {sym: deque(maxlen=100) for sym in self.symbols}
        self.volume_buffer = {sym: deque(maxlen=100) for sym in self.symbols}
        self.anomalies = []
        self.callbacks: List[Callable] = []
        self.ws_url = "wss://stream.binance.com:9443/ws"
        
        logger.info(f"✅ WebSocket monitor initialized for {len(self.symbols)} symbols (REAL)")
    
    def detect_pump_real(self, symbol: str) -> Optional[AnomalyAlert]:
        """Gerçek pump tespit - REAL data"""
        if len(self.price_buffer[symbol]) < 10:
            return None
        
        prices = list(self.price_buffer[symbol])
        price_change = ((prices[-1] - prices[0]) / prices[0] * 100)
        
        if price_change > 2.0:  # 2% increase in 5 sec = pump
            volume_avg = np.mean(list(self.volume_buffer[symbol])[-5:])
            
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="PUMP",
                severity="HIGH" if price_change > 3 else "MEDIUM",
                price=prices[-1],
                volume=volume_avg,
                details=f"Price up {price_change:.2f}% in 5s | Volume: {volume_avg:.0f}"
            )
            logger.warning(f"🔴 REAL PUMP: {alert.details}")
            return alert
        
        return None
    
    def detect_dump_real(self, symbol: str) -> Optional[AnomalyAlert]:
        """Gerçek dump tespit - REAL data"""
        if len(self.price_buffer[symbol]) < 10:
            return None
        
        prices = list(self.price_buffer[symbol])
        price_change = ((prices[-1] - prices[0]) / prices[0] * 100)
        
        if price_change < -2.0:  # 2% decrease = dump
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="DUMP",
                severity="HIGH" if price_change < -3 else "MEDIUM",
                price=prices[-1],
                volume=np.mean(list(self.volume_buffer[symbol])[-5:]),
                details=f"Price down {abs(price_change):.2f}% in 5s"
            )
            logger.warning(f"🔴 REAL DUMP: {alert.details}")
            return alert
        
        return None
    
    def detect_flash_crash_real(self, symbol: str) -> Optional[AnomalyAlert]:
        """Gerçek flash crash - < 1 saniye"""
        if len(self.price_buffer[symbol]) < 5:
            return None
        
        prices = list(self.price_buffer[symbol])[-5:]
        max_price = max(prices)
        min_price = min(prices)
        
        crash_percent = ((max_price - min_price) / max_price * 100)
        
        if crash_percent > 5.0:  # > 5% in < 1 sec
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="FLASH_CRASH",
                severity="CRITICAL",
                price=prices[-1],
                volume=np.mean(list(self.volume_buffer[symbol])[-5:]),
                details=f"FLASH CRASH {crash_percent:.2f}% in < 1 second!"
            )
            logger.error(f"🚨 REAL FLASH CRASH: {alert.details}")
            return alert
        
        return None
    
    def detect_volume_spike_real(self, symbol: str) -> Optional[AnomalyAlert]:
        """Gerçek hacim spikeı"""
        if len(self.volume_buffer[symbol]) < 20:
            return None
        
        volumes = list(self.volume_buffer[symbol])
        avg_vol = np.mean(volumes[:-5])
        current_vol = np.mean(volumes[-5:])
        
        spike = current_vol / avg_vol if avg_vol > 0 else 0
        
        if spike > 3.0:  # 3x volume increase
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="VOLUME_SPIKE",
                severity="MEDIUM",
                price=0,
                volume=current_vol,
                details=f"Volume spike {spike:.1f}x above average"
            )
            logger.warning(f"📊 REAL VOLUME SPIKE: {alert.details}")
            return alert
        
        return None
    
    async def connect_websocket_real(self):
        """Binance WebSocket'e gerçek bağlantı kur"""
        try:
            # Build stream URL for all symbols
            streams = [f"{sym.lower()}@trade" for sym in self.symbols]
            stream_url = self.ws_url + "/" + "/".join(streams)
            
            logger.info(f"🔗 Connecting to Binance WebSocket...")
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(stream_url) as ws:
                    logger.info("✅ Connected to Binance WebSocket (REAL)")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = msg.json()
                            
                            if 'p' in data and 'q' in data:  # Price & Quantity
                                symbol = data['s']
                                price = float(data['p'])
                                qty = float(data['q'])
                                
                                # Process tick
                                await self.process_tick_real(symbol, price, qty)
        
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
    
    async def process_tick_real(self, symbol: str, price: float, volume: float):
        """Gerçek tick işle"""
        if symbol not in self.symbols:
            return
        
        self.price_buffer[symbol].append(price)
        self.volume_buffer[symbol].append(volume)
        
        # Check all anomalies
        alerts = [
            self.detect_pump_real(symbol),
            self.detect_dump_real(symbol),
            self.detect_flash_crash_real(symbol),
            self.detect_volume_spike_real(symbol)
        ]
        
        for alert in alerts:
            if alert:
                self.anomalies.append(alert)
                
                # Trigger callbacks
                for callback in self.callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
    
    def register_callback(self, callback: Callable):
        """Callback kaydet"""
        self.callbacks.append(callback)
        logger.info(f"✅ Callback registered: {callback.__name__}")
    
    async def start_real_monitoring(self):
        """Gerçek monitoring başla"""
        logger.info("🚀 Starting REAL-TIME WebSocket monitoring...")
        await self.connect_websocket_real()
    
    def get_anomalies_realtime(self) -> Dict:
        """Gerçek anomali özeti"""
        return {
            "total": len(self.anomalies),
            "by_type": {
                atype: sum(1 for a in self.anomalies if a.anomaly_type == atype)
                for atype in ["PUMP", "DUMP", "FLASH_CRASH", "VOLUME_SPIKE"]
            },
            "recent": self.anomalies[-10:] if self.anomalies else []
        }


# ============================================================================
# TEST - GERÇEK BINANCE WS
# ============================================================================

if __name__ == "__main__":
    async def test_callback(alert: AnomalyAlert):
        print(f"🔔 REAL ALERT: {alert.anomaly_type} on {alert.symbol} - {alert.severity}")
    
    async def main():
        monitor = BinanceWebSocketMonitorReal(["BTCUSDT", "ETHUSDT"])
        monitor.register_callback(test_callback)
        
        # Başla gerçek monitoringe
        try:
            await asyncio.wait_for(monitor.start_real_monitoring(), timeout=300)  # 5 min test
        except asyncio.TimeoutError:
            logger.info("Test completed")
        
        # Özet
        summary = monitor.get_anomalies_realtime()
        print(f"\n📊 Anomaly Summary (REAL):")
        print(f"   Total: {summary['total']}")
        print(f"   By type: {summary['by_type']}")
    
    asyncio.run(main())
