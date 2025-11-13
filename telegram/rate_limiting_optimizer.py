"""
RATE LIMITING OPTIMIZER
Alert fatigue'i önle - çok sık bildirim gönderm
Smart batching ve smart filtering

⚠️ REAL DATA: Real user preferences ve real alert times
"""

import time
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitingOptimizer:
    """
    Akıllı rate limiting
    REAL user behavior'ı analiz et
    """
    
    def __init__(self):
        self.alert_queue = []
        self.last_alert_times = defaultdict(float)
        self.user_preferences = {}
        
        # Alert type'lı rate limits (saniye cinsinden)
        self.default_limits = {
            'CRITICAL': 60,      # 1 dakikada 1
            'HIGH': 300,         # 5 dakikada 1
            'MEDIUM': 900,       # 15 dakikada 1
            'LOW': 3600,         # Saatlik 1
            'PERFORMANCE': 86400  # Günlük 1
        }
    
    async def should_send_alert(self, alert_type: str, alert_id: str = None) -> bool:
        """
        Alert gönderilmeli mi?
        
        Args:
            alert_type: CRITICAL, HIGH, MEDIUM, LOW
            alert_id: Unique alert identifier
        
        Returns:
            bool: Send or not
        """
        
        now = time.time()
        limit = self.default_limits.get(alert_type, 300)
        
        key = f"{alert_type}_{alert_id}" if alert_id else alert_type
        last_time = self.last_alert_times.get(key, 0)
        
        time_since_last = now - last_time
        
        if time_since_last >= limit:
            self.last_alert_times[key] = now
            return True
        
        # Queue'ya ekle (daha sonra göndermek için)
        self.alert_queue.append({
            'type': alert_type,
            'id': alert_id,
            'queued_at': datetime.now(),
            'send_at': datetime.fromtimestamp(last_time + limit)
        })
        
        return False
    
    async def get_pending_alerts(self) -> List[Dict]:
        """
        Gönderilmek üzere bekleyen alerts'ler
        Batch'leme için
        """
        
        now = datetime.now()
        ready_alerts = []
        
        for alert in self.alert_queue[:]:
            if alert['send_at'] <= now:
                ready_alerts.append(alert)
                self.alert_queue.remove(alert)
        
        return ready_alerts
    
    async def batch_alerts(self, max_batch_size: int = 5) -> str:
        """
        Bekleyen alert'leri batch'le
        
        Returns:
            str: Batched message
        """
        
        pending = await self.get_pending_alerts()
        
        if not pending:
            return None
        
        # Batch oluştur
        batched = pending[:max_batch_size]
        
        message = "📬 <b>BATCHED ALERTS</b>\n\n"
        
        for alert in batched:
            message += f"• {alert['type']}: {alert['id']}\n"
        
        return message
    
    def set_user_preference(self, alert_type: str, enabled: bool, limit_seconds: int = None):
        """
        User preference ayarla
        Hangi alert'ler aktif, limit ne?
        """
        
        self.user_preferences[alert_type] = {
            'enabled': enabled,
            'limit': limit_seconds or self.default_limits.get(alert_type, 300)
        }
    
    def get_stats(self) -> Dict:
        """Alert statistics"""
        
        return {
            'queued_alerts': len(self.alert_queue),
            'last_alerts': dict(self.last_alert_times),
            'user_preferences': self.user_preferences
        }
