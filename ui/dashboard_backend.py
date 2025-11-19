# ui/dashboard_backend.py
"""
🚀 DEMIR AI v6.0 - ENTERPRISE DASHBOARD BACKEND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HYBRID ARCHITECTURE:
    A) WebSocket → Real-time price updates (1s interval)
    B) REST API → Signals, AI analysis, historical data

FEATURES:
    ✅ 100% Real data - ZERO mock/fake/fallback
    ✅ Multi-exchange price verification
    ✅ WebSocket with auto-reconnect
    ✅ Real-time layer analysis
    ✅ AI advisor opportunities
    ✅ Live performance tracking
    
DEPLOYMENT: Railway + GitHub
AUTHOR: DEMIR AI Research Team
DATE: 2025-11-19
VERSION: 6.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque

# Flask & SocketIO
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, disconnect

# Database & Utils
from database_manager_production import DatabaseManager
from utils.logger_setup import setup_logger
from utils.real_data_verifier_pro import RealDataVerifier
from utils.signal_validator_comprehensive import SignalValidator

# Integrations
from integrations.binance_websocket_v3 import BinanceWebSocketManager
from integrations.multi_exchange_api import MultiExchangeDataFetcher

# Analytics
from analytics.advisor_opportunity_service import AdvisorOpportunityService
from analytics.performance_engine import PerformanceEngine

# Advanced AI
from advanced_ai.signal_engine_integration import SignalEngineIntegration

logger = setup_logger(__name__)

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(
    __name__,
    static_folder=os.path.abspath('.'),
    static_url_path='',
    template_folder=os.path.abspath('.')
)

app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'demir-ai-secret-key-2025')

CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# ============================================================================
# GLOBAL MANAGERS & STATE
# ============================================================================

# Database
db_manager: Optional[DatabaseManager] = None

# WebSocket Manager
ws_manager: Optional[BinanceWebSocketManager] = None

# Data Fetcher
data_fetcher: Optional[MultiExchangeDataFetcher] = None

# Advisor Service
advisor_service: Optional[AdvisorOpportunityService] = None

# Performance Engine
performance_engine: Optional[PerformanceEngine] = None

# Signal Engine
signal_engine: Optional[SignalEngineIntegration] = None

# Real Data Verifier
real_data_verifier: Optional[RealDataVerifier] = None

# Signal Validator
signal_validator: Optional[SignalValidator] = None

# Connected WebSocket Clients
connected_clients = set()

# Price cache (in-memory for ultra-fast access)
price_cache = {}
price_cache_lock = threading.Lock()

# Layer scores cache
layer_scores_cache = {}
layer_scores_lock = threading.Lock()

# Signal cache
signal_cache = deque(maxlen=100)
signal_cache_lock = threading.Lock()

# Performance metrics cache
performance_metrics = {
    'total_signals': 0,
    'win_rate': 0.0,
    'total_pnl': 0.0,
    'sharpe_ratio': 0.0,
    'last_updated': None
}
performance_lock = threading.Lock()

# System health
system_health = {
    'database': False,
    'websocket': False,
    'api_binance': False,
    'api_bybit': False,
    'api_coinbase': False,
    'last_check': None
}
health_lock = threading.Lock()

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_services():
    """Initialize all services - 100% REAL DATA ONLY"""
    global db_manager, ws_manager, data_fetcher, advisor_service
    global performance_engine, signal_engine, real_data_verifier, signal_validator
    
    logger.info("="*80)
    logger.info("🚀 DEMIR AI v6.0 - DASHBOARD BACKEND INITIALIZATION")
    logger.info("="*80)
    
    try:
        # 1. Database Manager
        logger.info("📊 Initializing DatabaseManager...")
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment")
        
        db_manager = DatabaseManager(db_url)
        
        # Test connection
        if not db_manager.test_connection():
            raise ConnectionError("Database connection failed")
        
        logger.info("✅ DatabaseManager initialized successfully")
        
        with health_lock:
            system_health['database'] = True
        
        # 2. Multi-Exchange Data Fetcher
        logger.info("🌐 Initializing MultiExchangeDataFetcher...")
        data_fetcher = MultiExchangeDataFetcher()
        logger.info("✅ MultiExchangeDataFetcher initialized")
        
        # 3. Real Data Verifier (NO MOCK DATA)
        logger.info("🔍 Initializing RealDataVerifier...")
        real_data_verifier = RealDataVerifier()
        logger.info("✅ RealDataVerifier initialized - ZERO TOLERANCE FOR FAKE DATA")
        
        # 4. Signal Validator
        logger.info("✔️  Initializing SignalValidator...")
        signal_validator = SignalValidator()
        logger.info("✅ SignalValidator initialized")
        
        # 5. WebSocket Manager (Real-time prices)
        logger.info("📡 Initializing BinanceWebSocketManager...")
        ws_manager = BinanceWebSocketManager()
        
        # Start WebSocket in background thread
        ws_thread = threading.Thread(
            target=start_websocket_manager,
            daemon=True,
            name="WebSocketManager"
        )
        ws_thread.start()
        
        logger.info("✅ BinanceWebSocketManager started")
        
        with health_lock:
            system_health['websocket'] = True
        
        # 6. Advisor Service
        logger.info("🧠 Initializing AdvisorOpportunityService...")
        advisor_service = AdvisorOpportunityService(db_manager)
        logger.info("✅ AdvisorOpportunityService initialized")
        
        # 7. Performance Engine
        logger.info("📈 Initializing PerformanceEngine...")
        performance_engine = PerformanceEngine(db_manager)
        logger.info("✅ PerformanceEngine initialized")
        
        # 8. Signal Engine Integration
        logger.info("🎯 Initializing SignalEngineIntegration...")
        signal_engine = SignalEngineIntegration(db_manager, data_fetcher)
        logger.info("✅ SignalEngineIntegration initialized")
        
        logger.info("="*80)
        logger.info("🎉 ALL SERVICES INITIALIZED SUCCESSFULLY")
        logger.info("="*80)
        
        # Start background tasks
        start_background_tasks()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ INITIALIZATION FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# ============================================================================
# WEBSOCKET MANAGER
# ============================================================================

def start_websocket_manager():
    """Start WebSocket manager for real-time prices"""
    try:
        logger.info("Starting WebSocket price stream...")
        
        # Primary symbols
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        
        if ws_manager:
            asyncio.run(ws_manager.start_price_stream(
                symbols=symbols,
                callback=on_price_update
            ))
    except Exception as e:
        logger.error(f"WebSocket manager error: {e}")
        with health_lock:
            system_health['websocket'] = False

async def on_price_update(symbol: str, price: float, change_24h: float):
    """Callback for real-time price updates"""
    try:
        # Verify this is REAL data (not mock)
        if real_data_verifier:
            is_valid = await real_data_verifier.verify_price(
                symbol=symbol,
                price=price,
                exchange='binance'
            )
            
            if not is_valid:
                logger.warning(f"⚠️ INVALID PRICE DETECTED for {symbol}: {price} - REJECTED")
                return
        
        # Update price cache
        with price_cache_lock:
            price_cache[symbol] = {
                'price': float(price),
                'change_24h': float(change_24h),
                'timestamp': time.time()
            }
        
        # Broadcast to connected clients
        socketio.emit('price_update', {
            'symbol': symbol,
            'price': float(price),
            'change_24h': float(change_24h),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.debug(f"Price update error: {e}")

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

def start_background_tasks():
    """Start background monitoring and update tasks"""
    
    # Health check every 60 seconds
    health_thread = threading.Thread(
        target=health_check_loop,
        daemon=True,
        name="HealthCheck"
    )
    health_thread.start()
    
    # Performance metrics update every 30 seconds
    perf_thread = threading.Thread(
        target=performance_update_loop,
        daemon=True,
        name="PerformanceUpdate"
    )
    perf_thread.start()
    
    # Layer scores update every 10 seconds
    layer_thread = threading.Thread(
        target=layer_scores_update_loop,
        daemon=True,
        name="LayerScores"
    )
    layer_thread.start()
    
    logger.info("✅ Background tasks started")

def health_check_loop():
    """Background health check loop"""
    while True:
        try:
            time.sleep(60)  # Every 60 seconds
            
            with health_lock:
                # Database
                if db_manager:
                    system_health['database'] = db_manager.test_connection()
                
                # WebSocket
                if ws_manager:
                    system_health['websocket'] = ws_manager.is_connected()
                
                # APIs
                if data_fetcher:
                    system_health['api_binance'] = data_fetcher.check_binance_health()
                    system_health['api_bybit'] = data_fetcher.check_bybit_health()
                    system_health['api_coinbase'] = data_fetcher.check_coinbase_health()
                
                system_health['last_check'] = datetime.now().isoformat()
            
            # Emit health status to clients
            socketio.emit('health_status', system_health)
            
        except Exception as e:
            logger.error(f"Health check error: {e}")

def performance_update_loop():
    """Background performance metrics update"""
    while True:
        try:
            time.sleep(30)  # Every 30 seconds
            
            if performance_engine:
                metrics = performance_engine.get_current_metrics()
                
                with performance_lock:
                    performance_metrics.update({
                        'total_signals': metrics.get('total_signals', 0),
                        'win_rate': metrics.get('win_rate', 0.0),
                        'total_pnl': metrics.get('total_pnl', 0.0),
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0.0),
                        'last_updated': datetime.now().isoformat()
                    })
                
                # Emit to clients
                socketio.emit('performance_update', performance_metrics)
                
        except Exception as e:
            logger.error(f"Performance update error: {e}")

def layer_scores_update_loop():
    """Background layer scores update"""
    while True:
        try:
            time.sleep(10)  # Every 10 seconds
            
            if signal_engine:
                # Get latest layer scores for primary symbols
                for symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
                    scores = signal_engine.get_layer_scores(symbol)
                    
                    with layer_scores_lock:
                        layer_scores_cache[symbol] = scores
                    
                    # Emit to clients
                    socketio.emit('layer_scores', {
                        'symbol': symbol,
                        'scores': scores,
                        'timestamp': time.time()
                    })
            
        except Exception as e:
            logger.error(f"Layer scores update error: {e}")

# ============================================================================
# SOCKETIO EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    logger.info(f"✅ Client connected: {request.sid}")
    connected_clients.add(request.sid)
    
    # Send initial data
    emit('connection_status', {
        'status': 'connected',
        'timestamp': time.time(),
        'services': system_health
    })
    
    # Send cached prices immediately
    with price_cache_lock:
        if price_cache:
            emit('price_bulk', price_cache)
    
    # Send cached performance
    with performance_lock:
        emit('performance_update', performance_metrics)

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info(f"❌ Client disconnected: {request.sid}")
    connected_clients.discard(request.sid)

@socketio.on('subscribe_symbol')
def handle_subscribe(data):
    """Client subscribes to specific symbol updates"""
    try:
        symbol = data.get('symbol', 'BTCUSDT')
        logger.info(f"Client {request.sid} subscribed to {symbol}")
        
        # Send immediate update if available
        with price_cache_lock:
            if symbol in price_cache:
                emit('price_update', {
                    'symbol': symbol,
                    **price_cache[symbol]
                })
        
        with layer_scores_lock:
            if symbol in layer_scores_cache:
                emit('layer_scores', {
                    'symbol': symbol,
                    'scores': layer_scores_cache[symbol],
                    'timestamp': time.time()
                })
        
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        emit('error', {'message': str(e)})

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/')
def serve_dashboard():
    """Serve main dashboard HTML"""
    try:
        if os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        return "Dashboard not found", 404
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return "Error", 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    with health_lock:
        all_healthy = all(system_health.values())
        status_code = 200 if all_healthy else 503
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'degraded',
            'services': system_health,
            'timestamp': datetime.now().isoformat()
        }), status_code

@app.route('/api/prices/current', methods=['GET'])
def get_current_prices():
    """
    Get current prices for all tracked symbols
    100% REAL DATA - WebSocket feed
    """
    try:
        symbol = request.args.get('symbol')
        
        with price_cache_lock:
            if symbol:
                if symbol not in price_cache:
                    return jsonify({
                        'status': 'error',
                        'message': f'Symbol {symbol} not found'
                    }), 404
                
                return jsonify({
                    'status': 'success',
                    'data': {symbol: price_cache[symbol]},
                    'timestamp': time.time()
                })
            else:
                return jsonify({
                    'status': 'success',
                    'data': price_cache,
                    'count': len(price_cache),
                    'timestamp': time.time()
                })
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/signals/latest', methods=['GET'])
def get_latest_signals():
    """
    Get latest trading signals
    100% REAL - from database
    """
    try:
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 20))
        
        if not db_manager:
            return jsonify({
                'status': 'error',
                'message': 'Database not available'
            }), 503
        
        # Get from database
        signals = db_manager.get_recent_signals(symbol=symbol, limit=limit)
        
        # Validate each signal (NO MOCK DATA)
        validated_signals = []
        for sig in signals:
            if signal_validator and signal_validator.validate(sig):
                validated_signals.append(sig)
        
        return jsonify({
            'status': 'success',
            'data': validated_signals,
            'count': len(validated_signals),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/signals/consensus', methods=['GET'])
def get_consensus_signal():
    """
    Get consensus signal for a symbol
    Combines all 50+ layers for final decision
    """
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        
        if not signal_engine:
            return jsonify({
                'status': 'error',
                'message': 'Signal engine not available'
            }), 503
        
        # Generate consensus signal
        consensus = signal_engine.generate_consensus(symbol)
        
        if not consensus:
            return jsonify({
                'status': 'error',
                'message': f'No consensus available for {symbol}'
            }), 404
        
        # Validate (NO MOCK DATA)
        if signal_validator and not signal_validator.validate(consensus):
            logger.warning(f"⚠️ INVALID CONSENSUS SIGNAL for {symbol} - REJECTED")
            return jsonify({
                'status': 'error',
                'message': 'Signal validation failed'
            }), 400
        
        return jsonify({
            'status': 'success',
            'data': consensus,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error generating consensus: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/advisor/opportunities', methods=['GET'])
def get_advisor_opportunities():
    """
    Get AI advisor trade opportunities
    ADVISORY MODE - Bot never auto-trades
    """
    try:
        limit = int(request.args.get('limit', 10))
        min_confidence = float(request.args.get('min_confidence', 0.75))
        
        if not advisor_service:
            return jsonify({
                'status': 'error',
                'message': 'Advisor service not available'
            }), 503
        
        # Get top opportunities
        opportunities = advisor_service.get_top_opportunities(
            limit=limit,
            min_confidence=min_confidence
        )
        
        return jsonify({
            'status': 'success',
            'data': [opp.to_dict() for opp in opportunities],
            'count': len(opportunities),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/layers/scores', methods=['GET'])
def get_layer_scores():
    """
    Get current layer scores for a symbol
    Real-time analysis from 50+ layers
    """
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        
        with layer_scores_lock:
            if symbol not in layer_scores_cache:
                return jsonify({
                    'status': 'error',
                    'message': f'No layer scores for {symbol}'
                }), 404
            
            return jsonify({
                'status': 'success',
                'symbol': symbol,
                'scores': layer_scores_cache[symbol],
                'timestamp': time.time()
            })
        
    except Exception as e:
        logger.error(f"Error getting layer scores: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/performance/current', methods=['GET'])
def get_current_performance():
    """
    Get current performance metrics
    Win rate, PnL, Sharpe ratio, etc.
    """
    try:
        with performance_lock:
            return jsonify({
                'status': 'success',
                'data': performance_metrics,
                'timestamp': time.time()
            })
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """
    Get comprehensive system status
    """
    try:
        with health_lock:
            health = dict(system_health)
        
        with performance_lock:
            perf = dict(performance_metrics)
        
        with price_cache_lock:
            price_count = len(price_cache)
        
        return jsonify({
            'status': 'success',
            'data': {
                'health': health,
                'performance': perf,
                'websocket': {
                    'connected_clients': len(connected_clients),
                    'tracked_symbols': price_count
                },
                'services': {
                    'database': db_manager is not None,
                    'websocket_manager': ws_manager is not None,
                    'signal_engine': signal_engine is not None,
                    'advisor_service': advisor_service is not None,
                    'performance_engine': performance_engine is not None
                }
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    # Initialize services
    if not initialize_services():
        logger.error("Failed to initialize services")
        sys.exit(1)
    
    # Get port from environment (Railway)
    port = int(os.getenv('PORT', 8501))
    
    logger.info("="*80)
    logger.info(f"🚀 DEMIR AI DASHBOARD starting on port {port}")
    logger.info("="*80)
    
    # Run with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
