```python
import os
import requests
from datetime import datetime

class TelegramAlertLayer:
    """Send trading alerts via Telegram"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_signal(self, signal_type, symbol, price, confidence, details=""):
        """Send trading signal alert"""
        try:
            emoji = "🟢" if signal_type == "BULLISH" else "🔴" if signal_type == "BEARISH" else "⚪"
            
            message = f"{emoji} **{signal_type}** Signal\n"
            message += f"Symbol: {symbol}\n"
            message += f"Price: ${price:.2f}\n"
            message += f"Confidence: {confidence*100:.1f}%\n"
            if details:
                message += f"Details: {details}\n"
            message += f"Time: {datetime.now().strftime('%H:%M:%S')}"
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Telegram error: {e}")
            return {'ok': False, 'error': str(e)}
    
    def send_alert(self, title, message):
        """Send general alert"""
        try:
            full_msg = f"⚠️ {title}\n{message}\nTime: {datetime.now().strftime('%H:%M:%S')}"
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': full_msg,
                'parse_mode': 'Markdown'
            }
            return requests.post(url, json=data).json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def analyze(self, signal='NEUTRAL', symbol='BTCUSDT', price=0, confidence=0):
        """Send alert and return status"""
        return self.send_signal(signal, symbol, price, confidence)

telegram_layer = TelegramAlertLayer()
```
