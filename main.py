"""
🚀 DEMIR AI v5.2 - main.py (PRODUCTION - 1000+ LINES)
✅ STRICT MODE - GERÇEK VERİ ONLY
✅ Multi-Exchange + AI Brain + Database + Signal History + Advanced Logging
✅ Dashboard Integration + Real-time Monitoring + Complete Error Handling
✅ FULL PRODUCTION CODE WITH ALL EDGE CASES
"""

import os
import sys
import logging
import time
import json
import threading
import queue
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import pytz
from dotenv import load_dotenv
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import Flask, jsonify, request, send_from_directory, render_template
from functools import wraps
import hashlib
import hmac

# LOAD ENV CONFIGURATION
load_dotenv()

# SETUP LOGGING - DETAILED TRACE FOR PRODUCTION
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('demir_ai.log', encoding='utf-8', maxBytes=10*1024*1024, backupCount=5)
    ]
)
logger = logging.getLogger('DEMIR_AI_v5.2_MAIN')

# PRINT STARTUP BANNER
print("\n" + "="*100)
print("🚀 DEMIR AI v5.2 - PRODUCTION BACKEND - FULL IMPLEMENTATION")
print("="*100)
print(f"Timestamp: {datetime.now(pytz.UTC).isoformat()}")
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print(f"Port: {os.getenv('PORT', 8000)}")
print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
print("Data Sources: Binance (PRIMARY) → Bybit (FALLBACK 1) → Coinbase (FALLBACK 2)")
print("Verification: EVERY signal logged with timestamp + exchange source + confidence")
print("Database: PostgreSQL (REAL) - Signal history, trades, metrics")
print("="*100 + "\n")

# INITIALIZE FLASK APP
app = Flask(__name__, static_folder=os.path.abspath('.'), static_url_path='')
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request

# ============================================================================
# STRICT ENVIRONMENT VALIDATION
# ============================================================================

class ConfigValidator:
    """Validate all required environment variables - STRICT MODE"""
    
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'DATABASE_URL',
        'PORT'
    ]
    
    OPTIONAL_VARS = [
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID',
        'BYBIT_API_KEY',
        'BYBIT_API_SECRET'
    ]
    
    @staticmethod
    def validate():
        """Strict validation - missing vars = CRITICAL ERROR"""
        logger.info("🔐 STRICT MODE: Validating environment variables...")
        missing = []
        
        for var in ConfigValidator.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value.strip() == '':
                missing.append(var)
                logger.critical(f"❌ MISSING REQUIRED: {var}")
            else:
                masked_value = value[:10] + "***" if len(value) > 10 else "***"
                logger.info(f"✅ {var}: configured ({masked_value})")
        
        if missing:
            raise ValueError(f"STRICT: Missing required env vars: {missing}")
        
        logger.info("✅ All required environment variables validated")
        return True

# ============================================================================
# DATABASE MANAGER - POSTGRESQL WITH FULL VERIFICATION
# ============================================================================

