#!/usr/bin/env python3
"""
🔱 DEMIR AI - Telegram Notifier v2.0 (PRODUCTION)
Centralized Telegram notification system

KURALLAR:
✅ Telegram Bot API integration
✅ Async message sending
✅ Message queue system
✅ Retry logic + error handling
✅ Error loud - all logged
✅ ZERO MOCK - real Telegram API only
✅ Production grade reliability
"""

import os
import logging
import requests
import threading
import queue
import time
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_API_URL = "https://api.telegram.org/bot"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
MESSAGE_QUEUE_SIZE = 100

# ============================================================================
# MESSAGE TYPES
# ============================================================================

class AlertType(Enum):
    """Alert severity levels"""
    INFO = "ℹ️"      # Information
    SUCCESS = "✅"   # Success
    WARNING = "⚠️"   # Warning
    ERROR = "❌"     # Error
    CRITICAL = "🚨"  # Critical alert
    SIGNAL = "🎯"    # Trading signal
    TRADE = "💰"     # Trade execution
    PROFIT = "📈"    # Profit alert
    LOSS = "📉"      # Loss alert

# ============================================================================
# MESSAGE TEMPLATES
# ============================================================================

class MessageTemplates:
    """Predefined message templates"""
    
    @staticmethod
    def bot_startup() -> str:
        return f"🚀 <b>DEMIR AI Bot Started</b>\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def bot_shutdown() -> str:
        return f"🛑 <b>DEMIR AI Bot Stopped</b>\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def trading_signal(symbol: str, signal: str, confidence: float, price: float) -> str:
        signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
        return f"""
{signal_emoji} <b>Trading Signal</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {signal}
<b>Confidence:</b> {confidence:.1%}
<b>Price:</b> ${price:.2f}
<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
    
    @staticmethod
    def position_opened(symbol: str, side: str, size: float, entry: float) -> str:
        return f"""
💰 <b>Position Opened</b>

<b>Symbol:</b> {symbol}
<b>Side:</b> {side}
<b>Size:</b> {size:.4f}
<b>Entry:</b> ${entry:.2f}
<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
    
    @staticmethod
    def position_closed(symbol: str, pnl: float, roi: float) -> str:
        pnl_emoji = "📈" if pnl > 0 else "📉"
        return f"""
{pnl_emoji} <b>Position Closed</b>

<b>Symbol:</b> {symbol}
<b>P&L:</b> ${pnl:.2f}
<b>ROI:</b> {roi:.2%}
<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
    
    @staticmethod
    def error_alert(error_msg: str) -> str:
        return f"""
🚨 <b>Error Alert</b>

<b>Error:</b> {error_msg}
<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}

<i>Check logs for details</i>
"""
    
    @staticmethod
    def daily_report(metrics: Dict) -> str:
        return f"""
📊 <b>Daily Report</b>
{datetime.now().strftime('%Y-%m-%d')}

📈 <b>Return:</b> {metrics.get('return_pct', 0):.2f}%
🎯 <b>Win Rate:</b> {metrics.get('win_rate', 0):.1%}
📊 <b>Sharpe:</b> {metrics.get('sharpe_ratio', 0):.2f}
⚠️ <b>Max DD:</b> {metrics.get('max_drawdown', 0):.2%}
💹 <b>Trades:</b> {metrics.get('total_trades', 0)}

