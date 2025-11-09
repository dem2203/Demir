"""
=============================================================================
DEMIR AI v25.0 - TELEGRAM MULTI-CHANNEL NOTIFICATION SYSTEM
=============================================================================
Purpose: Telegram üzerinden kritik/uyarı/info bildirimleri ve kanallar
Location: /utils/ klasörü - UPDATE
Integrations: telegram_alert_system.py, daemon_uptime_monitor.py, streamlit_app.py
=============================================================================
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """Bildirim seviyeleri"""
    CRITICAL = "🔴 CRITICAL"  # Immediate action needed
    WARNING = "⚠️ WARNING"     # Attention needed
    INFO = "ℹ️ INFO"           # Informational
    SUCCESS = "✅ SUCCESS"     # Positive action


class TelegramChannel(Enum):
    """Telegram kanal tipleri"""
    CRITICAL = "critical_alerts"      # Flash crash, SL hit, errors
    WARNING = "warning_alerts"        # TP hit, signals, anomalies
    INFO = "info_channel"             # Stats, pings, history
    TRADE_LOG = "trade_log"           # All trades


@dataclass
class NotificationMessage:
    """Bildirim mesajı"""
    level: NotificationLevel
    channel: TelegramChannel
    title: str
    content: str
    symbol: Optional[str] = None
    image_url: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def format_message(self) -> str:
        """Format edilmiş mesaj"""
        return f"""
{self.level.value}
━━━━━━━━━━━━━━━━━━━━━━━━━
📌 {self.title}
{self.content}
⏰ {self.timestamp[:19]} CET
        """.strip()


class TelegramMultiChannelNotifier:
    """
    Çok-kanal Telegram bildirim sistemi
    
    Features:
    - 4 farklı kanal (Kritik/Uyarı/Info/Trade)
    - Async gönderim
    - Rate limiting
    - Mesaj formatting
    - Batch notifications
    """
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Channel configuration (need to be set via environment or UI)
        self.channels: Dict[TelegramChannel, str] = {
            TelegramChannel.CRITICAL: None,      # Chat ID or group
            TelegramChannel.WARNING: None,
            TelegramChannel.INFO: None,
            TelegramChannel.TRADE_LOG: None,
        }
        
        # Rate limiting
        self.rate_limit = {}  # {channel: last_message_time}
        self.min_interval = 1  # Minimum seconds between messages per channel
        
        # Message queue for batch sending
        self.message_queue: List[NotificationMessage] = []
        
        logger.info("✅ TelegramMultiChannelNotifier initialized")
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    def set_channel_id(self, channel: TelegramChannel, chat_id: str):
        """Kanal ID'sini ayarla"""
        self.channels[channel] = chat_id
        logger.info(f"✅ Channel {channel.value} set to {chat_id}")
    
    def configure_channels(self, config: Dict[str, str]):
        """Tüm kanalları ayarla
        
        config = {
            "critical": "-1001234567890",
            "warning": "-1001234567891",
            "info": "-1001234567892",
            "trade_log": "-1001234567893"
        }
        """
        channel_map = {
            "critical": TelegramChannel.CRITICAL,
            "warning": TelegramChannel.WARNING,
            "info": TelegramChannel.INFO,
            "trade_log": TelegramChannel.TRADE_LOG,
        }
        
        for key, chat_id in config.items():
            if key in channel_map:
                self.set_channel_id(channel_map[key], chat_id)
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def _can_send_to_channel(self, channel: TelegramChannel) -> bool:
        """Kanal rate limit kontrolü"""
        if channel not in self.rate_limit:
            self.rate_limit[channel] = datetime.now()
            return True
        
        elapsed = (datetime.now() - self.rate_limit[channel]).total_seconds()
        
        if elapsed >= self.min_interval:
            self.rate_limit[channel] = datetime.now()
            return True
        
        return False
    
    # ========================================================================
    # SENDING
    # ========================================================================
    
    async def send_message(self, notification: NotificationMessage) -> Tuple[bool, str]:
        """Mesaj gönder (async)"""
        chat_id = self.channels.get(notification.channel)
        
        if not chat_id:
            logger.warning(f"⚠️ Channel {notification.channel.value} not configured")
            return False, "Channel not configured"
        
        # Rate limiting
        if not self._can_send_to_channel(notification.channel):
            logger.warning(f"⏱️ Rate limited for {notification.channel.value}")
            return False, "Rate limited"
        
        # Format message
        message_text = notification.format_message()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": message_text,
                    "parse_mode": "HTML"
                }
                
                async with session.post(url, json=data) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ Message sent to {notification.channel.value}")
                        return True, "Message sent"
                    else:
                        error = await resp.text()
                        logger.error(f"❌ Failed to send message: {error}")
                        return False, error
        
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False, str(e)
    
    def send_message_sync(self, notification: NotificationMessage) -> Tuple[bool, str]:
        """Synchronous mesaj gönderme (blocking)"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.send_message(notification))
        except RuntimeError:
            # No event loop, create new
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.send_message(notification))
    
    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================
    
    def send_critical(self, title: str, content: str, symbol: Optional[str] = None) -> Tuple[bool, str]:
        """Kritik alert gönder"""
        notification = NotificationMessage(
            level=NotificationLevel.CRITICAL,
            channel=TelegramChannel.CRITICAL,
            title=title,
            content=content,
            symbol=symbol
        )
        return self.send_message_sync(notification)
    
    def send_warning(self, title: str, content: str, symbol: Optional[str] = None) -> Tuple[bool, str]:
        """Uyarı gönder"""
        notification = NotificationMessage(
            level=NotificationLevel.WARNING,
            channel=TelegramChannel.WARNING,
            title=title,
            content=content,
            symbol=symbol
        )
        return self.send_message_sync(notification)
    
    def send_info(self, title: str, content: str) -> Tuple[bool, str]:
        """Bilgi gönder"""
        notification = NotificationMessage(
            level=NotificationLevel.INFO,
            channel=TelegramChannel.INFO,
            title=title,
            content=content
        )
        return self.send_message_sync(notification)
    
    def send_trade_log(self, symbol: str, trade_type: str, entry: float, tp: float, sl: float) -> Tuple[bool, str]:
        """Trade log gönder"""
        content = f"""
