"""
🔔 PHASE 9.2 - ALERT SYSTEM (HYBRID MODE)
==========================================

Path: phase_9/alert_system.py
Date: 7 Kasım 2025, 15:49 CET

Multi-channel alert system: Email, SMS, Push, Dashboard
Notifies user when important signals occur
"""

import smtplib
import json
import logging
from datetime import datetime
from typing import Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertSystem:
    """Multi-channel alert system"""
    
    def __init__(self, config_path='phase_9/config.json'):
        """
        Initialize alert system
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.alerts_history = []
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from JSON"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found: {path}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'your_email@gmail.com',
                'sender_password': 'your_app_password',
                'recipient_email': 'your_email@gmail.com'
            },
            'sms': {
                'enabled': False,
                'provider': 'twilio',  # or 'vonage'
                'account_sid': 'YOUR_SID',
                'auth_token': 'YOUR_TOKEN',
                'from_number': '+1234567890',
                'to_number': '+0987654321'
            },
            'push': {
                'enabled': False,
                'service': 'firebase',
                'project_id': 'your_project'
            },
            'dashboard': {
                'enabled': True,
                'update_interval': 30  # seconds
            }
        }
    
    def send_email(self, message: str, subject: str = "🚨 Trading Alert"):
        """
        Send email alert
        
        Args:
            message: Alert message
            subject: Email subject
        """
        if not self.config['email']['enabled']:
            logger.info("📧 Email alerts disabled")
            return
        
        try:
            email_config = self.config['email']
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
            logger.info("✅ Email sent")
            self._record_alert('email', message)
            
        except Exception as e:
            logger.error(f"❌ Email error: {e}")
    
    def send_sms(self, message: str):
        """
        Send SMS alert
        
        Args:
            message: SMS message
        """
        if not self.config['sms']['enabled']:
            logger.info("📱 SMS alerts disabled")
            return
        
        try:
            sms_config = self.config['sms']
            provider = sms_config['provider']
            
            if provider == 'twilio':
                self._send_twilio_sms(message, sms_config)
            elif provider == 'vonage':
                self._send_vonage_sms(message, sms_config)
            
            logger.info("✅ SMS sent")
            self._record_alert('sms', message)
            
        except Exception as e:
            logger.error(f"❌ SMS error: {e}")
    
    def _send_twilio_sms(self, message: str, config: Dict):
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(config['account_sid'], config['auth_token'])
            client.messages.create(
                body=message,
                from_=config['from_number'],
                to=config['to_number']
            )
        except ImportError:
            logger.error("Twilio SDK not installed")
    
    def _send_vonage_sms(self, message: str, config: Dict):
        """Send SMS via Vonage (Nexmo)"""
        try:
            import vonage
            
            client = vonage.Client(api_key=config['account_sid'], api_secret=config['auth_token'])
            client.sms.send_message({
                "from": config['from_number'],
                "to": config['to_number'],
                "text": message
            })
        except ImportError:
            logger.error("Vonage SDK not installed")
    
    def send_push_notification(self, message: str, title: str = "Alert"):
        """
        Send push notification
        
        Args:
            message: Notification message
            title: Notification title
        """
        if not self.config['push']['enabled']:
            logger.info("🔔 Push alerts disabled")
            return
        
        try:
            push_config = self.config['push']
            
            if push_config['service'] == 'firebase':
                self._send_firebase_push(message, title, push_config)
            
            logger.info("✅ Push notification sent")
            self._record_alert('push', message)
            
        except Exception as e:
            logger.error(f"❌ Push error: {e}")
    
    def _send_firebase_push(self, message: str, title: str, config: Dict):
        """Send push via Firebase"""
        try:
            import firebase_admin
            from firebase_admin import messaging
            
            msg = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=message),
                data={'type': 'trading_alert'},
                tokens=self._get_firebase_tokens()
            )
            
            response = messaging.send_multicast(msg)
            logger.info(f"Firebase: {response.success} successful, {response.failure_count} failed")
            
        except ImportError:
            logger.error("Firebase SDK not installed")
    
    def _get_firebase_tokens(self) -> List[str]:
        """Get registered device tokens"""
        try:
            with open('phase_9/data/device_tokens.json', 'r') as f:
                data = json.load(f)
                return data.get('tokens', [])
        except FileNotFoundError:
            return []
    
    def update_dashboard(self, data: Dict):
        """
        Update live dashboard
        
        Args:
            data: Analysis data to display
        """
        if not self.config['dashboard']['enabled']:
            return
        
        try:
            dashboard_file = 'phase_9/data/dashboard_state.json'
            
            state = {
                'timestamp': datetime.now().isoformat(),
                'score': data.get('score'),
                'signal': data.get('signal'),
                'confidence': data.get('confidence'),
                'price': data.get('price'),
                'layers': data.get('layers')
            }
            
            with open(dashboard_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug("📊 Dashboard updated")
            
        except Exception as e:
            logger.error(f"Dashboard update error: {e}")
    
    def _record_alert(self, alert_type: str, message: str):
        """Record alert in history"""
        alert = {
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'message': message
        }
        
        self.alerts_history.append(alert)
        
        # Save to file
        try:
            with open('phase_9/data/alerts_history.json', 'a') as f:
                f.write(json.dumps(alert) + '\n')
        except Exception as e:
            logger.error(f"Alert history error: {e}")
    
    def get_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from last N hours"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alerts_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff
        ]


# ============================================================================
# HYBRID ALERT EXAMPLE
# ============================================================================

if __name__ == "__main__":
    alerts = AlertSystem()
    
    # Example alerts
    alerts.send_email("Score increased to 75 - LONG possible!")
    alerts.send_sms("BTCUSDT Score 75 - Check dashboard")
    alerts.update_dashboard({
        'score': 75,
        'signal': 'LONG',
        'confidence': 0.85
    })
    
    print("✅ Alert system demo complete")
