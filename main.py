# main.py - Signal Generation Loop - Production Grade
# DEMIR AI v5.0 - Real-time Market Analysis Engine

"""
DEMIR AI v5.0 - Main Signal Generator
Runs continuously, analyzes market every 5 seconds
Generates real signals from 62 layers
100% Real Data - No mock/fake/fallback
"""

import time
import logging
import sys
import os
from datetime import datetime
import requests
import json

# Import config & database
from config import SIGNAL_INTERVAL, TRADING_SYMBOLS, CONFIDENCE_THRESHOLD, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from database import db
from ai_brain import AIBrain

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('demir_ai.log')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# SIGNAL GENERATOR - PRODUCTION GRADE
# ============================================================================
class SignalGenerator:
    def __init__(self):
        """Initialize signal generator"""
        logger.info("🚀 Initializing DEMIR AI v5.0 Signal Generator...")
        
        self.ai_brain = AIBrain()
        self.signal_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # Telegram config
        self.telegram_token = TELEGRAM_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
        
        logger.info("✅ Signal Generator initialized")
        logger.info(f"📊 Monitoring symbols: {TRADING_SYMBOLS}")
        logger.info(f"⏱️  Signal interval: {SIGNAL_INTERVAL} seconds")
        logger.info(f"🎯 Confidence threshold: {CONFIDENCE_THRESHOLD:.0%}")
        logger.info("=" * 70)
    
    def send_telegram_alert(self, signal):
        """Send REAL alert to Telegram"""
        try:
            if not self.telegram_token or not self.telegram_chat_id:
                logger.warning("⚠️ Telegram credentials not configured")
                return False
            
            # Format message
            message = f"""
🤖 <b>DEMIR AI SIGNAL</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>Symbol:</b> {signal['symbol']}
🎯 <b>Signal:</b> {signal['type']}
💪 <b>Confidence:</b> {signal['confidence']:.1%}
📈 <b>Entry:</b> ${signal.get('entry', 0):.2f}
✅ <b>TP1:</b> ${signal.get('tp1', 0):.2f}
✅ <b>TP2:</b> ${signal.get('tp2', 0):.2f}
✅ <b>TP3:</b> ${signal.get('tp3', 0):.2f}
🛑 <b>SL:</b> ${signal.get('sl', 0):.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram alert sent: {signal['symbol']} {signal['type']}")
                return True
            else:
                logger.warning(f"⚠️ Telegram failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False
    
    def process_signal(self, symbol):
        """Process one symbol - generate signal from 62 layers"""
        try:
            # Analyze with AI brain (62 layers)
            signal = self.ai_brain.analyze(symbol)
            
            if not signal:
                return None
            
            self.signal_count += 1
            
            # Log signal
            logger.info(f"✅ SIGNAL #{self.signal_count}")
            logger.info(f"   Symbol: {signal['symbol']}")
            logger.info(f"   Type: {signal['type']}")
            logger.info(f"   Confidence: {signal['confidence']:.1%}")
            logger.info(f"   Entry: ${signal.get('entry', 0):.2f}")
            
            # Save to database (REAL persistence)
            trade_id = db.save_signal(signal)
            
            if trade_id:
                logger.info(f"   ✅ Saved to database (ID: {trade_id})")
            
            # Send Telegram if high confidence
            if signal['confidence'] >= CONFIDENCE_THRESHOLD:
                self.send_telegram_alert(signal)
            
            return signal
        
        except Exception as e:
            logger.error(f"❌ Signal processing error: {e}")
            self.error_count += 1
            return None
    
    def print_status(self):
        """Print system status"""
        uptime = datetime.now() - self.start_time
        logger.info(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DEMIR AI v5.0 - System Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  Uptime: {uptime}
📈 Signals Generated: {self.signal_count}
❌ Errors: {self.error_count}
🎯 Success Rate: {(self.signal_count / (self.signal_count + self.error_count) * 100) if (self.signal_count + self.error_count) > 0 else 0:.1f}%
🔄 Next cycle in {SIGNAL_INTERVAL} seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
    
    def run(self):
        """Main signal generation loop"""
        logger.info("🚀 Starting DEMIR AI v5.0 - Signal Generation Loop")
        logger.info("🔄 Every 5 seconds: 62 layers analyze market")
        logger.info("=" * 70)
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                cycle_start = datetime.now()
                
                logger.info(f"\n📍 Cycle #{cycle_count} - {cycle_start.strftime('%H:%M:%S')}")
                
                # Process each symbol
                for symbol in TRADING_SYMBOLS:
                    logger.info(f"🔬 Analyzing {symbol}...")
                    
                    signal = self.process_signal(symbol)
                    
                    # Small delay between symbols
                    time.sleep(0.5)
                
                # Print status every 10 cycles
                if cycle_count % 10 == 0:
                    self.print_status()
                
                # Wait for next cycle
                elapsed = (datetime.now() - cycle_start).total_seconds()
                wait_time = max(0, SIGNAL_INTERVAL - elapsed)
                
                logger.info(f"⏳ Cycle complete in {elapsed:.2f}s, waiting {wait_time:.2f}s...")
                
                time.sleep(wait_time)
        
        except KeyboardInterrupt:
            logger.info("\n🛑 System stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Fatal error in main loop: {e}")
            self.error_count += 1
            time.sleep(5)  # Retry after 5 seconds
            self.run()  # Restart

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        logger.info("""
╔════════════════════════════════════════════════════════════════════╗
║                    DEMIR AI v5.0 - VERSION 3                       ║
║              Professional AI Trading Bot - 62 Layers                ║
║                      100% Real Data Policy                          ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        
        generator = SignalGenerator()
        generator.run()
    
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)
