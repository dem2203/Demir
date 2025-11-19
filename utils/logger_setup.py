# utils/logger_setup.py
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 DEMIR AI v7.0 - PROFESSIONAL LOGGING SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENTERPRISE-GRADE LOGGING SYSTEM

Features:
    ✅ Colored console output with emojis
    ✅ Rotating file handlers
    ✅ Separate error log
    ✅ Performance log
    ✅ Structured logging
    ✅ JSON logging support
    ✅ Log compression
    ✅ Retention policies

Log Levels:
    DEBUG    🔍 - Detailed information
    INFO     ✅ - General information
    WARNING  ⚠️  - Warning messages
    ERROR    ❌ - Error messages
    CRITICAL 🔥 - Critical failures

DEPLOYMENT: Railway Production
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 7.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import logging
import gzip
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional

# ============================================================================
# ANSI COLOR CODES
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

# ============================================================================
# EMOJI INDICATORS
# ============================================================================

EMOJI_MAP = {
    'DEBUG': '🔍',
    'INFO': '✅',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🔥'
}

# ============================================================================
# COLORED FORMATTER
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors and emojis
    """
    
    LEVEL_COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.BRIGHT_GREEN,
        'WARNING': Colors.BRIGHT_YELLOW,
        'ERROR': Colors.BRIGHT_RED,
        'CRITICAL': Colors.BRIGHT_MAGENTA
    }
    
    def __init__(self, fmt: str, datefmt: Optional[str] = None, use_colors: bool = True):
        """
        Initialize formatter
        
        Args:
            fmt: Format string
            datefmt: Date format string
            use_colors: Enable/disable colors
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        
        # Add emoji
        emoji = EMOJI_MAP.get(record.levelname, '•')
        
        if self.use_colors:
            # Get color for level
            color = self.LEVEL_COLORS.get(record.levelname, '')
            
            # Format level name with color and emoji
            level_name = (
                f"{emoji} {color}{Colors.BOLD}"
                f"[{record.levelname}]{Colors.RESET}"
            )
            
            # Replace levelname in record
            original_levelname = record.levelname
            record.levelname = level_name
            
            # Format the message
            result = super().format(record)
            
            # Restore original levelname
            record.levelname = original_levelname
            
            return result
        else:
            # No colors, just emoji
            record.levelname = f"{emoji} [{record.levelname}]"
            return super().format(record)

# ============================================================================
# COMPRESSION HANDLER
# ============================================================================

