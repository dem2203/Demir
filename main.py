"""
🚀 DEMIR AI v5.2 - Core Signal Generator Engine
📊 Production-Grade Signal Generation Loop
🔐 100% Real Data Policy - NO MOCK, NO FAKE, NO FALLBACK

FIXED: asyncio.sleep → time.sleep
FIXED: INSERT query columns match trades table schema
FIXED: Logging handlers syntax

Location: GitHub Root / main.py (REPLACE EXISTING)
Date: 2025-11-15 23:40 CET
"""

import os
import sys
import logging
import json
import time  # ✅ FIX: Import time instead of asyncio for sleep
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import pytz
from dotenv import load_dotenv
import threading
import queue

load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION - PRODUCTION GRADE
# ============================================================================

# ✅ FIX: Corrected logging handlers syntax
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('DEMIR_AI_MAIN')

# ============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# ============================================================================

class ConfigValidator:
    """Validate all required environment variables"""
    
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'DATABASE_URL',
    ]
    
    @staticmethod
    def validate():
        """Validate all required variables"""
        missing_required = []
        for var in ConfigValidator.REQUIRED_VARS:
            if not os.getenv(var):
                missing_required.append(var)
        
        if missing_required:
            logger.critical(f"❌ MISSING REQUIRED ENV VARS: {missing_required}")
            raise ValueError(f"Missing required environment variables: {missing_required}")
        
        logger.info("✅ Environment validation passed")
        return True

# ============================================================================
# DATABASE CONNECTION MANAGER
# ============================================================================

class DatabaseManager:
    """Manage PostgreSQL connections and queries"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection error: {e}")
            raise
    
    def insert_signal(self, signal_data: Dict) -> bool:
        """
        Insert real signal into database (100% REAL DATA)
        ✅ FIX: Column names match actual trades table schema
        """
        try:
            cursor = self.connection.cursor()
            
            # ✅ FIX: Correct column names from trades table
            query = '''
            INSERT INTO trades (
                symbol, direction, entry_price, tp1, tp2, sl, entry_time, position_size
            ) VALUES (
                %(symbol)s, %(direction)s, %(entry_price)s, %(tp1)s, %(tp2)s,
                %(sl)s, %(entry_time)s, %(position_size)s
            )
            '''
            
            cursor.execute(query, signal_data)
            self.connection.commit()
            cursor.close()
            
            logger.info(f"✅ Signal saved: {signal_data['symbol']} {signal_data['direction']}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Insert signal error: {e}")
            self.connection.rollback()
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Database connection closed")

# ============================================================================
# REAL-TIME API DATA FETCHER
# ============================================================================

class RealTimeDataFetcher:
    """Fetch real-time price data from Binance"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEMIR-AI-v5.2'})
    
    def get_binance_price(self, symbol: str) -> Optional[float]:
        """Get real Binance futures price (100% REAL DATA)"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/ticker/price'
            params = {'symbol': symbol}
            response = self.session.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                logger.debug(f"✅ Binance {symbol}: ${price}")
                return price
            else:
                logger.warning(f"⚠️ Binance API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Binance price fetch error: {e}")
            return None
    
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """Get real OHLCV candlestick data from Binance (100% REAL DATA)"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/klines'
            params = {
                'symbol': symbol,
                'interval': timeframe,
                'limit': limit
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                klines = response.json()
                ohlcv_data = []
                
                for kline in klines:
                    ohlcv_data.append({
                        'timestamp': datetime.fromtimestamp(kline[0] / 1000, tz=pytz.UTC),
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[7])
                    })
                
                logger.info(f"✅ Fetched {len(ohlcv_data)} OHLCV candles for {symbol}")
                return ohlcv_data
            
            return []
            
        except Exception as e:
            logger.error(f"❌ OHLCV fetch error: {e}")
            return []

# ============================================================================
# TELEGRAM NOTIFICATION ENGINE
# ============================================================================

