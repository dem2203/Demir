# Demir/main.py

import asyncio
from consciousness.consciousness_engine import ConsciousnessEngine
from daemon.daemon_core import ContinuousMonitorDaemon
from recovery.disaster_recovery import DisasterRecoveryEngine
from watchdog.watchdog import SystemWatchdog
import os

async def main():
    config = {
        'BINANCE_API_KEY': os.getenv('BINANCE_API_KEY'),
        'BINANCE_API_SECRET': os.getenv('BINANCE_API_SECRET'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    }
    
    # Initialize all components
    consciousness = ConsciousnessEngine(config)
    daemon = ContinuousMonitorDaemon(config)
    watchdog = SystemWatchdog(config)
    
    # Start daemon (24/7 loop)
    await daemon.start()

if __name__ == "__main__":
    asyncio.run(main())
