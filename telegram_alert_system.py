"""
🔱 TELEGRAM ALERT SYSTEM - ENHANCED & MERGED
============================================
Date: 2 Kasım 2025
Version: 3.0 - ULTIMATE EDITION

Phase 3.1: Real-time Signal Notifications

WHAT IT DOES:
-------------
- Send AI trading signals to Telegram
- Real-time price alerts  
- Trade result notifications
- Performance summaries
- Multi-format support (HTML/Markdown)
- Error handling & fallbacks

FEATURES:
---------
✅ Signal alerts (LONG/SHORT/NEUTRAL)
✅ Entry/SL/TP with percentages
✅ Multi-level TP (TP1/TP2/TP3 with Fibonacci)
✅ Confidence + Score display
✅ Trade updates (WIN/LOSS)
✅ Daily performance summary
✅ Price breakout alerts
✅ Analysis completion notifications
✅ Rich emoji indicators
✅ HTML & Markdown support
✅ Error notifications
✅ Connection testing

USAGE:
------
from telegram_alert_system import TelegramAlertSystem
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

alert = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
alert.send_signal_alert(decision)
alert.send_trade_update(trade_id, 'WIN', pnl_usd=150, pnl_pct=3.2)
alert.send_performance_summary(performance_data)
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class TelegramAlertSystem:
    """
    Ultimate Telegram Alert System for trading signals and notifications
    Combines all features from both versions
    """
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize Telegram Alert System
        
        Args:
            bot_token: Telegram bot token (from @BotFather)
            chat_id: Telegram chat ID (from @userinfobot)
        
        Note:
            If not provided, will try to read from environment variables:
            - TELEGRAM_BOT_TOKEN
            - TELEGRAM_CHAT_ID
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            print("⚠️ TELEGRAM_BOT_TOKEN not set. Alerts disabled.")
        if not self.chat_id:
            print("⚠️ TELEGRAM_CHAT_ID not set. Alerts disabled.")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = bool(self.bot_token and self.chat_id)
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Send text message to Telegram
        
        Args:
            text: Message content
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            bool: Success status
        """
        if not self.enabled:
            print(f"📱 [TELEGRAM DISABLED] {text[:100]}")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram message sent!")
                return True
            else:
                print(f"❌ Telegram send error: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Telegram exception: {e}")
            return False
    
    def send_signal_alert(self, decision: Dict) -> bool:
        """
        Send AI trading signal to Telegram (ORIGINAL GITHUB VERSION)
        
        Args:
            decision: Decision dictionary from AI brain containing:
                - symbol: Trading pair
                - decision: LONG/SHORT/NEUTRAL/WAIT
                - final_score: AI score 0-100
                - confidence: Confidence 0-1
                - entry_price: Entry price
                - stop_loss: Stop loss price
                - position_size_usd: Position size in USD
                - risk_amount_usd: Risk amount in USD
                - risk_reward: Risk/Reward ratio
                - reason: Analysis reason
        
        Returns:
            bool: Success status
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
🔱 DEMIR AI TRADING SIGNAL 🔱

{emoji} {signal_color} {signal} {emoji}

📊 Coin: {decision.get('symbol', 'N/A')}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💯 Score: {score:.1f}/100
🎯 Confidence: {confidence:.0f}%
📐 R/R: 1:{decision.get('risk_reward', 0):.2f}

━━━━━━━━━━━━━━━━━━━━
💼 POZISYON PLANI

📍 Entry: ${decision.get('entry_price', 0):,.2f}
🛡️ Stop Loss: ${decision.get('stop_loss', 0):,.2f}

💰 Position: ${decision.get('position_size_usd', 0):,.2f}
⚠️ Risk: ${decision.get('risk_amount_usd', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━
🎯 TAKE PROFIT
"""
        
        # Calculate TP (Fibonacci levels)
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
💡 GEREKÇE:
{reason}

