import queue
import threading
import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramAlertQueue:
    """
    Queue-based Telegram alerts with retry
    Ensures no alerts are lost even if API fails
    """
    
    def __init__(self, token: str, chat_id: str, max_retries: int = 3):
        self.token = token
        self.chat_id = chat_id
        self.max_retries = max_retries
        self.alert_queue = queue.Queue()
        self.sent_alerts = []
        self.running = False
        
    def add_alert(self, message: str, priority: str = "normal"):
        """Add alert to queue"""
        alert = {
            'message': message,
            'priority': priority,
            'created_at': datetime.now(),
            'retries': 0
        }
        self.alert_queue.put(alert)
        logger.info(f"📱 Alert queued: {priority}")
    
    def _send_alert(self, alert: dict) -> bool:
        """Send single alert"""
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    'chat_id': self.chat_id,
                    'text': alert['message'],
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Alert sent to Telegram")
                self.sent_alerts.append(alert)
                return True
            else:
                logger.warning(f"⚠️ Telegram error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return False
    
    def _process_queue(self):
        """Process alert queue with retries"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=5)
                
                # Try to send
                sent = self._send_alert(alert)
                
                if not sent and alert['retries'] < self.max_retries:
                    alert['retries'] += 1
                    logger.warning(f"Retrying alert (attempt {alert['retries']})")
                    time.sleep(5)  # Wait before retry
                    self.alert_queue.put(alert)
                
                elif not sent:
                    logger.error(f"❌ Alert failed after {self.max_retries} retries")
            
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Queue error: {e}")
    
    def start(self):
        """Start alert processing thread"""
        self.running = True
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()
        logger.info("📱 Telegram queue started")
    
    def stop(self):
        """Stop alert processing"""
        self.running = False
        logger.info("📱 Telegram queue stopped")