🔀 {trade_type}
━━━━━━━━━━━━━━━━━━━━━
📊 Symbol: {symbol}
📥 Entry: ${entry}
📈 TP: ${tp}
📉 SL: ${sl}
        """.strip()
        
        notification = NotificationMessage(
            level=NotificationLevel.INFO,
            channel=TelegramChannel.TRADE_LOG,
            title=f"{trade_type} Signal",
            content=content,
            symbol=symbol
        )
        return self.send_message_sync(notification)
    
    # ========================================================================
    # TP/SL HIT ALERTS
    # ========================================================================
    
    def send_tp_hit(self, symbol: str, tp_level: int, price: float, pnl: float) -> Tuple[bool, str]:
        """Take Profit tetikleme bildirimi"""
        content = f"""
📊 {symbol}
━━━━━━━━━━━━━━━━━━━━━
🎯 TP{tp_level} HIT
💰 Price: ${price}
💵 PnL: +${pnl}
        """.strip()
        
        return self.send_warning(f"{symbol} TP{tp_level} HIT", content, symbol)
    
    def send_sl_hit(self, symbol: str, price: float, loss: float) -> Tuple[bool, str]:
        """Stop Loss tetikleme bildirimi"""
        content = f"""
📊 {symbol}
━━━━━━━━━━━━━━━━━━━━━
🛑 STOP LOSS HIT
💰 Price: ${price}
❌ Loss: -${loss}
        """.strip()
        
        return self.send_critical(f"{symbol} SL HIT", content, symbol)
    
    # ========================================================================
    # ERROR ALERTS
    # ========================================================================
    
    def send_error_alert(self, error_title: str, error_details: str) -> Tuple[bool, str]:
        """Hata bildirimi"""
        return self.send_critical(error_title, error_details)
    
    def send_api_error(self, api_name: str, error: str) -> Tuple[bool, str]:
        """API hatasını bildir"""
        content = f"""
⚠️ API ERROR
━━━━━━━━━━━━━━━━━━━━━
🔌 API: {api_name}
❌ Error: {error}
⏰ Action: Investigating...
        """.strip()
        
        return self.send_critical(f"{api_name} Error", content)
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def queue_message(self, notification: NotificationMessage):
        """Mesajı sıraya al (batch)"""
        self.message_queue.append(notification)
    
    async def send_queued_batch(self) -> Dict[str, Tuple[int, int]]:
        """Sıradaki tüm mesajları gönder"""
        results = {}
        
        for notification in self.message_queue:
            channel_name = notification.channel.value
            if channel_name not in results:
                results[channel_name] = (0, 0)
            
            success, msg = await self.send_message(notification)
            sent, failed = results[channel_name]
            
            if success:
                results[channel_name] = (sent + 1, failed)
            else:
                results[channel_name] = (sent, failed + 1)
        
        self.message_queue.clear()
        logger.info(f"✅ Batch sent: {results}")
        return results
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_channel_config(self) -> Dict:
        """Kanal konfigurasyonu al"""
        return {
            channel.value: self.channels[channel]
            for channel in TelegramChannel
        }


# ============================================================================
# TEST & USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize (use your own bot token)
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    notifier = TelegramMultiChannelNotifier(BOT_TOKEN)
    
    # Configure channels
    channels_config = {
        "critical": "-1001234567890",
        "warning": "-1001234567891",
        "info": "-1001234567892",
        "trade_log": "-1001234567893"
    }
    notifier.configure_channels(channels_config)
    
    # Test notifications
    print("\n📱 Testing Telegram Notifications:")
    print("\n1. Trade Log:")
    notifier.send_trade_log("BTCUSDT", "LONG", 50000, 52500, 48500)
    
    print("\n2. TP Hit:")
    notifier.send_tp_hit("BTCUSDT", 1, 51500, 1500)
    
    print("\n3. SL Hit:")
    notifier.send_sl_hit("ETHUSDT", 1800, 200)
    
    print("\n4. Error Alert:")
    notifier.send_api_error("Binance", "Connection timeout")
    
    print("\n5. Info:")
    notifier.send_info("Bot Status", "✅ System operational, 2 active trades")
    
    print("\n✅ All notifications queued/sent")
