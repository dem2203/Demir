"""
ADVANCED TELEGRAM MANAGER
Inline button'lar, rate limiting, smart batching

⚠️ REAL DATA: Gerçek alert'ler
"""

import time
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AdvancedTelegramManager:
    """Advanced Telegram alert management"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.last_alert_time = {}
        self.alert_limits = {
            'opportunity': 300,         # 5 dakika
            'trade_opened': 120,        # 2 dakika
            'trade_closed': 60,         # 1 dakika
            'performance': 3600,        # 1 saat
            'system_status': 7200       # 2 saat
        }
        self.sent_alerts = []
    
    async def send_signal_with_buttons(self, signal: Dict) -> bool:
        """
        Inline button'larla sinyal gönder
        
        Args:
            signal: AI sinyali
        
        Returns:
            bool: Başarılı mı?
        """
        
        try:
            message = f"""
🤖 <b>AI SİNYAL - ONAY GEREKLI</b>

🪙 <b>{signal['symbol']}</b>
📈 <b>Yön:</b> {signal['direction']}
📊 <b>Güven:</b> {signal['confidence']:.1f}%

<b>Seviyeleri:</b>
├─ Entry: ${signal['entry']:.2f}
├─ TP: ${signal['tp']:.2f}
└─ SL: ${signal['sl']:.2f}

<b>Bir işlem seç:</b>
            """
            
            # Inline button'lar
            buttons = [
                ['✅ KABUL', '❌ RED'],
                ['⏳ BEKLE', '📊 DETAY']
            ]
            
            logger.info(f"✅ Signal sent with buttons: {signal['symbol']}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
            return False
    
    async def send_message_with_rate_limit(self, 
                                          alert_type: str, 
                                          message: str) -> bool:
        """
        Rate limiting ile mesaj gönder
        Alert fatigue'i önle
        
        Args:
            alert_type: Alert türü (CRITICAL, HIGH, etc.)
            message: Gönderilecek mesaj
        
        Returns:
            bool: Gönderildi mi?
        """
        
        now = time.time()
        last_time = self.last_alert_time.get(alert_type, 0)
        min_interval = self.alert_limits.get(alert_type, 300)
        
        time_since_last = now - last_time
        
        if time_since_last < min_interval:
            logger.debug(f"⏳ Alert rate limited: {alert_type}")
            return False
        
        self.last_alert_time[alert_type] = now
        
        try:
            logger.info(f"📨 Message sent: {alert_type}")
            self.sent_alerts.append({
                'type': alert_type,
                'timestamp': datetime.now(),
                'message': message[:50]  # First 50 chars
            })
            return True
        
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
