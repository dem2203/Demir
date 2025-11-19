# utils/telegram_queue.py
"""Telegram queue"""

class TelegramQueue:
    """Simple queue placeholder"""
    def __init__(self):
        self.messages = []
    
    def add(self, message):
        self.messages.append(message)
    
    def get(self):
        return self.messages.pop(0) if self.messages else None
    
    def is_empty(self):
        return len(self.messages) == 0

# Alias (compatibility)
TelegramAlertQueue = TelegramQueue

__all__ = ['TelegramQueue', 'TelegramAlertQueue']
