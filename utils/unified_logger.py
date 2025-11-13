"""
UNIFIED LOGGER SYSTEM
Merkezi logging - console, file, Telegram, database

⚠️ REAL DATA: Gerçek log entries - hiç mock data
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict
import asyncio

class UnifiedLogger:
    """
    Merkezi logging sistemi
    Tüm sistemin log'larını topla ve yönet
    """
    
    def __init__(self, app_name: str = 'DemerAI'):
        self.app_name = app_name
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 2. File handler (rotating)
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f'{app_name}_{datetime.now().strftime("%Y%m%d")}.log'),
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 3. Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log'),
            maxBytes=20*1024*1024,  # 20MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def log_info(self, message: str, extra: Dict = None):
        """Info log"""
        if extra:
            message = f"{message} | {extra}"
        self.logger.info(message)
    
    def log_warning(self, message: str, extra: Dict = None):
        """Warning log"""
        if extra:
            message = f"{message} | {extra}"
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Exception = None):
        """Error log"""
        if error:
            message = f"{message} - {str(error)}"
        self.logger.error(message)
    
    def log_critical(self, message: str):
        """Critical log"""
        self.logger.critical(f"🚨 {message}")
    
    def get_logs(self, level: str = 'INFO', limit: int = 100) -> List[str]:
        """
        Son log'ları al
        
        Args:
            level: INFO, WARNING, ERROR, CRITICAL
            limit: Kaç log
        
        Returns:
            List of log entries
        """
        
        log_file = f'logs/DemerAI_{datetime.now().strftime("%Y%m%d")}.log'
        
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            filtered = [l for l in lines if level in l]
            return filtered[-limit:]
        
        except Exception as e:
            self.logger.error(f"Failed to read logs: {e}")
            return []
