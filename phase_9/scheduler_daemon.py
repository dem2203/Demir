"""
⏰ PHASE 9.1 - SCHEDULER DAEMON (HYBRID MODE)
==============================================

Path: phase_9/scheduler_daemon.py
Date: 7 Kasım 2025, 15:48 CET

Autonomous scheduler that runs AI analysis every 5 minutes
Stays alive in background, sends alerts when signal changes
User makes FINAL decision before trading
"""

import time
import threading
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase_9/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HybridScheduler:
    """Autonomous 7/24 scheduler with hybrid control"""
    
    def __init__(self, analysis_interval_minutes=5):
        """
        Initialize scheduler
        
        Args:
            analysis_interval_minutes: Run analysis every N minutes
        """
        self.interval = analysis_interval_minutes
        self.running = False
        self.thread = None
        self.analysis_history = []
        self.last_signal = None
        self.last_score = None
        self.alert_threshold = 5  # Alert if score changes by 5+
        
        logger.info(f"✅ Hybrid Scheduler initialized (interval: {self.interval}m)")
    
    def start(self):
        """Start background daemon thread"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self.thread.start()
        
        logger.info("🚀 Scheduler daemon started (7/24)")
    
    def stop(self):
        """Stop background daemon"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("⛔ Scheduler daemon stopped")
    
    def _daemon_loop(self):
        """Main loop that runs forever"""
        logger.info("📡 Entering daemon mode...")
        
        if SCHEDULE_AVAILABLE:
            schedule.every(self.interval).minutes.do(self._run_analysis)
            
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        else:
            # Fallback: manual timer
            while self.running:
                self._run_analysis()
                time.sleep(self.interval * 60)
    
    def _run_analysis(self):
        """Execute AI brain analysis"""
        try:
            from ai_brain import analyze_with_ai_brain
            
            timestamp = datetime.now()
            logger.info(f"🔄 Running analysis at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Run analysis
            result = analyze_with_ai_brain('BTCUSDT', '1h')
            
            # Extract key info
            score = result.get('final_score')
            signal = result.get('signal')
            confidence = result.get('confidence')
            
            # Store in history
            analysis_record = {
                'timestamp': timestamp.isoformat(),
                'score': score,
                'signal': signal,
                'confidence': confidence,
                'layers': result.get('layers')
            }
            
            self.analysis_history.append(analysis_record)
            
            # Check if alert needed
            self._check_alert(score, signal)
            
            # Update state
            self.last_score = score
            self.last_signal = signal
            
            logger.info(f"✅ Score: {score} | Signal: {signal} | Confidence: {confidence}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return None
    
    def _check_alert(self, new_score: float, new_signal: str):
        """
        Check if alert should be triggered
        
        Triggers alert when:
        - Signal changes (LONG→NEUTRAL, etc.)
        - Score significantly changes (±5 points)
        - Confidence is HIGH
        """
        should_alert = False
        reason = ""
        
        # Signal change
        if self.last_signal and self.last_signal != new_signal:
            should_alert = True
            reason = f"Signal changed: {self.last_signal} → {new_signal}"
        
        # Score jump
        if self.last_score and abs(new_score - self.last_score) >= self.alert_threshold:
            should_alert = True
            reason = f"Score jump: {self.last_score:.1f} → {new_score:.1f}"
        
        if should_alert:
            self._trigger_alert(new_score, new_signal, reason)
    
    def _trigger_alert(self, score: float, signal: str, reason: str):
        """Trigger alert via multiple channels"""
        from alert_system import AlertSystem
        
        alerts = AlertSystem()
        
        message = f"""
        🚨 HYBRID ALERT - Decision Required!
        
        ⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        📊 Score: {score:.1f}/100
        🎯 Signal: {signal}
        💡 Reason: {reason}
        
        👤 ACTION REQUIRED: Check dashboard and confirm entry/exit
        """
        
        alerts.send_email(message)
        alerts.send_sms(f"Score {score:.1f} {signal} - Check dashboard")
        
        logger.warning(f"🔔 ALERT SENT: {reason}")
    
    def get_status(self) -> Dict:
        """Get current daemon status"""
        return {
            'running': self.running,
            'interval': self.interval,
            'total_analyses': len(self.analysis_history),
            'last_score': self.last_score,
            'last_signal': self.last_signal,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_history(self, hours=24) -> List[Dict]:
        """Get analysis history from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [
            record for record in self.analysis_history
            if datetime.fromisoformat(record['timestamp']) > cutoff
        ]


# ============================================================================
# PHASE 9 DAEMON STARTER
# ============================================================================

if __name__ == "__main__":
    import sys
    
    scheduler = HybridScheduler(analysis_interval_minutes=5)
    
    try:
        scheduler.start()
        print("\n✅ HYBRID DAEMON RUNNING!")
        print("📊 Analysis every 5 minutes")
        print("🔔 Alerts on signal change / score jump")
        print("👤 You decide: Check alerts → Confirm trades")
        print("\nPress Ctrl+C to stop...\n")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⛔ Stopping daemon...")
        scheduler.stop()
        sys.exit(0)
