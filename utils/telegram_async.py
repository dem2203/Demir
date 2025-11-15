"""
🚀 DEMIR AI v5.2 - Telegram Integration Engine (Async)
📱 Real-time Notifications + Trade Tracking
🔔 24/7 Operational Telegram Bot

Location: GitHub Root / utils/telegram_async.py (REPLACE telegram_queue.py)
Size: ~1000 lines
Author: AI Research Agent
Date: 2025-11-15
"""

import os
import logging
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import pytz
from enum import Enum
import hashlib
import time

logger = logging.getLogger('TELEGRAM_ENGINE')

# ============================================================================
# NOTIFICATION TYPES
# ============================================================================

class NotificationType(Enum):
    """Types of notifications"""
    SIGNAL = 'signal'
    OPPORTUNITY = 'opportunity'
    RISK = 'risk'
    TRADE_TRACKING = 'trade_tracking'
    SYSTEM_STATUS = 'system_status'
    ERROR_ALERT = 'error_alert'

@dataclass
class SignalNotification:
    """Signal notification data"""
    symbol: str
    signal_type: str  # LONG, SHORT, NEUTRAL
    confidence: float
    entry_price: float
    tp1: float
    tp2: float
    tp3: float
    sl: float
    layer_scores: Dict
    reason: str
    timestamp: datetime
    
    def to_html(self) -> str:
        """Convert to HTML formatted message"""
        direction_emoji = '🟢' if self.signal_type == 'LONG' else '🔴' if self.signal_type == 'SHORT' else '⚪'
        
        return f'''
🚀 <b>YENİ SİNYAL - DEMIR AI v5.2</b>

📍 <b>Coin:</b> <code>{self.symbol}</code>
🎯 <b>Yön:</b> {direction_emoji} <b>{self.signal_type}</b>
💰 <b>Giriş:</b> <code>${self.entry_price:.2f}</code>
📈 <b>TP1:</b> <code>${self.tp1:.2f}</code> (1:1 Risk/Reward)
📈 <b>TP2:</b> <code>${self.tp2:.2f}</code> (1:2 Risk/Reward)
📈 <b>TP3:</b> <code>${self.tp3:.2f}</code> (1:3 Risk/Reward)
❌ <b>SL:</b> <code>${self.sl:.2f}</code>
🔒 <b>Güven:</b> <b>{self.confidence:.0f}%</b>

📊 <b>Layer Skoru:</b>
  • <b>Technical:</b> {self.layer_scores.get('technical', 0):.0%}
  • <b>ML:</b> {self.layer_scores.get('ml', 0):.0%}
  • <b>Sentiment:</b> {self.layer_scores.get('sentiment', 0):.0%}
  • <b>On-chain:</b> {self.layer_scores.get('onchain', 0):.0%}

💡 <b>Analiz:</b>
<i>{self.reason}</i>

⏱️ <b>Oluşturulan:</b> <code>{self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>
        '''

@dataclass
class OpportunityNotification:
    """Opportunity notification data"""
    title: str
    description: str
    action: str
    urgency: str  # LOW, MEDIUM, HIGH
    timestamp: datetime
    
    def to_html(self) -> str:
        """Convert to HTML formatted message"""
        urgency_emoji = '⚠️' if self.urgency == 'HIGH' else '💡' if self.urgency == 'MEDIUM' else 'ℹ️'
        
        return f'''
{urgency_emoji} <b>FIRSAT TESPİT EDİLDİ</b>

📌 <b>{self.title}</b>

{self.description}

🎯 <b>Önerilecek Aksiyon:</b>
<i>{self.action}</i>

⏱️ <b>Zaman:</b> <code>{self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>
        '''

@dataclass
class RiskNotification:
    """Risk notification data"""
    title: str
    description: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommendation: str
    timestamp: datetime
    
    def to_html(self) -> str:
        """Convert to HTML formatted message"""
        emoji = '🟢' if self.risk_level == 'LOW' else '🟡' if self.risk_level == 'MEDIUM' else '🔴' if self.risk_level == 'HIGH' else '🚨'
        
        return f'''
{emoji} <b>RİSK UYARISI</b>

📌 <b>{self.title}</b>

{self.description}

💾 <b>Tavsiye:</b>
<i>{self.recommendation}</i>

⏱️ <b>Zaman:</b> <code>{self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>
        '''

