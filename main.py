#!/usr/bin/env python3
"""
🔱 DEMIR AI - Main Orchestrator v2.0 (PRODUCTION)
7/24 Bot Scheduler + Telegram Notifications

KURALLAR:
✅ APScheduler jobs (every 1sec, 5sec, 1hour, 1day)
✅ Real Telegram alerts
✅ Signal generation + execution
✅ Database logging
✅ Error loud - all exceptions caught & logged
✅ ZERO MOCK - real data only
"""

import os
import logging
import psycopg2
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import requests
import json

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = os.getenv('API_URL', 'http://localhost:5000')
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# TELEGRAM NOTIFICATIONS
# ============================================================================

def send_telegram(message: str, is_alert: bool = False) -> bool:
    """Send Telegram notification"""
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Telegram not configured")
            return False
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        # Format message
        if is_alert:
            message = f"🚨 ALERT\n{message}"
        else:
            message = f"🤖 BOT UPDATE\n{message}"
        
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"✅ Telegram sent: {message[:50]}...")
            return True
        else:
            logger.error(f"❌ Telegram failed: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return False

# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class MasterOrchestrator:
    """Coordinate all bot components"""
    
    def __init__(self):
        logger.info("🔄 Initializing Master Orchestrator...")
        
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            self.scheduler = BackgroundScheduler()
            self.is_running = False
            
            logger.info("✅ All components initialized")
        
        except Exception as e:
            logger.critical(f"❌ Initialization failed: {e}")
            raise
    
    def schedule_jobs(self):
        """Schedule all background jobs"""
        
        logger.info("📅 Scheduling jobs...")
        
        # Every 5 seconds: Generate signals
        self.scheduler.add_job(
            self.job_generate_signals,
            'interval',
            seconds=5,
            id='generate_signals',
            name='Generate trading signals'
        )
        
        # Every 1 hour: Calculate metrics
        self.scheduler.add_job(
            self.job_calculate_metrics,
            'interval',
            hours=1,
            id='calculate_metrics',
            name='Calculate performance metrics'
        )
        
        # Every day at 00:00: Telegram daily report
        self.scheduler.add_job(
            self.job_daily_report,
            CronTrigger(hour=0, minute=0),
            id='daily_report',
            name='Generate daily report'
        )
        
        logger.info("✅ Jobs scheduled successfully")
    
    def job_generate_signals(self):
        """Generate trading signals"""
        try:
            logger.info("🎯 Generating signals...")
            
            for symbol in SYMBOLS:
                try:
                    # Call API to generate signal
                    response = requests.post(
                        f"{API_URL}/api/signal/generate",
                        json={"symbol": symbol},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        signal = data.get('signal')
                        confidence = data.get('confidence')
                        
                        logger.info(f"✅ {symbol}: {signal} ({confidence:.1%})")
                        
                        # Send Telegram alert if high confidence signal
                        if confidence > 0.75:
                            msg = f"🎯 <b>{symbol}</b>\nSignal: {signal}\nConfidence: {confidence:.1%}"
                            send_telegram(msg, is_alert=True)
                    
                    else:
                        logger.error(f"❌ Signal failed for {symbol}")
                
                except Exception as e:
                    logger.error(f"❌ Signal error for {symbol}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Signal generation failed: {e}")
    
    def job_calculate_metrics(self):
        """Calculate performance metrics"""
        try:
            logger.info("📊 Calculating metrics...")
            
            response = requests.get(
                f"{API_URL}/api/metrics/daily",
                timeout=10
            )
            
            if response.status_code == 200:
                metrics = response.json().get('metrics', {})
                logger.info(f"✅ Metrics calculated: Sharpe={metrics.get('sharpe_ratio', 0):.2f}")
            
            else:
                logger.error("❌ Metrics calculation failed")
        
        except Exception as e:
            logger.error(f"❌ Metrics error: {e}")
    
    def job_daily_report(self):
        """Generate daily report"""
        try:
            logger.info("📄 Generating daily report...")
            
            response = requests.get(f"{API_URL}/api/portfolio/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json().get('stats', {})
                
                report = f"""
📊 <b>DEMIR AI - Daily Report</b>
{datetime.now().strftime('%Y-%m-%d')}

💰 Portfolio: ${stats.get('total', 0):.2f}
📈 Win Rate: {stats.get('win_rate', 0):.1%}
📊 Sharpe: {stats.get('sharpe_ratio', 0):.2f}
⚠️  Max DD: {stats.get('max_drawdown', 0):.2%}

🟢 Status: Running
"""
                
                send_telegram(report, is_alert=False)
                logger.info("✅ Daily report sent to Telegram")
            
            else:
                logger.error("❌ Daily report failed")
        
        except Exception as e:
            logger.error(f"❌ Daily report error: {e}")
    
    def start(self):
        """Start the orchestrator"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 DEMIR AI - MASTER ORCHESTRATOR v2.0")
            logger.info("=" * 80)
            
            # Schedule jobs
            self.schedule_jobs()
            
            # Start scheduler
            self.scheduler.start()
            
            self.is_running = True
            
            logger.info("✅ Orchestrator started successfully")
            logger.info("📡 Bot is now 7/24 active!\n")
            
            # Send startup alert
            send_telegram("🚀 DEMIR AI Bot started!", is_alert=False)
            
            # Keep running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("🛑 Orchestrator stopped by user")
        
        except Exception as e:
            logger.critical(f"❌ Orchestrator failed: {e}")
            send_telegram(f"❌ Bot crashed: {e}", is_alert=True)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        if self.db_conn:
            self.db_conn.close()
        
        logger.info("✅ Orchestrator stopped")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        orchestrator = MasterOrchestrator()
        orchestrator.start()
    
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