━━━━━━━━━━━━━━━━━━━━
⚡ DEMIR AI Trading Bot v7.0 Phase 3
"""
        
        # Send
        return self.send_message(message)
    
    def send_signal(self, signal_data: Dict) -> bool:
        """
        Send formatted trading signal (ENHANCED VERSION)
        
        Args:
            signal_data: {
                'symbol': 'BTCUSDT',
                'signal': 'LONG',
                'score': 75.5,
                'confidence': 82,
                'entry': 50000,
                'stop_loss': 49000,
                'take_profit': 52000,
                'reason': 'Strong bullish momentum'
            }
        
        Returns:
            bool: Success status
        """
        
        symbol = signal_data.get('symbol', 'UNKNOWN')
        signal = signal_data.get('signal', 'NEUTRAL')
        score = signal_data.get('score', 50)
        confidence = signal_data.get('confidence', 0)
        entry = signal_data.get('entry', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        take_profit = signal_data.get('take_profit', 0)
        reason = signal_data.get('reason', 'No reason provided')
        
        # Emoji based on signal
        if signal == 'LONG':
            emoji = '🟢'
            direction = '📈 LONG'
        elif signal == 'SHORT':
            emoji = '🔴'
            direction = '📉 SHORT'
        else:
            emoji = '⚪'
            direction = '⏸️ NEUTRAL'
        
        # Format message
        message = f"""
{emoji} *NEW TRADING SIGNAL* {emoji}

*Symbol:* `{symbol}`
*Direction:* {direction}
*Score:* {score:.1f}/100
*Confidence:* {confidence}%

💰 *Trade Setup:*
Entry: `${entry:,.2f}`
Stop Loss: `${stop_loss:,.2f}` (-{abs((entry-stop_loss)/entry*100):.1f}%)
Take Profit: `${take_profit:,.2f}` (+{abs((take_profit-entry)/entry*100):.1f}%)

💡 *Reason:*
{reason}

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔱 *Demir AI Trading Bot*
"""
        
        return self.send_message(message.strip(), parse_mode='Markdown')
    
    def send_trade_update(self, trade_id: int, status: str, pnl_usd: float = 0, pnl_pct: float = 0) -> bool:
        """
        Send trade result to Telegram
        
        Args:
            trade_id: Trade ID
            status: 'WIN', 'LOSS', 'BREAKEVEN'
            pnl_usd: PnL in USD
            pnl_pct: PnL in percentage
        
        Returns:
            bool: Success status
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
🔱 TRADE UPDATE 🔱

{emoji} {color} {status} {emoji}

📋 Trade ID: #{trade_id}
⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 PnL: ${pnl_usd:+,.2f} ({pnl_pct:+.2f}%)

━━━━━━━━━━━━━━━━━━━━
⚡ DEMIR AI Trading Bot v7.0
"""
        
        return self.send_message(message)
    
    def send_trade_result(self, trade_data: Dict) -> bool:
        """
        Send trade result (alternative format)
        
        Args:
            trade_data: {
                'symbol': 'BTCUSDT',
                'signal': 'LONG',
                'entry': 50000,
                'exit': 52000,
                'pnl': 4.0,
                'result': 'WIN'
            }
        
        Returns:
            bool: Success status
        """
        
        symbol = trade_data.get('symbol', 'UNKNOWN')
        signal = trade_data.get('signal', 'UNKNOWN')
        entry = trade_data.get('entry', 0)
        exit_price = trade_data.get('exit', 0)
        pnl = trade_data.get('pnl', 0)
        result = trade_data.get('result', 'UNKNOWN')
        
        if result == 'WIN':
            emoji = '🎉'
            status = '✅ WIN'
        else:
            emoji = '😞'
            status = '❌ LOSS'
        
        text = f"""
{emoji} *TRADE CLOSED* {emoji}

*Symbol:* `{symbol}`
*Direction:* {signal}
*Result:* {status}

