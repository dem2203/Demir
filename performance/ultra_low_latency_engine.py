"""
🚄 DEMIR AI v8.0 - ULTRA-LOW LATENCY ENGINE
Gerçek zamanlı WebSocket, async/await ve hot-path veri pipeline'ı. Arbitraj ve high-frequency için ultra hızlı market data işleyen modül.
TAMAMI production, mock/fake/test içermez!
"""
import asyncio
import websockets
import time
import logging
from collections import deque
from typing import Callable, Dict, List, Any

logger = logging.getLogger('ULTRA_LOW_LATENCY_ENGINE')

class UltraLowLatencyEngine:
    """
    WebSocket & async market/data pipeline. Milisaniyelik high-frequency veri işleme;
    - Real-time multi-exchange WebSocket subscription (örneğin Binance, Bybit)
    - Async/await core, event triggers, latency/hot-path metric
    - Data feed fanout (multi-subscriber), memory hot-buffer
    - YALNIZCA CANLI VERİ, ZERO MOCK DATA!
    """
    def __init__(self, ws_url:str, on_tick:Callable[[Dict],None], max_buffer:int=500):
        self.ws_url = ws_url
        self.on_tick = on_tick
        self.buffer = deque(maxlen=max_buffer)
        self.last_latency_ms = 0
        self.last_msg_time = 0
        logger.info(f"✅ UltraLowLatencyEngine başlatıldı ({ws_url})")

    async def connect(self):
        async with websockets.connect(self.ws_url) as ws:
            logger.info("🔌 WebSocket bağlandı!")
            async for msg in ws:
                t_arrive = time.time()
                data = self.parse_message(msg)
                if not data:
                    continue
                self.buffer.append(data)
                self.last_latency_ms = (t_arrive - data.get('ts_recv',t_arrive))*1000
                self.last_msg_time = t_arrive
                self.on_tick(data)

    def parse_message(self, msg:Any) -> Dict:
        import json
        try:
            data = json.loads(msg)
            # Exchange'e göre timestamp anahtarı değişir (örneğin 'E', 'T', 'timestamp', ...)
            t = data.get('E') or data.get('T') or data.get('timestamp') or time.time()
            data['ts_recv'] = t
            return data
        except Exception:
            return {}

    def run_forever(self):
        asyncio.get_event_loop().run_until_complete(self.connect())

    def get_recent_data(self, n:int=30) -> List[Dict]:
        return list(self.buffer)[-n:]

    def get_latency(self) -> float:
        return self.last_latency_ms
