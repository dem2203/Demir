"""
DEMIR AI v5.0 - Main Entry Point
Signal Generation Loop - Every 5 Seconds
100% Real Data - No Mock/Fake/Fallback
"""
import time
import logging
from datetime import datetime
import asyncio
from config import SIGNAL_INTERVAL, TRADING_SYMBOLS
from database import db
from ai_brain import AIBrain
import requests
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self):
        self.ai_brain = AIBrain()
        self.signal_count = 0
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def send_telegram_alert(self, message):
        """Send REAL alert to Telegram"""
        try:
            if not self.telegram_token or not self.telegram_chat_id:
                logger.warning("⚠️ Telegram credentials missing")
                return
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Telegram alert sent")
            else:
                logger.warning(f"⚠️ Telegram send failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
    
    def generate_signal(self, symbol):
        """Generate signal from ALL 62 LAYERS"""
        try:
            logger.info(f"🔬 Analyzing {symbol} - 62 layers processing...")
            
            # Get real market data and run all 62 layers
            signal = self.ai_brain.analyze(symbol)
            
            if signal:
                self.signal_count += 1
                logger.info(f"✅ SIGNAL #{self.signal_count}: {symbol} {signal['type']} ({signal['confidence']:.1%})")
                
                # Save to database (REAL DATA)
                db.save_signal(signal)
                
                # Send high-confidence alerts
                if signal['confidence'] >= 0.75:
                    msg = f"🤖 <b>SIGNAL</b>\n{symbol}\n{signal['type']}\nConfidence: {signal['confidence']:.1%}"
                    self.send_telegram_alert(msg)
                
                return signal
        except Exception as e:
            logger.error(f"❌ Signal generation error: {e}")
            return None
    
    def run(self):
        """Main loop - Generate signals every 5 seconds"""
        logger.info("🚀 DEMIR AI v5.0 started - Signal generation loop")
        logger.info(f"📊 Monitoring symbols: {TRADING_SYMBOLS}")
        logger.info(f"⏱️  Signal interval: {SIGNAL_INTERVAL} seconds")
        logger.info("=" * 60)
        
        try:
            while True:
                for symbol in TRADING_SYMBOLS:
                    self.generate_signal(symbol)
                    time.sleep(SIGNAL_INTERVAL / len(TRADING_SYMBOLS))
        except KeyboardInterrupt:
            logger.info("🛑 System stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    generator = SignalGenerator()
    generator.run()
