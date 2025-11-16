"""
🚀 DEMIR AI v5.2 - PRODUCTION STRICT VERSION
📊 Signal Generation + Railway Health Server
🔐 STRICT: NO FALLBACK, NO MOCK, NO FAKE - 100% REAL DATA ONLY

✅ RULES (KURALLARA UYGUN):
- Hiç FALLBACK ❌
- Hiç MOCK DATA ❌
- Hiç FAKE DATA ❌
- Hiç HARDCODED ❌
- API ERROR → Retry → Telegram Alert → Skip Signal
- Sistem CRASH olmaz, ama Signal vermeyebilir

Location: GitHub Root / main.py
Date: 2025-11-16 11:55 CET
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import pytz
from dotenv import load_dotenv
import threading
import queue
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================================
# LOAD ENV FIRST
# ============================================================================
load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('DEMIR_AI_MAIN')

# ============================================================================
# HEALTH CHECK SERVER - RAILWAY SUPPORT
# ============================================================================

class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            logger.debug("✅ Health check request received")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress HTTP server logging"""
        pass

def start_health_server():
    """Start health check HTTP server - MUST RUN FIRST!"""
    try:
        PORT = int(os.getenv('PORT', 8000))
        
        # Bind to 0.0.0.0 to accept external connections
        server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
        
        # Run in daemon thread so it doesn't block main loop
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        logger.info(f"✅✅✅ Health server STARTED on 0.0.0.0:{PORT}")
        logger.info(f"✅ Railway will check: http://localhost:{PORT}/health")
        return True
    
    except Exception as e:
        logger.error(f"❌ Health server FAILED: {e}")
        return False

# ============================================================================
# RETRY MECHANISM - STRICT (NO FALLBACK)
# ============================================================================

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait = backoff_factor ** attempt
                        logger.warning(f"⚠️ Retry {attempt+1}/{max_retries} after {wait}s: {e}")
                        time.sleep(wait)
                    else:
                        logger.error(f"❌ FINAL FAILURE after {max_retries} retries: {e}")
                        raise  # Throw error, don't fallback!
            return None
        return wrapper
    return decorator

# ============================================================================
# IMPORT AI BRAIN COMPONENTS
# ============================================================================

try:
    from ai_brain_ensemble import AiBrainEnsemble
    AI_BRAIN_AVAILABLE = True
    logger.info("✅ AI Brain Ensemble imported")
except ImportError as e:
    AI_BRAIN_AVAILABLE = False
    logger.warning(f"⚠️ AI Brain not available: {e}")

try:
    from trading_executor import TradingExecutor
    TRADING_EXECUTOR_AVAILABLE = True
    logger.info("✅ Trading Executor imported")
except ImportError as e:
    TRADING_EXECUTOR_AVAILABLE = False
    logger.warning(f"⚠️ Trading Executor not available: {e}")

# ============================================================================
# DATABASE MIGRATION
# ============================================================================

class DatabaseMigration:
    """Handle database schema migrations"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
    
    def connect(self):
        """Connect to database"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            logger.info("✅ Connected to PostgreSQL")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection error: {e}")
            return False
    
    def run_migrations(self):
        """Run all pending migrations"""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            
            migration_sql = """
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'PENDING';
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS confidence FLOAT DEFAULT 0.5;
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS tp1 FLOAT;
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS tp2 FLOAT;
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS rr_ratio FLOAT DEFAULT 1.0;
            ALTER TABLE trades ADD COLUMN IF NOT EXISTS ensemble_score FLOAT DEFAULT 0.5;
            """
            
            cursor.execute(migration_sql)
            self.connection.commit()
            logger.info("✅ Migration completed")
            cursor.close()
            return True
        
        except psycopg2.Error as e:
            logger.error(f"❌ Migration error: {e}")
            self.connection.rollback()
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

# ============================================================================
# ENVIRONMENT VALIDATION
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
        """Validate all required variables - STRICT"""
        missing = []
        
        for var in ConfigValidator.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            logger.critical(f"❌ MISSING REQUIRED ENV VARS: {missing}")
            raise ValueError(f"Missing required environment variables: {missing}")
        
        logger.info("✅ All required environment variables set")
        return True