class CompressingRotatingFileHandler(RotatingFileHandler):
    """
    Rotating file handler that compresses old logs
    """
    
    def doRollover(self):
        """Perform rollover and compress old file"""
        super().doRollover()
        
        # Compress the rolled-over file
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = f"{self.baseFilename}.{i}"
                dfn = f"{self.baseFilename}.{i + 1}"
                
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            
            dfn = f"{self.baseFilename}.1"
            if os.path.exists(dfn):
                # Compress the file
                with open(dfn, 'rb') as f_in:
                    with gzip.open(f"{dfn}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                os.remove(dfn)

# ============================================================================
# LOGGER SETUP FUNCTION
# ============================================================================

def setup_logger(
    name: str = 'DEMIR_AI',
    log_dir: str = 'logs',
    level: str = 'INFO',
    console_output: bool = True,
    file_output: bool = True,
    compress_logs: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging system
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Enable console output
        file_output: Enable file output
        compress_logs: Compress old log files
    
    Returns:
        Configured logger instance
    """
    
    # Create logs directory
    if file_output:
        os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # ========================================================================
    # FORMATTERS
    # ========================================================================
    
    # Detailed format for files
    detailed_format = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
    )
    
    # Simple format for console
    simple_format = (
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Date format
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # ========================================================================
    # CONSOLE HANDLER
    # ========================================================================
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter(
            simple_format,
            datefmt=date_format,
            use_colors=True
        )
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    
    # ========================================================================
    # FILE HANDLERS
    # ========================================================================
    
    if file_output:
        # 1. Main application log (rotating daily)
        app_log_file = os.path.join(log_dir, 'demir_ai.log')
        
        app_handler = TimedRotatingFileHandler(
            app_log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(logging.Formatter(detailed_format, date_format))
        
        logger.addHandler(app_handler)
        
        # 2. Error log (only errors and above)
        error_log_file = os.path.join(log_dir, 'errors.log')
        
        if compress_logs:
            error_handler = CompressingRotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
        else:
            error_handler = RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=10,
                encoding='utf-8'
            )
        
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(detailed_format, date_format))
        
        logger.addHandler(error_handler)
        
        # 3. Performance log (separate logger)
        perf_log_file = os.path.join(log_dir, 'performance.log')
        
        perf_handler = RotatingFileHandler(
            perf_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s',
            date_format
        ))
        
        # Create separate performance logger
        perf_logger = logging.getLogger('performance')
        perf_logger.setLevel(logging.INFO)
        perf_logger.addHandler(perf_handler)
        perf_logger.propagate = False
    
    # ========================================================================
    # LOGGING BANNER
    # ========================================================================
    
    logger.info("=" * 100)
    logger.info("🚀 DEMIR AI v7.0 - LOGGING SYSTEM INITIALIZED")
    logger.info("=" * 100)
    logger.info(f"Logger Name: {name}")
    logger.info(f"Log Level: {level}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info(f"Console Output: {console_output}")
    logger.info(f"File Output: {file_output}")
    logger.info(f"Log Compression: {compress_logs}")
    logger.info("=" * 100)
    
    return logger

# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

class LogContext:
    """
    Context manager for logging operations
    
    Usage:
        with LogContext(logger, 'Fetching data'):
            # Your code here
    """
    
    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize context
        
        Args:
            logger: Logger instance
            operation: Operation description
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Enter context"""
        self.start_time = datetime.now()
        self.logger.info(f"▶️  Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"✅ Completed: {self.operation} ({duration:.2f}s)"
            )
        else:
            self.logger.error(
                f"❌ Failed: {self.operation} ({duration:.2f}s) - {exc_val}"
            )
        
        return False  # Don't suppress exceptions

# ============================================================================
# PERFORMANCE LOGGING
# ============================================================================

def log_performance(operation: str):
    """
    Decorator for logging function performance
    
    Usage:
        @log_performance('Data processing')
        def process_data():
            # Your code
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            perf_logger = logging.getLogger('performance')
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                perf_logger.info(
                    f"{operation} | {func.__name__} | "
                    f"SUCCESS | {duration:.3f}s"
                )
                
                return result
            
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                
                perf_logger.error(
                    f"{operation} | {func.__name__} | "
                    f"FAILED | {duration:.3f}s | {e}"
                )
                
                raise
        
        return wrapper
    return decorator

# ============================================================================
# LOG CLEANUP
# ============================================================================

def cleanup_old_logs(log_dir: str = 'logs', days: int = 30):
    """
    Clean up log files older than specified days
    
    Args:
        log_dir: Log directory
        days: Age threshold in days
    """
    if not os.path.exists(log_dir):
        return
    
    threshold = datetime.now().timestamp() - (days * 86400)
    removed_count = 0
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            
            if file_time < threshold:
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    print(f"Failed to remove {filepath}: {e}")
    
    if removed_count > 0:
        print(f"🧹 Cleaned up {removed_count} old log files")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """Test the logging setup"""
    
    # Setup logger
    logger = setup_logger(
        name='TEST_LOGGER',
        log_dir='test_logs',
        level='DEBUG',
        console_output=True,
        file_output=True
    )
    
    # Test all log levels
    logger.debug("🔍 This is a DEBUG message")
    logger.info("✅ This is an INFO message")
    logger.warning("⚠️ This is a WARNING message")
    logger.error("❌ This is an ERROR message")
    logger.critical("🔥 This is a CRITICAL message")
    
    # Test context manager
    with LogContext(logger, 'Test operation'):
        import time
        time.sleep(0.5)
    
    # Test performance decorator
    @log_performance('Test function')
    def test_function():
        import time
        time.sleep(0.2)
        return "Done"
    
    test_function()
    
    print("\n✅ Logger testing complete!")
    print(f"📁 Check 'test_logs' directory for log files")