@dataclass
class TradeTrackingNotification:
    """Trade tracking notification data"""
    symbol: str
    trade_type: str  # LONG, SHORT
    entry_price: float
    current_price: float
    pnl_percent: float
    status: str  # IN_PROFIT, IN_LOSS, BREAKEVEN, CLOSED
    timestamp: datetime
    
    def to_html(self) -> str:
        """Convert to HTML formatted message"""
        pnl_emoji = '📈' if self.pnl_percent >= 0 else '📉'
        status_emoji = '✅' if self.status == 'IN_PROFIT' else '🔴' if self.status == 'IN_LOSS' else '⚪'
        
        return f'''
📊 <b>AÇIK İŞLEM TAKIP</b>

📍 <b>{self.symbol}</b> {self.trade_type}
💰 <b>Entry:</b> <code>${self.entry_price:.2f}</code>
📈 <b>Current:</b> <code>${self.current_price:.2f}</code>
{pnl_emoji} <b>P&L:</b> <b>{self.pnl_percent:+.2f}%</b>
{status_emoji} <b>Status:</b> <b>{self.status}</b>

⏱️ <b>Zaman:</b> <code>{self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>
        '''

# ============================================================================
# ASYNC TELEGRAM API CLIENT
# ============================================================================

class TelegramAPIClient:
    """Async HTTP client for Telegram Bot API"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f'https://api.telegram.org/bot{token}'
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def init_session(self):
        """Initialize async HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ Telegram API client session initialized")
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("✅ Telegram API client session closed")
    
    async def send_message(self, text: str, parse_mode: str = 'HTML',
                          disable_web_page_preview: bool = True) -> bool:
        """Send message to Telegram chat"""
        try:
            await self.init_session()
            
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': disable_web_page_preview
            }
            
            async with self.session.post(
                f'{self.base_url}/sendMessage',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    logger.info("✅ Telegram message sent")
                    return True
                else:
                    logger.error(f"❌ Telegram API error: {response.status}")
                    return False
        
        except asyncio.TimeoutError:
            logger.error("❌ Telegram send timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
    
    async def send_message_with_retry(self, text: str, retries: int = 3,
                                     backoff: float = 2.0) -> bool:
        """Send message with exponential backoff retry"""
        for attempt in range(retries):
            try:
                result = await self.send_message(text)
                if result:
                    return True
            except Exception as e:
                logger.error(f"❌ Retry {attempt + 1}/{retries} failed: {e}")
            
            if attempt < retries - 1:
                wait_time = backoff ** attempt
                logger.info(f"⏰ Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
        
        return False

# ============================================================================
# NOTIFICATION QUEUE & PROCESSING
# ============================================================================

class NotificationQueue:
    """Async queue for notifications"""
    
    def __init__(self, max_size: int = 1000):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.processed = 0
        self.failed = 0
    
    async def put(self, notification: Dict):
        """Put notification in queue"""
        try:
            await self.queue.put(notification)
            logger.debug(f"📤 Notification queued (size: {self.queue.qsize()})")
        except asyncio.QueueFull:
            logger.error("❌ Notification queue full")
    
    async def get(self) -> Optional[Dict]:
        """Get notification from queue"""
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    def size(self) -> int:
        """Get queue size"""
        return self.queue.qsize()
    
    def stats(self) -> Dict:
        """Get queue statistics"""
        return {
            'size': self.queue.qsize(),
            'processed': self.processed,
            'failed': self.failed,
            'success_rate': self.processed / (self.processed + self.failed) * 100 if (self.processed + self.failed) > 0 else 0
        }

# ============================================================================
# TELEGRAM NOTIFICATION ENGINE
# ============================================================================

class TelegramNotificationEngine:
    """Main Telegram notification engine (async)"""
    
    def __init__(self, token: str, chat_id: str, worker_count: int = 3):
        self.token = token
        self.chat_id = chat_id
        self.api_client = TelegramAPIClient(token, chat_id)
        self.queue = NotificationQueue()
        self.worker_count = worker_count
        self.workers = []
        self.running = False
    
    async def start(self):
        """Start notification engine"""
        logger.info(f"🚀 Starting Telegram notification engine with {self.worker_count} workers...")
        
        await self.api_client.init_session()
        self.running = True
        
        # Start worker tasks
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
        
        logger.info("✅ Telegram notification engine started")
    
    async def stop(self):
        """Stop notification engine"""
        logger.info("🛑 Stopping Telegram notification engine...")
        self.running = False
        
        # Wait for all workers
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Close API session
        await self.api_client.close_session()
        
        logger.info(f"✅ Engine stopped. Stats: {self.queue.stats()}")
    
    async def _worker(self, worker_id: int):
        """Worker task for processing notifications"""
        logger.info(f"👷 Worker {worker_id} started")
        
        while self.running:
            try:
                notification = await self.queue.get()
                
                if notification is None:
                    continue
                
                # Send notification
                success = await self.api_client.send_message_with_retry(
                    text=notification['html'],
                    retries=3
                )
                
                if success:
                    self.queue.processed += 1
                    logger.info(f"✅ Notification processed by worker {worker_id}")
                else:
                    self.queue.failed += 1
                    logger.error(f"❌ Notification failed by worker {worker_id}")
            
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"👋 Worker {worker_id} stopped")
    
    async def queue_signal(self, signal_data: Dict):
        """Queue signal notification"""
        notification = SignalNotification(
            symbol=signal_data['symbol'],
            signal_type=signal_data['signal_type'],
            confidence=signal_data['confidence'],
            entry_price=signal_data['entry_price'],
            tp1=signal_data['tp1'],
            tp2=signal_data['tp2'],
            tp3=signal_data['tp3'],
            sl=signal_data['sl'],
            layer_scores=signal_data['layer_scores'],
            reason=signal_data.get('reason', 'AI-generated signal'),
            timestamp=datetime.now(pytz.UTC)
        )
        
        await self.queue.put({
            'type': NotificationType.SIGNAL.value,
            'html': notification.to_html(),
            'data': asdict(notification)
        })
    
    async def queue_opportunity(self, title: str, description: str, action: str,
                               urgency: str = 'MEDIUM'):
        """Queue opportunity notification"""
        notification = OpportunityNotification(
            title=title,
            description=description,
            action=action,
            urgency=urgency,
            timestamp=datetime.now(pytz.UTC)
        )
        
        await self.queue.put({
            'type': NotificationType.OPPORTUNITY.value,
            'html': notification.to_html(),
            'data': asdict(notification)
        })
    
    async def queue_risk(self, title: str, description: str, risk_level: str,
                        recommendation: str):
        """Queue risk notification"""
        notification = RiskNotification(
            title=title,
            description=description,
            risk_level=risk_level,
            recommendation=recommendation,
            timestamp=datetime.now(pytz.UTC)
        )
        
        await self.queue.put({
            'type': NotificationType.RISK.value,
            'html': notification.to_html(),
            'data': asdict(notification)
        })
    
    async def queue_trade_tracking(self, symbol: str, trade_type: str,
                                  entry_price: float, current_price: float):
        """Queue trade tracking notification"""
        pnl_percent = (current_price - entry_price) / entry_price * 100
        
        if pnl_percent > 0:
            status = 'IN_PROFIT'
        elif pnl_percent < 0:
            status = 'IN_LOSS'
        else:
            status = 'BREAKEVEN'
        
        notification = TradeTrackingNotification(
            symbol=symbol,
            trade_type=trade_type,
            entry_price=entry_price,
            current_price=current_price,
            pnl_percent=pnl_percent,
            status=status,
            timestamp=datetime.now(pytz.UTC)
        )
        
        await self.queue.put({
            'type': NotificationType.TRADE_TRACKING.value,
            'html': notification.to_html(),
            'data': asdict(notification)
        })
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'running': self.running,
            'queue_size': self.queue.size(),
            'queue_stats': self.queue.stats(),
            'worker_count': self.worker_count,
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }

# ============================================================================
# USAGE EXAMPLE & MAIN ENTRY
# ============================================================================

async def main_example():
    """Example usage"""
    engine = TelegramNotificationEngine(
        token=os.getenv('TELEGRAM_TOKEN'),
        chat_id=os.getenv('TELEGRAM_CHAT_ID'),
        worker_count=3
    )
    
    await engine.start()
    
    # Queue example signal
    await engine.queue_signal({
        'symbol': 'BTCUSDT',
        'signal_type': 'LONG',
        'confidence': 85,
        'entry_price': 97234.50,
        'tp1': 98500.00,
        'tp2': 99800.00,
        'tp3': 101000.00,
        'sl': 96500.00,
        'layer_scores': {
            'technical': 0.82,
            'ml': 0.88,
            'sentiment': 0.79,
            'onchain': 0.85
        },
        'reason': 'Strong bullish momentum + Whale accumulation'
    })
    
    # Wait for processing
    await asyncio.sleep(5)
    
    await engine.stop()

if __name__ == '__main__':
    asyncio.run(main_example())
