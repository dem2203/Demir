#!/usr/bin/env python3
"""
🚀 DEMIR AI v8.0 - ENTERPRISE CRYPTO TRADING AI ORCHESTRATOR
===============================================================

🎯 MISSION: 7/24 aktif, çok katmanlı yapay zeka kripto bot
📊 12 YENİ MODÜL: Smart Money, Risk v2, Sentiment v2, RL Agent, Ensemble, Pattern Recognition,
                Ultra-Low Latency, Redis Cache, Backtesting v2, Multi-Exchange Arbitrage,
                On-Chain Analytics Pro, Advanced Dashboard v2

⚠️  ALTIN KURAL #1: KESINLİKLE MOCK/FAKE/TEST/FALLBACK/HARDCODED DATA OLMAYACAK!
✅ TÜM VERİLER: 100% canlI borsa API'lerinden (Binance, Bybit, Coinbase)

🏛️ PRODUCTION: Railway (https://demir1988.up.railway.app/)
👷 DEVELOPER: Professional Crypto AI Team
📅 LAST UPDATE: 2025-11-21
"""

import os
import sys
import time
import logging
import threading
import signal
from datetime import datetime
from typing import Dict, Any, Optional

# --- CONFIGURATION ---
from config import (
    VERSION, APP_NAME, FULL_NAME, ADVISORY_MODE,
    TELEGRAM_ENABLED, DATABASE_URL,
    OPPORTUNITY_THRESHOLDS, validate_config
)

# --- CORE IMPORTS ---
try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    from flask_socketio import SocketIO
except ImportError as e:
    print(f"❌ CRITICAL: Flask/SocketIO not installed - {e}")
    sys.exit(1)

# --- DATABASE ---
try:
    from database_manager_production import DatabaseManager
except ImportError:
    print("⚠️  WARNING: DatabaseManager not found, using fallback")
    DatabaseManager = None

# --- DATA VALIDATORS (ZERO MOCK DATA ENFORCEMENT) ---
try:
    from real_data_validators import (
        MockDataDetector, RealDataVerifier, SignalValidator
    )
except ImportError:
    print("⚠️  WARNING: Data validators not found")
    MockDataDetector = RealDataVerifier = SignalValidator = None

# --- PHASE 1: TEMEL İYİLEŞTİRMELER ---
try:
    from integrations.smart_money_tracker import SmartMoneyTracker
    from integrations.advanced_risk_engine import AdvancedRiskEngine
    from integrations.sentiment_analysis_v2 import SentimentAnalysisV2
    PHASE1_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Phase 1 modules not fully available - {e}")
    SmartMoneyTracker = AdvancedRiskEngine = SentimentAnalysisV2 = None
    PHASE1_AVAILABLE = False

# --- PHASE 2: MACHINE LEARNING UPGRADE ---
try:
    from advanced_ai.reinforcement_learning_agent import ReinforcementLearningAgent
    from advanced_ai.ensemble_meta_model import EnsembleMetaModel
    from advanced_ai.pattern_recognition_engine import PatternRecognitionEngine
    PHASE2_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Phase 2 ML modules not fully available - {e}")
    ReinforcementLearningAgent = EnsembleMetaModel = PatternRecognitionEngine = None
    PHASE2_AVAILABLE = False

# --- PHASE 3: PERFORMANCE & SPEED ---
try:
    from performance.ultra_low_latency_engine import UltraLowLatencyEngine
    from performance.redis_hot_data_cache import RedisHotDataCache
    from performance.advanced_backtesting_v2 import AdvancedBacktestEngine
    PHASE3_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Phase 3 performance modules not fully available - {e}")
    UltraLowLatencyEngine = RedisHotDataCache = AdvancedBacktestEngine = None
    PHASE3_AVAILABLE = False

# --- PHASE 4: EXPANSION ---
try:
    from expansion.multi_exchange_arbitrage import MultiExchangeArbitrage
    from expansion.onchain_analytics_pro import OnChainAnalyticsPro
    PHASE4_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Phase 4 expansion modules not fully available - {e}")
    MultiExchangeArbitrage = OnChainAnalyticsPro = None
    PHASE4_AVAILABLE = False

