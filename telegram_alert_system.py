# ============================================================================
# DEMIR AI TRADING BOT - Telegram Alert System
# ============================================================================
# Phase 3.1: Real-time Signal Alerts via Telegram
# Date: 4 Kasım 2025, 22:30 CET
# Version: 1.0 - PRODUCTION READY
#
# ✅ FEATURES:
# - Real-time trading signals via Telegram
# - Price alerts
# - Entry/Exit notifications
# - Win/Loss tracking
# - Daily performance summary
# - Emoji-rich messages
# ============================================================================

import os
import asyncio
from datetime import datetime
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError

class TelegramAlertSystem:
    """
    Telegram Alert System for real-time trading notifications
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram bot

        Args:
            bot_token: Telegram bot token (from @BotFather)
            chat_id: Telegram chat ID (your user ID)
        """
        # Get from environment variables or parameters
        self.bot_token = bot_token or os.getenv('TELEGRAM_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            print("⚠️ Telegram credentials not found!")
            print("   Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in Render environment")
            self.enabled = False
        else:
            self.bot = Bot(token=self.bot_token)
            self.enabled = True
            print("✅ Telegram Alert System initialized")

    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send message to Telegram

        Args:
            message: Message text (supports HTML formatting)
            parse_mode: 'HTML' or 'Markdown'

        Returns:
            bool: Success status
        """
        if not self.enabled:
            print("⚠️ Telegram not enabled, message not sent")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            print("✅ Telegram message sent successfully")
            return True
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
            return False

    def send_signal_alert(self, symbol: str, signal: str, score: float, confidence: float, 
                         price: float, entry: float, tp: float, sl: float) -> bool:
        """
        Send trading signal alert

        Args:
            symbol: Trading pair (BTCUSDT)
            signal: LONG/SHORT/NEUTRAL
            score: AI score (0-100)
            confidence: Confidence level (0-1)
            price: Current price
            entry: Entry price
            tp: Take profit
            sl: Stop loss

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        # Emoji based on signal
        emoji = "🟢" if signal == "LONG" else "🔴" if signal == "SHORT" else "⚪"

        # Confidence emoji
        conf_emoji = "🔥" if confidence > 0.7 else "⚡" if confidence > 0.5 else "💡"

        message = f"""
{emoji} <b>DEMIR AI SIGNAL</b> {emoji}

<b>Symbol:</b> {symbol}
<b>Signal:</b> {signal}
<b>AI Score:</b> {score:.1f}/100
<b>Confidence:</b> {conf_emoji} {confidence:.1%}

💰 <b>TRADE SETUP:</b>
├ Entry: ${entry:,.2f}
├ Take Profit: ${tp:,.2f} (+{((tp-entry)/entry*100):.2f}%)
└ Stop Loss: ${sl:,.2f} ({((sl-entry)/entry*100):.2f}%)

📊 Current Price: ${price:,.2f}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CET

🤖 <i>Demir AI Trading Bot v14.1</i>
        """

        # Run async function synchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.send_message(message))

    def send_price_alert(self, symbol: str, price: float, target: float, 
                        alert_type: str = "TARGET_HIT") -> bool:
        """
        Send price alert

        Args:
            symbol: Trading pair
            price: Current price
            target: Target price
            alert_type: TARGET_HIT / STOP_LOSS / TAKE_PROFIT

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        emoji_map = {
            "TARGET_HIT": "🎯",
            "STOP_LOSS": "🛑",
            "TAKE_PROFIT": "💰"
        }

        emoji = emoji_map.get(alert_type, "📊")

        message = f"""
{emoji} <b>PRICE ALERT</b>

<b>Symbol:</b> {symbol}
<b>Alert Type:</b> {alert_type}

💵 <b>Current:</b> ${price:,.2f}
🎯 <b>Target:</b> ${target:,.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CET
        """

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.send_message(message))

    def send_performance_summary(self, total_trades: int, wins: int, losses: int, 
                                win_rate: float, total_pnl: float, roi: float) -> bool:
        """
        Send daily performance summary

        Args:
            total_trades: Total number of trades
            wins: Number of winning trades
            losses: Number of losing trades
            win_rate: Win rate percentage (0-1)
            total_pnl: Total P&L in USD
            roi: Return on Investment (0-1)

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        # Emoji based on performance
        perf_emoji = "🚀" if roi > 0.1 else "📈" if roi > 0 else "📉"

        message = f"""
{perf_emoji} <b>DAILY PERFORMANCE SUMMARY</b>

📊 <b>TRADE STATISTICS:</b>
├ Total Trades: {total_trades}
├ Wins: 🟢 {wins}
├ Losses: 🔴 {losses}
└ Win Rate: {win_rate:.1%}

💰 <b>FINANCIAL:</b>
├ Total P&L: ${total_pnl:,.2f}
└ ROI: {roi:.2%}

📅 {datetime.now().strftime('%Y-%m-%d')}
⏰ {datetime.now().strftime('%H:%M:%S')} CET

🤖 <i>Demir AI Trading Bot v14.1</i>
        """

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.send_message(message))

    def send_system_status(self, status: str, layers_active: int, total_layers: int, 
                          last_update: str) -> bool:
        """
        Send system status update

        Args:
            status: ONLINE / OFFLINE / ERROR
            layers_active: Number of active layers
            total_layers: Total number of layers
            last_update: Last update timestamp

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        status_emoji = "🟢" if status == "ONLINE" else "🔴" if status == "ERROR" else "⚪"

        message = f"""
{status_emoji} <b>SYSTEM STATUS</b>

<b>Status:</b> {status}
<b>AI Layers:</b> {layers_active}/{total_layers} active

⏰ Last Update: {last_update}

🤖 <i>Demir AI Trading Bot v14.1</i>
        """

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.send_message(message))

# ============================================================================
# HELPER FUNCTIONS FOR STREAMLIT INTEGRATION
# ============================================================================

def create_telegram_bot():
    """
    Create and return Telegram bot instance

    Returns:
        TelegramAlertSystem: Bot instance
    """
    return TelegramAlertSystem()

def test_telegram_connection():
    """
    Test Telegram bot connection

    Returns:
        bool: Connection status
    """
    bot = TelegramAlertSystem()
    if not bot.enabled:
        return False

    test_message = """
🧪 <b>TEST MESSAGE</b>

✅ Telegram bot connection successful!
🤖 Demir AI Trading Bot v14.1
⏰ """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " CET"

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(bot.send_message(test_message))

# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("="*80)
    print("🤖 TELEGRAM ALERT SYSTEM TEST")
    print("="*80)

    # Test connection
    if test_telegram_connection():
        print("✅ Telegram test successful!")

        # Test signal alert
        bot = create_telegram_bot()
        bot.send_signal_alert(
            symbol="BTCUSDT",
            signal="LONG",
            score=75.5,
            confidence=0.82,
            price=35000,
            entry=35100,
            tp=36000,
            sl=34500
        )
        print("✅ Signal alert sent!")
    else:
        print("❌ Telegram test failed!")
        print("   Make sure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set")
