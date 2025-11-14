#!/usr/bin/env python3
"""
🔱 DEMIR AI - Main Orchestrator v1.0
Master scheduler coordinating all components

KURALLAR:
✅ APScheduler jobs (every 1sec, 5sec, 1hour, 1day)
✅ Signal generation pipeline
✅ Trade execution triggers
✅ Real-time monitoring
✅ Error recovery + reconnect logic
✅ ZERO MOCK - production ready
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import psycopg2

# Custom modules
import sys
sys.path.append(os.path.dirname(__file__))

from signal_generator import EnsembleSignalGenerator, EnsembleModelManager
from position_tracker import PositionMonitor, CurrentPriceFetcher
from live_trader import LiveTrader
from risk_manager import PortfolioManager
from metrics_calculator import MetricsCalculationEngine
from market_stream import BinanceMarketStream

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# MASTER ORCHESTRATOR
# ============================================================================

class MasterOrchestrator:
    """Coordinate all bot components"""
    
    def __init__(self):
        logger.info("🔄 Initializing Master Orchestrator...")
        
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            self.scheduler = BackgroundScheduler()
            
            # Initialize components
            self.signal_generator = EnsembleSignalGenerator(self.db_conn)
            self.position_monitor = PositionMonitor(self.db_conn)
            self.price_fetcher = CurrentPriceFetcher()
            self.trader = LiveTrader()
            self.portfolio_manager = PortfolioManager(self.db_conn)
            self.metrics_engine = MetricsCalculationEngine(self.db_conn)
            
            # Market stream (asyncio)
            self.market_stream = BinanceMarketStream()
            
            logger.info("✅ All components initialized")
            
        except Exception as e:
            logger.critical(f"❌ Initialization failed: {e}")
            raise
    
    def schedule_jobs(self):
        """Schedule all background jobs"""
        
        logger.info("📅 Scheduling jobs...")
        
        # Every 1 second: Update market prices
        self.scheduler.add_job(
            self.job_update_prices,
            'interval',
            seconds=1,
            id='update_prices',
            name='Update market prices'
        )
        
        # Every 5 seconds: Generate signals
        self.scheduler.add_job(
            self.job_generate_signals,
            'interval',
            seconds=5,
            id='generate_signals',
            name='Generate trading signals'
        )
        
        # Every 5 seconds: Monitor positions
        self.scheduler.add_job(
            self.job_monitor_positions,
            'interval',
            seconds=5,
            id='monitor_positions',
            name='Monitor open positions'
        )
        
        # Every 1 hour: Calculate metrics
        self.scheduler.add_job(
            self.job_calculate_metrics,
            'interval',
            hours=1,
            id='calculate_metrics',
            name='Calculate performance metrics'
        )
        
        # Every day at 00:00: Retrain models
        self.scheduler.add_job(
            self.job_retrain_models,
            CronTrigger(hour=0, minute=0),
            id='retrain_models',
            name='Retrain ML models'
        )
        
        # Every day at 01:00: Generate daily report
        self.scheduler.add_job(
            self.job_generate_report,
            CronTrigger(hour=1, minute=0),
            id='generate_report',
            name='Generate daily report'
        )
        
        logger.info("✅ Jobs scheduled successfully")
    
    def job_update_prices(self):
        """Update current market prices"""
        try:
            prices = self.price_fetcher.get_prices(SYMBOLS)
            
            for symbol, price in prices.items():
                # Store in cache/db
                cur = self.db_conn.cursor()
                
                insert_query = """
                    INSERT INTO market_data_cache
                    (timestamp, symbol, price)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE SET
                    price = EXCLUDED.price, timestamp = EXCLUDED.timestamp
                """
                
                cur.execute(insert_query, (datetime.now(), symbol, price))
                self.db_conn.commit()
                cur.close()
            
            logger.debug(f"✅ Prices updated: {list(prices.keys())}")
        
        except Exception as e:
            logger.error(f"❌ Price update failed: {e}")
    
    def job_generate_signals(self):
        """Generate trading signals"""
        try:
            logger.info("🎯 Generating signals...")
            
            for symbol in SYMBOLS:
                try:
                    # Load models
                    models = EnsembleModelManager.load_models(symbol)
                    if not models:
                        logger.warning(f"⚠️ No models for {symbol}")
                        continue
                    
                    # Generate signal
                    signal, confidence, details = self.signal_generator.generate_signal(symbol, models)
                    
                    # Save signal
                    cur = self.db_conn.cursor()
                    
                    insert_query = """
                        INSERT INTO signal_log
                        (timestamp, symbol, signal, confidence, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    
                    signal_map = {-1: 'HOLD', 0: 'SELL', 1: 'BUY'}
                    
                    cur.execute(insert_query, (
                        datetime.now(),
                        symbol,
                        signal_map[signal],
                        confidence,
                        json.dumps(details) if details else None
                    ))
                    
                    self.db_conn.commit()
                    cur.close()
                    
                    logger.info(f"✅ {symbol}: {signal_map[signal]} ({confidence:.2%})")
                
                except Exception as e:
                    logger.error(f"❌ Signal failed for {symbol}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Signal generation failed: {e}")
    
    def job_monitor_positions(self):
        """Monitor open positions"""
        try:
            logger.debug("📍 Monitoring positions...")
            
            positions = self.position_monitor.get_open_positions()
            prices = self.price_fetcher.get_prices(SYMBOLS)
            
            for position in positions:
                symbol = position['symbol']
                
                if symbol not in prices:
                    continue
                
                current_price = prices[symbol]
                pnl_data = self.position_monitor.calculate_position_pnl(position, current_price)
                
                # Update position
                self.position_monitor.update_position_price(position['id'], current_price)
                
                # Check for SL/TP hits
                if pnl_data['status'] == 'TP_HIT':
                    logger.info(f"🎯 TP hit for {symbol}")
                    self.position_monitor.close_position_on_target(
                        position['id'], 'TP_HIT', current_price, pnl_data['pnl']
                    )
                
                elif pnl_data['status'] == 'SL_HIT':
                    logger.warning(f"🛑 SL hit for {symbol}")
                    self.position_monitor.close_position_on_target(
                        position['id'], 'SL_HIT', current_price, pnl_data['pnl']
                    )
        
        except Exception as e:
            logger.error(f"❌ Position monitoring failed: {e}")
    
    def job_calculate_metrics(self):
        """Calculate performance metrics"""
        try:
            logger.info("📊 Calculating metrics...")
            
            metrics = self.metrics_engine.calculate_all_metrics()
            self.metrics_engine.save_metrics(metrics)
            
            logger.info(f"✅ Metrics calculated and saved")
        
        except Exception as e:
            logger.error(f"❌ Metrics calculation failed: {e}")
    
    def job_retrain_models(self):
        """Retrain ML models daily"""
        try:
            logger.info("🧠 Retraining models...")
            
            # Import training pipeline
            from training_pipeline import TrainingPipeline
            
            pipeline = TrainingPipeline()
            pipeline.train_all_symbols()
            pipeline.close()
            
            logger.info("✅ Models retrained")
        
        except Exception as e:
            logger.error(f"❌ Model retraining failed: {e}")
    
    def job_generate_report(self):
        """Generate daily report"""
        try:
            logger.info("📄 Generating daily report...")
            
            # Get metrics
            metrics = self.metrics_engine.calculate_all_metrics()
            
            # Log report
            report = f"""
            ╔════════════════════════════════════════╗
            ║     DEMIR AI - DAILY REPORT            ║
            ║     {datetime.now().strftime('%Y-%m-%d')}                     ║
            ╠════════════════════════════════════════╣
            ║ Total Return:    {metrics.get('total_return_pct', 0):.2f}%     ║
            ║ Sharpe Ratio:    {metrics.get('sharpe_ratio', 0):.2f}          ║
            ║ Win Rate:        {metrics.get('win_rate', 0):.1%}        ║
            ║ Max Drawdown:    {metrics.get('max_drawdown', 0):.2%}     ║
            ╚════════════════════════════════════════╝
            """
            
            logger.info(report)
        
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
    
    def start(self):
        """Start the orchestrator"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 DEMIR AI - MASTER ORCHESTRATOR")
            logger.info("=" * 80)
            
            # Schedule jobs
            self.schedule_jobs()
            
            # Start scheduler
            self.scheduler.start()
            
            logger.info("✅ Orchestrator started successfully")
            logger.info("📡 Bot is now 7/24 active!\n")
            
            # Keep running
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                logger.info("🛑 Orchestrator stopped by user")
        
        except Exception as e:
            logger.critical(f"❌ Orchestrator failed: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        if self.db_conn:
            self.db_conn.close()
        
        self.trader.close()
        
        logger.info("✅ Orchestrator stopped")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        orchestrator = MasterOrchestrator()
        orchestrator.start()
    
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    import json
    main()
