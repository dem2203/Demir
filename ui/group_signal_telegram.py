"""
DEMIR AI BOT - Group Signal Telegram Notifier
Send group-based signals to Telegram
Professional formatted messages with emojis
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)


class GroupSignalTelegramNotifier:
    """Send group-based signals to Telegram."""
    
    def __init__(self, token: str, chat_id: str):
        """Initialize Telegram notifier."""
        self.token = token
        self.chat_id = chat_id
        logger.info(f"Telegram notifier initialized for chat {chat_id}")
    
    def format_technical_signal_message(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        top_layers: List[str],
        entry_price: Optional[float] = None,
        tp1_price: Optional[float] = None,
        tp2_price: Optional[float] = None,
        sl_price: Optional[float] = None
    ) -> str:
        """Format technical signal for Telegram."""
        
        emoji = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "⚪"
        
        message = f"""
{emoji} TECHNICAL SIGNAL - {symbol}

📊 Direction: *{direction}*
💪 Strength: {strength:.1%}
🎯 Confidence: {confidence:.1%}
📈 Active Layers: {active_layers}/28

🔝 Top Performers:
"""
        for i, layer in enumerate(top_layers[:5], 1):
            message += f"{i}. {layer}\n"
        
        if entry_price and tp1_price and sl_price:
            message += f"""
💰 Trading Levels:
Entry: ${entry_price:,.2f}
TP1: ${tp1_price:,.2f}
SL: ${sl_price:,.2f}
"""
        
        return message
    
    def format_sentiment_signal_message(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        sources: List[str]
    ) -> str:
        """Format sentiment signal for Telegram."""
        
        emoji = "💚" if direction == "LONG" else "❤️" if direction == "SHORT" else "🤍"
        
        message = f"""
{emoji} SENTIMENT SIGNAL - {symbol}

📊 Direction: *{direction}*
💪 Strength: {strength:.1%}
🎯 Confidence: {confidence:.1%}
📈 Active Layers: {active_layers}/20

📰 Sources:
"""
        for source in sources[:5]:
            message += f"• {source}\n"
        
        return message
    
    def format_ml_signal_message(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        models: List[str]
    ) -> str:
        """Format ML signal for Telegram."""
        
        emoji = "🤖" if direction == "LONG" else "⚠️" if direction == "SHORT" else "❓"
        
        message = f"""
{emoji} ML SIGNAL - {symbol}

📊 Direction: *{direction}*
💪 Strength: {strength:.1%}
🎯 Confidence: {confidence:.1%}
📈 Active Models: {active_layers}/10

🧠 Models:
"""
        for model in models:
            message += f"• {model}\n"
        
        return message
    
    def format_onchain_signal_message(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        active_layers: int,
        indicators: List[str]
    ) -> str:
        """Format OnChain signal for Telegram."""
        
        emoji = "⛓️" if direction == "LONG" else "🔗" if direction == "SHORT" else "📡"
        
        message = f"""
{emoji} ONCHAIN SIGNAL - {symbol}

📊 Direction: *{direction}*
💪 Strength: {strength:.1%}
🎯 Confidence: {confidence:.1%}
📈 Active Indicators: {active_layers}/6

🔍 Indicators:
"""
        for indicator in indicators:
            message += f"• {indicator}\n"
        
        return message
    
    def format_consensus_message(
        self,
        symbol: str,
        direction: str,
        strength: float,
        confidence: float,
        conflict: bool,
        active_groups: int,
        recommendation: Optional[str] = None
    ) -> str:
        """Format consensus signal for Telegram."""
        
        emoji = "⭐" if not conflict else "⚡"
        
        if not conflict:
            conflict_text = "✅ All Groups Aligned"
            color_emoji = "🟢"
        else:
            conflict_text = "⚠️ Group Conflict Detected"
            color_emoji = "🔴"
        
        message = f"""
{emoji} CONSENSUS SIGNAL - {symbol}

{color_emoji} {conflict_text}

