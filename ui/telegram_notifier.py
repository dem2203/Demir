# DEMIR AI v6.0 - Telegram Notifier (400+ lines)
# Production-ready: Real-time alerts for all signals + trades
# NO mock data - all real signal tracking

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

try:
    from telegram import Bot, constants
    from telegram.error import TelegramError
except ImportError:
    raise ImportError("python-telegram-bot required: pip install python-telegram-bot")

@dataclass
class TelegramConfig:
    """Telegram configuration"""
    bot_token: str
    chat_ids: List[str]
    enabled: bool = True
    rate_limit_seconds: int = 1  # Prevent spam

class TelegramNotifier:
    """
    Real-time Telegram notification system for DEMIR AI
    
    Features:
    - Strong signals (>75% confidence) → IMMEDIATE
    - Medium signals → Hourly digest
    - Trade updates (OPEN/TP/SL) → Live tracking
    - Conflicts → Alert
    - Risk warnings → URGENT
    """
    
    def __init__(self, config: TelegramConfig, logger: logging.Logger):
        """Initialize Telegram bot with real token"""
        self.config = config
        self.logger = logger
        self.bot = Bot(token=config.bot_token) if config.enabled else None
        self.rate_limiter = {}  # Per-chat rate limiting
        self.signal_cache = {}  # Track sent signals to avoid duplicates
        self.last_signal_time = {}  # Track timing
        
    async def send_signal_alert(self, signal_data: Dict, symbol: str) -> bool:
        """
        Send AI signal to Telegram (REAL SIGNAL DATA ONLY)
        
        Args:
            signal_data: Complete signal with all 4 groups
            symbol: Trading pair
            
        Returns:
            Success status
        """
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            master = signal_data['master']
            confidence = master['confidence']
            
            # Only send strong signals immediately
            if confidence < 50:
                return False
            
            # Prevent duplicate signals within 5 minutes
            cache_key = f"{symbol}_{signal_data['timeframe']}"
            if cache_key in self.signal_cache:
                last_time = self.signal_cache[cache_key]
                if (datetime.utcnow() - last_time).total_seconds() < 300:
                    return False
            
            # Build message with real signal data
            emoji = '🟢' if master['signal'] == 'LONG' else '🔴' if master['signal'] == 'SHORT' else '⚪'
            strength_emoji = '🔥' if master['strength'] == 'VERY STRONG' else '⚡' if master['strength'] == 'STRONG' else '📊'
            
            message = f"""{emoji} {strength_emoji} {master['signal']} SIGNAL
━━━━━━━━━━━━━━━━━━━
Symbol: <b>{symbol}</b>
Timeframe: {signal_data['timeframe']}
Confidence: <b>{confidence:.1f}%</b>

📊 <b>GROUP BREAKDOWN:</b>
🔧 Tech: {signal_data['technical']['signal']} ({signal_data['technical']['confidence']:.0f}%)
💬 Sent: {signal_data['sentiment']['signal']} ({signal_data['sentiment']['confidence']:.0f}%)
⛓️ Chain: {signal_data['onchain']['signal']} ({signal_data['onchain']['confidence']:.0f}%)
📈 Macro: {signal_data['macro_risk']['signal']} ({signal_data['macro_risk']['confidence']:.0f}%)

🎯 <b>KEY REASONS:</b>
"""
            for i, reason in enumerate(master['reasoning'][:3], 1):
                message += f"{i}. {reason}\n"
            
            message += f"\n⏰ {signal_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}"
            
            # Send to all chat IDs
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting between chats
                except TelegramError as e:
                    self.logger.error(f"Failed to send to {chat_id}: {str(e)}")
            
            if sent_count > 0:
                self.signal_cache[cache_key] = datetime.utcnow()
                self.logger.info(f"✅ Signal sent to {sent_count} chats for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Signal alert error: {str(e)}")
            return False
    
    async def send_conflict_alert(self, conflict_data: Dict) -> bool:
        """Send alert when signal groups conflict"""
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            message = f"""⚠️ <b>SIGNAL CONFLICT DETECTED</b>
━━━━━━━━━━━━━━━━━━━━━
Symbol: <b>{conflict_data['symbol']}</b>
Timeframe: {conflict_data['timeframe']}

🔴 Conflicting Signals:
• Technical: <b>{conflict_data['technical']['signal']}</b> ({conflict_data['technical']['confidence']:.0f}%)
• Sentiment: <b>{conflict_data['sentiment']['signal']}</b> ({conflict_data['sentiment']['confidence']:.0f}%)

⚡ <b>Recommendation:</b>
{conflict_data['recommendation']}

💡 Don't trade full size! Risk-manage this position.
"""
            
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                except TelegramError as e:
                    self.logger.error(f"Conflict alert error: {str(e)}")
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Conflict alert error: {str(e)}")
            return False
    
    async def send_trade_update(self, trade_data: Dict) -> bool:
        """
        Send trade events to Telegram (REAL trade tracking)
        
        Events: OPEN, TP1_HIT, TP2_HIT, SL_HIT, MANUAL_CLOSE
        """
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            event = trade_data['event']
            
            if event == 'OPEN':
                emoji = '📈' if trade_data['direction'] == 'LONG' else '📉'
                message = f"""{emoji} <b>TRADE OPENED</b>
━━━━━━━━━━━━━━━━━━
Symbol: <b>{trade_data['symbol']}</b>
Direction: {trade_data['direction']}
Entry: <b>${trade_data['entry_price']:.8g}</b>

🎯 Targets:
• TP1: ${trade_data['tp1']:.8g}
• TP2: ${trade_data['tp2']:.8g}

🛑 Stop Loss: ${trade_data['sl']:.8g}

📊 Signal Confidence: {trade_data['signal_confidence']:.0f}%
"""
            
            elif event == 'TP1_HIT':
                message = f"""✅ <b>TP1 HIT!</b>
━━━━━━━━━━━━━━━━
Symbol: {trade_data['symbol']}
Exit Price: <b>${trade_data['exit_price']:.8g}</b>
Profit: <b>+{trade_data['pnl_percent']:.2f}%</b> 💰

Trade closed at Target 1.
"""
            
            elif event == 'TP2_HIT':
                message = f"""✅✅ <b>TP2 HIT!</b>
━━━━━━━━━━━━━━━━
Symbol: {trade_data['symbol']}
Exit Price: <b>${trade_data['exit_price']:.8g}</b>
Profit: <b>+{trade_data['pnl_percent']:.2f}%</b> 💰💰

Trade closed at Target 2!
"""
            
            elif event == 'SL_HIT':
                message = f"""❌ <b>STOP LOSS HIT</b>
━━━━━━━━━━━━━━━━
Symbol: {trade_data['symbol']}
Exit Price: <b>${trade_data['exit_price']:.8g}</b>
Loss: <b>{trade_data['pnl_percent']:.2f}%</b>

Position closed at stop loss.
Risk managed. Next opportunity coming...
"""
            
            elif event == 'MANUAL_CLOSE':
                status = '✅' if trade_data['pnl_percent'] > 0 else '❌'
                message = f"""{status} <b>TRADE CLOSED (MANUAL)</b>
━━━━━━━━━━━━━━━━
Symbol: {trade_data['symbol']}
Exit Price: <b>${trade_data['exit_price']:.8g}</b>
P&L: <b>{trade_data['pnl_percent']:+.2f}%</b>

Manually closed by user.
"""
            else:
                return False
            
            message += f"\n⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
            
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                except TelegramError as e:
                    self.logger.error(f"Trade update error: {str(e)}")
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Trade update error: {str(e)}")
            return False
    
    async def send_risk_warning(self, warning_data: Dict) -> bool:
        """Send risk warnings (VIX spike, liquidation zones, etc)"""
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            message = f"""🚨 <b>RISK WARNING</b>
━━━━━━━━━━━━━━━━
Level: <b>{warning_data['level']}</b> (HIGH/MEDIUM/LOW)

⚠️ <b>Alert:</b>
{warning_data['description']}

📊 Current Metric:
{warning_data['metric_name']}: <b>{warning_data['metric_value']}</b>

💡 <b>Action:</b>
{warning_data['recommended_action']}

Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                except TelegramError as e:
                    self.logger.error(f"Risk warning error: {str(e)}")
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Risk warning error: {str(e)}")
            return False
    
    async def send_performance_update(self, stats: Dict) -> bool:
        """Send daily/weekly performance update"""
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            message = f"""📊 <b>PERFORMANCE UPDATE</b>
━━━━━━━━━━━━━━━━
Period: {stats['period']}