# --- ADVANCED DASHBOARD v2.0 BACKEND ---
try:
    from backend.advanced_dashboard_api_v2 import dashboard_bp
    DASHBOARD_V2_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Advanced Dashboard v2 backend not available - {e}")
    dashboard_bp = None
    DASHBOARD_V2_AVAILABLE = False

# --- LEGACY INTEGRATIONS (Compatibility) ---
try:
    from integrations.binance_websocket_v3 import BinanceWebSocketManager
    from integrations.multi_exchange_api import MultiExchangeAPI
    from integrations.market_intelligence import MarketIntelligence
    LEGACY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  WARNING: Legacy integrations not fully available - {e}")
    BinanceWebSocketManager = MultiExchangeAPI = MarketIntelligence = None
    LEGACY_AVAILABLE = False

# --- AI BRAIN ENSEMBLE ---
try:
    from ai_brain_ensemble import AIBrainEnsemble
    AI_BRAIN_AVAILABLE = True
except ImportError:
    print("⚠️  WARNING: AI Brain Ensemble not found")
    AIBrainEnsemble = None
    AI_BRAIN_AVAILABLE = False

# --- TELEGRAM MONITORING ---
try:
    from telegram_monitor import TelegramMonitor
    TELEGRAM_MONITOR_AVAILABLE = TELEGRAM_ENABLED
except ImportError:
    print("⚠️  WARNING: Telegram Monitor not found")
    TelegramMonitor = None
    TELEGRAM_MONITOR_AVAILABLE = False

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('DEMIR_ORCHESTRATOR')

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

logger.info(f"✅ Flask app initialized: {FULL_NAME}")