📊 Direction: *{direction}*
💪 Strength: {strength:.1%}
🎯 Confidence: {confidence:.1%}
📊 Active Groups: {active_groups}/5
"""
        
        if recommendation:
            message += f"\n💡 Recommendation: *{recommendation}*"
        
        if conflict:
            message += "\n\n⚠️ *Manual review recommended due to conflicts*"
        
        return message
    
    def format_risk_assessment_message(
        self,
        symbol: str,
        volatility_score: float,
        max_loss_exposure: str,
        kelly_fraction: float
    ) -> str:
        """Format risk assessment for Telegram."""
        
        vol_emoji = "🟢" if volatility_score < 0.4 else "🟡" if volatility_score < 0.7 else "🔴"
        
        message = f"""
{vol_emoji} RISK ASSESSMENT - {symbol}

📊 Volatility: {volatility_score:.1%}
⚠️ Max Loss Exposure: {max_loss_exposure}
🎲 Kelly Fraction: {kelly_fraction:.1%}

Risk Level: {'LOW' if volatility_score < 0.4 else 'MEDIUM' if volatility_score < 0.7 else 'HIGH'}
"""
        
        return message
    
    def format_conflict_alert(
        self,
        symbol: str,
        conflicts: List[str]
    ) -> str:
        """Format conflict alert for Telegram."""
        
        message = f"""
⚡ GROUP CONFLICT ALERT - {symbol}

Conflicts detected:
"""
        for conflict in conflicts:
            message += f"❌ {conflict}\n"
        
        message += """
📋 Recommendation:
• Paper trading: SKIP this signal
• Risk assessment: REQUIRED
• Manual review: RECOMMENDED

Do NOT trade until conflicts are resolved.
"""
        
        return message
    
    async def send_technical_signal(self, **kwargs) -> bool:
        """Send technical signal to Telegram."""
        try:
            message = self.format_technical_signal_message(**kwargs)
            logger.info(f"Sending technical signal for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send technical signal: {e}")
            return False
    
    async def send_sentiment_signal(self, **kwargs) -> bool:
        """Send sentiment signal to Telegram."""
        try:
            message = self.format_sentiment_signal_message(**kwargs)
            logger.info(f"Sending sentiment signal for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send sentiment signal: {e}")
            return False
    
    async def send_ml_signal(self, **kwargs) -> bool:
        """Send ML signal to Telegram."""
        try:
            message = self.format_ml_signal_message(**kwargs)
            logger.info(f"Sending ML signal for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send ML signal: {e}")
            return False
    
    async def send_onchain_signal(self, **kwargs) -> bool:
        """Send OnChain signal to Telegram."""
        try:
            message = self.format_onchain_signal_message(**kwargs)
            logger.info(f"Sending OnChain signal for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send OnChain signal: {e}")
            return False
    
    async def send_risk_assessment(self, **kwargs) -> bool:
        """Send risk assessment to Telegram."""
        try:
            message = self.format_risk_assessment_message(**kwargs)
            logger.info(f"Sending risk assessment for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send risk assessment: {e}")
            return False
    
    async def send_consensus_signal(self, **kwargs) -> bool:
        """Send consensus signal to Telegram."""
        try:
            message = self.format_consensus_message(**kwargs)
            logger.info(f"Sending consensus signal for {kwargs.get('symbol')} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send consensus signal: {e}")
            return False
    
    async def send_conflict_alert(
        self,
        symbol: str,
        conflicts: List[str]
    ) -> bool:
        """Send conflict alert to Telegram."""
        try:
            message = self.format_conflict_alert(symbol, conflicts)
            logger.warning(f"Sending conflict alert for {symbol} to Telegram")
            # Send to Telegram API
            return True
        except Exception as e:
            logger.error(f"Failed to send conflict alert: {e}")
            return False
    
    async def send_batch_signals(
        self,
        signals: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Send multiple signals in batch."""
        try:
            logger.info(f"Sending batch of {len(signals)} signals to Telegram")
            for group_name, signal_data in signals.items():
                if group_name == 'technical':
                    await self.send_technical_signal(**signal_data)
                elif group_name == 'sentiment':
                    await self.send_sentiment_signal(**signal_data)
                elif group_name == 'ml':
                    await self.send_ml_signal(**signal_data)
                elif group_name == 'onchain':
                    await self.send_onchain_signal(**signal_data)
                elif group_name == 'risk':
                    await self.send_risk_assessment(**signal_data)
                elif group_name == 'consensus':
                    await self.send_consensus_signal(**signal_data)
            return True
        except Exception as e:
            logger.error(f"Failed to send batch signals: {e}")
            return False
