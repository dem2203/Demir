cat > health_monitor.py << 'EOF'
import os
import time
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, env):
        self.env = env
        
    def start_monitoring(self, interval):
        logger.info("🔍 Health Monitor started")
        while True:
            try:
                # Check main.py
                result = subprocess.run(
                    ["pgrep", "-f", "main.py"],
                    capture_output=True
                )
                
                if result.returncode != 0:
                    logger.warning("⚠️ main.py restarting...")
                    subprocess.Popen([
                        "python", "main.py",
                        "--mode=production"
                    ], env=self.env)
                else:
                    logger.info("✅ System healthy")
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    m = HealthMonitor(dict(os.environ))
    m.start_monitoring(60)
EOF

# Verify
ls -la health_monitor.py