💰 *Performance:*
Entry: `${entry:,.2f}`
Exit: `${exit_price:,.2f}`
P&L: {pnl:+.2f}%

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔱 *Demir AI Trading Bot*
"""
        
        return self.send_message(text.strip(), parse_mode='Markdown')
    
    def send_performance_summary(self, performance_data: Dict) -> bool:
        """
        Send performance summary to Telegram
        
        Args:
            performance_data: {
                'total_trades': 10,
                'winning_trades': 7,
                'losing_trades': 3,
                'win_rate': 70.0,
                'total_pnl_usd': 1250.50,
                'sharpe_ratio': 1.8,
                'profit_factor': 2.3,
                'max_drawdown': -8.5
            }
        
        Returns:
            bool: Success status
        """
        
        message = f"""
🔱 PERFORMANCE SUMMARY 🔱

📊 GENEL İSTATİSTİKLER

📈 Total Trades: {performance_data.get('total_trades', 0)}
✅ Winning: {performance_data.get('winning_trades', 0)}
❌ Losing: {performance_data.get('losing_trades', 0)}
🎯 Win Rate: {performance_data.get('win_rate', 0):.1f}%

💰 Total PnL: ${performance_data.get('total_pnl_usd', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━
📈 ADVANCED METRICS

📊 Sharpe Ratio: {performance_data.get('sharpe_ratio', 0):.2f}
💎 Profit Factor: {performance_data.get('profit_factor', 0):.2f}
📉 Max Drawdown: {performance_data.get('max_drawdown', 0):.2f}%

━━━━━━━━━━━━━━━━━━━━
⚡ DEMIR AI Trading Bot v7.0
"""
        
        return self.send_message(message)
    
    def send_daily_summary(self, summary_data: Dict) -> bool:
        """
        Send daily performance summary (alternative format)
        
        Args:
            summary_data: {
                'total_trades': 10,
                'wins': 7,
                'losses': 3,
                'win_rate': 70.0,
                'total_pnl': 12.5,
                'best_trade': 5.2,
                'worst_trade': -2.1
            }
        
        Returns:
            bool: Success status
        """
        
        total = summary_data.get('total_trades', 0)
        wins = summary_data.get('wins', 0)
        losses = summary_data.get('losses', 0)
        win_rate = summary_data.get('win_rate', 0)
        pnl = summary_data.get('total_pnl', 0)
        best = summary_data.get('best_trade', 0)
        worst = summary_data.get('worst_trade', 0)
        
        emoji = '🎉' if pnl > 0 else '😐' if pnl == 0 else '📉'
        
        text = f"""
{emoji} *DAILY SUMMARY* {emoji}

📊 *Performance:*
Total Trades: {total}
Wins: {wins} ✅
Losses: {losses} ❌
Win Rate: {win_rate:.1f}%

💰 *P&L:*
Total: {pnl:+.2f}%
Best Trade: {best:+.2f}%
Worst Trade: {worst:+.2f}%

⏰ {datetime.now().strftime('%Y-%m-%d')}

🔱 *Demir AI Trading Bot*
"""
        
        return self.send_message(text.strip(), parse_mode='Markdown')
    
    def send_price_alert(self, symbol: str, price: float, alert_type: str, message: str = "") -> bool:
        """
        Send price alert
        
        Args:
            symbol: Trading pair
            price: Current price
            alert_type: 'BREAKOUT', 'SUPPORT', 'RESISTANCE', 'HIGH', 'LOW'
            message: Additional context
        
        Returns:
            bool: Success status
        """
        
        emoji_map = {
            'BREAKOUT': '🚀',
            'SUPPORT': '🛡️',
            'RESISTANCE': '⚡',
            'HIGH': '📈',
            'LOW': '📉'
        }
        
        emoji = emoji_map.get(alert_type, '📊')
        
        text = f"""
{emoji} *PRICE ALERT* {emoji}

*Symbol:* `{symbol}`
*Price:* `${price:,.2f}`
*Alert Type:* {alert_type}

{message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self.send_message(text.strip(), parse_mode='Markdown')
    
    def send_analysis_complete(self, symbol: str, score: float, signal: str, layers: int = 15) -> bool:
        """
        Send analysis completion notification
        
        Args:
            symbol: Trading pair
            score: Final AI score
            signal: LONG/SHORT/NEUTRAL
            layers: Number of layers analyzed
        
        Returns:
            bool: Success status
        """
        
        if signal == 'LONG':
            emoji = '🟢'
        elif signal == 'SHORT':
            emoji = '🔴'
        else:
            emoji = '⚪'
        
        text = f"""
{emoji} *ANALYSIS COMPLETE* {emoji}

*Symbol:* `{symbol}`
*Score:* {score:.1f}/100
*Signal:* {signal}
*Layers:* {layers}/15

🧠 AI analysis finished!

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self.send_message(text.strip(), parse_mode='Markdown')
    
    def send_error(self, error_message: str) -> bool:
        """
        Send error notification
        
        Args:
            error_message: Error description
        
        Returns:
            bool: Success status
        """
        
        text = f"""
⚠️ *ERROR ALERT* ⚠️

{error_message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔱 *Demir AI Trading Bot*
"""
        
        return self.send_message(text.strip(), parse_mode='Markdown')
    
    def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Returns:
            bool: Connection status
        """
        if not self.enabled:
            print("❌ Telegram not configured")
            return False
        
        test_message = """
🔱 DEMIR AI TRADING BOT 🔱

✅ Connection Test Successful!

Telegram Alert System aktif.
Sinyaller bu kanala gönderilecek.

⚡ DEMIR AI Trading Bot v7.0 Phase 3
"""
        
        return self.send_message(test_message.strip())

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_alert_system(bot_token: str = None, chat_id: str = None) -> TelegramAlertSystem:
    """
    Factory function to create TelegramAlertSystem instance
    
    Args:
        bot_token: Optional bot token (will use env var if not provided)
        chat_id: Optional chat ID (will use env var if not provided)
    
    Returns:
        TelegramAlertSystem: Configured alert system
    """
    return TelegramAlertSystem(bot_token, chat_id)

# ============================================================================
# USAGE EXAMPLE & TEST
# ============================================================================
if __name__ == "__main__":
    print("🔱 TELEGRAM ALERT SYSTEM - ULTIMATE TEST")
    print("=" * 60)
    
    # Import from config
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        alert_system = TelegramAlertSystem(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    except:
        print("⚠️ Config not found, using environment variables...")
        alert_system = TelegramAlertSystem()
    
    if not alert_system.enabled:
        print("❌ Telegram not configured!")
        print("\n💡 To enable:")
        print("1. Create bot with @BotFather")
        print("2. Get chat ID from @userinfobot")
        print("3. Set environment variables or add to config.py:")
        print("   TELEGRAM_BOT_TOKEN='your_bot_token'")
        print("   TELEGRAM_CHAT_ID='your_chat_id'")
        exit()
    
    # Test connection
    print("\n1️⃣ Testing connection...")
    success = alert_system.test_connection()
    
    if success:
        print("✅ Telegram Alert System ready!")
        
        # Test signal alert (GitHub version)
        print("\n2️⃣ Testing signal alert (GitHub format)...")
        decision = {
            'symbol': 'BTCUSDT',
            'decision': 'LONG',
            'final_score': 75.5,
            'confidence': 0.82,
            'entry_price': 50000,
            'stop_loss': 49000,
            'position_size_usd': 1000,
            'risk_amount_usd': 20,
            'risk_reward': 2.5,
            'reason': 'Strong bullish momentum detected by 15-layer AI analysis'
        }
        alert_system.send_signal_alert(decision)
        
        print("\n" + "=" * 60)
        print("✅ All tests complete!")
    else:
        print("❌ Connection failed! Check bot token and chat ID.")