class TelegramNotificationEngine:
    """Send real-time notifications to Telegram"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if self.token and self.chat_id:
            self.api_url = f'https://api.telegram.org/bot{self.token}'
        else:
            self.api_url = None
        
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
    
    def start(self):
        """Start notification worker thread"""
        if not self.api_url:
            logger.warning("⚠️ Telegram not configured (TELEGRAM_TOKEN/CHAT_ID not set)")
            return
        
        self.running = True
        self.worker_thread.start()
        logger.info("✅ Telegram notification engine started")
    
    def _worker(self):
        """Worker thread for async notifications"""
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                self._send_message(message)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Notification worker error: {e}")
    
    def _send_message(self, message: str, retries: int = 3) -> bool:
        """Send message with retry logic"""
        if not self.api_url:
            return False
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    f'{self.api_url}/sendMessage',
                    json={'chat_id': self.chat_id, 'text': message, 'parse_mode': 'HTML'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("✅ Telegram notification sent")
                    return True
                else:
                    logger.warning(f"⚠️ Telegram error (attempt {attempt+1}/{retries}): {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Telegram send error (attempt {attempt+1}/{retries}): {e}")
            
            if attempt < retries - 1:
                time.sleep(1)  # ✅ FIX: Using time.sleep() instead of asyncio.sleep()
        
        return False
    
    def queue_signal_notification(self, signal: Dict):
        """Queue signal notification for async delivery"""
        message = f'''
🚀 YENİ SİNYAL - DEMIR AI v5.2

📍 Coin: {signal['symbol']}
🎯 Yön: {'🟢 LONG' if signal['direction'] == 'LONG' else '🔴 SHORT' if signal['direction'] == 'SHORT' else '⚪ WAIT'}
💰 Giriş: ${signal['entry_price']:.2f}
📈 TP1: ${signal['tp1']:.2f}
📈 TP2: ${signal['tp2']:.2f}
❌ SL: ${signal['sl']:.2f}

⏱️ Zaman: {signal['entry_time']}
Oluşturulan: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}
        '''
        
        if self.api_url:
            self.queue.put(message)
    
    def stop(self):
        """Stop notification engine"""
        self.running = False
        self.worker_thread.join(timeout=5)
        logger.info("✅ Telegram notification engine stopped")

# ============================================================================
# MAIN SIGNAL GENERATION LOOP
# ============================================================================

class DemirAISignalGenerator:
    """Main orchestrator for signal generation (100% REAL DATA)"""
    
    def __init__(self):
        # Validate environment
        ConfigValidator.validate()
        
        # Initialize components
        self.db = DatabaseManager(os.getenv('DATABASE_URL'))
        self.fetcher = RealTimeDataFetcher()
        self.telegram = TelegramNotificationEngine()
        
        # Configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.cycle_interval = 300  # 5 minutes
        self.last_signal_time = {}
        self.min_signal_interval = 60
        self.min_confidence = 70
        
        logger.info("✅ DEMIR AI Signal Generator initialized")
    
    def start(self):
        """Start the main signal generation loop (24/7 OPERATIONAL)"""
        logger.info("🚀 Starting DEMIR AI v5.2 Signal Generation Loop")
        logger.info(f"📊 Monitoring symbols: {self.symbols}")
        logger.info(f"⏱️ Cycle interval: {self.cycle_interval} seconds")
        
        self.telegram.start()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                logger.info(f"\n{'='*70}")
                logger.info(f"CYCLE {cycle_count} - {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
                logger.info(f"{'='*70}")
                
                # Process each symbol
                for symbol in self.symbols:
                    try:
                        self._process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"❌ Error processing {symbol}: {e}")
                
                # ✅ FIX: Using time.sleep() instead of asyncio.sleep()
                logger.info(f"⏰ Next cycle in {self.cycle_interval} seconds...")
                time.sleep(self.cycle_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Signal generator stopped by user")
        except Exception as e:
            logger.critical(f"❌ Critical error in signal loop: {e}")
        finally:
            self._cleanup()
    
    def _process_symbol(self, symbol: str):
        """Process single symbol (100% REAL DATA ANALYSIS)"""
        logger.info(f"\n📍 Processing: {symbol}")
        
        # Fetch real prices
        price = self.fetcher.get_binance_price(symbol)
        
        if not price:
            logger.warning(f"⚠️ Could not fetch price for {symbol}")
            return
        
        # Fetch OHLCV data
        ohlcv_1h = self.fetcher.get_ohlcv_data(symbol, '1h', 100)
        
        if not ohlcv_1h:
            logger.warning(f"⚠️ Could not fetch OHLCV for {symbol}")
            return
        
        # Generate signal (simplified demo - replace with AI brain)
        signal = self._generate_test_signal(symbol, price, ohlcv_1h)
        
        if not signal:
            logger.warning(f"⚠️ No signal generated for {symbol}")
            return
        
        # Save to database
        signal_data = {
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'tp1': signal['tp1'],
            'tp2': signal['tp2'],
            'sl': signal['sl'],
            'entry_time': datetime.now(pytz.UTC),
            'position_size': 1.0
        }
        
        if self.db.insert_signal(signal_data):
            logger.info(f"✅ Signal saved to database")
            self.telegram.queue_signal_notification(signal_data)
            logger.info(f"✅ Telegram notification queued")
    
    def _generate_test_signal(self, symbol: str, price: float, ohlcv: List[Dict]) -> Optional[Dict]:
        """Generate test signal from OHLCV data"""
        if len(ohlcv) < 2:
            return None
        
        # Simple logic: if price > SMA, LONG; else SHORT
        sma = sum([c['close'] for c in ohlcv[-20:]]) / 20
        
        if price > sma:
            direction = 'LONG'
            tp1 = price * 1.02
            tp2 = price * 1.05
            sl = price * 0.98
        else:
            direction = 'SHORT'
            tp1 = price * 0.98
            tp2 = price * 0.95
            sl = price * 1.02
        
        return {
            'symbol': symbol,
            'direction': direction,
            'entry_price': price,
            'tp1': tp1,
            'tp2': tp2,
            'sl': sl,
            'entry_time': datetime.now(pytz.UTC)
        }
    
    def _cleanup(self):
        """Graceful shutdown"""
        logger.info("\n🛑 Cleaning up...")
        self.telegram.stop()
        self.db.close()
        logger.info("✅ Shutdown complete")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        generator = DemirAISignalGenerator()
        generator.start()
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")
        sys.exit(1)
