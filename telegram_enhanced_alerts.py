"""
📱 TELEGRAM ENHANCED ALERT SYSTEM
Version: 3.0 - Proactive Alerts
Date: 10 Kasım 2025, 23:30 CET

FEATURES:
- Hourly market updates
- Real-time signal alerts
- Price movement notifications
- Opportunity detection
"""

import os
import requests
from datetime import datetime
import time
import threading

class TelegramEnhancedAlerts:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Price tracking for alerts
        self.last_prices = {}
        self.alert_threshold = 0.03  # 3% price change
        
    def send_message(self, text, parse_mode='Markdown'):
        """Send Telegram message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram send error: {e}")
            return False
    
    def get_real_prices(self):
        """Binance REST API"""
        try:
            url = "https://fapi.binance.com/fapi/v1/ticker/price"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                prices = {}
                for item in data:
                    if item['symbol'] in ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']:
                        prices[item['symbol']] = float(item['price'])
                return prices
        except:
            pass
        return {}
    
    def get_ai_signal(self):
        """Get signal from AI Brain"""
        try:
            from ai_brain import AIBrain
            ai_brain = AIBrain()
            
            prices = self.get_real_prices()
            market_data = {
                'btc_price': prices.get('BTCUSDT', 0),
                'eth_price': prices.get('ETHUSDT', 0),
                'btc_prev_price': prices.get('BTCUSDT', 0) * 0.99,
                'timestamp': datetime.now(),
                'volume_24h': 0,
                'volume_7d_avg': 0,
                'funding_rate': 0
            }
            
            result = ai_brain.analyze(market_data)
            return {
                'signal': result.signal.value,
                'confidence': result.confidence,
                'score': result.overall_score
            }
        except:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'score': 50}
    
    def check_price_alerts(self, current_prices):
        """Check for significant price movements"""
        alerts = []
        
        for symbol, current_price in current_prices.items():
            if symbol in self.last_prices:
                last_price = self.last_prices[symbol]
                change_pct = ((current_price - last_price) / last_price) * 100
                
                if abs(change_pct) >= self.alert_threshold * 100:
                    direction = "📈" if change_pct > 0 else "📉"
                    alerts.append({
                        'symbol': symbol,
                        'change': change_pct,
                        'direction': direction,
                        'price': current_price
                    })
        
        # Update last prices
        self.last_prices = current_prices.copy()
        
        return alerts
    
    def send_hourly_update(self):
        """Send hourly market update"""
        prices = self.get_real_prices()
        analysis = self.get_ai_signal()
        
        # Emoji for signal
        if analysis['signal'] == 'LONG':
            signal_emoji = "🟢"
        elif analysis['signal'] == 'SHORT':
            signal_emoji = "🔴"
        else:
            signal_emoji = "🟡"
        
        message = f"""
🔱 *DEMIR AI - Hourly Update*
⏰ {datetime.now().strftime('%H:%M CET')}

📊 *Market Prices:*
₿ BTC: ${prices.get('BTCUSDT', 0):,.2f}
Ξ ETH: ${prices.get('ETHUSDT', 0):,.2f}
Ł LTC: ${prices.get('LTCUSDT', 0):,.2f}

{signal_emoji} *AI Signal:* {analysis['signal']}
📈 *Confidence:* {analysis['confidence']:.1f}%
🧠 *AI Score:* {analysis['score']}/100

🤖 Bot Status: 🟢 Active 24/7
        """
        
        self.send_message(message.strip())
    
    def send_signal_alert(self, analysis, prices):
        """Send alert for strong signals (confidence > 70%)"""
        if analysis['confidence'] > 70:
            signal_emoji = "🟢" if analysis['signal'] == 'LONG' else "🔴"
            
            message = f"""
⚡ *STRONG SIGNAL DETECTED!*

{signal_emoji} *Signal:* {analysis['signal']}
🎯 *Confidence:* {analysis['confidence']:.1f}%
💎 *AI Score:* {analysis['score']}/100

💰 *Current Prices:*
₿ BTC: ${prices.get('BTCUSDT', 0):,.2f}
Ξ ETH: ${prices.get('ETHUSDT', 0):,.2f}

⏳ *Action:* Consider {analysis['signal']} entry
🔗 Dashboard: https://demir2203.up.railway.app
            """
            
            self.send_message(message.strip())
    
    def send_price_movement_alert(self, alerts):
        """Send alert for significant price movements"""
        if not alerts:
            return
        
        message = "⚡ *PRICE MOVEMENT ALERT!*\n\n"
        
        for alert in alerts:
            message += f"{alert['direction']} *{alert['symbol'].replace('USDT', '')}*: "
            message += f"{alert['change']:+.2f}% → ${alert['price']:,.2f}\n"
        
        message += f"\n⏰ {datetime.now().strftime('%H:%M CET')}"
        
        self.send_message(message.strip())
    
    def start_monitoring(self):
        """Start 24/7 monitoring loop"""
        print("🤖 Telegram monitoring started (24/7)")
        
        while True:
            try:
                # Get current data
                prices = self.get_real_prices()
                analysis = self.get_ai_signal()
                
                # Check for price alerts
                price_alerts = self.check_price_alerts(prices)
                if price_alerts:
                    self.send_price_movement_alert(price_alerts)
                
                # Check for strong signals
                if analysis['confidence'] > 70:
                    self.send_signal_alert(analysis, prices)
                
                # Hourly update (check if new hour)
                current_minute = datetime.now().minute
                if current_minute == 0:  # Top of the hour
                    self.send_hourly_update()
                    time.sleep(60)  # Wait 1 minute to avoid duplicate
                
                # Wait before next check (every 5 minutes)
                time.sleep(300)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)

# ============================================================================
# AUTO-START IN BACKGROUND
# ============================================================================

def start_telegram_daemon():
    """Start Telegram monitoring in background thread"""
    alert_system = TelegramEnhancedAlerts()
    
    # Run in background thread
    thread = threading.Thread(target=alert_system.start_monitoring, daemon=True)
    thread.start()
    
    print("✅ Telegram alert system running in background")

# Start automatically when imported
if __name__ != "__main__":
    start_telegram_daemon()
