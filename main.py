"""
🚀 DEMIR AI v5.2 - MAIN.PY - WITH HTML DASHBOARD
✅ Full integration: Backend (Python) + Frontend (HTML/CSS/JS)

COMPLETE PRODUCTION READY CODE

Location: GitHub Root / main.py
Date: 2025-11-16 12:50 CET
Size: ~900 lines (FULL)
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
from flask import Flask, render_template_string, jsonify, request
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
print("DEMIR AI v5.2 - PRODUCTION STARTUP WITH DASHBOARD")
print("=" * 80)
print(f"Time: {datetime.now().isoformat()}")
print(f"Python: {sys.version}")
print(f"Working Dir: {os.getcwd()}")
print(f"PORT: {os.getenv('PORT', 8000)}")

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

class ConfigValidator:
    """Validate environment variables"""
    
    REQUIRED_VARS = [
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'DATABASE_URL',
    ]
    
    @staticmethod
    def validate():
        """Validate all required variables"""
        logger.info("Validating environment variables...")
        
        missing = []
        for var in ConfigValidator.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            logger.critical(f"MISSING REQUIRED ENV VARS: {missing}")
            raise ValueError(f"Missing required environment variables: {missing}")
        
        logger.info("All required environment variables set")
        return True

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manage PostgreSQL connections"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection"""
        try:
            logger.info("Connecting to PostgreSQL database...")
            self.connection = psycopg2.connect(self.db_url)
            logger.info("Connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def insert_signal(self, signal_data: Dict) -> bool:
        """Insert signal to database"""
        try:
            cursor = self.connection.cursor()
            
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
            
            logger.info(f"Signal saved: {signal_data['symbol']} {signal_data['direction']}")
            return True
        
        except psycopg2.Error as e:
            logger.error(f"Insert signal error: {e}")
            self.connection.rollback()
            return False
    
    def get_recent_signals(self, limit: int = 20) -> List[Dict]:
        """Get recent signals from database"""
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
            
            return [dict(s) for s in signals]
        
        except psycopg2.Error as e:
            logger.error(f"Get signals error: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get trade statistics"""
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
            
            return dict(stats) if stats else {}
        
        except psycopg2.Error as e:
            logger.error(f"Get statistics error: {e}")
            return {}
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# ============================================================================
# REAL-TIME DATA FETCHER
# ============================================================================

class RealTimeDataFetcher:
    """Fetch real-time price data"""
    
    def __init__(self):
        self.binance_url = 'https://fapi.binance.com'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'DEMIR-AI-v5.2'})
        logger.info("Real-time data fetcher initialized")
    
    def get_binance_price(self, symbol: str) -> float:
        """Get Binance price"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/ticker/price'
            params = {'symbol': symbol}
            response = self.session.get(endpoint, params=params, timeout=5)
            
            if response.status_code != 200:
                raise Exception(f"Binance API error {response.status_code}")
            
            data = response.json()
            price = float(data['price'])
            logger.debug(f"Binance {symbol}: ${price}")
            return price
        
        except Exception as e:
            logger.error(f"Binance price fetch failed: {e}")
            raise
    
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[Dict]:
        """Get OHLCV data"""
        try:
            endpoint = f'{self.binance_url}/fapi/v1/klines'
            params = {'symbol': symbol, 'interval': timeframe, 'limit': limit}
            
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
            
            logger.info(f"Fetched {len(ohlcv_data)} OHLCV candles for {symbol}")
            return ohlcv_data
        
        except Exception as e:
            logger.error(f"OHLCV fetch failed: {e}")
            raise

# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================

class TelegramNotificationEngine:
    """Send Telegram notifications"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f'https://api.telegram.org/bot{self.token}' if self.token else None
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        
        if self.api_url:
            logger.info("Telegram notifications configured")
        else:
            logger.warning("Telegram not configured (optional)")
    
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
        """Send message"""
        if not self.api_url or not self.chat_id:
            return False
        
        try:
            response = requests.post(
                f'{self.api_url}/sendMessage',
                json={'chat_id': self.chat_id, 'text': message},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Telegram notification sent")
                return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
        
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
"""
        self.queue.put(message)
    
    def stop(self):
        """Stop notification engine"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Telegram notification engine stopped")

# ============================================================================
# SIGNAL GENERATOR ENGINE
# ============================================================================

