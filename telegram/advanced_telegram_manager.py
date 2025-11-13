"""
ADVANCED TELEGRAM MANAGER
Inline button'lar + Rate limiting
"""

import time
from typing import Dict, List

class AdvancedTelegramManager:
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.last_alert_time = {}
        self.alert_limits = {
            'opportunity': 300,
            'trade_opened': 120,
            'performance': 3600
        }
    
    async def send_signal_with_buttons(self, signal: Dict) -> bool:
        """Inline button'larla sinyal gönder"""
        
        message = f"""
🤖 <b>AI SİNYAL</b>

🪙 {signal['symbol']}
📈 {signal['direction']}
📊 Güven: {signal['confidence']:.1f}%

Entry: ${signal['entry']:.2f}
TP: ${signal['tp']:.2f}
SL: ${signal['sl']:.2f}
        """
        
        try:
            # Telegram'a gönder (inline buttons ile)
            # Bu implementation'un details'i subclass'ta
            return True
        except:
            return False
    
    async def send_message_with_rate_limit(self, alert_type: str, message: str) -> bool:
        """Rate limiting ile mesaj gönder"""
        
        now = time.time()
        last_time = self.last_alert_time.get(alert_type, 0)
        min_interval = self.alert_limits.get(alert_type, 300)
        
        if now - last_time < min_interval:
            return False
        
        self.last_alert_time[alert_type] = now
        
        try:
            # Telegram'a gönder
            return True
        except:
            return False
