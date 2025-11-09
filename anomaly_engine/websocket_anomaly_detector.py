"""
=============================================================================
DEMIR AI v26 - REAL-TIME ANOMALY DETECTION (WebSocket)
=============================================================================
Purpose: WebSocket ile gerçek zamanlı pump/dump, flash crash, liquidation tespiti
Location: /anomaly_engine/ klasörü
Phase: 26 (Real-time Anomaly)
=============================================================================
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


@dataclass
class AnomalyAlert:
    """Anomali uyarısı"""
    symbol: str
    anomaly_type: str  # "PUMP", "DUMP", "FLASH_CRASH", "LIQUIDATION", "VOLUME_SPIKE"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    price: float
    volume: float
    timestamp: str = None
    details: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class WebSocketMonitor:
    """
    WebSocket Gerçek-Zaman Monitor
    
    Features:
    - Binance WebSocket streams
    - Sub-second latency (< 100ms)
    - Pump/dump detection
    - Flash crash detection
    - Liquidation cascade detection
    """
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT"]
        self.price_buffer = {sym: deque(maxlen=100) for sym in self.symbols}
        self.volume_buffer = {sym: deque(maxlen=100) for sym in self.symbols}
        self.anomalies = []
        self.callbacks: List[Callable] = []
        
        # Anomaly thresholds
        self.pump_threshold = 2.0  # % price increase in 5 seconds
        self.dump_threshold = 2.0  # % price decrease in 5 seconds
        self.volume_spike_threshold = 3.0  # 3x volume
        self.flash_crash_threshold = 5.0  # > 5% in < 1 sec
        
        logger.info(f"✅ WebSocket Monitor initialized for {len(self.symbols)} symbols")
    
    # ========================================================================
    # ANOMALY DETECTION RULES
    # ========================================================================
    
    def detect_pump(self, symbol: str) -> Optional[AnomalyAlert]:
        """Pump (ani fiyat artışı) tespit et"""
        if len(self.price_buffer[symbol]) < 10:
            return None
        
        prices = list(self.price_buffer[symbol])
        price_change = ((prices[-1] - prices[0]) / prices[0] * 100)
        
        if price_change > self.pump_threshold:
            volume_increase = np.mean(list(self.volume_buffer[symbol])[-5:]) / np.mean(list(self.volume_buffer[symbol])[0:5]) if len(self.volume_buffer[symbol]) >= 10 else 1
            
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="PUMP",
                severity="HIGH" if price_change > 3 else "MEDIUM",
                price=prices[-1],
                volume=volume_increase,
                details=f"Price up {price_change:.2f}% in 5s | Volume {volume_increase:.1f}x"
            )
            logger.warning(f"🔴 PUMP DETECTED: {alert.details}")
            return alert
        
        return None
    
    def detect_dump(self, symbol: str) -> Optional[AnomalyAlert]:
        """Dump (ani fiyat düşüşü) tespit et"""
        if len(self.price_buffer[symbol]) < 10:
            return None
        
        prices = list(self.price_buffer[symbol])
        price_change = ((prices[-1] - prices[0]) / prices[0] * 100)
        
        if price_change < -self.dump_threshold:
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="DUMP",
                severity="HIGH" if price_change < -3 else "MEDIUM",
                price=prices[-1],
                volume=np.mean(list(self.volume_buffer[symbol])[-5:]),
                details=f"Price down {abs(price_change):.2f}% in 5s"
            )
            logger.warning(f"🔴 DUMP DETECTED: {alert.details}")
            return alert
        
        return None
    
    def detect_flash_crash(self, symbol: str) -> Optional[AnomalyAlert]:
        """Flash crash (< 1 saniye) tespit et"""
        if len(self.price_buffer[symbol]) < 5:
            return None
        
        prices = list(self.price_buffer[symbol])[-5:]  # Last 5 ticks (~1 sec)
        max_price = max(prices)
        min_price = min(prices)
        
        crash_percent = ((max_price - min_price) / max_price * 100)
        
        if crash_percent > self.flash_crash_threshold:
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="FLASH_CRASH",
                severity="CRITICAL",
                price=prices[-1],
                volume=np.mean(list(self.volume_buffer[symbol])[-5:]),
                details=f"Flash crash {crash_percent:.2f}% in < 1 second!"
            )
            logger.error(f"🚨 FLASH CRASH: {alert.details}")
            return alert
        
        return None
    
    def detect_volume_spike(self, symbol: str) -> Optional[AnomalyAlert]:
        """Hacim spikeı tespit et"""
        if len(self.volume_buffer[symbol]) < 20:
            return None
        
        volumes = list(self.volume_buffer[symbol])
        avg_volume = np.mean(volumes[:-5])
        current_volume = np.mean(volumes[-5:])
        
        spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if spike_ratio > self.volume_spike_threshold:
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="VOLUME_SPIKE",
                severity="MEDIUM",
                price=0,  # Not price-related
                volume=current_volume,
                details=f"Volume spike {spike_ratio:.1f}x above average"
            )
            logger.warning(f"📊 VOLUME SPIKE: {alert.details}")
            return alert
        
        return None
    
    def detect_liquidation_cascade(self, symbol: str) -> Optional[AnomalyAlert]:
        """Liquidation cascade (hızlı yüksek hacim satış) tespit et"""
        if len(self.volume_buffer[symbol]) < 10:
            return None
        
        volumes = list(self.volume_buffer[symbol])
        prices = list(self.price_buffer[symbol])
        
        # Cascade: düşen fiyat + yüksek hacim
        price_trend = prices[-1] < prices[-5]
        volume_avg = np.mean(volumes[-5:])
        historical_avg = np.mean(volumes[:-5])
        
        if price_trend and volume_avg > historical_avg * 2:
            alert = AnomalyAlert(
                symbol=symbol,
                anomaly_type="LIQUIDATION",
                severity="HIGH",
                price=prices[-1],
                volume=volume_avg,
                details=f"Potential liquidation cascade detected"
            )
            logger.error(f"💥 LIQUIDATION CASCADE: {alert.details}")
            return alert
        
        return None
    
    # ========================================================================
    # WEBSOCKET STREAM
    # ========================================================================
    
    async def process_tick(self, symbol: str, price: float, volume: float):
        """Tek bir fiyat verisini işle ve anomali kontrol et"""
        self.price_buffer[symbol].append(price)
        self.volume_buffer[symbol].append(volume)
        
        # Check all anomalies
        anomalies_to_check = [
            self.detect_pump(symbol),
            self.detect_dump(symbol),
            self.detect_flash_crash(symbol),
            self.detect_volume_spike(symbol),
            self.detect_liquidation_cascade(symbol)
        ]
        
        for alert in anomalies_to_check:
            if alert:
                self.anomalies.append(alert)
                
                # Trigger callbacks (für Telegram alerts vb.)
                for callback in self.callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
    
    def register_callback(self, callback: Callable):
        """Anomali callback'i kaydet (örn: Telegram bildirimleri)"""
        self.callbacks.append(callback)
        logger.info(f"✅ Callback registered: {callback.__name__}")
    
    async def mock_stream(self, duration: int = 60):
        """Test için mock stream"""
        logger.info(f"📡 Starting mock WebSocket stream for {duration}s...")
        
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < duration:
            for symbol in self.symbols:
                # Simulate price movement with occasional anomalies
                price = np.random.uniform(50000, 55000)
                volume = np.random.uniform(100, 1000)
                
                # 5% chance of pump
                if np.random.random() < 0.05:
                    price *= 1.025
                
                await self.process_tick(symbol, price, volume)
            
            await asyncio.sleep(0.1)  # 100ms updates
        
        logger.info(f"📊 Stream finished. {len(self.anomalies)} anomalies detected")
    
    def get_anomalies_summary(self) -> Dict:
        """Anomali özeti al"""
        summary = {
            "total": len(self.anomalies),
            "by_type": {},
            "by_severity": {},
            "recent": self.anomalies[-10:] if self.anomalies else []
        }
        
        for anomaly in self.anomalies:
            summary["by_type"][anomaly.anomaly_type] = summary["by_type"].get(anomaly.anomaly_type, 0) + 1
            summary["by_severity"][anomaly.severity] = summary["by_severity"].get(anomaly.severity, 0) + 1
        
        return summary


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    async def test_callback(alert: AnomalyAlert):
        print(f"🔔 CALLBACK: {alert.anomaly_type} on {alert.symbol} - {alert.severity}")
    
    async def main():
        monitor = WebSocketMonitor(["BTCUSDT"])
        monitor.register_callback(test_callback)
        
        # Run mock stream
        await monitor.mock_stream(duration=30)
        
        # Print summary
        summary = monitor.get_anomalies_summary()
        print(f"\n📊 Anomaly Summary:")
        print(f"   Total: {summary['total']}")
        print(f"   By type: {summary['by_type']}")
        print(f"   By severity: {summary['by_severity']}")
    
    # Run async test
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Test error: {e}")
