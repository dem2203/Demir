"""
DEMIR AI BOT - Logger Setup
Centralized professional logging configuration
Production-grade logging with structured output
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    json_format: bool = True
) -> logging.Logger:
    """
    Setup a logger with console and optional file handlers.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
        json_format: Whether to use JSON formatting

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "demir_ai") -> logging.Logger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logger(
            name,
            level=logging.INFO,
            log_file="logs/demir_ai.log",
            json_format=True
        )
    return _logger


def setup_all_loggers():
    """Setup loggers for all modules."""
    module_names = [
        "data_detector",
        "real_data_verifier",
        "signal_validator",
        "layer_optimizer",
        "api_health_monitor",
        "response_cache",
        "circuit_breaker",
        "backtest_engine",
        "ml_trainer",
        "trading_executor",
        "database_manager",
        "signal_engine"
    ]

    loggers = {}
    for name in module_names:
        loggers[name] = get_logger(name)

    return loggers


if __name__ == "__main__":
    logger = get_logger()
    logger.info("Logger setup test")
    logger.warning("Warning test")
    logger.error("Error test")
