# health_monitor.py - System Health Monitoring

import logging
import psycopg2
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor system health"""
    
    def __init__(self):
        self.checks = {}
        self.last_check = {}
    
    def check_database(self, connection_string):
        """Check database connectivity"""
        try:
            conn = psycopg2.connect(connection_string)
            conn.close()
            self.checks['database'] = True
            logger.info("✅ Database: OK")
            return True
        except Exception as e:
            self.checks['database'] = False
            logger.error(f"❌ Database: {e}")
            return False
    
    def check_binance_api(self):
        """Check Binance API"""
        try:
            response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
            self.checks['binance_api'] = response.status_code == 200
            logger.info("✅ Binance API: OK")
            return True
        except Exception as e:
            self.checks['binance_api'] = False
            logger.error(f"❌ Binance API: {e}")
            return False
    
    def get_status(self):
        """Get overall system status"""
        return all(self.checks.values())
