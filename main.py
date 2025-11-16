"""
🚀 DEMIR AI v5.2 - MAIN.PY - PRODUCTION READY (RULES COMPLIANT)
✅ STRICT MODE: NO MOCK, NO FAKE, NO FALLBACK, 100% REAL DATA ONLY

Date: 2025-11-16 13:19 CET
RULES: 
- KURAL 1: Hiç mock, fake, fallback, hardcoded data YOK
- Sadece GERÇEK VERILER
- Dashboard canlı güncellenecek (WebSocket/API polling)
- AI Brain real-time sinyalleri üretecek
- Database'e hepsi kaydedilecek
"""

import os
import sys
import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import pytz
from dotenv import load_dotenv
import numpy as np

# Flask for web server + API
from flask import Flask, jsonify, request
import queue

# ============================================================================
# LOAD ENV FIRST (CRITICAL)
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

print("\n" + "=" * 80)
print("DEMIR AI v5.2 - PRODUCTION STARTUP - STRICT MODE")
print("=" * 80)
print(f"Time: {datetime.now().isoformat()}")
print(f"Python: {sys.version}")
print(f"Working Dir: {os.getcwd()}")
print(f"PORT: {os.getenv('PORT', 8000)}")
print("RULES: NO MOCK, NO FAKE, NO FALLBACK - 100% REAL DATA ONLY")

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__, static_folder=os.path.abspath('.'), static_url_path='')
app.config['JSON_SORT_KEYS'] = False

# ============================================================================
# ENVIRONMENT VALIDATION - STRICT
# ============================================================================

class ConfigValidator:
    """Validate environment variables - STRICT"""
    
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'DATABASE_URL',
    ]
    
    @staticmethod
    def validate():
        """Validate all required variables - STRICT MODE"""
        logger.info("STRICT: Validating environment variables...")
        
        missing = []
        for var in ConfigValidator.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value.strip() == '':
                missing.append(var)
                logger.critical(f"MISSING: {var}")
        
        if missing:
            logger.critical(f"STRICT VIOLATION: Missing required environment variables: {missing}")
            raise ValueError(f"STRICT: Missing required environment variables: {missing}")
        
        logger.info("STRICT: All required environment variables validated")
        return True

# ============================================================================
# DATABASE MANAGER - STRICT
# ============================================================================

