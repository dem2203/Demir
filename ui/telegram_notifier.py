"""
DEMIR AI BOT - Telegram Notifier (UPDATED)
Group-based Telegram alerts
Async support for concurrent sending
Professional formatted messages
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GroupBasedTelegramNotifier:
    """Send group-based signals to Telegram."""
    
    def __init__(self, token: str, chat_id: str):
        """Initialize Telegram notifier."""
        try:
            from ui.group_signal_telegram import GroupSignalTelegramNotifier
            self.notifier = GroupSignalTelegramNotifier(token, chat_id)
            self.token = token
            self.chat_id = chat_id
            logger.info(f"Telegram notifier initialized for chat {chat_id}")
        except ImportError as e:
            logger.error(f"Failed to import GroupSignalTelegramNotifier: {e}")
            raise
    
    async def send_group_signals(
        self,
        symbol: str,
        group_signals: Dict[str, Any]
    ) -> bool:
        """Send all group signals to Telegram."""
        try:
            logger.info(f"Sending group signals for {symbol} to Telegram")
            
            tasks = []
            
            # Send technical
            if group_signals.get('technical'):
                tech = group_signals['technical']
                tasks.append(self.notifier.send_technical_signal(
                    symbol=symbol,
                    direction=tech.get('direction', 'NEUTRAL'),
                    strength=tech.get('strength', 0.0),
                    confidence=tech.get('confidence', 0.0),
                    active_layers=tech.get('active_layers', 0),
                    top_layers=list(tech.get('layer_details', {}).keys())[:3]
                ))
            
            # Send sentiment
            if group_signals.get('sentiment'):
                sent = group_signals['sentiment']
                tasks.append(self.notifier.send_sentiment_signal(
                    symbol=symbol,
                    direction=sent.get('direction', 'NEUTRAL'),
                    strength=sent.get('strength', 0.0),
                    confidence=sent.get('confidence', 0.0),
                    active_layers=sent.get('active_layers', 0),
                    sources=[]
                ))
            
            # Send ML
            if group_signals.get('ml'):
                ml = group_signals['ml']
                tasks.append(self.notifier.send_ml_signal(
                    symbol=symbol,
                    direction=ml.get('direction', 'NEUTRAL'),
                    strength=ml.get('strength', 0.0),
                    confidence=ml.get('confidence', 0.0),
                    active_layers=ml.get('active_layers', 0),
                    models=[]
                ))
            
            # Send OnChain
            if group_signals.get('onchain'):
                oc = group_signals['onchain']
                tasks.append(self.notifier.send_onchain_signal(
                    symbol=symbol,
                    direction=oc.get('direction', 'NEUTRAL'),
                    strength=oc.get('strength', 0.0),
                    confidence=oc.get('confidence', 0.0),
                    active_layers=oc.get('active_layers', 0),
                    indicators=[]
                ))
            
            # Run all tasks concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for r in results if r is True)
                logger.info(f"Sent {success_count}/{len(results)} group signals")
                return success_count == len(results)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send group signals: {e}")
            return False
    
    async def send_risk_alert(self, symbol: str, risk_data: Dict[str, Any]) -> bool:
        """Send risk assessment to Telegram."""
        try:
            logger.info(f"Sending risk alert for {symbol}")
            result = await self.notifier.send_risk_assessment(
                symbol=symbol,
                volatility_score=risk_data.get('volatility_score', 0.5),
                max_loss_exposure=risk_data.get('max_loss_exposure', 'N/A'),
                kelly_fraction=risk_data.get('kelly_fraction', 0.1)
            )
            return result
        except Exception as e:
            logger.error(f"Failed to send risk alert: {e}")
            return False
    
    async def send_consensus_signal(
        self,
        symbol: str,
        consensus_data: Dict[str, Any],
        conflict_detected: bool = False
    ) -> bool:
        """Send consensus signal to Telegram."""
        try:
            logger.info(f"Sending consensus for {symbol}")
            result = await self.notifier.send_consensus_signal(
                symbol=symbol,
                direction=consensus_data.get('direction', 'NEUTRAL'),
                strength=consensus_data.get('strength', 0.5),
                confidence=consensus_data.get('confidence', 0.0),
                conflict=conflict_detected
            )
            return result
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
            logger.warning(f"Sending conflict alert for {symbol}")
            result = await self.notifier.send_conflict_alert(symbol, conflicts)
            return result
        except Exception as e:
            logger.error(f"Failed to send conflict alert: {e}")
            return False
    
    async def send_all_signals(
        self,
        symbol: str,
        orchestrated_result: Dict[str, Any]
    ) -> bool:
        """Send all signals in one batch."""
        try:
            logger.info(f"Sending all signals for {symbol}")
            
            # Send group signals
            await self.send_group_signals(symbol, orchestrated_result.get('groups', {}))
            
            # Send risk
            if orchestrated_result.get('risk'):
                await self.send_risk_alert(symbol, orchestrated_result['risk'])
            
            # Send consensus
            if orchestrated_result.get('consensus'):
                await self.send_consensus_signal(
                    symbol,
                    orchestrated_result['consensus'],
                    orchestrated_result.get('conflict_detected', False)
                )
            
            # Send conflict alert if needed
            if orchestrated_result.get('conflict_detected'):
                await self.send_conflict_alert(
                    symbol,
                    orchestrated_result.get('conflicts', [])
                )
            
            logger.info(f"All signals sent for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send all signals: {e}")
            return False
