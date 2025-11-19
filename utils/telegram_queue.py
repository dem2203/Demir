# utils/telegram_queue.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 DEMIR AI v7.0 - TELEGRAM QUEUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TELEGRAM MESSAGE QUEUE MANAGEMENT

Features:
    ✅ Thread-safe message queue
    ✅ Priority message handling
    ✅ Rate limiting support
    ✅ Batch sending capability

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

# ============================================================================
# TELEGRAM QUEUE
# ============================================================================

class TelegramQueue:
    """
    Thread-safe Telegram message queue
    
    Features:
        - FIFO message queue
        - Priority handling
        - Rate limiting awareness
        - Batch operations
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize Telegram queue
        
        Args:
            max_size: Maximum queue size
        """
        self.queue = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.stats = {
            'total_added': 0,
            'total_sent': 0,
            'total_failed': 0
        }
        
        logger.info(f"✅ TelegramQueue initialized (max_size: {max_size})")
    
    def add(self, message: str, priority: str = 'normal', metadata: Optional[Dict[str, Any]] = None):
        """
        Add message to queue
        
        Args:
            message: Message text
            priority: 'high', 'normal', 'low'
            metadata: Additional message metadata
        """
        with self.lock:
            message_obj = {
                'message': message,
                'priority': priority,
                'metadata': metadata or {},
                'timestamp': datetime.now(),
                'attempts': 0
            }
            
            # High priority: add to front
            if priority == 'high':
                self.queue.appendleft(message_obj)
            # Normal/low priority: add to back
            else:
                self.queue.append(message_obj)
            
            self.stats['total_added'] += 1
            
            logger.debug(f"📱 Added to queue ({priority}): {message[:50]}...")
    
    def get(self) -> Optional[Dict[str, Any]]:
        """
        Get next message from queue
        
        Returns:
            Message object or None if empty
        """
        with self.lock:
            if len(self.queue) > 0:
                return self.queue.popleft()
            return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all messages and clear queue
        
        Returns:
            List of message objects
        """
        with self.lock:
            messages = list(self.queue)
            self.queue.clear()
            return messages
    
    def get_batch(self, batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get batch of messages
        
        Args:
            batch_size: Number of messages to get
        
        Returns:
            List of message objects
        """
        with self.lock:
            messages = []
            for _ in range(min(batch_size, len(self.queue))):
                if len(self.queue) > 0:
                    messages.append(self.queue.popleft())
            return messages
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """
        Peek at next message without removing
        
        Returns:
            Message object or None
        """
        with self.lock:
            if len(self.queue) > 0:
                return self.queue[0]
            return None
    
    def size(self) -> int:
        """Get current queue size"""
        with self.lock:
            return len(self.queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size() == 0
    
    def clear(self):
        """Clear all messages"""
        with self.lock:
            self.queue.clear()
            logger.info("🗑️ Queue cleared")
    
    def mark_sent(self):
        """Mark message as successfully sent"""
        self.stats['total_sent'] += 1
    
    def mark_failed(self):
        """Mark message as failed"""
        self.stats['total_failed'] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'current_size': len(self.queue),
                'total_added': self.stats['total_added'],
                'total_sent': self.stats['total_sent'],
                'total_failed': self.stats['total_failed'],
                'success_rate': (
                    self.stats['total_sent'] / 
                    max(self.stats['total_added'], 1) * 100
                )
            }
