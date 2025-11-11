# ============================================================================
# LAYER 4: WEBSOCKET REALTIME (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/websocket_realtime_v5.py
# Durum: YENİ (eski mock versiyonu replace et)

import asyncio
import websockets
import json

class WebSocketRealtimeLayer:
    """
    Real WebSocket connection to Binance
    - Live price updates
    - Live order updates
    - Live trade execution
    """
    
    def __init__(self):
        logger.info("✅ WebSocketRealtimeLayer initialized")
        self.ws = None
        self.connected = False

    async def connect_to_stream(self, symbols: list):
        """
        Connect to REAL Binance WebSocket stream
        """
        
        try:
            stream_names = [f"{sym.lower()}@kline_1m" for sym in symbols]
            streams_url = "wss://stream.binance.com:9443/stream?streams=" + "/".join(stream_names)
            
            logger.info(f"🔌 Connecting to WebSocket: {streams_url}")
            
            async with websockets.connect(streams_url) as websocket:
                self.ws = websocket
                self.connected = True
                logger.info("✅ WebSocket connected")
                
                while self.connected:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=30)
                        data = json.loads(message)
                        
                        # Process real data
                        yield data
                        
                    except asyncio.TimeoutError:
                        logger.warning("WebSocket timeout")
                        continue
                    
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise

    def disconnect(self):
        """Disconnect from WebSocket"""
        self.connected = False
        logger.info("🔌 WebSocket disconnected")

