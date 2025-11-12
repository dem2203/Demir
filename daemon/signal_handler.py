
import asyncio
import logging
import os
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

# ============================================================================
# SETUP LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 1-7 IMPORTS
# ============================================================================

# PHASE 1: Telegram
try:
    from telegram_alerts_advanced import TelegramAlertsAdvanced
    from telegram_message_templates import TelegramMessageTemplates
    phase1_ok = True
except Exception as e:
    logger.warning(f"Phase 1 import failed: {e}")
    phase1_ok = False

# PHASE 2: Performance Analytics
try:
    from performance_analyzer import PerformanceAnalyzer
    phase2_ok = True
except Exception as e:
    logger.warning(f"Phase 2 import failed: {e}")
    phase2_ok = False

# PHASE 3: Opportunity Scanner
try:
    from pattern_recognition import PatternRecognizer
    from whale_detector import WhaleDetector
    phase3_ok = True
except Exception as e:
    logger.warning(f"Phase 3 import failed: {e}")
    phase3_ok = False

# PHASE 4: Backtesting
try:
    from backtest_engine import BacktestEngine
    phase4_ok = True
except Exception as e:
    logger.warning(f"Phase 4 import failed: {e}")
    phase4_ok = False

# PHASE 5: Multi-Exchange
try:
    from exchange_integrations import get_connector
    from arbitrage_scanner import ArbitrageScanner
    phase5_ok = True
except Exception as e:
    logger.warning(f"Phase 5 import failed: {e}")
    phase5_ok = False

# PHASE 6: Auto-Trading
try:
    from auto_trader import AutoTrader
    from order_manager import OrderManager
    from position_calculator import PositionCalculator
    phase6_ok = True
except Exception as e:
    logger.warning(f"Phase 6 import failed: {e}")
    phase6_ok = False

# PHASE 7: Advanced Analytics
try:
    from advanced_analytics import AdvancedAnalytics
    from ml_model_trainer import MLModelTrainer
    from correlation_analyzer import CorrelationAnalyzer
    phase7_ok = True
except Exception as e:
    logger.warning(f"Phase 7 import failed: {e}")
    phase7_ok = False

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Signal:
    """AI Trading Signal"""
    symbol: str
    direction: str  # LONG, SHORT
    confidence: float  # 0-100
    entry_price: float
    take_profit: float
    stop_loss: float
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "AI_BRAIN"
    signal_id: str = field(default_factory=str)