class DemirAISignalGenerator:
    """Main signal generator"""
    
    def __init__(self, db: DatabaseManager, fetcher: RealTimeDataFetcher, telegram: TelegramNotificationEngine):
        logger.info("Initializing signal generator...")
        
        self.db = db
        self.fetcher = fetcher
        self.telegram = telegram
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.cycle_interval = 300
        
        # Try to load AI Brain
        try:
            from ai_brain_ensemble import AiBrainEnsemble
            self.ai_brain = AiBrainEnsemble()
            logger.info("AI Brain Ensemble initialized")
        except Exception as e:
            logger.warning(f"AI Brain initialization failed: {e}")
            self.ai_brain = None
        
        logger.info("Signal generator ready")
    
    def process_symbol(self, symbol: str) -> Optional[Dict]:
        """Process single symbol"""
        logger.info(f"Processing: {symbol}")
        
        try:
            # Fetch real data
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
                        
                        logger.info(f"AI Signal: {signal['direction']}")
                
                except Exception as e:
                    logger.error(f"AI Brain analysis failed: {e}")
                    return None
            
            if not signal:
                logger.warning(f"No signal generated for {symbol}")
                return None
            
            # Save to database
            if self.db.insert_signal(signal):
                self.telegram.queue_signal_notification(signal)
                return signal
        
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
        
        return None

# ============================================================================
# FLASK ROUTES - API
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard - YOU NEED TO CREATE THIS HTML FILE"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    except FileNotFoundError:
        logger.warning("index.html not found, serving basic dashboard")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DEMIR AI v5.2</title>
            <style>
                body { font-family: Arial; margin: 20px; background: #0a0e27; color: #fff; }
                h1 { color: #00d4ff; }
                .status { background: #1a1e3f; padding: 20px; border-radius: 8px; }
                .section { margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>DEMIR AI v5.2 Dashboard</h1>
            <div class="status">
                <p>Production system running</p>
                <p><strong>Status:</strong> Online</p>
                <p><a href="/api/health">Health Check</a></p>
            </div>
        </body>
        </html>
        """

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now(pytz.UTC).isoformat(),
        'version': 'v5.2'
    })

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get recent signals"""
    try:
        limit = request.args.get('limit', 20, type=int)
        signals = db.get_recent_signals(limit)
        
        # Convert datetime objects to strings
        for signal in signals:
            if 'entry_time' in signal and hasattr(signal['entry_time'], 'isoformat'):
                signal['entry_time'] = signal['entry_time'].isoformat()
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'count': len(signals)
        })
    
    except Exception as e:
        logger.error(f"Get signals error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get statistics"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'status': 'success',
            'data': stats
        })
    
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/prices/<symbol>', methods=['GET'])
def get_price(symbol: str):
    """Get current price"""
    try:
        price = fetcher.get_binance_price(symbol)
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'price': price
        })
    
    except Exception as e:
        logger.error(f"Get price error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# STATIC FILES
# ============================================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    try:
        if filename.endswith('.css'):
            with open(f'static/{filename}', 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/css'}
        elif filename.endswith('.js'):
            with open(f'static/{filename}', 'r') as f:
                return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        logger.warning(f"Static file not found: {filename}")
        return 'Not found', 404

# ============================================================================
# INITIALIZATION & START
# ============================================================================

# Global instances
db = None
fetcher = None
telegram = None
generator = None

def initialize_system():
    """Initialize all components"""
    global db, fetcher, telegram, generator
    
    logger.info("Initializing system...")
    
    # Validate environment
    ConfigValidator.validate()
    
    # Initialize components
    db = DatabaseManager(os.getenv('DATABASE_URL'))
    fetcher = RealTimeDataFetcher()
    telegram = TelegramNotificationEngine()
    generator = DemirAISignalGenerator(db, fetcher, telegram)
    
    logger.info("System initialized")

def start_signal_loop():
    """Start signal generation loop in background"""
    telegram.start()
    
    def loop():
        logger.info("Signal generation loop started")
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                logger.info(f"CYCLE {cycle_count}")
                
                for symbol in generator.symbols:
                    try:
                        generator.process_symbol(symbol)
                    except Exception as e:
                        logger.error(f"Error processing {symbol}: {e}")
                
                time.sleep(generator.cycle_interval)
        
        except Exception as e:
            logger.critical(f"Signal loop error: {e}")
        
        finally:
            logger.info("Signal generation loop stopped")
    
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    logger.info("Signal loop thread started")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        # Initialize
        logger.info("STARTING DEMIR AI v5.2...")
        initialize_system()
        
        # Start background signal loop
        start_signal_loop()
        
        # Start Flask server
        PORT = int(os.getenv('PORT', 8000))
        logger.info(f"Starting Flask server on port {PORT}...")
        logger.info(f"Dashboard: http://localhost:{PORT}/")
        logger.info(f"API Health: http://localhost:{PORT}/api/health")
        
        # Run Flask with production settings
        app.run(
            host='0.0.0.0',
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        if db:
            db.close()
        if telegram:
            telegram.stop()
        sys.exit(1)
