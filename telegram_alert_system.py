# 🔔 TELEGRAM ALERT SYSTEM
# Phase 3.1: Real-time Signal Notifications
# Date: 1 Kasım 2025

"""
Telegram Bot ile AI sinyal bildirimleri gönder.

Özellikler:
- LONG/SHORT/NEUTRAL sinyalleri
- Entry/SL/TP fiyatları
- Confidence + Score
- Instant notification
- Formatted message

Kullanım:
from telegram_alert_system import TelegramAlertSystem
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

alert = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
alert.send_signal_alert(decision)
"""

import requests
import json
from datetime import datetime

class TelegramAlertSystem:
    def __init__(self, bot_token, chat_id):
        """
        Telegram Alert System initialization
        
        Args:
            bot_token (str): Telegram bot token (from BotFather)
            chat_id (str): Telegram chat ID (from @userinfobot)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text, parse_mode='HTML'):
        """
        Send message to Telegram
        
        Args:
            text (str): Message content
            parse_mode (str): 'HTML' or 'Markdown'
        
        Returns:
            bool: Success?
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Telegram send error: {response.status_code}")
                print(response.text)
                return False
        
        except Exception as e:
            print(f"❌ Telegram exception: {e}")
            return False
    
    def send_signal_alert(self, decision):
        """
        Send AI trading signal to Telegram
        
        Args:
            decision (dict): Decision dictionary from AI brain
        
        Returns:
            bool: Success?
        """
        # Choose emoji
        signal_emoji = {
            'LONG': '📈',
            'SHORT': '📉',
            'NEUTRAL': '⏸️',
            'WAIT': '⏳'
        }
        
        signal = decision.get('decision', 'NEUTRAL')
        emoji = signal_emoji.get(signal, '🎯')
        
        # Confidence and score
        confidence = decision.get('confidence', 0) * 100
        score = decision.get('final_score', 0)
        
        # Color (HTML)
        if signal == 'LONG':
            signal_color = '🟢'
        elif signal == 'SHORT':
            signal_color = '🔴'
        else:
            signal_color = '⚪'
        
        # Create message
        message = f"""
🔱 <b>DEMIR AI TRADING SIGNAL</b> 🔱

{emoji} <b>{signal_color} {signal}</b> {emoji}

📊 <b>Coin:</b> {decision.get('symbol', 'N/A')}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💯 <b>Score:</b> {score:.1f}/100
🎯 <b>Confidence:</b> {confidence:.0f}%
📐 <b>R/R:</b> 1:{decision.get('risk_reward', 0):.2f}

━━━━━━━━━━━━━━━━━━━━

💼 <b>POZISYON PLANI</b>

📍 <b>Entry:</b> ${decision.get('entry_price', 0):,.2f}
🛡️ <b>Stop Loss:</b> ${decision.get('stop_loss', 0):,.2f}
💰 <b>Position:</b> ${decision.get('position_size_usd', 0):,.2f}
⚠️ <b>Risk:</b> ${decision.get('risk_amount_usd', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━

🎯 <b>TAKE PROFIT</b>
"""
        
        # Calculate TP
        if decision.get('entry_price') and decision.get('stop_loss'):
            risk_amount = abs(decision['entry_price'] - decision['stop_loss'])
            
            if signal == 'LONG':
                tp1 = decision['entry_price'] + (risk_amount * 1.0)
                tp2 = decision['entry_price'] + (risk_amount * 1.618)
                tp3 = decision['entry_price'] + (risk_amount * 2.618)
            else:
                tp1 = decision['entry_price'] - (risk_amount * 1.0)
                tp2 = decision['entry_price'] - (risk_amount * 1.618)
                tp3 = decision['entry_price'] - (risk_amount * 2.618)
            
            tp1_pct = ((tp1 - decision['entry_price']) / decision['entry_price'] * 100)
            tp2_pct = ((tp2 - decision['entry_price']) / decision['entry_price'] * 100)
            tp3_pct = ((tp3 - decision['entry_price']) / decision['entry_price'] * 100)
            
            message += f"""
TP1: ${tp1:,.2f} ({tp1_pct:+.2f}%) [50%]
TP2: ${tp2:,.2f} ({tp2_pct:+.2f}%) [30%]
TP3: ${tp3:,.2f} ({tp3_pct:+.2f}%) [20%]
"""
        
        # Reason
        reason = decision.get('reason', 'N/A')
        if len(reason) > 200:
            reason = reason[:200] + "..."
        
        message += f"""
━━━━━━━━━━━━━━━━━━━━

💡 <b>GEREKÇE:</b>
{reason}

━━━━━━━━━━━━━━━━━━━━

⚡ <i>DEMIR AI Trading Bot v7.0 Phase 3</i>
"""
        
        # Send
        return self.send_message(message)
    
    def send_trade_update(self, trade_id, status, pnl_usd=0, pnl_pct=0):
        """
        Send trade result to Telegram
        
        Args:
            trade_id (int): Trade ID
            status (str): 'WIN', 'LOSS', 'BREAKEVEN'
            pnl_usd (float): PnL in USD
            pnl_pct (float): PnL in percentage
        
        Returns:
            bool: Success?
        """
        # Choose emoji
        if status == 'WIN':
            emoji = '✅'
            color = '🟢'
        elif status == 'LOSS':
            emoji = '❌'
            color = '🔴'
        else:
            emoji = '➖'
            color = '⚪'
        
        message = f"""
🔱 <b>TRADE UPDATE</b> 🔱

{emoji} <b>{color} {status}</b> {emoji}

📋 <b>Trade ID:</b> #{trade_id}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 <b>PnL:</b> ${pnl_usd:+,.2f} ({pnl_pct:+.2f}%)

━━━━━━━━━━━━━━━━━━━━

⚡ <i>DEMIR AI Trading Bot v7.0</i>
"""
        
        return self.send_message(message)
    
    def send_performance_summary(self, performance_data):
        """
        Send performance summary to Telegram
        
        Args:
            performance_data (dict): Performance metrics
        
        Returns:
            bool: Success?
        """
        message = f"""
🔱 <b>PERFORMANCE SUMMARY</b> 🔱

📊 <b>GENEL İSTATİSTİKLER</b>

📈 <b>Total Trades:</b> {performance_data.get('total_trades', 0)}
✅ <b>Winning:</b> {performance_data.get('winning_trades', 0)}
❌ <b>Losing:</b> {performance_data.get('losing_trades', 0)}

🎯 <b>Win Rate:</b> {performance_data.get('win_rate', 0):.1f}%
💰 <b>Total PnL:</b> ${performance_data.get('total_pnl_usd', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━

📈 <b>ADVANCED METRICS</b>

📊 <b>Sharpe Ratio:</b> {performance_data.get('sharpe_ratio', 0):.2f}
💎 <b>Profit Factor:</b> {performance_data.get('profit_factor', 0):.2f}
📉 <b>Max Drawdown:</b> {performance_data.get('max_drawdown', 0):.2f}%

━━━━━━━━━━━━━━━━━━━━

⚡ <i>DEMIR AI Trading Bot v7.0</i>
"""
        
        return self.send_message(message)
    
    def test_connection(self):
        """
        Test Telegram connection
        
        Returns:
            bool: Success?
        """
        test_message = """
🔱 <b>DEMIR AI TRADING BOT</b> 🔱

✅ <b>Connection Test Successful!</b>

Telegram Alert System aktif.
Sinyaller bu kanala gönderilecek.

⚡ <i>DEMIR AI Trading Bot v7.0 Phase 3</i>
"""
        return self.send_message(test_message)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Import from config
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    except:
        print("⚠️ config.py'de TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID environment variables gerekli!")
        exit()
    
    # Create alert system
    alert_system = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # Test
    print("📱 Telegram bağlantısı test ediliyor...")
    success = alert_system.test_connection()
    
    if success:
        print("✅ Telegram Alert System hazır!")
    else:
        print("❌ Telegram bağlantısı başarısız! Bot token ve chat ID kontrol et.")