🟢 Status: Running
"""

# ============================================================================
# TELEGRAM NOTIFIER
# ============================================================================

class TelegramNotifier:
    """Centralized Telegram notification system"""
    
    def __init__(self):
        """Initialize notifier"""
        logger.info("🔄 Initializing Telegram Notifier...")
        
        self.message_queue = queue.Queue(maxsize=MESSAGE_QUEUE_SIZE)
        self.is_running = False
        self.worker_thread = None
        
        # Validate tokens
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Telegram tokens not configured - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Telegram Notifier initialized")
    
    def start(self):
        """Start the notifier worker thread"""
        if not self.enabled:
            logger.warning("⚠️ Telegram notifier is disabled")
            return
        
        logger.info("🚀 Starting Telegram worker thread...")
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("✅ Telegram worker thread started")
    
    def stop(self):
        """Stop the notifier worker thread"""
        logger.info("🛑 Stopping Telegram worker thread...")
        
        self.is_running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        logger.info("✅ Telegram worker thread stopped")
    
    def _worker(self):
        """Worker thread that processes message queue"""
        logger.info("⚙️ Telegram worker thread running")
        
        while self.is_running:
            try:
                # Get message from queue (timeout 1 second)
                try:
                    message = self.message_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Send message
                self._send_message(message)
                
                # Mark as done
                self.message_queue.task_done()
            
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
    
    def _send_message(self, message: str, retries: int = 0) -> bool:
        """Send message to Telegram with retry logic"""
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram not enabled")
                return False
            
            url = f"{TELEGRAM_API_URL}{TELEGRAM_TOKEN}/sendMessage"
            
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram sent ({len(message)} chars)")
                return True
            
            else:
                logger.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
                
                # Retry logic
                if retries < MAX_RETRIES:
                    logger.info(f"🔄 Retrying... (attempt {retries + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    return self._send_message(message, retries + 1)
                
                return False
        
        except requests.Timeout:
            logger.error("❌ Telegram request timeout")
            
            if retries < MAX_RETRIES:
                logger.info(f"🔄 Retrying after timeout...")
                time.sleep(RETRY_DELAY)
                return self._send_message(message, retries + 1)
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    def send(self, message: str, async_mode: bool = True) -> bool:
        """Send notification"""
        try:
            if not self.enabled:
                logger.warning("⚠️ Telegram not enabled")
                return False
            
            if async_mode:
                # Queue message for async sending
                self.message_queue.put(message, block=False)
                logger.debug(f"📤 Message queued (queue size: {self.message_queue.qsize()})")
                return True
            
            else:
                # Send immediately
                return self._send_message(message)
        
        except queue.Full:
            logger.error("❌ Message queue full - message dropped")
            return False
        
        except Exception as e:
            logger.error(f"❌ Send error: {e}")
            return False
    
    def send_signal(self, symbol: str, signal: str, confidence: float, price: float) -> bool:
        """Send trading signal notification"""
        message = MessageTemplates.trading_signal(symbol, signal, confidence, price)
        return self.send(message, async_mode=True)
    
    def send_position_opened(self, symbol: str, side: str, size: float, entry: float) -> bool:
        """Send position opened notification"""
        message = MessageTemplates.position_opened(symbol, side, size, entry)
        return self.send(message, async_mode=True)
    
    def send_position_closed(self, symbol: str, pnl: float, roi: float) -> bool:
        """Send position closed notification"""
        message = MessageTemplates.position_closed(symbol, pnl, roi)
        return self.send(message, async_mode=True)
    
    def send_error(self, error_msg: str) -> bool:
        """Send error alert"""
        message = MessageTemplates.error_alert(error_msg)
        return self.send(message, async_mode=True)
    
    def send_daily_report(self, metrics: Dict) -> bool:
        """Send daily performance report"""
        message = MessageTemplates.daily_report(metrics)
        return self.send(message, async_mode=False)
    
    def send_startup(self) -> bool:
        """Send startup notification"""
        message = MessageTemplates.bot_startup()
        return self.send(message, async_mode=False)
    
    def send_shutdown(self) -> bool:
        """Send shutdown notification"""
        message = MessageTemplates.bot_shutdown()
        return self.send(message, async_mode=False)

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_notifier_instance: Optional[TelegramNotifier] = None

def get_notifier() -> TelegramNotifier:
    """Get or create global notifier instance"""
    global _notifier_instance
    
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    
    return _notifier_instance

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def send_notification(message: str, async_mode: bool = True) -> bool:
    """Send a notification"""
    return get_notifier().send(message, async_mode)

def send_signal(symbol: str, signal: str, confidence: float, price: float) -> bool:
    """Send trading signal"""
    return get_notifier().send_signal(symbol, signal, confidence, price)

def send_position_opened(symbol: str, side: str, size: float, entry: float) -> bool:
    """Send position opened alert"""
    return get_notifier().send_position_opened(symbol, side, size, entry)

def send_position_closed(symbol: str, pnl: float, roi: float) -> bool:
    """Send position closed alert"""
    return get_notifier().send_position_closed(symbol, pnl, roi)

def send_error(error_msg: str) -> bool:
    """Send error alert"""
    return get_notifier().send_error(error_msg)

def send_daily_report(metrics: Dict) -> bool:
    """Send daily report"""
    return get_notifier().send_daily_report(metrics)

def start_notifier():
    """Start notifier worker"""
    get_notifier().start()

def stop_notifier():
    """Stop notifier worker"""
    get_notifier().stop()

# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 TELEGRAM NOTIFIER TEST")
    logger.info("=" * 80)
    
    notifier = get_notifier()
    notifier.start()
    
    # Test signals
    logger.info("📤 Sending test notifications...")
    
    notifier.send_startup()
    
    notifier.send_signal("BTCUSDT", "BUY", 0.78, 43250.50)
    notifier.send_position_opened("BTCUSDT", "LONG", 0.5, 43250.50)
    notifier.send_position_closed("BTCUSDT", 125.50, 0.0289)
    
    metrics = {
        "return_pct": 2.45,
        "win_rate": 0.623,
        "sharpe_ratio": 1.8,
        "max_drawdown": -0.15,
        "total_trades": 12
    }
    notifier.send_daily_report(metrics)
    
    notifier.send_shutdown()
    
    # Wait for queue to process
    time.sleep(5)
    notifier.stop()
    
    logger.info("✅ Test completed")
