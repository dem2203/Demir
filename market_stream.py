#!/usr/bin/env python3
"""
🔱 DEMIR AI - Market Stream v1.0
Real-time WebSocket data from Binance Futures

KURALLAR:
✅ Binance WebSocket stream
✅ Real-time price updates (1 saniye)
✅ Database write (tick data)
✅ Error handling + reconnect
✅ ZERO MOCK - live market data only
"""

import os
import psycopg2
import logging
import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Optional

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
BINANCE_WS_URL = "wss://fstream.binance.com/ws"
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# MARKET STREAM
# ============================================================================

class BinanceMarketStream:
    """Connect to Binance WebSocket for real-time data"""
    
    def __init__(self):
        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.ws = None
        self.is_connected = False
        logger.info("✅ Market stream initialized")
    
    async def connect(self):
        """Connect to Binance WebSocket"""
        try:
            streams = [f"{symbol.lower()}@kline_1m" for symbol in SYMBOLS]
            stream_url = "/".join(streams)
            full_url = f"{BINANCE_WS_URL}/{stream_url}"
            
            logger.info(f"📡 Connecting to Binance WebSocket...")
            
            self.ws = await websockets.connect(full_url)
            self.is_connected = True
            
            logger.info("✅ Connected to Binance WebSocket")
            return True
        
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.is_connected = False
            return False
    
    async def stream_data(self):
        """Stream data from WebSocket"""
        try:
            while self.is_connected:
                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                    data = json.loads(message)
                    
                    await self.process_kline(data)
                
                except asyncio.TimeoutError:
                    logger.warning("⚠️ WebSocket timeout - reconnecting...")
                    await self.reconnect()
                
                except Exception as e:
                    logger.error(f"❌ Stream error: {e}")
                    await self.reconnect()
        
        except Exception as e:
            logger.critical(f"❌ Streaming failed: {e}")
    
    async def process_kline(self, data: Dict):
        """Process kline (candlestick) data"""
        try:
            kline = data.get('k', {})
            
            symbol = kline.get('s')
            close_price = float(kline.get('c'))
            timestamp = datetime.fromtimestamp(kline.get('T') / 1000)
            
            # Save to database
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO market_data_ticks
                (timestamp, symbol, price, volume)
                VALUES (%s, %s, %s, %s)
            """
            
            cur.execute(insert_query, (
                timestamp,
                symbol,
                close_price,
                float(kline.get('v', 0))
            ))
            
            self.db_conn.commit()
            cur.close()
            
            logger.debug(f"💹 {symbol}: ${close_price}")
        
        except Exception as e:
            logger.error(f"❌ Kline processing failed: {e}")
    
    async def reconnect(self):
        """Reconnect to WebSocket"""
        logger.info("🔄 Reconnecting to WebSocket...")
        
        if self.ws:
            await self.ws.close()
        
        await asyncio.sleep(5)
        await self.connect()
    
    def close(self):
        """Close connection"""
        self.is_connected = False
        if self.db_conn:
            self.db_conn.close()
        logger.info("✅ Stream closed")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - MARKET STREAM v1.0")
        logger.info("=" * 80)
        
        stream = BinanceMarketStream()
        
        if await stream.connect():
            await stream.stream_data()
        
        stream.close()
    
    except KeyboardInterrupt:
        logger.info("🛑 Stream stopped by user")
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
