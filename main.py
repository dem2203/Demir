# main.py - Signal Generation Engine
# DEMIR AI v5.0 - 100% REAL DATA POLICY
# NO MOCK, NO FAKE, NO FALLBACK - ONLY REAL SIGNALS

"""
Production-grade signal generator
Every 5 seconds: Analyzes market with 62 layers
Generates REAL signals from REAL data
Saves to REAL PostgreSQL
Sends REAL Telegram alerts
"""

import time
import logging
import sys
import os
from datetime import datetime
import requests

# Import from local modules (MUST EXIST)
from config import (
    DATABASE_URL, TRADING_SYMBOLS, SIGNAL_INTERVAL, 
    CONFIDENCE_THRESHOLD, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, LOG_LEVEL
)
from database import db
from ai_brain import AIBrain

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('demir_ai.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# REAL PRICE FETCHER - 100% REAL DATA
# ============================================================================
class RealPriceFetcher:
    """Fetch REAL prices from Binance API"""
    
    @staticmethod
    def get_binance_price(symbol):
        """
        Fetch REAL price from Binance
        NO MOCK DATA - REAL API CALL
        """
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                logger.info(f"✅ {symbol} REAL price: ${price:.2f}")
                return price
            else:
                logger.error(f"❌ Binance API error: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Price fetch error: {e}")
            return None

# ============================================================================
# REAL TELEGRAM NOTIFIER - 100% REAL ALERTS
# ============================================================================
class RealTelegramNotifier:
    """Send REAL alerts to Telegram"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"
    
    def send_signal_alert(self, signal):
        """
        Send REAL Telegram alert
        NO FALLBACK - REAL MESSAGE OR NOTHING
        """
        try:
            if not self.token or not self.chat_id:
                logger.warning("⚠️ Telegram not configured - skipping alert")
                return False
            
            message = self._format_message(signal)
            
            params = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                data=params,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram alert sent: {signal['symbol']} {signal['type']}")
                return True
            else:
                logger.error(f"❌ Telegram error: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")
            return False
    
    def _format_message(self, signal):
        """Format signal for Telegram"""
        return f"""
🤖 <b>DEMIR AI SIGNAL</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Symbol:</b> {signal['symbol']}
🎯 <b>Signal:</b> {signal['type']}
💪 <b>Confidence:</b> {signal['confidence']:.1%}
📈 <b>Entry:</b> ${signal['entry']:.2f}
✅ <b>TP1:</b> ${signal['tp1']:.2f}
✅ <b>TP2:</b> ${signal['tp2']:.2f}
✅ <b>TP3:</b> ${signal['tp3']:.2f}
🛑 <b>SL:</b> ${signal['sl']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} UTC
        """

# ============================================================================
# SIGNAL GENERATOR - 100% REAL
# ============================================================================
class SignalGenerator:
    """Generate REAL signals from REAL market data"""
    
    def __init__(self):
        """Initialize generator"""
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI v5.0 - Signal Generator Starting")
        logger.info("=" * 80)
        logger.info("⚠️  STRICT POLICY: 100% REAL DATA ONLY")
        logger.info("     ❌ NO MOCK DATA")
        logger.info("     ❌ NO FAKE DATA")
        logger.info("     ❌ NO FALLBACK DATA")
        logger.info("     ✅ ONLY REAL APIs")
        logger.info("     ✅ ONLY REAL SIGNALS")
        logger.info("=" * 80)
        
        # Initialize components
        self.ai_brain = AIBrain()
        self.price_fetcher = RealPriceFetcher()
        self.telegram = RealTelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        
        # Statistics
        self.cycle_count = 0
        self.signals_generated = 0
        self.failed_cycles = 0
        self.start_time = datetime.now()
        
        logger.info(f"📊 Monitoring symbols: {', '.join(TRADING_SYMBOLS)}")
        logger.info(f"⏱️  Signal interval: {SIGNAL_INTERVAL} seconds")
        logger.info(f"🎯 Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
        logger.info("=" * 80)
    
    def generate_real_signal(self, symbol):
        """
        Generate signal from REAL price data
        REAL Binance API → REAL AI analysis → REAL database → REAL Telegram
        """
        try:
            logger.info(f"\n🔬 Analyzing {symbol}...")
            
            # STEP 1: Fetch REAL price from Binance
            price = self.price_fetcher.get_binance_price(symbol)
            
            if not price:
                logger.warning(f"⚠️  Could not fetch price for {symbol} - skipping")
                return False
            
            # STEP 2: Analyze with REAL AI Brain (62 layers)
            signal = self.ai_brain.analyze(symbol, price)
            
            if not signal:
                logger.warning(f"⚠️  AI analysis failed for {symbol}")
                return False
            
            self.signals_generated += 1
            
            # Log signal details
            logger.info(f"✅ SIGNAL GENERATED (#{self.signals_generated})")
            logger.info(f"   Symbol: {signal['symbol']}")
            logger.info(f"   Type: {signal['type']}")
            logger.info(f"   Confidence: {signal['confidence']:.1%}")
            logger.info(f"   Entry: ${signal['entry']:.2f}")
            logger.info(f"   TP1: ${signal['tp1']:.2f} | TP2: ${signal['tp2']:.2f} | TP3: ${signal['tp3']:.2f}")
            logger.info(f"   SL: ${signal['sl']:.2f}")
            
            # STEP 3: Save to REAL PostgreSQL database
            trade_id = db.save_signal(signal)
            
            if trade_id:
                logger.info(f"   ✅ Saved to PostgreSQL (Trade ID: {trade_id})")
            else:
                logger.error(f"   ❌ Failed to save to database")
            
            # STEP 4: Send REAL Telegram alert (if high confidence)
            if signal['confidence'] >= CONFIDENCE_THRESHOLD:
                logger.info(f"   📱 Confidence {signal['confidence']:.1%} >= {CONFIDENCE_THRESHOLD:.0%}")
                logger.info(f"   → Sending Telegram alert...")
                
                telegram_sent = self.telegram.send_signal_alert(signal)
                
                if telegram_sent:
                    logger.info(f"   ✅ Telegram alert sent successfully")
                else:
                    logger.warning(f"   ⚠️  Telegram alert not sent (check credentials)")
            else:
                logger.info(f"   ⓘ Confidence {signal['confidence']:.1%} < {CONFIDENCE_THRESHOLD:.0%} - Telegram skipped")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            self.failed_cycles += 1
            return False
    
    def print_cycle_summary(self):
        """Print cycle summary"""
        uptime = datetime.now() - self.start_time
        success_rate = (self.signals_generated / max(1, self.cycle_count)) * 100 if self.cycle_count > 0 else 0
        
        logger.info(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CYCLE SUMMARY (Every 10 cycles)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  Uptime: {uptime}
📈 Total Cycles: {self.cycle_count}
✅ Signals Generated: {self.signals_generated}
❌ Failed Cycles: {self.failed_cycles}
📊 Success Rate: {success_rate:.1f}%
🔄 Next cycle in {SIGNAL_INTERVAL} seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
    
    def run(self):
        """Main loop - 100% REAL signal generation"""
        logger.info("\n🚀 Starting main analysis loop...")
        logger.info("🔄 Every 5 seconds: 62 layers analyze REAL market data\n")
        
        try:
            while True:
                self.cycle_count += 1
                cycle_start = datetime.now()
                
                logger.info(f"\n{'='*80}")
                logger.info(f"📍 CYCLE #{self.cycle_count} - {cycle_start.strftime('%H:%M:%S UTC')}")
                logger.info(f"{'='*80}")
                
                # Process each symbol
                for symbol in TRADING_SYMBOLS:
                    self.generate_real_signal(symbol)
                    time.sleep(0.5)  # Small delay between symbols
                
                # Print summary every 10 cycles
                if self.cycle_count % 10 == 0:
                    self.print_cycle_summary()
                
                # Wait for next cycle
                elapsed = (datetime.now() - cycle_start).total_seconds()
                wait_time = max(0, SIGNAL_INTERVAL - elapsed)
                
                if wait_time > 0:
                    logger.info(f"⏳ Cycle complete ({elapsed:.2f}s), waiting {wait_time:.2f}s...")
                    time.sleep(wait_time)
        
        except KeyboardInterrupt:
            logger.info("\n\n🛑 System stopped by user (Ctrl+C)")
            logger.info(f"📊 Final statistics: {self.signals_generated} signals generated")
        
        except Exception as e:
            logger.error(f"\n❌ FATAL ERROR: {e}")
            logger.info("💔 System will restart in 5 seconds...")
            time.sleep(5)
            self.run()  # Auto-restart

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        generator = SignalGenerator()
        generator.run()
    
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)
