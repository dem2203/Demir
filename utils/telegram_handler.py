import requests
import streamlit as st
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_MESSAGE_FORMAT


class TelegramHandler:
    """Handles Telegram bot messaging and alerts"""
    
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message):
        """Send a message to Telegram chat"""
        try:
            if not self.token or not self.chat_id:
                st.warning("Telegram configuration missing")
                return False
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()['ok']
            
        except requests.exceptions.RequestException as e:
            st.error(f"Telegram API error: {str(e)}")
            return False
    
    def send_alert(self, signal, confidence, entry_price, tp1, tp2, tp3, sl, coins):
        """Send trading alert to Telegram"""
        try:
            message = f"""
<b>🤖 DEMIR AI Market Update</b>
<b>Time:</b> {datetime.now().strftime('%H:%M UTC')}

<b>📊 Trading Signal</b>
<b>Signal:</b> <b>{signal}</b> ({confidence}% confidence)

<b>💰 Targets</b>
<b>Entry:</b> ${entry_price:,.2f}
<b>TP1:</b> ${tp1:,.2f}
<b>TP2:</b> ${tp2:,.2f}
<b>TP3:</b> ${tp3:,.2f}
<b>SL:</b> ${sl:,.2f}

<b>📈 Monitored Coins:</b> {', '.join(coins)}

<b>🔧 System Status:</b> ✅ All operational
            """
            
            return self.send_message(message)
            
        except Exception as e:
            st.error(f"Error sending alert: {str(e)}")
            return False
    
    def send_status_report(self, phase_count, factor_count, system_health):
        """Send system status report"""
        try:
            message = f"""
<b>📊 DEMIR AI System Status Report</b>
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

<b>✅ Phases Active:</b> {phase_count}/26
<b>📈 Factors Analyzed:</b> {factor_count}
<b>💚 System Health:</b> {system_health}%

<b>Last Update:</b> Just now
            """
            
            return self.send_message(message)
            
        except Exception as e:
            st.error(f"Error sending report: {str(e)}")
            return False
    
    def send_error_alert(self, error_title, error_message):
        """Send error notification"""
        try:
            message = f"""
<b>⚠️ DEMIR AI Error Alert</b>
<b>Time:</b> {datetime.now().strftime('%H:%M:%S UTC')}

<b>Error:</b> {error_title}
<b>Details:</b> {error_message}

<b>Action:</b> Please check the dashboard immediately.
            """
            
            return self.send_message(message)
            
        except Exception as e:
            st.error(f"Error sending error alert: {str(e)}")
            return False
    
    def test_connection(self):
        """Test Telegram connection"""
        try:
            if not self.token or not self.chat_id:
                st.error("Telegram configuration missing!")
                return False
            
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                st.success("✅ Telegram connection successful!")
                return True
            else:
                st.error("❌ Telegram connection failed!")
                return False
                
        except requests.exceptions.RequestException as e:
            st.error(f"Telegram test error: {str(e)}")
            return False


# Global Telegram Handler instance
telegram_handler = TelegramHandler()