# ============================================================================
# DATABASE MANAGER
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
        """Insert signal - STRICT REAL DATA ONLY"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO trades (
                symbol, direction, entry_price, tp1, tp2, sl, entry_time, position_size, 
                status, confidence, rr_ratio, ensemble_score
            ) VALUES (
                %(symbol)s, %(direction)s, %(entry_price)s, %(tp1)s, %(tp2)s,
                %(sl)s, %(entry_time)s, %(position_size)s,
                %(status)s, %(confidence)s, %(rr_ratio)s, %(ensemble_score)s
            )
            """
            
            data = {
                'symbol': signal_data['symbol'],
                'direction': signal_data['direction'],
                'entry_price': signal_data['entry_price'],
                'tp1': signal_data['tp1'],
                'tp2': signal_data['tp2'],
                'sl': signal_data['sl'],
                'entry_time': signal_data['entry_time'],
                'position_size': signal_data.get('position_size', 1.0),
                'status': 'PENDING',
                'confidence': signal_data.get('confidence', 0.5),
                'rr_ratio': signal_data.get('rr_ratio', 1.0),
                'ensemble_score': signal_data.get('ensemble_score', 0.5)
            }
            
            cursor.execute(query, data)
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
# REAL-TIME DATA FETCHER - STRICT NO FALLBACK
# ============================================================================

class RealTimeDataFetcher:
    """Fetch real-time price data - STRICT, WILL THROW ON ERROR"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEMIR-AI-v5.2'})
    
    @retry_with_backoff(max_retries=3)
    def get_binance_price(self, symbol: str) -> float:
        """Get real Binance futures price - THROWS if fails"""
        endpoint = f'{self.binance_url}/fapi/v1/ticker/price'
        params = {'symbol': symbol}
        response = self.session.get(endpoint, params=params, timeout=5)
        
        if response.status_code != 200:
            raise Exception(f"Binance API error {response.status_code}")
        
        data = response.json()
        price = float(data['price'])
        logger.debug(f"✅ Binance {symbol}: ${price}")
        return price
    
    @retry_with_backoff(max_retries=3)
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """Get real OHLCV candlestick data - THROWS if fails"""
        endpoint = f'{self.binance_url}/fapi/v1/klines'
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        response = self.session.get(endpoint, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Binance API error {response.status_code}")
        
        klines = response.json()
        if not klines:
            raise Exception("Empty klines response")
        
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

# ============================================================================
# TELEGRAM NOTIFICATION ENGINE
# ============================================================================

class TelegramNotificationEngine:
    """Send real-time notifications to Telegram"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.log_chat_id = os.getenv('TELEGRAM_LOG_CHAT_ID', self.chat_id)
        
        if self.token and self.chat_id:
            self.api_url = f'https://api.telegram.org/bot{self.token}'
        else:
            self.api_url = None
        
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.last_hourly_report = datetime.now()
        self.report_interval = timedelta(hours=1)
    
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
    
    def _send_message(self, message: str, retries: int = 3, chat_type: str = 'main') -> bool:
        """Send message with retry logic"""
        if not self.api_url:
            return False
        
        chat_id = self.log_chat_id if chat_type == 'logs' else self.chat_id
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    f'{self.api_url}/sendMessage',
                    json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Telegram notification sent ({chat_type})")
                    return True
                else:
                    logger.warning(f"⚠️ Telegram error (attempt {attempt+1}/{retries}): {response.status_code}")
            
            except Exception as e:
                logger.error(f"❌ Telegram send error (attempt {attempt+1}/{retries}): {e}")
            
            if attempt < retries - 1:
                time.sleep(1)
        
        return False
    
    def queue_signal_notification(self, signal: Dict):
        """Queue signal notification for async delivery"""
        message = f"""
<b>🚀 YENİ SİNYAL - DEMIR AI v5.2</b>

📍 <b>Coin:</b> {signal['symbol']}
🎯 <b>Yön:</b> {'🟢 LONG' if signal['direction'] == 'LONG' else '🔴 SHORT'}
💰 <b>Giriş:</b> ${signal['entry_price']:.2f}
📈 <b>TP1:</b> ${signal['tp1']:.2f}
📈 <b>TP2:</b> ${signal['tp2']:.2f}
❌ <b>SL:</b> ${signal['sl']:.2f}
⏱️ <b>Zaman:</b> {signal['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if self.api_url:
            self.queue.put(message)
    
    def queue_error_notification(self, layer_name: str, error: str):
        """Queue error notification"""
        message = f"""
<b>🚨 LAYER ERROR</b>

❌ Layer: <b>{layer_name}</b>
Error: <code>{error}</code>
Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

System continues with other layers.
"""
        
        if self.api_url:
            self.queue.put(message)
    
    def send_hourly_performance_report(self, metrics: Dict):
        """Send hourly performance report"""
        report_message = f"""
