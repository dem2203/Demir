# main.py - PRODUCTION READY

import asyncio
import logging
from utils.base_layer import BaseLayer
from utils.multi_api_orchestrator import MultiAPIOrchestrator
from consciousness.root_cause_analyzer import RootCauseAnalyzer
from learning.model_drift_detector import ModelDriftDetector
from telegram.advanced_telegram_manager import AdvancedTelegramManager
from database.persistence_layer import PersistenceLayer
from utils.unified_logger import UnifiedLogger

logger = logging.getLogger(__name__)


class DemerAIBot:
    """Main orchestrator for Demir AI"""
    
    def __init__(self):
        self.logger = UnifiedLogger('DemerAI')
        self.api_orchestrator = MultiAPIOrchestrator()
        self.consciousness = RootCauseAnalyzer()
        self.model_drift_detector = ModelDriftDetector()
        self.telegram = AdvancedTelegramManager(
            os.getenv('TELEGRAM_TOKEN'),
            os.getenv('TELEGRAM_CHAT_ID')
        )
        self.db = PersistenceLayer()
    
    async def start_trading_cycle(self):
        """Main trading loop"""
        
        while True:
            try:
                # 1. Get real prices from all sources
                prices = await self.api_orchestrator.get_portfolio_prices(
                    ['BTC', 'ETH', 'SOL', 'ADA']
                )
                
                # 2. Run analysis (all 100+ layers)
                signals = await self.analyze_signals(prices)
                
                # 3. Check model drift
                drift = self.model_drift_detector.detect_drift(self.metrics)
                
                # 4. Execute trades
                for signal in signals:
                    if signal['valid']:
                        trade = await self.execute_trade(signal)
                        await self.db.save_trade(trade)
                
                # 5. Send Telegram alert
                await self.telegram.send_signal_with_buttons(signal)
                
                # 6. Sleep
                await asyncio.sleep(300)  # 5 minutes
            
            except Exception as e:
                self.logger.log_error(f"Trading cycle error: {e}")
                await asyncio.sleep(60)

async def main():
    bot = DemerAIBot()
    await bot.start_trading_cycle()

if __name__ == '__main__':
    asyncio.run(main())
