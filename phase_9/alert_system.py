"""
ALERT SYSTEM v2 - TELEGRAM + EMAIL + DASHBOARD
===============================================
Date: 7 Kasım 2025, 20:10 CET
Version: 2.0 - Real Telegram Integration + Proper Error Handling
"""

import os
import requests
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSystem:
    """Multi-channel alert system with Telegram, Email, Dashboard"""
    
    def __init__(self):
        """Initialize alert system with environment variables"""
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.alerts_history = []
        
        logger.info(f"✅ Alert System v2 initialized")
        logger.info(f" Telegram configured: {bool(self.telegram_token)}")
    
    # ============================================
    # TELEGRAM ALERTS
    # ============================================
    
    def send_telegram_alert(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send alert via Telegram
        
        Args:
            message: Alert message (supports HTML)
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            bool: Success status
        """
        
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("⚠️ Telegram not configured (missing TOKEN or CHAT_ID)")
            return False
        
        try:
            logger.info(f" 📱 Sending Telegram alert...")
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('ok'):
                logger.info(f" ✅ Telegram message sent (ID: {data['result']['message_id']})")
                self._record_alert('telegram', message)
                return True
            else:
                logger.error(f" ❌ Telegram error: {data.get('description', 'Unknown')}")
                return False
        
        except requests.exceptions.Timeout:
            logger.error(f" ❌ Telegram timeout")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f" ❌ Telegram connection error")
            return False
        except Exception as e:
            logger.error(f" ❌ Telegram error: {str(e)[:60]}")
            return False
    
    # ============================================
    # TRADING SIGNAL ALERTS
    # ============================================
    
    def send_trading_signal(self, signal: Dict) -> bool:
        """
        Send formatted trading signal alert
        
        Args:
            signal: {
                'symbol': 'BTCUSDT',
                'score': 75,
                'action': 'LONG' / 'SHORT' / 'NEUTRAL',
                'confidence': 0.85,
                'entry': 45000,
                'tp': 48000,
                'sl': 42000,
                'price': 45000
            }
        """
        
        try:
            symbol = signal.get('symbol', 'UNKNOWN')
            score = signal.get('score', 50)
            action = signal.get('action', 'NEUTRAL')
            confidence = signal.get('confidence', 0)
            entry = signal.get('entry', 0)
            tp = signal.get('tp', 0)
            sl = signal.get('sl', 0)
            price = signal.get('price', 0)
            
            # Emoji mapping
            emoji_map = {
                'LONG': '🟢 LONG',
                'SHORT': '🔴 SHORT',
                'NEUTRAL': '🟡 NEUTRAL'
            }
            emoji = emoji_map.get(action, action)
            
            # Format message
            message = f"""
<b>🤖 TRADING SIGNAL</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {emoji}
<b>Score:</b> {score}/100
<b>Confidence:</b> {confidence:.0%}

<b>Current Price:</b> ${price:,.2f}
<b>Entry:</b> ${entry:,.2f}
<b>Take Profit:</b> ${tp:,.2f}
<b>Stop Loss:</b> ${sl:,.2f}

<i>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
            
            logger.info(f"\n{message}")
            return self.send_telegram_alert(message, parse_mode="HTML")
        
        except Exception as e:
            logger.error(f"❌ Error formatting signal: {str(e)[:60]}")
            return False
    
    # ============================================
    # LAYER ANALYSIS ALERTS
    # ============================================
    
    def send_layer_analysis(self, analysis: Dict) -> bool:
        """
        Send layer-by-layer analysis alert
        
        Args:
            analysis: {'vix': 65, 'rates': 45, 'macro': 70, ...}
        """
        
        try:
            message = "<b>📊 LAYER ANALYSIS</b>\n\n"
            
            for layer_name, score in sorted(analysis.items()):
                if score is None:
                    score_text = "❌ ERROR"
                else:
                    score = float(score)
                    if score >= 65:
                        emoji = "🟢"
                    elif score <= 35:
                        emoji = "🔴"
                    else:
                        emoji = "🟡"
                    score_text = f"{emoji} {score:.0f}"
                
                message += f"{layer_name.upper():20} {score_text}\n"
            
            message += f"\n<i>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
            
            return self.send_telegram_alert(message, parse_mode="HTML")
        
        except Exception as e:
            logger.error(f"❌ Error formatting analysis: {str(e)[:60]}")
            return False
    
    # ============================================
    # ALERT STATUS
    # ============================================
    
    def send_status(self, status_data: Dict) -> bool:
        """
        Send system status alert
        
        Args:
            status_data: {
                'system': 'RUNNING',
                'layers_active': 15,
                'last_analysis': '2025-11-07 20:15:00',
                'errors': 0
            }
        """
        
        try:
            status = status_data.get('system', 'UNKNOWN')
            emoji = "✅" if status == "RUNNING" else "⚠️"
            
            message = f"""
<b>{emoji} SYSTEM STATUS</b>

<b>Status:</b> {status}
<b>Active Layers:</b> {status_data.get('layers_active', 0)}/15
<b>Last Analysis:</b> {status_data.get('last_analysis', 'N/A')}
<b>Errors:</b> {status_data.get('errors', 0)}

<i>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
            
            return self.send_telegram_alert(message, parse_mode="HTML")
        
        except Exception as e:
            logger.error(f"❌ Error formatting status: {str(e)[:60]}")
            return False
    
    # ============================================
    # ALERT HISTORY
    # ============================================
    
    def _record_alert(self, alert_type: str, message: str):
        """Record alert in history"""
        alert = {
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'message': message[:100]  # Truncate for storage
        }
        
        self.alerts_history.append(alert)
        
        # Keep last 100 alerts in memory
        if len(self.alerts_history) > 100:
            self.alerts_history = self.alerts_history[-100:]
        
        # Optionally save to file
        try:
            with open('phase_9/data/alerts_history.json', 'a') as f:
                f.write(json.dumps(alert) + '\n')
        except:
            pass  # Ignore file write errors
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get alerts from last N hours"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        result = []
        
        for alert in self.alerts_history:
            try:
                alert_time = datetime.fromisoformat(alert['timestamp'])
                if alert_time > cutoff:
                    result.append(alert)
            except:
                pass
        
        return result
    
    # ============================================
    # DASHBOARD UPDATE
    # ============================================
    
    def update_dashboard(self, data: Dict) -> bool:
        """Update live dashboard state"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'score': data.get('score'),
                'signal': data.get('signal'),
                'confidence': data.get('confidence'),
                'price': data.get('price'),
                'layers': data.get('layers'),
                'trade_levels': data.get('trade_levels')
            }
            
            # Save to JSON
            os.makedirs('phase_9/data', exist_ok=True)
            with open('phase_9/data/dashboard_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug("📊 Dashboard state updated")
            return True
        
        except Exception as e:
            logger.error(f"❌ Dashboard update error: {str(e)[:60]}")
            return False

# ============================================
# MODULE-LEVEL FUNCTIONS
# ============================================

_alert_system = None

def _get_alert_system():
    """Get or create alert system instance"""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system

def send_trading_signal(signal: Dict) -> bool:
    """Send trading signal alert"""
    return _get_alert_system().send_trading_signal(signal)

def send_layer_analysis(analysis: Dict) -> bool:
    """Send layer analysis alert"""
    return _get_alert_system().send_layer_analysis(analysis)

def send_status(status_data: Dict) -> bool:
    """Send status alert"""
    return _get_alert_system().send_status(status_data)

def send_telegram_alert(message: str) -> bool:
    """Send raw Telegram alert"""
    return _get_alert_system().send_telegram_alert(message)

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔔 ALERT SYSTEM v2 - TEST")
    print("="*70)
    
    alerts = AlertSystem()
    
    # Test 1: Trading Signal
    print("\n1️⃣ Testing Trading Signal...")
    result = alerts.send_trading_signal({
        'symbol': 'BTCUSDT',
        'score': 75,
        'action': 'LONG',
        'confidence': 0.85,
        'entry': 45000,
        'tp': 48000,
        'sl': 42000,
        'price': 45000
    })
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 2: Layer Analysis
    print("\n2️⃣ Testing Layer Analysis...")
    result = alerts.send_layer_analysis({
        'vix': 65,
        'rates': 45,
        'macro': 70,
        'cross_asset': 55,
        'momentum': 75
    })
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    # Test 3: Status
    print("\n3️⃣ Testing Status Alert...")
    result = alerts.send_status({
        'system': 'RUNNING',
        'layers_active': 15,
        'last_analysis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'errors': 0
    })
    print(f"   Result: {'✅ Sent' if result else '❌ Failed'}")
    
    print("\n" + "="*70)
    print(f"Alert History: {len(alerts.alerts_history)} alerts recorded")
    print("="*70)
