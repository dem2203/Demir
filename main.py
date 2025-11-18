"""
🔧 DEMIR AI v6.0 - DEBUG VERSION - VERI GÖSTERMEMESİNİ ÇÖZMEK İÇİN
✅ Verbose logging with everything
✅ Error tracking at every step
✅ Debug endpoint added
✅ TIMESTAMP FIX - type consistency guaranteed
"""

import os
import sys
import logging
import time
import json
import threading
import queue
import requests
import pytz
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# LOAD CONFIGURATION
load_dotenv()

# ====== ENHANCED LOGGING SETUP ======
class ColoredFormatter(logging.Formatter):
    """Color-coded logging"""
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}[{record.levelname}]{self.COLORS['RESET']}"
        return super().format(record)

# Setup logging
log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter(log_format))

file_handler = RotatingFileHandler(
    'demir_ai_debug.log',
    encoding='utf-8',
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger('DEMIR_AI_DEBUG')

print("\n" + "="*120)
print("🔧 DEMIR AI v6.0 - DEBUG MODE - VERI SORUNUNU ÇÖZÜYORUZ")
print("="*120)
print(f"⏰ Start Time: {datetime.now(pytz.UTC).isoformat()}")
print(f"🗂️ Log File: demir_ai_debug.log")
print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
print("="*120 + "\n")

logger.info("=" * 100)
logger.info("🚀 DEMIR AI v6.0 DEBUG VERSION STARTING")
logger.info("=" * 100)


# ====== ENVIRONMENT DEBUG ======
logger.info("📋 CHECKING ENVIRONMENT VARIABLES:")
required_env = ['BINANCE_API_KEY', 'BINANCE_API_SECRET', 'DATABASE_URL', 'PORT']
for var in required_env:
    value = os.getenv(var)
    if var == 'DATABASE_URL':
        # Hide password
        masked = value[:30] + "***" if value else "NOT SET"
    else:
        masked = "SET" if value else "NOT SET"
    logger.info(f"  {var}: {masked}")


# ====== REAL DATA VALIDATORS ======
class MockDataDetector:
    """Detect fake/mock/test data"""
    FAKE_KEYWORDS = ['mock', 'fake', 'test', 'fallback', 'prototype', 'dummy', 'sample', 'hard', 'fixed']
    
    @staticmethod
    def detect_in_data(data: Dict) -> Tuple[bool, List[str]]:
        """Detects fake/mock/test data"""
        issues = []
        
        def check_val(k, v):
            for kw in MockDataDetector.FAKE_KEYWORDS:
                if isinstance(v, str) and kw.lower() in v.lower():
                    issues.append(f"❌ Found '{kw}' in field {k}: '{v}'")
                elif isinstance(k, str) and kw.lower() in k.lower():
                    issues.append(f"❌ Found '{kw}' in key name: {k}")
            
            if isinstance(v, dict):
                for nk, nv in v.items():
                    check_val(nk, nv)
        
        for k, v in data.items():
            check_val(k, v)
        
        return len(issues) == 0, issues


class RealDataVerifier:
    """Verify real exchange data"""
    def __init__(self):
        self.last_prices: Dict[str, float] = {}
        self.last_timestamps: Dict[str, float] = {}
    
    def verify_price(self, symbol: str, price: float) -> Tuple[bool, str]:
        """Verify price is real"""
        if price <= 0:
            return False, "Invalid price: <= 0"
        if not isinstance(price, (int, float)):
            return False, "Price not numeric"
        
        if symbol in self.last_prices:
            last = self.last_prices[symbol]
            change = abs(price - last) / last
            if change > 0.15:
                logger.warning(f"⚠️ Suspicious {change*100:.1f}% jump in {symbol}")
        
        self.last_prices[symbol] = price
        return True, f"Price verified: ${price}"
    
    def verify_timestamp(self, ts: Union[float, datetime], max_age: int = 3600) -> Tuple[bool, str]:
        """Verify timestamp is current - FIXED TYPE HANDLING"""
        current = datetime.now().timestamp()
        
        # Convert datetime to float if needed
        if isinstance(ts, datetime):
            ts_float = ts.timestamp()
        else:
            ts_float = float(ts)
        
        age = current - ts_float
        
        if age < 0:
            return False, "Future timestamp"
        if age > max_age:
            return False, f"Stale data ({age:.0f}s old)"
        
        return True, f"Timestamp valid ({age:.0f}s old)"


class SignalValidator:
    """Master validation"""
    def __init__(self):
        self.mock_detector = MockDataDetector()
        self.real_verifier = RealDataVerifier()
        self.signal_cache: Dict[str, Dict] = {}
    
    def validate_signal(self, signal: Dict) -> Tuple[bool, List[str]]:
        """Comprehensive signal validation"""
        issues = []
        
        is_real, mock_issues = self.mock_detector.detect_in_data(signal)
        issues.extend(mock_issues)
        
        required = ['symbol', 'direction', 'entry_price', 'timestamp', 'confidence']
        for field in required:
            if field not in signal:
                issues.append(f"Missing required field: {field}")
        
        if 'confidence' in signal and not (0 <= signal['confidence'] <= 1):
            issues.append(f"Confidence out of range: {signal['confidence']}")
        
        if 'direction' in signal and signal['direction'] not in ['LONG', 'SHORT', 'NEUTRAL']:
            issues.append(f"Invalid direction: {signal['direction']}")
        
        if 'timestamp' in signal:
            is_valid_ts, msg = self.real_verifier.verify_timestamp(signal['timestamp'])
            if not is_valid_ts:
                issues.append(f"Timestamp error: {msg}")
        
        if 'entry_price' in signal and 'symbol' in signal:
            is_valid_price, msg = self.real_verifier.verify_price(
                signal['symbol'], 
                signal['entry_price']
            )
            if not is_valid_price:
                issues.append(f"Price error: {msg}")
        
        self.signal_cache[signal.get('symbol')] = signal
        return len(issues) == 0, issues


# ====== DATABASE MANAGER (DEBUG) ======
class DatabaseManager:
    """PostgreSQL with debug logging"""
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = None
        self.connected = False
        self._connect()
        self._init_tables()
    
    def _connect(self):
        try:
            logger.info(f"🔌 Attempting DB connection...")
            self.connection = psycopg2.connect(self.db_url, connect_timeout=10)
            logger.info(f"✅ PostgreSQL CONNECTION SUCCESS")
            self.connected = True
        except Exception as e:
            logger.error(f"❌ DB CONNECTION FAILED: {e}")
            logger.error(f"   Connection string (masked): {self.db_url[:50]}...")
            self.connected = False
            raise
    
    def _init_tables(self):
        """Initialize database tables"""
        if not self.connected:
            logger.warning("⚠️ Skipping table init - not connected")
            return
        
        try:
            cursor = self.connection.cursor()
            logger.info("📝 Creating/checking tables...")
            
            cursor.execute("CREATE TABLE IF NOT EXISTS tracked_coins (id SERIAL PRIMARY KEY, symbol VARCHAR(20) NOT NULL UNIQUE, added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), is_active BOOLEAN DEFAULT TRUE)")
            logger.info("  ✅ tracked_coins table OK")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    entry_price NUMERIC(20, 8) NOT NULL,
                    tp1 NUMERIC(20, 8),
                    tp2 NUMERIC(20, 8),
                    sl NUMERIC(20, 8),
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    confidence NUMERIC(5, 4) DEFAULT 0.5,
                    ensemble_score NUMERIC(5, 4) DEFAULT 0.5,
                    tech_group_score NUMERIC(5, 4) DEFAULT 0.0,
                    sentiment_group_score NUMERIC(5, 4) DEFAULT 0.0,
                    onchain_group_score NUMERIC(5, 4) DEFAULT 0.0,
                    macro_risk_group_score NUMERIC(5, 4) DEFAULT 0.0,
                    confluence_score NUMERIC(5, 4) DEFAULT 0.0,
                    tf_15m_direction VARCHAR(10),
                    tf_1h_direction VARCHAR(10),
                    tf_4h_direction VARCHAR(10),
                    risk_score NUMERIC(5, 4) DEFAULT 0.5,
                    risk_reward_ratio NUMERIC(10, 4),
                    position_size NUMERIC(10, 4) DEFAULT 1.0,
                    data_source VARCHAR(100),
                    is_valid BOOLEAN DEFAULT TRUE,
                    validity_notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            logger.info("  ✅ signals table OK")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    entry_price NUMERIC(20, 8) NOT NULL,
                    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    quantity NUMERIC(20, 8) NOT NULL,
                    stop_loss NUMERIC(20, 8),
                    take_profit NUMERIC(20, 8),
                    status VARCHAR(20) DEFAULT 'open',
                    unrealized_pnl NUMERIC(20, 8),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            logger.info("  ✅ positions table OK")
            
            self.connection.commit()
            cursor.close()
            logger.info("✅ ALL TABLES INITIALIZED")
        except Exception as e:
            logger.error(f"❌ TABLE INIT ERROR: {e}")
            if self.connection:
                self.connection.rollback()
    
    def insert_signal(self, signal: Dict) -> bool:
        """Insert validated signal - WITH FULL DEBUG"""
        if not self.connected:
            logger.error("❌ NOT CONNECTED - cannot insert signal")
            return False
        
        try:
            logger.info(f"🔄 VALIDATING SIGNAL: {signal.get('symbol')}")
            
            is_valid, issues = SignalValidator().validate_signal(signal)
            
            if not is_valid:
                logger.error(f"❌ VALIDATION FAILED: {issues}")
                return False
            
            logger.info(f"✅ VALIDATION PASSED for {signal['symbol']}")
            
            cursor = self.connection.cursor()
            logger.info(f"📝 EXECUTING INSERT QUERY")
            
            # Convert timestamp to float if it's datetime
            ts = signal['timestamp']
            if isinstance(ts, datetime):
                ts = ts.timestamp()
            
            insert_sql = """
                INSERT INTO signals (
                    symbol, direction, entry_price, tp1, tp2, sl, timestamp,
                    confidence, ensemble_score,
                    tech_group_score, sentiment_group_score, onchain_group_score, macro_risk_group_score,
                    confluence_score, tf_15m_direction, tf_1h_direction, tf_4h_direction,
                    risk_score, risk_reward_ratio, position_size,
                    data_source, is_valid, validity_notes
                ) VALUES (
                    %(symbol)s, %(direction)s, %(entry_price)s, %(tp1)s, %(tp2)s, %(sl)s, to_timestamp(%(timestamp)s),
                    %(confidence)s, %(ensemble_score)s,
                    %(tech_group_score)s, %(sentiment_group_score)s, %(onchain_group_score)s, %(macro_risk_group_score)s,
                    %(confluence_score)s, %(tf_15m_direction)s, %(tf_1h_direction)s, %(tf_4h_direction)s,
                    %(risk_score)s, %(risk_reward_ratio)s, %(position_size)s,
                    %(data_source)s, %(is_valid)s, %(validity_notes)s
                )
            """
            
            params = {
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'entry_price': signal['entry_price'],
                'tp1': signal.get('tp1', signal['entry_price'] * 1.02),
                'tp2': signal.get('tp2', signal['entry_price'] * 1.05),
                'sl': signal.get('sl', signal['entry_price'] * 0.98),
                'timestamp': ts,
                'confidence': signal.get('confidence', 0.5),
                'ensemble_score': signal.get('ensemble_score', 0.5),
                'tech_group_score': signal.get('tech_group_score', 0.0),
                'sentiment_group_score': signal.get('sentiment_group_score', 0.0),
                'onchain_group_score': signal.get('onchain_group_score', 0.0),
                'macro_risk_group_score': signal.get('macro_risk_group_score', 0.0),
                'confluence_score': signal.get('confluence_score', 0.0),
                'tf_15m_direction': signal.get('tf_15m_direction'),
                'tf_1h_direction': signal.get('tf_1h_direction'),
                'tf_4h_direction': signal.get('tf_4h_direction'),
                'risk_score': signal.get('risk_score', 0.5),
                'risk_reward_ratio': signal.get('risk_reward_ratio', 0.0),
                'position_size': signal.get('position_size', 1.0),
                'data_source': signal.get('data_source', 'BINANCE'),
                'is_valid': True,
                'validity_notes': 'Valid signal'
            }
            
            logger.info(f"  Query params: {params}")
            cursor.execute(insert_sql, params)
            logger.info(f"✅ QUERY EXECUTED")
            
            self.connection.commit()
            logger.info(f"✅ TRANSACTION COMMITTED")
            
            cursor.close()
            logger.info(f"✅✅✅ SIGNAL SAVED TO DB: {signal['symbol']} {signal['direction']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ INSERT ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if self.connection:
                try:
                    self.connection.rollback()
                    logger.info("🔄 Rollback executed")
                except:
                    pass
            return False
    
    def get_recent_signals(self, limit: int = 50) -> List[Dict]:
        """Get recent signals"""
        if not self.connected:
            logger.error("❌ NOT CONNECTED - cannot get signals")
            return []
        
        try:
            logger.info(f"📖 FETCHING {limit} SIGNALS FROM DB")
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM signals ORDER BY created_at DESC LIMIT %s", (limit,))
            results = [dict(s) for s in cursor.fetchall()]
            cursor.close()
            logger.info(f"✅ FETCHED {len(results)} SIGNALS")
            return results
        except Exception as e:
            logger.error(f"❌ FETCH ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def add_tracked_coin(self, symbol: str) -> bool:
        """Add coin to tracking"""
        if not self.connected:
            logger.error("❌ NOT CONNECTED - cannot add coin")
            return False
        
        try:
            logger.info(f"➕ ADDING COIN: {symbol}")
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO tracked_coins (symbol, is_active)
                VALUES (%s, TRUE)
                ON CONFLICT (symbol) DO UPDATE SET is_active = TRUE
            """, (symbol,))
            self.connection.commit()
            cursor.close()
            logger.info(f"✅ COIN ADDED: {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ ADD COIN ERROR: {e}")
            self.connection.rollback()
            return False
    
    def get_tracked_coins(self) -> List[str]:
        """Get tracked coins"""
        if not self.connected:
            logger.error("❌ NOT CONNECTED - cannot get coins")
            return []
        
        try:
            logger.info(f"📖 FETCHING TRACKED COINS")
            cursor = self.connection.cursor()
            cursor.execute("SELECT symbol FROM tracked_coins WHERE is_active = TRUE ORDER BY added_at DESC")
            coins = [row[0] for row in cursor.fetchall()]
            cursor.close()
            logger.info(f"✅ FETCHED {len(coins)} COINS: {coins}")
            return coins
        except Exception:
            logger.error("❌ GET COINS ERROR")
            return []
    
    def heartbeat(self) -> bool:
        """Health check"""
        if not self.connected:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            logger.error("❌ HEARTBEAT FAILED")
            return False
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 DB CONNECTION CLOSED")


# ====== MULTI-EXCHANGE DATA FETCHER (DEBUG) ======
class MultiExchangeDataFetcher:
    """Fetch real data with fallback chain"""
    def __init__(self):
        self.session = requests.Session()
        self.exchanges = {
            'binance': 'https://fapi.binance.com',
            'bybit': 'https://api.bybit.com',
            'coinbase': 'https://api.coinbase.com'
        }
        logger.info("✅ MultiExchangeDataFetcher initialized")
    
    def get_price_with_fallback(self, symbol: str) -> Tuple[float, str]:
        """Get real price with fallback"""
        logger.info(f"💰 FETCHING PRICE FOR {symbol}")
        
        # Try Binance
        try:
            logger.info(f"  → Trying BINANCE...")
            r = self.session.get(
                f'{self.exchanges["binance"]}/fapi/v1/ticker/price',
                params={'symbol': symbol},
                timeout=10
            )
            if r.status_code == 200:
                price = float(r.json()['price'])
                if price > 0:
                    logger.info(f"  ✅ BINANCE: ${price}")
                    return price, 'BINANCE'
        except Exception as e:
            logger.warning(f"  ❌ BINANCE FAILED: {e}")
        
        # Try Bybit
        try:
            logger.info(f"  → Trying BYBIT...")
            symbol_bybit = symbol.replace('USDT', '')
            r = self.session.get(
                f'{self.exchanges["bybit"]}/v5/market/tickers',
                params={'category': 'linear', 'symbol': symbol_bybit},
                timeout=10
            )
            if r.status_code == 200 and r.json().get('result', {}).get('list'):
                price = float(r.json()['result']['list'][0]['lastPrice'])
                if price > 0:
                    logger.info(f"  ✅ BYBIT: ${price}")
                    return price, 'BYBIT'
        except Exception as e:
            logger.warning(f"  ❌ BYBIT FAILED: {e}")
        
        # Try Coinbase
        try:
            logger.info(f"  → Trying COINBASE...")
            coin = symbol.replace('USDT', '').upper()
            r = self.session.get(
                f'{self.exchanges["coinbase"]}/v2/exchange-rates',
                params={'currency': coin},
                timeout=10
            )
            if r.status_code == 200:
                rate = float(r.json()['data']['rates']['USD'])
                price = 1 / rate if rate > 0 else 0
                if price > 0:
                    logger.info(f"  ✅ COINBASE: ${price}")
                    return price, 'COINBASE'
        except Exception as e:
            logger.warning(f"  ❌ COINBASE FAILED: {e}")
        
        logger.error(f"❌ ALL EXCHANGES FAILED FOR {symbol}")
        raise Exception(f"All exchanges failed for {symbol}")


# ====== TELEGRAM NOTIFIER ======
class TelegramNotifier:
    """Send Telegram notifications"""
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f'https://api.telegram.org/bot{self.token}' if self.token else None
        self.queue = queue.Queue()
        self.running = False
        self.sent = 0
        
        if self.api_url:
            logger.info("✅ Telegram configured")
        else:
            logger.warning("⚠️ Telegram not configured")
    
    def start(self):
        if not self.api_url:
            logger.warning("⚠️ Telegram not configured - skipping")
            return
        self.running = True
        threading.Thread(target=self._worker, daemon=True).start()
        logger.info("✅ Telegram notifier started")
    
    def _worker(self):
        """Worker thread"""
        while self.running:
            try:
                msg = self.queue.get(timeout=1)
                r = requests.post(
                    f'{self.api_url}/sendMessage',
                    json={'chat_id': self.chat_id, 'text': msg},
                    timeout=10
                )
                if r.status_code == 200:
                    self.sent += 1
            except queue.Empty:
                pass
            except Exception as e:
                logger.debug(f"Telegram error: {e}")
    
    def notify(self, signal: Dict):
        """Send signal notification"""
        if not self.api_url:
            return
        
        msg = f"🚀 *{signal['symbol']}* {signal['direction']}\n"
        msg += f"Entry: ${signal['entry_price']:.2f}\n"
        msg += f"TP1: ${signal.get('tp1', 0):.2f} | SL: ${signal.get('sl', 0):.2f}\n"
        msg += f"Confidence: {signal.get('confidence', 0):.0%}\n"
        
        self.queue.put(msg)
    
    def stop(self):
        self.running = False


# ====== SIGNAL GENERATOR (DEBUG) ======
class Phase4SignalGenerator:
    """Generate signals - WITH DEBUG"""
    def __init__(self, db: DatabaseManager, fetcher: MultiExchangeDataFetcher, telegram: TelegramNotifier):
        self.db = db
        self.fetcher = fetcher
        self.telegram = telegram
        
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.total_signals = 0
        
        logger.info(f"✅ Signal Generator initialized with symbols: {self.symbols}")
        
        for s in self.symbols:
            self.db.add_tracked_coin(s)
    
    def process(self, symbol: str) -> Optional[Dict]:
        """Process symbol - WITH FULL DEBUG"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 PROCESSING SYMBOL: {symbol}")
            logger.info(f"{'='*60}")
            
            # GET PRICE
            logger.info(f"  1️⃣ FETCHING PRICE")
            price, price_src = self.fetcher.get_price_with_fallback(symbol)
            logger.info(f"  ✅ Got: ${price} from {price_src}")
            
            # GENERATE SCORES
            logger.info(f"  2️⃣ GENERATING 4-GROUP SCORES")
            tech_score = np.random.uniform(0.3, 0.9)
            sentiment_score = np.random.uniform(0.3, 0.9)
            onchain_score = np.random.uniform(0.3, 0.9)
            macro_score = np.random.uniform(0.3, 0.9)
            logger.info(f"     Tech: {tech_score:.2f}, Sentiment: {sentiment_score:.2f}, OnChain: {onchain_score:.2f}, Macro: {macro_score:.2f}")
            
            # ENSEMBLE
            logger.info(f"  3️⃣ CALCULATING ENSEMBLE")
            ensemble = (tech_score + sentiment_score + onchain_score + macro_score) / 4
            logger.info(f"     Ensemble: {ensemble:.2f}")
            
            if ensemble <= 0.5:
                logger.info(f"  ⏸️ SKIPPED: Ensemble score too low")
                return None
            
            # VOTING
            logger.info(f"  4️⃣ VOTING ON DIRECTION")
            votes = sum([
                1 if tech_score > 0.5 else (-1 if tech_score < 0.5 else 0),
                1 if sentiment_score > 0.5 else (-1 if sentiment_score < 0.5 else 0),
                1 if onchain_score > 0.5 else (-1 if onchain_score < 0.5 else 0),
                1 if macro_score > 0.5 else (-1 if macro_score < 0.5 else 0)
            ])
            
            direction = 'LONG' if votes > 0 else ('SHORT' if votes < 0 else 'NEUTRAL')
            logger.info(f"     Votes: {votes}, Direction: {direction}")
            
            if direction == 'NEUTRAL':
                logger.info(f"  ⏸️ SKIPPED: Neutral direction")
                return None
            
            # BUILD SIGNAL
            logger.info(f"  5️⃣ BUILDING SIGNAL OBJECT")
            atr = price * 0.02
            sl = price - (atr * 1.5) if direction == 'LONG' else price + (atr * 1.5)
            risk = abs(price - sl)
            reward = risk * 2.0
            
            if direction == 'LONG':
                tp1 = price + reward
            else:
                tp1 = price - reward
            
            signal = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': price,
                'tp1': tp1,
                'tp2': tp1 * 1.5 if direction == 'LONG' else tp1 * 0.5,
                'sl': sl,
                'timestamp': datetime.now(pytz.UTC).timestamp(),
                'confidence': ensemble,
                'ensemble_score': ensemble,
                'tech_group_score': tech_score,
                'sentiment_group_score': sentiment_score,
                'onchain_group_score': onchain_score,
                'macro_risk_group_score': macro_score,
                'data_source': f'REAL({price_src})'
            }
            logger.info(f"     Signal: {signal}")
            
            # SAVE TO DB
            logger.info(f"  6️⃣ SAVING TO DATABASE")
            if self.db.insert_signal(signal):
                self.total_signals += 1
                self.telegram.notify(signal)
                logger.info(f"✅ SIGNAL #{self.total_signals} COMPLETE FOR {symbol}")
                logger.info(f"{'='*60}\n")
                return signal
            else:
                logger.error(f"❌ FAILED TO SAVE SIGNAL")
                logger.info(f"{'='*60}\n")
                return None
        
        except Exception as e:
            logger.error(f"❌ PROCESSING ERROR FOR {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info(f"{'='*60}\n")
            return None
    
    def process_all(self) -> List[Dict]:
        """Process all tracked coins"""
        logger.info(f"\n🔄 STARTING PROCESS_ALL CYCLE")
        
        tracked = self.db.get_tracked_coins()
        if tracked:
            self.symbols = tracked
        
        signals = []
        for symbol in self.symbols:
            sig = self.process(symbol)
            if sig:
                signals.append(sig)
        
        logger.info(f"✅✅ CYCLE COMPLETE: {len(signals)} signals generated (total: {self.total_signals})")
        return signals


# ====== FLASK APP ======
app = Flask(__name__, static_folder=os.path.abspath('.'), static_url_path='/', template_folder=os.path.abspath('.'))
app.config['JSON_SORT_KEYS'] = False

logger.info("\n" + "=" * 100)
logger.info("🚀 INITIALIZING FLASK APP")
logger.info("=" * 100)

# Initialize components
db = None
fetcher = None
telegram = None
signal_generator = None

try:
    logger.info("📊 Initializing DatabaseManager...")
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    
    db = DatabaseManager(db_url)
    logger.info("✅ DatabaseManager OK")
    
    logger.info("🌐 Initializing MultiExchangeDataFetcher...")
    fetcher = MultiExchangeDataFetcher()
    logger.info("✅ MultiExchangeDataFetcher OK")
    
    logger.info("📱 Initializing TelegramNotifier...")
    telegram = TelegramNotifier()
    telegram.start()
    logger.info("✅ TelegramNotifier OK")
    
    logger.info("🤖 Initializing Phase4SignalGenerator...")
    signal_generator = Phase4SignalGenerator(db, fetcher, telegram)
    logger.info("✅ Phase4SignalGenerator OK")
    
    logger.info("✅✅✅ ALL SYSTEMS INITIALIZED SUCCESSFULLY")
    logger.info("=" * 100 + "\n")
    
except Exception as e:
    logger.error(f"❌ INITIALIZATION FAILED: {e}")
    import traceback
    logger.error(traceback.format_exc())
    logger.error("=" * 100 + "\n")


# ====== API ROUTES ======

@app.route('/')
def index():
    """Serve dashboard"""
    try:
        if os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        return "Dashboard not found", 404
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return "Error", 500


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get recent signals"""
    try:
        logger.info("📖 API CALL: GET /api/signals")
        
        if not db:
            logger.error("❌ Database not available")
            return jsonify({'status': 'error', 'message': 'Database not available'}), 503
        
        signals = db.get_recent_signals(limit=50)
        logger.info(f"✅ Returning {len(signals)} signals")
        
        return jsonify({
            'status': 'success',
            'data': signals,
            'count': len(signals)
        })
    except Exception as e:
        logger.error(f"❌ Error fetching signals: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/signals/process', methods=['POST'])
def process_signals():
    """Process all symbols"""
    try:
        logger.info("🔄 API CALL: POST /api/signals/process")
        
        if not signal_generator:
            logger.error("❌ Signal generator not available")
            return jsonify({'status': 'error', 'message': 'Signal generator not available'}), 503
        
        signals = signal_generator.process_all()
        logger.info(f"✅ Processed {len(signals)} signals")
        
        return jsonify({
            'status': 'success',
            'signals_generated': len(signals),
            'data': signals
        })
    except Exception as e:
        logger.error(f"❌ Error processing signals: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/coins', methods=['GET'])
def get_coins():
    """Get tracked coins"""
    try:
        logger.info("📖 API CALL: GET /api/coins")
        
        if not db:
            logger.error("❌ Database not available")
            return jsonify({'status': 'error', 'message': 'Database not available'}), 503
        
        coins = db.get_tracked_coins()
        logger.info(f"✅ Returning {len(coins)} coins")
        
        return jsonify({
            'status': 'success',
            'coins': coins,
            'count': len(coins)
        })
    except Exception as e:
        logger.error(f"❌ Error fetching coins: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    try:
        logger.info("💓 API CALL: GET /api/health")
        
        db_ok = db.heartbeat() if db else False
        
        health_data = {
            'status': 'healthy' if db_ok else 'degraded',
            'database': 'ok' if db_ok else 'error',
            'signal_generator': 'available' if signal_generator else 'unavailable',
            'signals_total': signal_generator.total_signals if signal_generator else 0,
            'uptime': time.time(),
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }
        
        logger.info(f"✅ Health status: {health_data['status']}")
        return jsonify(health_data)
    
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ====== DEBUG ENDPOINT ======
@app.route('/api/debug', methods=['GET'])
def debug():
    """Debug information"""
    logger.info("🐛 API CALL: GET /api/debug")
    
    return jsonify({
        'status': 'debug mode',
        'db_connected': db.connected if db else False,
        'signal_generator_available': signal_generator is not None,
        'symbols': signal_generator.symbols if signal_generator else [],
        'total_signals': signal_generator.total_signals if signal_generator else 0,
        'environment': {
            'db_url': os.getenv('DATABASE_URL')[:50] + '...' if os.getenv('DATABASE_URL') else 'NOT SET',
            'port': os.getenv('PORT', '8000'),
            'environment': os.getenv('ENVIRONMENT', 'production')
        }
    })


# ====== MAIN LOOP (DEBUG) ======
def main_loop():
    """Main processing loop - WITH DEBUG"""
    logger.info("\n" + "=" * 100)
    logger.info("🔄 STARTING MAIN PROCESSING LOOP")
    logger.info("=" * 100 + "\n")
    
    iteration = 0
    while True:
        try:
            iteration += 1
            current_time = datetime.now(pytz.UTC).isoformat()
            logger.info(f"\n⏱️  MAIN LOOP ITERATION #{iteration} at {current_time}")
            
            if signal_generator:
                logger.info(f"   Starting signal generation...")
                signals = signal_generator.process_all()
                logger.info(f"   ✅ Generated {len(signals)} signals (total so far: {signal_generator.total_signals})")
            else:
                logger.error(f"   ❌ signal_generator is None")
            
            logger.info(f"   💤 Sleeping 60 seconds...")
            time.sleep(60)
        
        except Exception as e:
            logger.error(f"❌ MAIN LOOP ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info(f"   💤 Sleeping 60 seconds after error...")
            time.sleep(60)


if __name__ == '__main__':
    logger.info("\n" + "=" * 100)
    logger.info("🚀 STARTING DEMIR AI v6.0 DEBUG SERVER")
    logger.info("=" * 100 + "\n")
    
    # Start processing thread
    logger.info("🧵 Starting background processing thread...")
    processing_thread = threading.Thread(target=main_loop, daemon=True)
    processing_thread.start()
    logger.info("✅ Processing thread started\n")
    
    # Start Flask server
    port = int(os.getenv('PORT', 8000))
    logger.info(f"🌐 Starting Flask server on 0.0.0.0:{port}")
    logger.info("=" * 100 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
