# ============================================================================
# MONITORING & ALERTING SYSTEM
# ============================================================================

MONITORING_CONTENT = """
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict
import requests
import json

logger = logging.getLogger(__name__)

class SystemMonitor:
    '''
    Continuous system monitoring with Telegram alerts
    '''
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_log_chat_id = os.getenv('TELEGRAM_LOG_CHAT_ID')
        
        self.last_report_time = datetime.now()
        self.report_interval = timedelta(hours=1)  # Hourly reports
        
        self.metrics = {
            'uptime_seconds': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0,
            'api_calls': 0,
            'errors': 0,
            'last_signal': None,
            'current_positions': 0
        }
    
    def update_metrics(self, executor_metrics: Dict):
        '''Update metrics from trading executor'''
        try:
            self.metrics['total_trades'] = executor_metrics.get('total_trades', 0)
            self.metrics['winning_trades'] = executor_metrics.get('winning_trades', 0)
            self.metrics['total_pnl'] = executor_metrics.get('total_pnl', 0)
            self.metrics['current_positions'] = executor_metrics.get('open_positions', 0)
        except Exception as e:
            logger.error(f"❌ Metrics update error: {e}")
    
    async def periodic_health_check(self):
        '''Run health checks every hour'''
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hour
                
                health_report = self._generate_health_report()
                self._send_telegram_alert(health_report, chat_type='metrics')
                
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                self._send_telegram_alert(f"❌ HEALTH CHECK FAILED: {e}", chat_type='errors')
    
    def _generate_health_report(self) -> str:
        '''Generate hourly health report'''
        try:
            win_rate = (self.metrics['winning_trades'] / max(self.metrics['total_trades'], 1) * 100)
            
            report = f"""
📊 HOURLY PERFORMANCE REPORT
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Trading:
  • Total Trades: {self.metrics['total_trades']}
  • Winning: {self.metrics['winning_trades']}
  • Win Rate: {win_rate:.1f}%
  • Total PnL: ${self.metrics['total_pnl']:,.2f}
  • Open Positions: {self.metrics['current_positions']}

🔧 System:
  • API Calls: {self.metrics['api_calls']}
  • Errors: {self.metrics['errors']}
  • Uptime: {self.metrics['uptime_seconds'] / 3600:.1f}h

✅ Status: OPERATIONAL
            """
            
            return report.strip()
        
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            return "❌ Report generation failed"
    
    def _send_telegram_alert(self, message: str, chat_type: str = 'metrics'):
        '''Send alert to appropriate Telegram chat'''
        try:
            if chat_type == 'metrics':
                chat_id = self.telegram_chat_id
            else:
                chat_id = self.telegram_log_chat_id
            
            if not self.telegram_token or not chat_id:
                logger.warning("⚠️ Telegram credentials missing")
                return
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            params = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, params=params, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ Alert sent to {chat_type} chat")
            else:
                logger.warning(f"⚠️ Telegram error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ Send alert error: {e}")
    
    def log_trade_execution(self, trade_result: Dict):
        '''Log every trade execution to Telegram'''
        try:
            log_message = f"""
✅ TRADE EXECUTED
Symbol: {trade_result.get('symbol')}
Direction: {trade_result.get('direction')}
Entry: ${trade_result.get('entry_price', 0):.2f}
Quantity: {trade_result.get('quantity', 0):.4f}
TP1: ${trade_result.get('tp1', 0):.2f}
SL: ${trade_result.get('sl', 0):.2f}
RR Ratio: {trade_result.get('rr_ratio', 0):.2f}
Confidence: {trade_result.get('confidence', 0):.0%}
Time: {datetime.now().isoformat()}
            """
            
            self._send_telegram_alert(log_message.strip(), chat_type='metrics')
        
        except Exception as e:
            logger.error(f"❌ Log trade error: {e}")
    
    def log_error(self, error_message: str):
        '''Log errors to Telegram'''
        try:
            error_log = f"""
❌ ERROR DETECTED
Message: {error_message}
Time: {datetime.now().isoformat()}
            """
            
            self._send_telegram_alert(error_log.strip(), chat_type='errors')
        
        except Exception as e:
            logger.error(f"❌ Log error error: {e}")

# Global monitor instance
system_monitor = SystemMonitor()
"""