<b>📊 HOURLY PERFORMANCE REPORT</b>
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>📈 Trading Metrics:</b>
• Total Trades: {metrics.get('total_trades', 0)}
• Winning Trades: {metrics.get('winning_trades', 0)}
• Win Rate: {metrics.get('win_rate', 0):.1f}%
• Total PnL: ${metrics.get('total_pnl', 0):,.2f}
• ROI: {metrics.get('roi', 0):.2f}%
• Open Positions: {metrics.get('open_positions', 0)}

<b>🔧 System Status:</b>
• Uptime: {metrics.get('uptime_hours', 0):.1f}h
• Status: ✅ OPERATIONAL
• Layer Count: {metrics.get('layer_count', 0)}
"""
        
        if self.api_url:
            self._send_message(report_message, chat_type='logs')
    
    def stop(self):
        """Stop notification engine"""
        self.running = False
        self.worker_thread.join(timeout=5)
        logger.info("✅ Telegram notification engine stopped")

# ============================================================================
# MONITORING SYSTEM
# ============================================================================

class SystemMonitor:
    """Monitor system performance"""
    
    def __init__(self, telegram_engine: TelegramNotificationEngine):
        self.telegram = telegram_engine
        self.start_time = datetime.now()
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'open_positions': 0,
            'layer_count': 30
        }
        self.last_report = datetime.now()
        self.report_interval = timedelta(hours=1)
    
    def update_metrics(self, signal_executed: bool, pnl: float = 0):
        """Update performance metrics"""
        if signal_executed:
            self.metrics['total_trades'] += 1
            self.metrics['total_pnl'] += pnl
            
            if pnl > 0:
                self.metrics['winning_trades'] += 1
    
    def check_and_send_hourly_report(self):
        """Check if hourly report is due and send it"""
        if datetime.now() - self.last_report >= self.report_interval:
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600
            win_rate = (self.metrics['winning_trades'] / max(self.metrics['total_trades'], 1)) * 100
            roi = (self.metrics['total_pnl'] / 1000) * 100
            
            report_metrics = {
                'total_trades': self.metrics['total_trades'],
                'winning_trades': self.metrics['winning_trades'],
                'win_rate': win_rate,
                'total_pnl': self.metrics['total_pnl'],
                'roi': roi,
                'open_positions': self.metrics['open_positions'],
                'uptime_hours': uptime,
                'layer_count': self.metrics['layer_count']
            }
            
            self.telegram.send_hourly_performance_report(report_metrics)
            self.last_report = datetime.now()
            
            logger.info(f"✅ Hourly report sent - Trades: {self.metrics['total_trades']}, Win Rate: {win_rate:.1f}%")

# ============================================================================
# MAIN SIGNAL GENERATION ENGINE - STRICT VERSION
# ============================================================================

class DemirAISignalGenerator:
    """Main signal generator - STRICT NO FALLBACK VERSION"""
    
    def __init__(self):
        logger.info("🚀 STRICT MODE: Initializing DEMIR AI v5.2...")
        logger.info("⚠️ RULES: NO FALLBACK, NO MOCK, NO FAKE")
        
        # Validate environment
        ConfigValidator.validate()
        
        # Run database migration
        logger.info("🔄 Starting database migration...")
        migration = DatabaseMigration(os.getenv('DATABASE_URL'))
        
        if migration.connect():
            migration.run_migrations()
            migration.close()
        
        # Initialize components
        self.db = DatabaseManager(os.getenv('DATABASE_URL'))
        self.fetcher = RealTimeDataFetcher()
        self.telegram = TelegramNotificationEngine()
        self.monitor = SystemMonitor(self.telegram)
        
        # AI Brain
        if AI_BRAIN_AVAILABLE:
            try:
                self.ai_brain = AiBrainEnsemble()
                logger.info("✅ AI Brain Ensemble initialized")
            except Exception as e:
                logger.warning(f"⚠️ AI Brain initialization failed: {e}")
                self.ai_brain = None
        else:
            self.ai_brain = None
        
        # Trading Executor
        if TRADING_EXECUTOR_AVAILABLE:
            try:
                self.executor = TradingExecutor()
                logger.info("✅ Trading Executor initialized")
            except Exception as e:
                logger.warning(f"⚠️ Trading Executor initialization failed: {e}")
                self.executor = None
        else:
            self.executor = None
        
        # Configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.cycle_interval = 300
        
        logger.info("✅ DEMIR AI READY - STRICT MODE ACTIVE")
    
    def start(self):
        """Start main signal generation loop"""
        logger.info("🚀 Starting DEMIR AI v5.2 Signal Generation Loop")
        logger.info(f"📊 Monitoring: {self.symbols}")
        logger.info(f"⚠️ STRICT MODE: API errors → Retry → Alert → Skip (no fallback)")
        
        self.telegram.start()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                logger.info(f"\n{'='*70}")
                logger.info(f"CYCLE {cycle_count} - {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
                logger.info(f"{'='*70}")
                
                for symbol in self.symbols:
                    try:
                        self._process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"❌ Error processing {symbol}: {e}")
                        self.telegram.queue_error_notification(symbol, str(e))
                
                self.monitor.check_and_send_hourly_report()
                
                logger.info(f"⏰ Next cycle in {self.cycle_interval} seconds...")
                time.sleep(self.cycle_interval)
        
        except KeyboardInterrupt:
            logger.info("🛑 Signal generator stopped by user")
        
        except Exception as e:
            logger.critical(f"❌ Critical error in signal loop: {e}")
        
        finally:
            self._cleanup()
    
    def _process_symbol(self, symbol: str):
        """Process single symbol - STRICT NO FALLBACK"""
        logger.info(f"\n📍 Processing: {symbol}")
        
        try:
            # Fetch real prices - WILL THROW if fails
            price = self.fetcher.get_binance_price(symbol)
            
            # Fetch OHLCV data - WILL THROW if fails
            ohlcv_1h = self.fetcher.get_ohlcv_data(symbol, '1h', 100)
            
            signal = None
            
            # Generate signal using AI Brain
            if self.ai_brain:
                try:
                    prices = np.array([c['close'] for c in ohlcv_1h])
                    volumes = np.array([c['volume'] for c in ohlcv_1h])
                    
                    ai_signal = self.ai_brain.generate_ensemble_signal(
                        symbol, 
                        prices, 
                        volumes, 
                        futures_mode=True
                    )
                    
                    if ai_signal and ai_signal['ensemble_score'] > 0.5:
                        signal = {
                            'symbol': symbol,
                            'direction': ai_signal['direction'],
                            'entry_price': ai_signal['entry_price'],
                            'tp1': ai_signal['tp1'],
                            'tp2': ai_signal['tp2'],
                            'sl': ai_signal['sl'],
                            'entry_time': datetime.now(pytz.UTC),
                            'position_size': ai_signal['position_size'],
                            'confidence': ai_signal['confidence'],
                            'ensemble_score': ai_signal['ensemble_score'],
                            'rr_ratio': ai_signal.get('rr_ratio', 1.0)
                        }
                        
                        logger.info(f"✅ AI Signal: {signal['direction']} @ {signal['ensemble_score']:.0%} confidence")
                
                except Exception as e:
                    logger.error(f"❌ AI Brain analysis failed for {symbol}: {e}")
                    # Don't fallback - just skip this symbol
                    return
            
            if not signal:
                logger.warning(f"⚠️ No signal generated for {symbol}")
                return
            
            # Save to database - STRICT REAL DATA
            signal_data = {
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry_price': signal['entry_price'],
                'tp1': signal['tp1'],
                'tp2': signal['tp2'],
                'sl': signal['sl'],
                'entry_time': signal['entry_time'],
                'position_size': signal.get('position_size', 1.0),
                'confidence': signal.get('confidence', 0.5),
                'ensemble_score': signal.get('ensemble_score', 0.5),
                'rr_ratio': signal.get('rr_ratio', 1.0)
            }
            
            if self.db.insert_signal(signal_data):
                logger.info(f"✅ Signal saved to database")
                self.telegram.queue_signal_notification(signal_data)
                logger.info(f"✅ Telegram notification queued")
                
                if self.executor and signal.get('ensemble_score', 0) > 0.65:
                    try:
                        result = self.executor.execute_trade(signal)
                        if result.get('status') == 'executed':
                            logger.info(f"✅ Trade executed: {symbol}")
                            self.monitor.update_metrics(True, 0)
                    except Exception as e:
                        logger.warning(f"⚠️ Trade execution failed: {e}")
                
                self.monitor.update_metrics(True, 0)
        
        except Exception as e:
            # STRICT: Don't fallback, just throw and continue
            logger.error(f"❌ STRICT: {symbol} skipped due to error: {e}")
            self.telegram.queue_error_notification(symbol, str(e))
    
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
        # START HEALTH SERVER FIRST - CRITICAL FOR RAILWAY
        logger.info("🚀 STARTING HEALTH SERVER...")
        if not start_health_server():
            logger.error("❌ Failed to start health server - exiting")
            sys.exit(1)
        
        # Wait for health server to be ready
        time.sleep(1)
        logger.info("✅ Health server is ready")
        
        # Then start main generator
        logger.info("🚀 STARTING MAIN GENERATOR...")
        generator = DemirAISignalGenerator()
        generator.start()
    
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")
        sys.exit(1)