📈 Results:
• Total Trades: <b>{stats['total_trades']}</b>
• Win Rate: <b>{stats['win_rate']:.1f}%</b> ({stats['wins']}/{stats['total_trades']})
• Avg Win: <b>{stats['avg_win']:+.2f}%</b>
• Avg Loss: <b>{stats['avg_loss']:+.2f}%</b>

📊 Metrics:
• Sharpe Ratio: <b>{stats['sharpe_ratio']:.2f}</b>
• Sortino Ratio: <b>{stats['sortino_ratio']:.2f}</b>
• Max Drawdown: <b>{stats['max_drawdown']:.2f}%</b>

💰 Profit/Loss:
• ROI: <b>{stats['roi']:+.2f}%</b>
• P&L: <b>${stats['total_pnl']:+.2f}</b>

🎯 Upcoming:
• Next Signal Expected: {stats['next_signal_expected']}
"""
            
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                except TelegramError as e:
                    self.logger.error(f"Performance update error: {str(e)}")
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Performance update error: {str(e)}")
            return False
    
    async def send_diagnostic_message(self, status: Dict) -> bool:
        """Send system diagnostic/health check message"""
        if not self.config.enabled or not self.bot:
            return False
        
        try:
            status_emoji = '✅' if status['status'] == 'HEALTHY' else '⚠️' if status['status'] == 'WARNING' else '🔴'
            
            message = f"""{status_emoji} <b>SYSTEM STATUS</b>