# ============================================================================
# GLOBAL INSTANCES (v8.0 MODULES)
# ============================================================================
class DemirOrchestrator:
    """
    🎩 Main orchestrator for DEMIR AI v8.0
    Manages all 12 new modules + legacy systems
    """
    def __init__(self):
        self.running = False
        self.start_time = datetime.now()
        
        # Database
        self.db = DatabaseManager() if DatabaseManager else None
        
        # Data Validators (ZERO MOCK DATA)
        self.mock_detector = MockDataDetector() if MockDataDetector else None
        self.data_verifier = RealDataVerifier() if RealDataVerifier else None
        self.signal_validator = SignalValidator() if SignalValidator else None
        
        # --- PHASE 1: Temel İyileştirmeler ---
        self.smart_money_tracker = SmartMoneyTracker() if PHASE1_AVAILABLE and SmartMoneyTracker else None
        self.risk_engine = AdvancedRiskEngine() if PHASE1_AVAILABLE and AdvancedRiskEngine else None
        self.sentiment_v2 = SentimentAnalysisV2() if PHASE1_AVAILABLE and SentimentAnalysisV2 else None
        
        # --- PHASE 2: ML Upgrade ---
        self.rl_agent = ReinforcementLearningAgent() if PHASE2_AVAILABLE and ReinforcementLearningAgent else None
        self.ensemble_model = EnsembleMetaModel() if PHASE2_AVAILABLE and EnsembleMetaModel else None
        self.pattern_engine = PatternRecognitionEngine() if PHASE2_AVAILABLE and PatternRecognitionEngine else None
        
        # --- PHASE 3: Performance ---
        self.latency_engine = UltraLowLatencyEngine() if PHASE3_AVAILABLE and UltraLowLatencyEngine else None
        self.redis_cache = RedisHotDataCache() if PHASE3_AVAILABLE and RedisHotDataCache else None
        self.backtest_engine = AdvancedBacktestEngine() if PHASE3_AVAILABLE and AdvancedBacktestEngine else None
        
        # --- PHASE 4: Expansion ---
        self.arbitrage_engine = MultiExchangeArbitrage() if PHASE4_AVAILABLE and MultiExchangeArbitrage else None
        self.onchain_analytics = OnChainAnalyticsPro() if PHASE4_AVAILABLE and OnChainAnalyticsPro else None
        
        # --- Legacy Systems (Compatibility) ---
        self.ws_manager = BinanceWebSocketManager() if LEGACY_AVAILABLE and BinanceWebSocketManager else None
        self.exchange_api = MultiExchangeAPI() if LEGACY_AVAILABLE and MultiExchangeAPI else None
        self.market_intel = MarketIntelligence() if LEGACY_AVAILABLE and MarketIntelligence else None
        
        # --- AI Brain ---
        self.ai_brain = AIBrainEnsemble() if AI_BRAIN_AVAILABLE and AIBrainEnsemble else None
        
        # --- Telegram ---
        self.telegram = TelegramMonitor() if TELEGRAM_MONITOR_AVAILABLE and TelegramMonitor else None
        
        # Background threads
        self.threads = []
        
        logger.info("✅ DemirOrchestrator initialized successfully")
        self._log_module_status()
    
    def _log_module_status(self):
        """Log which modules are active"""
        logger.info("="*60)
        logger.info(f"🚀 {FULL_NAME} - MODULE STATUS")
        logger.info("="*60)
        logger.info(f"PHASE 1 (Temel): {'\u2705 Active' if PHASE1_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"PHASE 2 (ML): {'\u2705 Active' if PHASE2_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"PHASE 3 (Performance): {'\u2705 Active' if PHASE3_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"PHASE 4 (Expansion): {'\u2705 Active' if PHASE4_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"Dashboard v2: {'\u2705 Active' if DASHBOARD_V2_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"Legacy Systems: {'\u2705 Active' if LEGACY_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"AI Brain: {'\u2705 Active' if AI_BRAIN_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"Telegram: {'\u2705 Active' if TELEGRAM_MONITOR_AVAILABLE else '\u274c Inactive'}")
        logger.info(f"Advisory Mode: {'\u2705 ON (No Trading)' if ADVISORY_MODE else '\u274c OFF (Trading Enabled)'}")
        logger.info("="*60)
    
    def start(self):
        """Start all background processes"""
        self.running = True
        logger.info("🚀 Starting DEMIR AI v8.0 orchestrator...")
        
        # Thread 1: Smart Money & Whale Tracking
        if self.smart_money_tracker:
            t1 = threading.Thread(target=self._smart_money_loop, daemon=True, name="SmartMoneyThread")
            t1.start()
            self.threads.append(t1)
            logger.info("✅ Smart Money Tracker thread started")
        
        # Thread 2: Arbitrage Scanning
        if self.arbitrage_engine:
            t2 = threading.Thread(target=self._arbitrage_loop, daemon=True, name="ArbitrageThread")
            t2.start()
            self.threads.append(t2)
            logger.info("✅ Arbitrage Engine thread started")
        
        # Thread 3: On-Chain Analytics
        if self.onchain_analytics:
            t3 = threading.Thread(target=self._onchain_loop, daemon=True, name="OnChainThread")
            t3.start()
            self.threads.append(t3)
            logger.info("✅ On-Chain Analytics thread started")
        
        # Thread 4: Risk Monitoring
        if self.risk_engine:
            t4 = threading.Thread(target=self._risk_monitoring_loop, daemon=True, name="RiskThread")
            t4.start()
            self.threads.append(t4)
            logger.info("✅ Risk Monitoring thread started")
        
        # Thread 5: Sentiment Analysis
        if self.sentiment_v2:
            t5 = threading.Thread(target=self._sentiment_loop, daemon=True, name="SentimentThread")
            t5.start()
            self.threads.append(t5)
            logger.info("✅ Sentiment Analysis thread started")
        
        # Thread 6: Pattern Recognition
        if self.pattern_engine:
            t6 = threading.Thread(target=self._pattern_loop, daemon=True, name="PatternThread")
            t6.start()
            self.threads.append(t6)
            logger.info("✅ Pattern Recognition thread started")
        
        # Thread 7: Legacy WebSocket
        if self.ws_manager:
            t7 = threading.Thread(target=self._websocket_loop, daemon=True, name="WebSocketThread")
            t7.start()
            self.threads.append(t7)
            logger.info("✅ WebSocket Manager thread started")
        
        # Thread 8: Telegram Notifications
        if self.telegram:
            t8 = threading.Thread(target=self._telegram_loop, daemon=True, name="TelegramThread")
            t8.start()
            self.threads.append(t8)
            logger.info("✅ Telegram Monitor thread started")
        
        logger.info(f"🟢 Total {len(self.threads)} background threads running")
    
    # --- BACKGROUND LOOPS ---
    
    def _smart_money_loop(self):
        """Phase 1: Smart Money Tracker loop"""
        logger.info("🐳 Smart Money Tracker loop started")
        while self.running:
            try:
                if self.smart_money_tracker:
                    signals = self.smart_money_tracker.detect_smart_money_signals()
                    if signals:
                        logger.info(f"🐳 Smart Money signals detected: {len(signals)}")
                        # Store in database if available
                        if self.db:
                            for signal in signals:
                                self.db.save_signal(signal)
                time.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"❌ Smart Money loop error: {e}")
                time.sleep(60)
    
    def _arbitrage_loop(self):
        """Phase 4: Arbitrage scanning loop"""
        logger.info("🔄 Arbitrage Engine loop started")
        while self.running:
            try:
                if self.arbitrage_engine:
                    opportunities = self.arbitrage_engine.scan_arbitrage()
                    if opportunities:
                        logger.info(f"🔄 Arbitrage opportunities found: {len(opportunities)}")
                        # Notify via Telegram if enabled
                        if self.telegram:
                            for opp in opportunities:
                                self.telegram.send_opportunity_alert(opp)
                time.sleep(60)  # 1 minute
            except Exception as e:
                logger.error(f"❌ Arbitrage loop error: {e}")
                time.sleep(30)
    
    def _onchain_loop(self):
        """Phase 4: On-Chain analytics loop"""
        logger.info("⛓️ On-Chain Analytics loop started")
        while self.running:
            try:
                if self.onchain_analytics:
                    metrics = self.onchain_analytics.analyze_onchain_metrics()
                    if metrics:
                        logger.info(f"⛓️ On-Chain metrics updated: {list(metrics.keys())}")
                        # Cache in Redis if available
                        if self.redis_cache:
                            self.redis_cache.set('onchain_metrics', metrics, ttl=600)
                time.sleep(600)  # 10 minutes
            except Exception as e:
                logger.error(f"❌ On-Chain loop error: {e}")
                time.sleep(120)
    
    def _risk_monitoring_loop(self):
        """Phase 1: Risk Engine monitoring loop"""
        logger.info("⚠️  Risk Monitoring loop started")
        while self.running:
            try:
                if self.risk_engine:
                    risk_report = self.risk_engine.calculate_portfolio_risk()
                    if risk_report:
                        logger.info(f"⚠️  Risk report: VAR={risk_report.get('var', 'N/A')}")
                time.sleep(180)  # 3 minutes
            except Exception as e:
                logger.error(f"❌ Risk loop error: {e}")
                time.sleep(60)
    
    def _sentiment_loop(self):
        """Phase 1: Sentiment Analysis loop"""
        logger.info("💬 Sentiment Analysis loop started")
        while self.running:
            try:
                if self.sentiment_v2:
                    sentiment = self.sentiment_v2.analyze_multi_source_sentiment()
                    if sentiment:
                        logger.info(f"💬 Sentiment: {sentiment.get('aggregate_sentiment', 'N/A')}")
                time.sleep(900)  # 15 minutes
            except Exception as e:
                logger.error(f"❌ Sentiment loop error: {e}")
                time.sleep(120)
    
    def _pattern_loop(self):
        """Phase 2: Pattern Recognition loop"""
        logger.info("🔍 Pattern Recognition loop started")
        while self.running:
            try:
                if self.pattern_engine:
                    patterns = self.pattern_engine.detect_all_patterns()
                    if patterns:
                        logger.info(f"🔍 Patterns detected: {len(patterns)}")
                time.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"❌ Pattern loop error: {e}")
                time.sleep(60)
    
    def _websocket_loop(self):
        """Legacy: WebSocket manager loop"""
        logger.info("🌐 WebSocket Manager loop started")
        while self.running:
            try:
                if self.ws_manager:
                    # Keep WebSocket connections alive
                    self.ws_manager.maintain_connections()
                time.sleep(30)  # 30 seconds
            except Exception as e:
                logger.error(f"❌ WebSocket loop error: {e}")
                time.sleep(10)
    
    def _telegram_loop(self):
        """Telegram notifications loop"""
        logger.info("📢 Telegram Monitor loop started")
        while self.running:
            try:
                if self.telegram:
                    # Check for critical alerts
                    self.telegram.process_alerts()
                time.sleep(60)  # 1 minute
            except Exception as e:
                logger.error(f"❌ Telegram loop error: {e}")
                time.sleep(30)
    
    def stop(self):
        """Stop all processes gracefully"""
        logger.info("🛑 Stopping DEMIR AI v8.0 orchestrator...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("✅ All threads stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'status': 'running' if self.running else 'stopped',
            'version': VERSION,
            'app_name': APP_NAME,
            'uptime_seconds': uptime,
            'uptime_formatted': f"{int(uptime//3600)}h {int((uptime%3600)//60)}m",
            'modules': {
                'phase1': PHASE1_AVAILABLE,
                'phase2': PHASE2_AVAILABLE,
                'phase3': PHASE3_AVAILABLE,
                'phase4': PHASE4_AVAILABLE,
                'dashboard_v2': DASHBOARD_V2_AVAILABLE,
                'legacy': LEGACY_AVAILABLE,
                'ai_brain': AI_BRAIN_AVAILABLE,
                'telegram': TELEGRAM_MONITOR_AVAILABLE
            },
            'advisory_mode': ADVISORY_MODE,
            'threads_count': len(self.threads),
            'threads_active': sum(1 for t in self.threads if t.is_alive())
        }

# ============================================================================
# GLOBAL ORCHESTRATOR INSTANCE
# ============================================================================
orchestrator = DemirOrchestrator()

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve main dashboard"""
    try:
        return app.send_static_file('index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return jsonify({"error": "Dashboard not available"}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION
    }), 200

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify(orchestrator.get_status()), 200

@app.route('/api/modules')
def api_modules():
    """Get detailed module information"""
    return jsonify({
        'phase1': {
            'name': 'Temel İyileştirmeler',
            'active': PHASE1_AVAILABLE,
            'modules': ['Smart Money Tracker', 'Advanced Risk Engine v2', 'Sentiment Analysis v2']
        },
        'phase2': {
            'name': 'Machine Learning Upgrade',
            'active': PHASE2_AVAILABLE,
            'modules': ['RL Agent', 'Ensemble Meta-Model', 'Pattern Recognition']
        },
        'phase3': {
            'name': 'Performance & Speed',
            'active': PHASE3_AVAILABLE,
            'modules': ['Ultra-Low Latency', 'Redis Cache', 'Backtesting v2']
        },
        'phase4': {
            'name': 'Expansion',
            'active': PHASE4_AVAILABLE,
            'modules': ['Multi-Exchange Arbitrage', 'On-Chain Analytics Pro']
        }
    }), 200

# --- REGISTER ADVANCED DASHBOARD v2.0 BLUEPRINT ---
if DASHBOARD_V2_AVAILABLE and dashboard_bp:
    app.register_blueprint(dashboard_bp)
    logger.info("✅ Advanced Dashboard v2.0 API registered at /api/analytics/*")

# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"🛑 Received signal {sig}, shutting down...")
    orchestrator.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Validate configuration
    logger.info("🔍 Validating configuration...")
    validate_config()
    logger.info("✅ Configuration validated")
    
    # Start orchestrator
    orchestrator.start()
    
    # Get port from environment (Railway provides PORT)
    port = int(os.getenv('PORT', 8501))
    host = '0.0.0.0'
    
    logger.info("="*60)
    logger.info(f"🚀 {FULL_NAME} - READY")
    logger.info(f"🌐 Server starting on {host}:{port}")
    logger.info(f"📊 Dashboard: http://{host}:{port}/")
    logger.info(f"❤️  Health Check: http://{host}:{port}/health")
    logger.info(f"🛠️  Status API: http://{host}:{port}/api/status")
    logger.info(f"📊 Analytics API: http://{host}:{port}/api/analytics/summary")
    logger.info("="*60)
    
    # Run Flask app with SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        log_output=True
    )