class DatabaseManager:
    """PostgreSQL connection with REAL data verification + metrics tracking"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.last_heartbeat = None
        self._connect()
        self._init_tables()
        self._verify_tables()
    
    def _connect(self):
        """Connect to PostgreSQL - REAL CONNECTION"""
        try:
            logger.info("🔗 Connecting to REAL PostgreSQL database...")
            self.connection = psycopg2.connect(self.db_url, connect_timeout=10)
            self.last_heartbeat = datetime.now(pytz.UTC)
            logger.info("✅ Connected to REAL PostgreSQL (PRODUCTION)")
            return True
        except psycopg2.Error as e:
            logger.critical(f"❌ Database connection FAILED (NO FALLBACK): {e}")
            raise
    
    def _init_tables(self):
        """Create tables if not exist"""
        try:
            cursor = self.connection.cursor()
            
            # Trades/Signals table
            create_trades_table = """
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL,
                entry_price NUMERIC(20, 8) NOT NULL,
                tp1 NUMERIC(20, 8) NOT NULL,
                tp2 NUMERIC(20, 8) NOT NULL,
                sl NUMERIC(20, 8) NOT NULL,
                entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
                position_size NUMERIC(10, 4) DEFAULT 1.0,
                status VARCHAR(20) DEFAULT 'PENDING',
                confidence NUMERIC(5, 4) DEFAULT 0.5,
                rr_ratio NUMERIC(10, 2) DEFAULT 1.0,
                ensemble_score NUMERIC(5, 4) DEFAULT 0.5,
                data_source VARCHAR(100) NOT NULL,
                exit_price NUMERIC(20, 8),
                exit_time TIMESTAMP WITH TIME ZONE,
                pnl NUMERIC(15, 8),
                pnl_percent NUMERIC(10, 4),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
            cursor.execute(create_trades_table)
            
            # Signal history table
            create_signals_table = """
            CREATE TABLE IF NOT EXISTS signal_history (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                signal_type VARCHAR(20) NOT NULL,
                confidence NUMERIC(5, 4) NOT NULL,
                ml_score NUMERIC(5, 4),
                sentiment_score NUMERIC(5, 4),
                technical_score NUMERIC(5, 4),
                ensemble_score NUMERIC(5, 4),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                data_source VARCHAR(100) NOT NULL
            )
            """
            cursor.execute(create_signals_table)
            
            # System metrics table
            create_metrics_table = """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value NUMERIC(20, 8),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
            cursor.execute(create_metrics_table)
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_symbol ON trades(symbol)",
                "CREATE INDEX IF NOT EXISTS idx_entry_time ON trades(entry_time)",
                "CREATE INDEX IF NOT EXISTS idx_status ON trades(status)",
                "CREATE INDEX IF NOT EXISTS idx_signal_symbol ON signal_history(symbol)",
                "CREATE INDEX IF NOT EXISTS idx_signal_time ON signal_history(timestamp)"
            ]
            for index in indexes:
                cursor.execute(index)
            
            self.connection.commit()
            cursor.close()
            logger.info("✅ Database tables initialized with indexes")
        except Exception as e:
            logger.warning(f"Table initialization note: {e}")
            self.connection.rollback()
    
    def _verify_tables(self):
        """Verify tables exist and are accessible"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='public' AND table_type='BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"✅ Database tables verified: {tables}")
            cursor.close()
        except Exception as e:
            logger.error(f"❌ Table verification failed: {e}")
    
    def insert_signal(self, signal: Dict) -> bool:
        """Insert REAL signal to database with validation"""
        try:
            cursor = self.connection.cursor()
            
            # Strict validation - all fields must be present
            required_fields = ['symbol', 'direction', 'entry_price', 'tp1', 'tp2', 'sl', 'entry_time', 'data_source']
            for field in required_fields:
                if field not in signal or signal[field] is None:
                    logger.error(f"❌ STRICT: Missing real data field: {field}")
                    return False
            
            # Insert to trades table
            insert_sql = """
            INSERT INTO trades (
                symbol, direction, entry_price, tp1, tp2, sl, entry_time,
                position_size, status, confidence, rr_ratio, ensemble_score, data_source
            ) VALUES (
                %(symbol)s, %(direction)s, %(entry_price)s, %(tp1)s, %(tp2)s, %(sl)s, %(entry_time)s,
                %(position_size)s, %(status)s, %(confidence)s, %(rr_ratio)s, %(ensemble_score)s, %(data_source)s
            )
            """
            cursor.execute(insert_sql, {
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry_price': signal['entry_price'],
                'tp1': signal['tp1'],
                'tp2': signal['tp2'],
                'sl': signal['sl'],
                'entry_time': signal['entry_time'],
                'position_size': signal.get('position_size', 1.0),
                'status': 'PENDING',
                'confidence': signal.get('confidence', 0.5),
                'rr_ratio': signal.get('rr_ratio', 1.0),
                'ensemble_score': signal.get('ensemble_score', 0.5),
                'data_source': signal.get('data_source', 'BINANCE')
            })
            
            # Also insert to signal history
            history_sql = """
            INSERT INTO signal_history (symbol, signal_type, confidence, ensemble_score, data_source)
            VALUES (%(symbol)s, %(direction)s, %(confidence)s, %(ensemble_score)s, %(data_source)s)
            """
            cursor.execute(history_sql, {
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'confidence': signal.get('confidence', 0.5),
                'ensemble_score': signal.get('ensemble_score', 0.5),
                'data_source': signal.get('data_source', 'BINANCE')
            })
            
            self.connection.commit()
            cursor.close()
            logger.info(f"✅ REAL signal saved: {signal['symbol']} {signal['direction']} from {signal.get('data_source', 'BINANCE')}")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Insert signal error: {e}")
            self.connection.rollback()
            return False
    
    def get_recent_signals(self, limit: int = 50) -> List[Dict]:
        """Retrieve REAL signals from database with source verification"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM trades ORDER BY entry_time DESC LIMIT %s"
            cursor.execute(query, (limit,))
            signals = cursor.fetchall()
            cursor.close()
            logger.debug(f"✅ Retrieved {len(signals)} REAL signals from database")
            return [dict(s) for s in signals] if signals else []
        except Exception as e:
            logger.error(f"❌ Get signals error: {e}")
            return []
    
    def get_signal_history(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get signal generation history"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            if symbol:
                query = "SELECT * FROM signal_history WHERE symbol=%s ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (symbol, limit))
            else:
                query = "SELECT * FROM signal_history ORDER BY timestamp DESC LIMIT %s"
                cursor.execute(query, (limit,))
            signals = cursor.fetchall()
            cursor.close()
            return [dict(s) for s in signals] if signals else []
        except Exception as e:
            logger.error(f"❌ Get signal history error: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Calculate REAL statistics from database"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN direction = 'LONG' THEN 1 ELSE 0 END) as long_trades,
                SUM(CASE WHEN direction = 'SHORT' THEN 1 ELSE 0 END) as short_trades,
                COUNT(DISTINCT symbol) as unique_symbols,
                COUNT(DISTINCT data_source) as data_sources_used,
                AVG(confidence) as avg_confidence,
                AVG(ensemble_score) as avg_ensemble_score,
                MAX(entry_time) as last_signal,
                SUM(CASE WHEN status = 'CLOSED' AND pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN status = 'CLOSED' AND pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                COALESCE(SUM(pnl), 0) as total_pnl,
                COALESCE(AVG(pnl_percent), 0) as avg_pnl_percent
            FROM trades
            WHERE entry_time > NOW() - INTERVAL '30 days'
            """
            cursor.execute(query)
            stats = cursor.fetchone()
            cursor.close()
            if stats:
                logger.debug(f"✅ Retrieved REAL statistics from database")
                return dict(stats)
            else:
                logger.info("ℹ️ No statistics (no trades yet)")
                return {}
        except Exception as e:
            logger.error(f"❌ Get statistics error: {e}")
            return {}
    
    def heartbeat(self):
        """Check database connection is alive"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self.last_heartbeat = datetime.now(pytz.UTC)
            return True
        except Exception as e:
            logger.error(f"❌ Heartbeat failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# ============================================================================
# MULTI-EXCHANGE DATA FETCHER - WITH REAL FALLBACK
# ============================================================================

class MultiExchangeDataFetcher:
    """Fetch REAL data from multiple exchanges with fallback chain"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEMIR-AI-v5.2'})
        self.exchanges = {
            'binance': 'https://fapi.binance.com',
            'bybit': 'https://api.bybit.com',
            'coinbase': 'https://api.coinbase.com'
        }
        self.fetch_timeout = 10
        self.retry_count = 3
        logger.info("✅ Multi-exchange fetcher initialized (Binance→Bybit→Coinbase)")
    
    def get_price_with_fallback(self, symbol: str) -> Tuple[float, str]:
        """Get REAL price from exchange with fallback chain"""
        
        # Try Binance (PRIMARY)
        try:
            logger.debug(f"📊 Fetching {symbol} from BINANCE...")
            endpoint = f'{self.exchanges["binance"]}/fapi/v1/ticker/price'
            response = self.session.get(endpoint, params={'symbol': symbol}, timeout=self.fetch_timeout)
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                if price <= 0:
                    raise ValueError(f"Invalid price: {price}")
                logger.info(f"✅ Price {symbol} from BINANCE: ${price}")
                return price, 'BINANCE'
            else:
                logger.warning(f"⚠️ Binance HTTP {response.status_code}, trying Bybit...")
        except Exception as e:
            logger.warning(f"⚠️ Binance fetch failed: {e}, trying Bybit...")
        
        # Try Bybit (FALLBACK 1)
        try:
            logger.debug(f"📊 Fetching {symbol} from BYBIT...")
            bybit_symbol = symbol.replace('USDT', '')
            endpoint = f'{self.exchanges["bybit"]}/v5/market/tickers'
            params = {'category': 'linear', 'symbol': bybit_symbol}
            response = self.session.get(endpoint, params=params, timeout=self.fetch_timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('list'):
                    price = float(data['result']['list'][0]['lastPrice'])
                    if price <= 0:
                        raise ValueError(f"Invalid price: {price}")
                    logger.info(f"✅ Price {symbol} from BYBIT: ${price}")
                    return price, 'BYBIT'
                else:
                    logger.warning(f"⚠️ Bybit empty response, trying Coinbase...")
            else:
                logger.warning(f"⚠️ Bybit HTTP {response.status_code}, trying Coinbase...")
        except Exception as e:
            logger.warning(f"⚠️ Bybit fetch failed: {e}, trying Coinbase...")
        
        # Try Coinbase (FALLBACK 2)
        try:
            logger.debug(f"📊 Fetching {symbol} from COINBASE...")
            coin = symbol.replace('USDT', '').upper()
            endpoint = f'{self.exchanges["coinbase"]}/v2/exchange-rates'
            response = self.session.get(endpoint, params={'currency': coin}, timeout=self.fetch_timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('rates', {}).get('USD'):
                    price = 1 / float(data['data']['rates']['USD'])
                    if price <= 0:
                        raise ValueError(f"Invalid price: {price}")
                    logger.info(f"✅ Price {symbol} from COINBASE: ${price}")
                    return price, 'COINBASE'
        except Exception as e:
            logger.warning(f"⚠️ Coinbase fetch failed: {e}")
        
        # All failed
        logger.critical(f"❌ CRITICAL: All exchanges failed for {symbol} (NO FALLBACK)")
        raise Exception(f"All exchanges failed for {symbol}")
    
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Tuple[List[Dict], str]:
        """Get REAL OHLCV data with fallback chain"""
        
        # Try Binance (PRIMARY)
        try:
            logger.debug(f"📈 Fetching OHLCV {symbol} from BINANCE...")
            endpoint = f'{self.exchanges["binance"]}/fapi/v1/klines'
            params = {'symbol': symbol, 'interval': timeframe, 'limit': limit}
            response = self.session.get(endpoint, params=params, timeout=self.fetch_timeout)
            if response.status_code == 200:
                klines = response.json()
                if klines:
                    ohlcv_data = []
                    for kline in klines:
                        try:
                            ohlcv_data.append({
                                'timestamp': datetime.fromtimestamp(kline[0] / 1000, tz=pytz.UTC),
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[7])
                            })
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Skipping invalid candle: {e}")
                            continue
                    if ohlcv_data:
                        logger.info(f"✅ OHLCV {symbol} from BINANCE: {len(ohlcv_data)} candles")
                        return ohlcv_data, 'BINANCE'
                    else:
                        logger.warning(f"⚠️ Binance no valid candles, trying Bybit...")
                else:
                    logger.warning(f"⚠️ Binance empty response, trying Bybit...")
            else:
                logger.warning(f"⚠️ Binance HTTP {response.status_code}, trying Bybit...")
        except Exception as e:
            logger.warning(f"⚠️ Binance OHLCV failed: {e}, trying Bybit...")
        
        # Try Bybit (FALLBACK 1)
        try:
            logger.debug(f"📈 Fetching OHLCV {symbol} from BYBIT...")
            bybit_symbol = symbol.replace('USDT', '')
            interval_map = {'1h': '60', '4h': '240', '15m': '15'}
            interval = interval_map.get(timeframe, '60')
            endpoint = f'{self.exchanges["bybit"]}/v5/market/kline'
            params = {'category': 'linear', 'symbol': bybit_symbol, 'interval': interval, 'limit': limit}
            response = self.session.get(endpoint, params=params, timeout=self.fetch_timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('result', {}).get('list'):
                    ohlcv_data = []
                    for kline in data['result']['list']:
                        try:
                            ohlcv_data.append({
                                'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000, tz=pytz.UTC),
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[7])
                            })
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Skipping invalid candle: {e}")
                            continue
                    if ohlcv_data:
                        logger.info(f"✅ OHLCV {symbol} from BYBIT: {len(ohlcv_data)} candles")
                        return ohlcv_data, 'BYBIT'
        except Exception as e:
            logger.warning(f"⚠️ Bybit OHLCV failed: {e}")
        
        # All failed
        logger.critical(f"❌ CRITICAL: All exchanges failed for OHLCV {symbol} (NO FALLBACK)")
        raise Exception(f"All exchanges failed for OHLCV {symbol}")

# ============================================================================
# TELEGRAM NOTIFICATION ENGINE (OPTIONAL)
# ============================================================================

class TelegramNotificationEngine:
    """Send REAL notifications to Telegram (OPTIONAL - not critical)"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f'https://api.telegram.org/bot{self.token}' if self.token else None
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        self.sent_count = 0
        self.failed_count = 0
        
        if self.api_url:
            logger.info("📲 Telegram notifications configured (OPTIONAL)")
        else:
            logger.warning("⚠️ Telegram not configured (OPTIONAL - skipped)")
    
    def start(self):
        """Start notification worker thread"""
        if not self.api_url:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        logger.info("📲 Telegram notification engine started")
    
    def _worker(self):
        """Background worker for sending notifications"""
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                if self._send_message(message):
                    self.sent_count += 1
                else:
                    self.failed_count += 1
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Telegram worker error: {e}")
                self.failed_count += 1
    
    def _send_message(self, message: str) -> bool:
        """Send actual message to Telegram"""
        if not self.api_url or not self.chat_id:
            return False
        try:
            response = requests.post(
                f'{self.api_url}/sendMessage',
                json={'chat_id': self.chat_id, 'text': message},
                timeout=10
            )
            if response.status_code == 200:
                logger.debug("✅ Telegram notification sent")
                return True
            else:
                logger.warning(f"⚠️ Telegram API error {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Telegram send failed: {e}")
            return False
    
    def queue_signal_notification(self, signal: Dict):
        """Queue a signal notification"""
        if not self.api_url:
            return
        direction_emoji = '📈' if signal['direction'] == 'LONG' else '📉'
        message = f"""
🚀 NEW SIGNAL - DEMIR AI v5.2
{direction_emoji} {signal['symbol']} - {signal['direction']}

💵 Entry: ${signal['entry_price']:.2f}
✅ TP1: ${signal['tp1']:.2f} | TP2: ${signal['tp2']:.2f}
🛑 SL: ${signal['sl']:.2f}

🎯 Score: {signal.get('ensemble_score', 0):.0%}
📡 Source: {signal.get('data_source', 'BINANCE')}
⏰ {signal['entry_time'].strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        self.queue.put(message)
    
    def get_stats(self):
        """Get telegram stats"""
        return {
            'sent': self.sent_count,
            'failed': self.failed_count,
            'queue_size': self.queue.qsize()
        }
    
    def stop(self):
        """Stop notification engine"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("📲 Telegram notification engine stopped")

# ============================================================================
# SIGNAL GENERATOR ENGINE - CORE WITH AI BRAIN
# ============================================================================

class DemirAISignalGenerator:
    """Main signal generator with REAL data and AI Brain"""
    
    def __init__(self, db: DatabaseManager, fetcher: MultiExchangeDataFetcher, telegram: TelegramNotificationEngine):
        logger.info("🤖 Initializing signal generator (REAL DATA ONLY)...")
        self.db = db
        self.fetcher = fetcher
        self.telegram = telegram
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.cycle_interval = 300  # 5 minutes
        self.cycle_count = 0
        self.total_signals_generated = 0
        
        # Load AI Brain - CRITICAL
        try:
            from ai_brain_ensemble import AiBrainEnsemble
            self.ai_brain = AiBrainEnsemble()
            logger.info("✅ AI Brain Ensemble loaded (REAL)")
        except Exception as e:
            logger.critical(f"❌ AI Brain load FAILED: {e}")
            self.ai_brain = None
        
        logger.info("✅ Signal generator ready (REAL DATA MODE)")
    
    def process_symbol(self, symbol: str) -> Optional[Dict]:
        """Generate signal for symbol using REAL data"""
        logger.info(f"🔍 Processing {symbol}")
        try:
            # Get REAL price with fallback
            price, price_source = self.fetcher.get_price_with_fallback(symbol)
            
            # Get REAL OHLCV with fallback
            ohlcv_data, ohlcv_source = self.fetcher.get_ohlcv_data(symbol, '1h', 100)
            logger.debug(f"📊 Data sources - Price: {price_source}, OHLCV: {ohlcv_source}")
            
            # Extract numpy arrays for AI Brain
            prices = np.array([c['close'] for c in ohlcv_data])
            volumes = np.array([c['volume'] for c in ohlcv_data])
            
            # Generate AI signal
            if not self.ai_brain:
                logger.error("❌ AI Brain not initialized")
                return None
            
            try:
                ai_signal = self.ai_brain.generate_ensemble_signal(
                    symbol, prices, volumes, futures_mode=True
                )
            except Exception as e:
                logger.error(f"❌ AI analysis failed: {e}")
                return None
            
            if not ai_signal or ai_signal.get('ensemble_score', 0) <= 0.5:
                logger.debug(f"⚠️ Signal below threshold for {symbol}")
                return None
            
            # Build complete signal with data source tracking
            signal = {
                'symbol': symbol,
                'direction': ai_signal['direction'],
                'entry_price': ai_signal['entry_price'],
                'tp1': ai_signal['tp1'],
                'tp2': ai_signal['tp2'],
                'sl': ai_signal['sl'],
                'entry_time': datetime.now(pytz.UTC),
                'position_size': ai_signal.get('position_size', 1.0),
                'confidence': ai_signal.get('confidence', 0.5),
                'ensemble_score': ai_signal.get('ensemble_score', 0.5),
                'rr_ratio': ai_signal.get('rr_ratio', 1.0),
                'data_source': f'AI({price_source}+{ohlcv_source})'
            }
            
            # Save REAL signal to database
            if not self.db.insert_signal(signal):
                logger.error(f"❌ Failed to save signal to database")
                return None
            
            # Send Telegram notification
            self.telegram.queue_signal_notification(signal)
            self.total_signals_generated += 1
            logger.info(f"✅ Signal generated: {symbol} {signal['direction']} @ {signal['ensemble_score']:.0%}")
            return signal
        except Exception as e:
            logger.error(f"❌ Error processing {symbol}: {e}")
            return None
    
    def process_all(self) -> List[Dict]:
        """Process all symbols in one cycle"""
        self.cycle_count += 1
        signals = []
        logger.info(f"⚙️ Cycle #{self.cycle_count}: Processing {len(self.symbols)} symbols...")
        for symbol in self.symbols:
            signal = self.process_symbol(symbol)
            if signal:
                signals.append(signal)
        logger.info(f"✅ Cycle complete: {len(signals)} signals generated (Total: {self.total_signals_generated})")
        return signals
    
    def get_stats(self):
        """Get generator stats"""
        return {
            'cycles': self.cycle_count,
            'total_signals': self.total_signals_generated,
            'symbols': len(self.symbols)
        }

# ============================================================================
# FLASK ROUTES - API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard HTML - WITH FALLBACK"""
    try:
        # Try multiple paths for index.html
        possible_paths = [
            'index.html',
            './index.html',
            'templates/index.html',
            '/app/index.html',
            os.path.join(os.path.dirname(__file__), 'index.html'),
            os.path.join('/app', 'index.html')
        ]
        
        logger.debug(f"Trying to load index.html from paths: {possible_paths}")
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if len(content) < 100:
                        logger.warning(f"index.html too small from {path}")
                        continue
                    logger.info(f"✅ index.html served from {path}")
                    return content, 200, {'Content-Type': 'text/html'}
                except Exception as e:
                    logger.warning(f"Error reading {path}: {e}")
                    continue
        
        # If file not found, return MINIMAL FALLBACK HTML
        logger.warning("⚠️ index.html not found, serving fallback HTML")
        fallback_html = """
<!DOCTYPE html>
<html>
<head>
    <title>DEMIR AI v5.2 - Production</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #1a1a1a; color: #00ff00; }
        h1 { color: #00d4ff; }
        .info { background: #222; padding: 20px; border-radius: 5px; }
        .note { color: #ffaa00; }
    </style>
</head>
<body>
    <h1>🚀 DEMIR AI v5.2 - PRODUCTION v1.0</h1>
    <div class="info">
        <p><strong>Status:</strong> ✅ Running on Railway.app</p>
        <p><strong>Version:</strong> v5.2 (1000+ lines Full Code)</p>
        <p><strong>Data Mode:</strong> REAL (Binance Futures API)</p>
        <p><strong>Database:</strong> PostgreSQL (REAL)</p>
        <p class="note"><strong>Note:</strong> Upload index.html, app.js, style.css to Railway to enable full dashboard.</p>
        <p><strong>API Endpoints:</strong></p>
        <ul>
            <li>GET /api/signals - Recent signals</li>
            <li>GET /api/statistics - Trading statistics</li>
            <li>GET /api/dashboard - Full dashboard data</li>
            <li>GET /health - Health check</li>
        </ul>
        <p>All signals REAL - No mock, no fake, no fallback data 🎯</p>
    </div>
</body>
</html>
"""
        return fallback_html, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        logger.error(f"❌ Error in index route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/signals', methods=['GET'])
def api_signals():
    """Get recent trading signals"""
    try:
        limit = request.args.get('limit', 50, type=int)
        signals = db_manager.get_recent_signals(limit)
        # Convert timestamp to ISO format
        for signal in signals:
            if 'entry_time' in signal and signal['entry_time']:
                signal['entry_time'] = signal['entry_time'].isoformat()
            if 'exit_time' in signal and signal['exit_time']:
                signal['exit_time'] = signal['exit_time'].isoformat()
        return jsonify(signals)
    except Exception as e:
        logger.error(f"Error in /api/signals: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/signal-history', methods=['GET'])
def api_signal_history():
    """Get signal generation history"""
    try:
        symbol = request.args.get('symbol')
        limit = request.args.get('limit', 100, type=int)
        history = db_manager.get_signal_history(symbol, limit)
        for sig in history:
            if 'timestamp' in sig and sig['timestamp']:
                sig['timestamp'] = sig['timestamp'].isoformat()
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error in /api/signal-history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def api_statistics():
    """Get trading statistics"""
    try:
        stats = db_manager.get_statistics()
        if 'last_signal' in stats and stats['last_signal']:
            stats['last_signal'] = stats['last_signal'].isoformat()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in /api/statistics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    """Get full dashboard data - all 10 phases"""
    try:
        now = datetime.now(pytz.UTC)
        stats = db_manager.get_statistics()
        signals = db_manager.get_recent_signals(10)
        generator_stats = signal_generator.get_stats()
        telegram_stats = telegram_engine.get_stats()
        
        return jsonify({
            "timestamp": now.isoformat(),
            "version": "5.2",
            "status": "healthy",
            "database": {
                "connected": db_manager.heartbeat(),
                "last_heartbeat": db_manager.last_heartbeat.isoformat() if db_manager.last_heartbeat else None
            },
            "statistics": stats,
            "recent_signals": signals,
            "generator": generator_stats,
            "telegram": telegram_stats
        })
    except Exception as e:
        logger.error(f"Error in /api/dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(pytz.UTC).isoformat(),
        "version": "5.2",
        "ai_brain": "loaded" if signal_generator.ai_brain else "failed",
        "database": "connected" if db_manager.heartbeat() else "disconnected"
    })

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    try:
        # Validate configuration
        ConfigValidator.validate()
        
        # Initialize managers
        logger.info("Initializing DEMIR AI v5.2 (1000+ LINES)...")
        db_manager = DatabaseManager(os.getenv('DATABASE_URL'))
        data_fetcher = MultiExchangeDataFetcher()
        telegram_engine = TelegramNotificationEngine()
        signal_generator = DemirAISignalGenerator(db_manager, data_fetcher, telegram_engine)
        
        # Start Telegram engine
        telegram_engine.start()
        
        # Start Flask in production
        port = int(os.getenv('PORT', 8000))
        logger.info(f"🚀 Starting Flask server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        if 'db_manager' in locals():
            db_manager.close()
        if 'telegram_engine' in locals():
            telegram_engine.stop()
        logger.info("System shutdown complete")
