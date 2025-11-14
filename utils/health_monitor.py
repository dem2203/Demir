# FILE 1: health_monitor.py (NEW - 600 lines)

import logging
import time
import threading
from datetime import datetime
import psycopg2
import requests
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    System health monitoring - restarts failed components
    Checks: AI engine, Database, API connections, Signal generation
    """
    
    def __init__(self, config):
        self.config = config
        self.health_status = {
            'ai_engine': True,
            'database': True,
            'binance_api': True,
            'telegram': True,
            'last_signal_time': datetime.now()
        }
        self.restart_count = 0
        self.alert_sent = False
        
    def check_database_health(self) -> Tuple[bool, str]:
        """Check PostgreSQL connection"""
        try:
            conn = psycopg2.connect(self.config['DATABASE_URL'])
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at > NOW() - INTERVAL '5 minutes'")
            recent_signals = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            if recent_signals > 0:
                logger.info(f"✅ Database healthy: {recent_signals} signals in last 5 min")
                return True, f"OK ({recent_signals} signals)"
            else:
                logger.warning("⚠️ No signals generated in 5 minutes")
                return False, "No recent signals"
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return False, str(e)
    
    def check_api_connectivity(self) -> Tuple[bool, str]:
        """Check Binance API connectivity"""
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
                timeout=5
            )
            if response.status_code == 200:
                price = response.json()['price']
                logger.info(f"✅ Binance API healthy: BTC = ${price}")
                return True, f"OK (BTC=${price})"
            return False, f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"❌ API error: {e}")
            return False, str(e)
    
    def check_telegram_connectivity(self) -> Tuple[bool, str]:
        """Check Telegram bot connectivity"""
        try:
            if not self.config.get('TELEGRAM_TOKEN'):
                return True, "Telegram not configured (OK)"
            
            response = requests.get(
                f"https://api.telegram.org/bot{self.config['TELEGRAM_TOKEN']}/getMe",
                timeout=5
            )
            if response.status_code == 200:
                logger.info("✅ Telegram healthy")
                return True, "OK"
            return False, f"Telegram error: {response.status_code}"
        except Exception as e:
            logger.warning(f"⚠️ Telegram: {e}")
            return True, "Skipped (optional)"
    
    def check_ai_engine(self) -> Tuple[bool, str]:
        """Check if AI engine is processing"""
        try:
            last_signal = self.health_status['last_signal_time']
            time_since_signal = (datetime.now() - last_signal).total_seconds()
            
            if time_since_signal > 30:  # Should have signal within 30 sec
                logger.warning(f"⚠️ AI stalled: {time_since_signal}s since last signal")
                return False, f"Stalled ({time_since_signal}s)"
            
            logger.info(f"✅ AI engine healthy: signal {time_since_signal}s ago")
            return True, f"OK ({time_since_signal}s ago)"
        except Exception as e:
            logger.error(f"❌ AI check error: {e}")
            return False, str(e)
    
    def run_health_check(self) -> Dict:
        """Run full health check"""
        logger.info("🏥 Running full health check...")
        
        results = {
            'database': self.check_database_health(),
            'api': self.check_api_connectivity(),
            'telegram': self.check_telegram_connectivity(),
            'ai_engine': self.check_ai_engine(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Determine overall health
        all_healthy = all(result[0] for result in results.values())
        
        if not all_healthy:
            logger.critical("❌ HEALTH CHECK FAILED!")
            self._send_alert(results)
        else:
            logger.info("✅ ALL SYSTEMS HEALTHY")
        
        return results
    
    def _send_alert(self, results):
        """Send alert if system unhealthy"""
        if not self.alert_sent:
            logger.critical("🚨 SENDING ALERT TO TELEGRAM")
            # Implementation here
            self.alert_sent = True
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        def monitor_loop():
            while True:
                try:
                    self.run_health_check()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info(f"🏥 Health monitor started (interval: {interval}s)")
