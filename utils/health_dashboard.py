"""
🚀 DEMIR AI v5.2 - Health Dashboard & System Monitoring
📡 Real-time system health, API status, connectivity check
🎯 24/7 Operational Monitoring

Location: GitHub Root / utils/health_dashboard.py (NEW FILE)
Size: ~800 lines
Author: AI Research Agent
Date: 2025-11-15
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import pytz
import asyncio
import aiohttp
import threading
import time

logger = logging.getLogger('HEALTH_DASHBOARD')

# ============================================================================
# HEALTH CHECK ENGINE
# ============================================================================

class HealthCheckEngine:
    """Monitor system health and report status"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connection = self._connect()
        self.checks_completed = 0
        self.last_check = None
    
    def _connect(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            logger.error(f"❌ DB connect error: {e}")
            return None
    
    # =====================================================================
    # INDIVIDUAL HEALTH CHECKS
    # =====================================================================
    
    def check_database(self) -> Dict:
        """Check database connectivity and performance"""
        try:
            start = time.time()
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            elapsed = (time.time() - start) * 1000  # ms
            cursor.close()
            
            return {
                'component': 'database',
                'status': 'ONLINE' if elapsed < 100 else 'DEGRADED',
                'response_time_ms': round(elapsed, 2),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
        except Exception as e:
            return {
                'component': 'database',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def check_binance_api(self) -> Dict:
        """Check Binance API connectivity"""
        try:
            start = time.time()
            response = requests.get(
                'https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT',
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                price = response.json().get('price')
                return {
                    'component': 'api_binance',
                    'status': 'ONLINE',
                    'response_time_ms': round(elapsed, 2),
                    'price': price,
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
            else:
                return {
                    'component': 'api_binance',
                    'status': 'DEGRADED',
                    'status_code': response.status_code,
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
        except Exception as e:
            return {
                'component': 'api_binance',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def check_bybit_api(self) -> Dict:
        """Check Bybit API connectivity"""
        try:
            start = time.time()
            response = requests.get(
                'https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT',
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return {
                    'component': 'api_bybit',
                    'status': 'ONLINE',
                    'response_time_ms': round(elapsed, 2),
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
            else:
                return {
                    'component': 'api_bybit',
                    'status': 'DEGRADED',
                    'status_code': response.status_code,
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
        except Exception as e:
            return {
                'component': 'api_bybit',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def check_coinbase_api(self) -> Dict:
        """Check Coinbase API connectivity"""
        try:
            start = time.time()
            response = requests.get(
                'https://api.coinbase.com/v2/prices/BTC-USD/spot',
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return {
                    'component': 'api_coinbase',
                    'status': 'ONLINE',
                    'response_time_ms': round(elapsed, 2),
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
            else:
                return {
                    'component': 'api_coinbase',
                    'status': 'DEGRADED',
                    'status_code': response.status_code,
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
        except Exception as e:
            return {
                'component': 'api_coinbase',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def check_telegram(self) -> Dict:
        """Check Telegram connectivity"""
        try:
            token = os.getenv('TELEGRAM_TOKEN')
            if not token:
                return {
                    'component': 'telegram',
                    'status': 'UNCONFIGURED',
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
            
            start = time.time()
            response = requests.get(
                f'https://api.telegram.org/bot{token}/getMe',
                timeout=5
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return {
                    'component': 'telegram',
                    'status': 'ONLINE',
                    'response_time_ms': round(elapsed, 2),
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
            else:
                return {
                    'component': 'telegram',
                    'status': 'OFFLINE',
                    'status_code': response.status_code,
                    'timestamp': datetime.now(pytz.UTC).isoformat()
                }
        except Exception as e:
            return {
                'component': 'telegram',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    def check_signal_generation(self) -> Dict:
        """Check signal generation health"""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT COUNT(*) as count, MAX(timestamp) as latest
                FROM trades
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            signal_count = result['count'] if result else 0
            latest = result['latest'] if result else None
            
            # Should have at least 10 signals per hour (5-min interval × 3 coins)
            status = 'ONLINE' if signal_count >= 10 else 'DEGRADED' if signal_count > 0 else 'OFFLINE'
            
            return {
                'component': 'signal_generator',
                'status': status,
                'signals_last_hour': signal_count,
                'latest_signal': latest.isoformat() if latest else None,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
        except Exception as e:
            return {
                'component': 'signal_generator',
                'status': 'OFFLINE',
                'error': str(e),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
    
    # =====================================================================
    # COMPREHENSIVE HEALTH REPORT
    # =====================================================================
    
    def get_complete_health_report(self) -> Dict:
        """Get complete system health report"""
        logger.info("📊 Generating complete health report...")
        
        checks = {
            'database': self.check_database(),
            'binance': self.check_binance_api(),
            'bybit': self.check_bybit_api(),
            'coinbase': self.check_coinbase_api(),
            'telegram': self.check_telegram(),
            'signal_generator': self.check_signal_generation()
        }
        
        # Overall status
        statuses = [c.get('status') for c in checks.values()]
        if 'OFFLINE' in statuses and statuses.count('OFFLINE') >= 2:
            overall = 'CRITICAL'
        elif 'OFFLINE' in statuses:
            overall = 'WARNING'
        elif 'DEGRADED' in statuses:
            overall = 'DEGRADED'
        else:
            overall = 'HEALTHY'
        
        report = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'overall_status': overall,
            'checks': checks,
            'summary': {
                'online': sum(1 for c in checks.values() if c.get('status') == 'ONLINE'),
                'degraded': sum(1 for c in checks.values() if c.get('status') == 'DEGRADED'),
                'offline': sum(1 for c in checks.values() if c.get('status') == 'OFFLINE'),
                'total': len(checks)
            }
        }
        
        logger.info(f"✅ Health report: {overall}")
        return report
    
    def save_health_report(self, report: Dict) -> bool:
        """Save health report to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO health_reports (
                    report_data, overall_status, timestamp
                ) VALUES (%s, %s, %s)
            """, (
                json.dumps(report),
                report['overall_status'],
                datetime.now(pytz.UTC)
            ))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"❌ Save report error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

# ============================================================================
# CONTINUOUS MONITORING WORKER
# ============================================================================

class HealthMonitoringWorker:
    """Continuous health monitoring in background"""
    
    def __init__(self, db_url: str, interval_seconds: int = 300):
        self.engine = HealthCheckEngine(db_url)
        self.interval = interval_seconds
        self.running = False
        self.worker_thread = None
    
    def start(self):
        """Start monitoring worker"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info(f"✅ Health monitoring started (interval: {self.interval}s)")
    
    def _worker_loop(self):
        """Worker loop - runs continuously"""
        while self.running:
            try:
                report = self.engine.get_complete_health_report()
                self.engine.save_health_report(report)
                
                # Alert if critical
                if report['overall_status'] == 'CRITICAL':
                    logger.critical("🚨 CRITICAL SYSTEM ISSUE DETECTED")
                    # Send Telegram alert
                    self._send_alert(report)
                
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"❌ Worker error: {e}")
                time.sleep(self.interval)
    
    def _send_alert(self, report: Dict):
        """Send Telegram alert"""
        try:
            token = os.getenv('TELEGRAM_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if token and chat_id:
                offline = [k for k, v in report['checks'].items() if v.get('status') == 'OFFLINE']
                message = f"🚨 CRITICAL: {', '.join(offline)} offline"
                
                requests.post(
                    f'https://api.telegram.org/bot{token}/sendMessage',
                    json={'chat_id': chat_id, 'text': message}
                )
        except:
            pass
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.worker_thread.join(timeout=5)
        self.engine.close()
        logger.info("✅ Health monitoring stopped")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    engine = HealthCheckEngine(os.getenv('DATABASE_URL'))
    report = engine.get_complete_health_report()
    print(json.dumps(report, indent=2, default=str))
    engine.close()