@dataclass
class TradeExecution:
    """Executed Trade Record"""
    signal_id: str
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    take_profit: float
    stop_loss: float
    status: str  # PENDING, EXECUTED, CLOSED
    timestamp: datetime = field(default_factory=datetime.now)
    pnl: float = 0.0

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class SignalOrchestrator:
    """
    Main signal orchestrator
    Coordinates all PHASE 1-7 features
    Runs 24/7 on Railway
    """
    
    def __init__(self):
        """Initialize orchestrator"""
        logger.info("=" * 80)
        logger.info("🤖 DEMIR AI SIGNAL ORCHESTRATOR - VERSION 3.0")
        logger.info("=" * 80)
        
        # Initialize components
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
        self.running = True
        self.pending_signals: List[Signal] = []
        self.executed_trades: List[TradeExecution] = []
        
        # PHASE 1: Telegram
        if phase1_ok:
            self.telegram_alerts = TelegramAlertsAdvanced()
            self.message_templates = TelegramMessageTemplates()
            logger.info("✅ PHASE 1: Telegram alerts initialized")
        
        # PHASE 2: Analytics
        if phase2_ok:
            self.performance_analyzer = PerformanceAnalyzer()
            logger.info("✅ PHASE 2: Performance analytics initialized")
        
        # PHASE 3: Patterns & Whales
        if phase3_ok:
            self.pattern_recognizer = PatternRecognizer()
            self.whale_detector = WhaleDetector()
            logger.info("✅ PHASE 3: Pattern & whale detection initialized")
        
        # PHASE 4: Backtesting
        if phase4_ok:
            self.backtest_engine = BacktestEngine()
            logger.info("✅ PHASE 4: Backtesting engine initialized")
        
        # PHASE 5: Arbitrage
        if phase5_ok:
            self.arbitrage_scanner = ArbitrageScanner()
            logger.info("✅ PHASE 5: Arbitrage scanner initialized")
        
        # PHASE 6: Auto-Trading
        if phase6_ok:
            self.auto_trader = AutoTrader()
            self.order_manager = OrderManager()
            self.position_calculator = PositionCalculator()
            logger.info("✅ PHASE 6: Auto-trader & order manager initialized")
        
        # PHASE 7: Advanced Analytics
        if phase7_ok:
            self.advanced_analytics = AdvancedAnalytics()
            self.ml_trainer = MLModelTrainer()
            self.correlation_analyzer = CorrelationAnalyzer()
            logger.info("✅ PHASE 7: Advanced analytics & ML initialized")
        
        logger.info("=" * 80)
    
    async def start(self):
        """Start main event loop - 24/7 operation"""
        logger.info("🎬 Starting 24/7 signal orchestration...")
        logger.info("   Running all PHASE 1-7 loops concurrently")
        
        tasks = [
            self._hourly_reports(),
            self._opportunity_scanning(),
            self._performance_tracking(),
            self._arbitrage_monitoring(),
            self._position_management(),
            self._ml_training()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("⏹️ Orchestrator stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            self.running = False
    
    # ===== PHASE 1: TELEGRAM HOURLY REPORTS =====
    
    async def _hourly_reports(self):
        """PHASE 1: Send hourly Telegram reports"""
        if not phase1_ok:
            return
        
        logger.info("📊 Starting hourly report loop (PHASE 1)")
        
        while self.running:
            try:
                signal_data = {
                    'long_signals': len([s for s in self.pending_signals if s.direction == 'LONG']),
                    'short_signals': len([s for s in self.pending_signals if s.direction == 'SHORT']),
                    'avg_confidence': np.mean([s.confidence for s in self.pending_signals]) if self.pending_signals else 0,
                    'direction': 'LONG' if len([s for s in self.pending_signals if s.direction == 'LONG']) > 0 else 'NEUTRAL',
                    'confidence': max([s.confidence for s in self.pending_signals], default=0),
                }
                
                await self.telegram_alerts.send_hourly_report(signal_data)
                logger.info(f"✅ Hourly report sent - {signal_data['long_signals']} LONG, {signal_data['short_signals']} SHORT")
                
                await asyncio.sleep(3600)  # Every hour
            
            except Exception as e:
                logger.error(f"❌ Hourly report error: {e}")
                await asyncio.sleep(300)
    
    # ===== PHASE 2: PERFORMANCE TRACKING =====
    
    async def _performance_tracking(self):
        """PHASE 2: Track performance & generate suggestions"""
        if not phase2_ok:
            return
        
        logger.info("📈 Starting performance tracking loop (PHASE 2)")
        
        while self.running:
            try:
                stats = self.performance_analyzer.get_trade_statistics(days=7)
                accuracy = self.performance_analyzer.get_signal_accuracy(days=7)
                suggestions = self.performance_analyzer.get_improvement_suggestions()
                
                logger.info(f"📊 Stats: {stats.get('total_trades')} trades, {stats.get('win_rate_percent', 0):.1f}% win rate")
                logger.info(f"🎯 Accuracy: {accuracy.get('accuracy_percent', 0):.1f}%")
                
                if suggestions:
                    for sugg in suggestions:
                        logger.info(f"💡 {sugg}")
                
                await asyncio.sleep(3600)  # Every hour
            
            except Exception as e:
                logger.error(f"❌ Performance tracking error: {e}")
                await asyncio.sleep(300)
    
    # ===== PHASE 3: OPPORTUNITY SCANNING =====
    
    async def _opportunity_scanning(self):
        """PHASE 3: Scan for trading opportunities"""
        if not phase3_ok:
            return
        
        logger.info("🎯 Starting opportunity scanner loop (PHASE 3)")
        
        while self.running:
            try:
                for symbol in self.symbols:
                    # Detect patterns
                    h_s = await self.pattern_recognizer.detect_head_and_shoulders(symbol, '1h')
                    
                    if h_s.get('pattern_found'):
                        logger.warning(f"🎯 Pattern found: {symbol} {h_s.get('type')}")
                        await self.telegram_alerts.send_urgent_opportunity_alert(
                            symbol, 'LONG', h_s.get('confidence', 0)
                        )
                    
                    # Detect whales
                    whales = await self.whale_detector.detect_large_transactions(symbol)
                    
                    if whales.get('large_buys', 0) > 0:
                        logger.warning(f"🐋 Whales detected: {symbol} - {whales.get('large_buys')} buys")
                    
                    await asyncio.sleep(0.5)
                
                await asyncio.sleep(600)  # Every 10 minutes
            
            except Exception as e:
                logger.error(f"❌ Scanning error: {e}")
                await asyncio.sleep(300)
    
    # ===== PHASE 5: ARBITRAGE MONITORING =====
    
    async def _arbitrage_monitoring(self):
        """PHASE 5: Monitor multi-exchange arbitrage"""
        if not phase5_ok:
            return
        
        logger.info("💱 Starting arbitrage monitor loop (PHASE 5)")
        
        while self.running:
            try:
                for symbol in self.symbols:
                    result = await self.arbitrage_scanner.scan_arbitrage(symbol)
                    
                    if result.get('opportunity'):
                        logger.warning(
                            f"💰 Arbitrage: {result['buy_exchange']} → {result['sell_exchange']} "
                            f"Profit: {result.get('profit_potential', 0):.2f}%"
                        )
                
                await asyncio.sleep(300)  # Every 5 minutes
            
            except Exception as e:
                logger.error(f"❌ Arbitrage error: {e}")
                await asyncio.sleep(300)
    
    # ===== PHASE 6: POSITION MANAGEMENT (24/7) =====
    
    async def _position_management(self):
        """PHASE 6: Monitor positions 24/7"""
        if not phase6_ok:
            return
        
        logger.info("📍 Starting position manager (24/7) (PHASE 6)")
        
        await self.order_manager.monitor_positions()
    
    # ===== PHASE 7: ML TRAINING =====
    
    async def _ml_training(self):
        """PHASE 7: Daily ML model retraining"""
        if not phase7_ok:
            return
        
        logger.info("🧠 Starting daily ML training loop (PHASE 7)")
        
        await self.ml_trainer.retrain_models_daily()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for Railway"""
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 15 + "🤖 DEMIR AI TRADING BOT - LIVE OPERATION" + " " * 22 + "║")
    logger.info("║" + " " * 20 + "Production Grade Signal Orchestrator" + " " * 21 + "║")
    logger.info("║" + " " * 25 + "Version 3.0 - November 12, 2025" + " " * 22 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    logger.info("")
    logger.info("PHASES INTEGRATION:")
    logger.info(f"  ✅ PHASE 1: Telegram Alerts & Templates ................ {'OK' if phase1_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 2: Performance Analytics ...................... {'OK' if phase2_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 3: Pattern Recognition & Whales .............. {'OK' if phase3_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 4: Backtesting Engine ........................ {'OK' if phase4_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 5: Multi-Exchange Arbitrage .................. {'OK' if phase5_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 6: Auto-Trader & Order Manager ............... {'OK' if phase6_ok else 'SKIP'}")
    logger.info(f"  ✅ PHASE 7: Advanced Analytics & ML ................... {'OK' if phase7_ok else 'SKIP'}")
    logger.info("")
    logger.info("OPERATION MODE: 🟢 LIVE TRADING 24/7")
    logger.info("")
    
    orchestrator = SignalOrchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    import numpy as np
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⏹️ Signal orchestrator stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