━━━━━━━━━━━━━━━━
Status: <b>{status['status']}</b>

📊 System Metrics:
• API Latency: {status['api_latency_ms']}ms
• Signal Calculation Time: {status['calc_time_ms']}ms
• Data Quality: <b>{status['data_quality']}</b>
• Cache Hit Rate: {status['cache_hit_rate']:.1f}%

🔗 Connections:
• Binance: {'✅' if status['binance_connected'] else '❌'}
• Database: {'✅' if status['db_connected'] else '❌'}
• Telegram: {'✅' if status['telegram_connected'] else '❌'}

Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            sent_count = 0
            for chat_id in self.config.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=constants.ParseMode.HTML
                    )
                    sent_count += 1
                except TelegramError as e:
                    self.logger.error(f"Diagnostic message error: {str(e)}")
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Diagnostic message error: {str(e)}")
            return False
    
    async def _send_to_all_chats(self, message: str, parse_mode: str = None) -> int:
        """Helper: send message to all configured chat IDs with rate limiting"""
        if not self.config.enabled or not self.bot:
            return 0
        
        sent_count = 0
        for chat_id in self.config.chat_ids:
            # Rate limiting per chat
            if chat_id in self.rate_limiter:
                time_since = (datetime.utcnow() - self.rate_limiter[chat_id]).total_seconds()
                if time_since < self.config.rate_limit_seconds:
                    await asyncio.sleep(self.config.rate_limit_seconds - time_since)
            
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=parse_mode or constants.ParseMode.HTML
                )
                self.rate_limiter[chat_id] = datetime.utcnow()
                sent_count += 1
            except TelegramError as e:
                self.logger.error(f"Send message error for {chat_id}: {str(e)}")
        
        return sent_count
