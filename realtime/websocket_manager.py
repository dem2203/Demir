"""
WEBSOCKET MANAGER
Robust retry + real-time data streaming
"""

import asyncio
import websockets
import json
import logging

logger = logging.getLogger(__name__)

class RobustWebSocketManager:
    
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.ws = None
        self.reconnect_count = 0
        self.max_reconnect_attempts = 10
    
    async def connect_with_retry(self):
        """Bağlantı retry mantığı"""
        
        while self.reconnect_count < self.max_reconnect_attempts:
            try:
                self.ws = await asyncio.wait_for(
                    websockets.connect(self.stream_url),
                    timeout=5.0
                )
                logger.info("✅ WebSocket connected")
                self.reconnect_count = 0
                
                await self.listen()
                
            except asyncio.TimeoutError:
                logger.warning("⏱️ WebSocket timeout")
                self.reconnect_count += 1
            
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                self.reconnect_count += 1
            
            wait_time = min(2 ** self.reconnect_count, 60)
            logger.info(f"🔄 Reconnecting in {wait_time}s...")
            await asyncio.sleep(wait_time)
        
        logger.critical("❌ Max reconnection attempts reached")
    
    async def listen(self):
        """WebSocket listen loop"""
        
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self.process_realtime_data(data)
        
        except Exception as e:
            logger.error(f"Listen error: {e}")
            await self.connect_with_retry()
    
    async def process_realtime_data(self, data: dict):
        """Real-time veri işle"""
        logger.debug(f"Processing: {data}")