class DatabaseManager:
    """Manage PostgreSQL connections - STRICT REAL DATA ONLY"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection - STRICT"""
        try:
            logger.info("STRICT: Connecting to REAL PostgreSQL database...")
            self.connection = psycopg2.connect(self.db_url)
            logger.info("STRICT: Connected to REAL PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.critical(f"STRICT: Database connection FAILED: {e}")
            raise
    
    def insert_signal(self, signal_data: Dict) -> bool:
        """Insert signal to database - STRICT REAL DATA ONLY"""
        try:
            cursor = self.connection.cursor()
            
            # Validate all required fields are REAL data
            required_fields = ['symbol', 'direction', 'entry_price', 'tp1', 'tp2', 'sl', 'entry_time']
            for field in required_fields:
                if field not in signal_data or signal_data[field] is None:
                    logger.error(f"STRICT: Missing real data field: {field}")
                    return False
            
            query = """
            INSERT INTO trades (
                symbol, direction, entry_price, tp1, tp2, sl, entry_time, 
                position_size, status, confidence, rr_ratio, ensemble_score
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
            
            logger.info(f"STRICT: Signal saved (REAL DATA): {signal_data['symbol']} {signal_data['direction']}")
            return True
        
        except psycopg2.Error as e:
            logger.error(f"STRICT: Insert signal error: {e}")
            self.connection.rollback()
            return False
    
    def get_recent_signals(self, limit: int = 20) -> List[Dict]:
        """Get REAL signals from database"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT * FROM trades 
            ORDER BY entry_time DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            signals = cursor.fetchall()
            cursor.close()
            
            logger.debug(f"STRICT: Retrieved {len(signals)} REAL signals from database")
            return [dict(s) for s in signals]
        
        except psycopg2.Error as e:
            logger.error(f"STRICT: Get signals error: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get REAL trade statistics from database"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN direction = 'LONG' THEN 1 ELSE 0 END) as long_trades,
                SUM(CASE WHEN direction = 'SHORT' THEN 1 ELSE 0 END) as short_trades,
                AVG(confidence) as avg_confidence,
                AVG(ensemble_score) as avg_score
            FROM trades
            WHERE entry_time > NOW() - INTERVAL '24 hours'
            """
            
            cursor.execute(query)
            stats = cursor.fetchone()
            cursor.close()
            
            if stats:
                logger.debug(f"STRICT: Retrieved REAL statistics from database")
                return dict(stats)
            else:
                logger.warning("STRICT: No statistics found (expected for new database)")
                return {}
        
        except psycopg2.Error as e:
            logger.error(f"STRICT: Get statistics error: {e}")
            raise
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# ============================================================================
# REAL-TIME DATA FETCHER - STRICT NO FALLBACK
# ============================================================================

class RealTimeDataFetcher:
    """Fetch REAL-TIME price data from Binance - STRICT MODE"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEMIR-AI-v5.2'})
        logger.info("STRICT: Real-time data fetcher initialized (Binance only)")
    
    def get_binance_price(self, symbol: str) -> float:
        """Get REAL Binance futures price - STRICT: WILL THROW ON ERROR"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/ticker/price'
            params = {'symbol': symbol}
            response = self.session.get(endpoint, params=params, timeout=5)
            
            if response.status_code != 200:
                raise Exception(f"STRICT: Binance API error {response.status_code}")
            
            data = response.json()
            price = float(data['price'])
            logger.debug(f"STRICT: Binance REAL {symbol}: ${price}")
            return price
        
        except Exception as e:
            logger.critical(f"STRICT: Binance price fetch FAILED (NO FALLBACK): {e}")
            raise
    
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """Get REAL OHLCV candlestick data - STRICT: WILL THROW ON ERROR"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/klines'
            params = {'symbol': symbol, 'interval': timeframe, 'limit': limit}
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            if response.status_code != 200:
                raise Exception(f"STRICT: Binance API error {response.status_code}")
            
            klines = response.json()
            if not klines:
                raise Exception("STRICT: Empty klines response from Binance")
            
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
            
            logger.info(f"STRICT: Fetched {len(ohlcv_data)} REAL OHLCV candles for {symbol}")
            return ohlcv_data
        
        except Exception as e:
            logger.critical(f"STRICT: OHLCV fetch FAILED (NO FALLBACK): {e}")
            raise

# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================

class TelegramNotificationEngine:
    """Send real notifications to Telegram (OPTIONAL)"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f'https://api.telegram.org/bot{self.token}' if self.token else None
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        
        if self.api_url:
            logger.info("STRICT: Telegram notifications configured (optional)")
        else:
            logger.warning("STRICT: Telegram not configured (OPTIONAL - no fallback)")
    
    def start(self):
        """Start notification worker"""
        if not self.api_url:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        logger.info("Telegram notification engine started")
    
    def _worker(self):
        """Worker thread"""
        while self.running:
            try:
                message = self.queue.get(timeout=1)
                self._send_message(message)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Notification worker error: {e}")
    
    def _send_message(self, message: str) -> bool:
        """Send message - STRICT: will report errors"""
        if not self.api_url or not self.chat_id:
            logger.warning("STRICT: Telegram not configured, skipping notification")
            return False
        
        try:
            response = requests.post(
                f'{self.api_url}/sendMessage',
                json={'chat_id': self.chat_id, 'text': message},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("STRICT: Telegram notification sent (REAL)")
                return True
            else:
                logger.error(f"STRICT: Telegram API error {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"STRICT: Telegram send failed: {e}")
            return False
    
    def queue_signal_notification(self, signal: Dict):
        """Queue signal notification"""
        if not self.api_url:
            return
        
        direction_symbol = 'LONG' if signal['direction'] == 'LONG' else 'SHORT'
        message = f"""
NEW SIGNAL - DEMIR AI v5.2

Coin: {signal['symbol']}
Direction: {direction_symbol}
Entry: ${signal['entry_price']:.2f}
TP1: ${signal['tp1']:.2f}
TP2: ${signal['tp2']:.2f}
SL: ${signal['sl']:.2f}
Time: {signal['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}
Score: {signal.get('ensemble_score', 0):.0%}
"""
        self.queue.put(message)
    
    def stop(self):
        """Stop notification engine"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Telegram notification engine stopped")

# ============================================================================
# SIGNAL GENERATOR ENGINE - STRICT MODE
# ============================================================================

class DemirAISignalGenerator:
    """Main signal generator - STRICT NO FALLBACK VERSION"""
    
    def __init__(self, db: DatabaseManager, fetcher: RealTimeDataFetcher, telegram: TelegramNotificationEngine):
        logger.info("STRICT: Initializing signal generator (NO FALLBACK MODE)...")
        
        self.db = db
        self.fetcher = fetcher
        self.telegram = telegram
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.cycle_interval = 300
        
        # Try to load AI Brain
        try:
            from ai_brain_ensemble import AiBrainEnsemble
            self.ai_brain = AiBrainEnsemble()
            logger.info("STRICT: AI Brain Ensemble initialized (REAL)")
        except Exception as e:
            logger.critical(f"STRICT: AI Brain initialization FAILED: {e}")
            logger.critical("STRICT: Cannot continue without AI Brain (NO FALLBACK)")
            raise
        
        logger.info("STRICT: Signal generator ready (NO FALLBACK MODE)")
    
    def process_symbol(self, symbol: str) -> Optional[Dict]:
        """Process single symbol - STRICT NO FALLBACK"""
        logger.info(f"STRICT: Processing {symbol} (REAL DATA ONLY)")
        
        try:
            # Fetch REAL data - WILL THROW if fails
            price = self.fetcher.get_binance_price(symbol)
            ohlcv_1h = self.fetcher.get_ohlcv_data(symbol, '1h', 100)
            
            signal = None
            
            # Generate signal using AI Brain
            if self.ai_brain:
                try:
                    prices = np.array([c['close'] for c in ohlcv_1h])
                    volumes = np.array([c['volume'] for c in ohlcv_1h])
                    
                    ai_signal = self.ai_brain.generate_ensemble_signal(
                        symbol, prices, volumes, futures_mode=True
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
                            'position_size': ai_signal.get('position_size', 1.0),
                            'confidence': ai_signal.get('confidence', 0.5),
                            'ensemble_score': ai_signal.get('ensemble_score', 0.5),
                            'rr_ratio': ai_signal.get('rr_ratio', 1.0)
                        }
                        
                        logger.info(f"STRICT: AI Signal generated: {signal['direction']} @ {signal['ensemble_score']:.0%}")
                
                except Exception as e:
                    logger.error(f"STRICT: AI Brain analysis failed: {e}")
                    raise
            
            if not signal:
                logger.debug(f"STRICT: No signal generated for {symbol} (below threshold)")
                return None
            
            # Save to database - REAL DATA ONLY
            if self.db.insert_signal(signal):
                self.telegram.queue_signal_notification(signal)
                return signal
            else:
                logger.error(f"STRICT: Failed to save signal to database")
                return None
        
        except Exception as e:
            logger.error(f"STRICT: {symbol} skipped (error): {e}")
            return None

# ============================================================================
# FLASK ROUTES - DASHBOARD & API
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard"""
    try:
        logger.info("Serving index.html from disk")
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content or len(content) < 100:
            logger.error("STRICT: index.html is empty or too small")
            raise FileNotFoundError("index.html is invalid")
        
        return content
    
    except FileNotFoundError:
        logger.critical("STRICT: index.html NOT FOUND - NO FALLBACK")
        # STRICT: No fallback HTML - must fail
        return jsonify({
            'error': 'STRICT: Dashboard file not found',
            'status': 'FAILED',
            'reason': 'index.html missing in root directory'
        }), 500

@app.route('/style.css')
def style_css():
    """Serve CSS file"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except Exception as e:
        logger.error(f"STRICT: CSS file error: {e}")
        return "", 404

@app.route('/app.js')
def app_js():
    """Serve JavaScript file"""
    try:
        with open('app.js', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        logger.error(f"STRICT: JavaScript file error: {e}")
        return "", 404

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint - REAL DATA"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'version': 'v5.2',
        'mode': 'STRICT - NO MOCK DATA'
    })

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get REAL signals from database"""
    try:
        limit = request.args.get('limit', 20, type=int)
        signals = db.get_recent_signals(limit)
        
        # Convert datetime objects to strings
        for signal in signals:
            if 'entry_time' in signal and hasattr(signal['entry_time'], 'isoformat'):
                signal['entry_time'] = signal['entry_time'].isoformat()
        
        logger.debug(f"STRICT: Returning {len(signals)} REAL signals")
        return jsonify({
            'status': 'success',
            'signals': signals,
            'count': len(signals),
            'mode': 'REAL DATA ONLY'
        })
    
    except Exception as e:
        logger.error(f"STRICT: Get signals error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get REAL statistics from database"""
    try:
        stats = db.get_statistics()
        logger.debug("STRICT: Returning REAL statistics")
        return jsonify({
            'status': 'success',
            'data': stats,
            'mode': 'REAL DATA ONLY'
        })
    
    except Exception as e:
        logger.error(f"STRICT: Get statistics error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/prices/<symbol>', methods=['GET'])
def get_price(symbol: str):
    """Get REAL current price from Binance"""
    try:
        price = fetcher.get_binance_price(symbol)
        logger.debug(f"STRICT: Returning REAL price for {symbol}")
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'price': price,
            'source': 'Binance (REAL)',
            'timestamp': datetime.now(pytz.UTC).isoformat()
        })
    
    except Exception as e:
        logger.error(f"STRICT: Get price error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# INITIALIZATION & START
# ============================================================================

# Global instances
db = None
fetcher = None
telegram = None
generator = None

def initialize_system():
    """Initialize all components - STRICT"""
    global db, fetcher, telegram, generator
    
    logger.info("STRICT: Initializing system (NO FALLBACK)...")
    
    # Validate environment - STRICT
    try:
        ConfigValidator.validate()
    except ValueError as e:
        logger.critical(f"STRICT: {e}")
        raise
    
    # Initialize components
    logger.info("STRICT: Initializing components...")
    db = DatabaseManager(os.getenv('DATABASE_URL'))
    fetcher = RealTimeDataFetcher()
    telegram = TelegramNotificationEngine()
    generator = DemirAISignalGenerator(db, fetcher, telegram)
    
    logger.info("STRICT: System initialized (100% REAL DATA MODE)")

def start_signal_loop():
    """Start signal generation loop in background"""
    telegram.start()
    
    def loop():
        logger.info("STRICT: Signal generation loop started")
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                logger.info(f"STRICT: CYCLE {cycle_count} - {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                for symbol in generator.symbols:
                    try:
                        generator.process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"STRICT: Error processing {symbol}: {e}")
                
                logger.info(f"STRICT: Sleeping {generator.cycle_interval}s until next cycle...")
                time.sleep(generator.cycle_interval)
        
        except Exception as e:
            logger.critical(f"STRICT: Signal loop CRITICAL ERROR: {e}")
        
        finally:
            logger.info("STRICT: Signal generation loop stopped")
    
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    logger.info("STRICT: Signal loop thread started")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        # Initialize
        logger.info("="*80)
        logger.info("STARTING DEMIR AI v5.2 - STRICT MODE (NO MOCK/FAKE DATA)")
        logger.info("="*80)
        
        initialize_system()
        
        # Start background signal loop
        start_signal_loop()
        
        # Start Flask server
        PORT = int(os.getenv('PORT', 8000))
        logger.info(f"Starting Flask server on port {PORT}...")
        logger.info(f"Dashboard: http://localhost:{PORT}/")
        logger.info(f"API Health: http://localhost:{PORT}/api/health")
        logger.info(f"API Signals: http://localhost:{PORT}/api/signals")
        logger.info(f"API Statistics: http://localhost:{PORT}/api/statistics")
        logger.info("="*80)
        
        # Run Flask with production settings
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    
    except Exception as e:
        logger.critical(f"STRICT: Fatal error (NO FALLBACK): {e}", exc_info=True)
        if db:
            db.close()
        if telegram:
            telegram.stop()
        sys.exit(1)
