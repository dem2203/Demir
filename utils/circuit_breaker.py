import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Stop trading
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """
    Circuit breaker pattern - prevents cascading failures
    Pauses trading if error rate too high, auto-recovers
    """
    
    def __init__(self, 
                 failure_threshold: float = 0.1,  # 10% error rate
                 recovery_timeout: int = 60):      # 60 sec recovery
        
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
    
    def record_success(self):
        """Record successful trade"""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            logger.info("✅ Circuit recovered - resuming trading")
            self.state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record failed trade"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        error_rate = self.failure_count / (self.failure_count + self.success_count + 1)
        
        if error_rate > self.failure_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        """Open circuit - stop trading"""
        if self.state != CircuitState.OPEN:
            logger.critical("🚨 CIRCUIT BREAKER OPEN - TRADING PAUSED")
            logger.critical(f"Error rate exceeded {self.failure_threshold*100:.0f}%")
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()
    
    def check_recovery(self) -> bool:
        """Check if circuit should recover"""
        if self.state == CircuitState.OPEN:
            time_elapsed = (datetime.now() - self.opened_at).total_seconds()
            
            if time_elapsed > self.recovery_timeout:
                logger.info("🔄 Testing circuit recovery...")
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
                self.success_count = 0
                return True
        
        return False
    
    def can_trade(self) -> bool:
        """Check if trading is allowed"""
        self.check_recovery()
        
        if self.state == CircuitState.OPEN:
            logger.warning("⚠️ Trading paused (circuit open)")
            return False
        
        return True
