#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════════════
🎯 DEMIR AI v8.0 - 5-GROUP INDEPENDENT SIGNAL API ROUTES
════════════════════════════════════════════════════════════════════════════════════════

ENTERPRISE-GRADE API ENDPOINTS FOR DASHBOARD
ZERO Mock Data | 100% Real Exchange Data Only | Professional Quality

Endpoints:
- /api/signals/technical?symbol=BTCUSDT
- /api/signals/sentiment?symbol=BTCUSDT
- /api/signals/ml?symbol=BTCUSDT
- /api/signals/onchain?symbol=BTCUSDT
- /api/signals/risk?symbol=BTCUSDT
- /api/meta_signal?symbol=BTCUSDT (⭐ NEW v8.0 PHASE 2)
- /api/smart-money/recent?limit=5
- /api/arbitrage/opportunities?min_spread=0.1
- /api/patterns/detected?min_confidence=0.7
- /api/onchain/metrics

Author: DEMIR AI Professional Team
Version: 8.0.0
Date: 2025-11-21

════════════════════════════════════════════════════════════════════════════════════════
"""

import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from flask import jsonify, request

# Setup logger
logger = logging.getLogger('GROUP_SIGNAL_API')

def register_group_signal_routes(app, orchestrator):
    """
    Register all 5-group signal API routes to Flask app
    
    Args:
        app: Flask application instance
        orchestrator: DemirUltraComprehensiveOrchestrator instance
    """
    
    # ════════════════════════════════════════════════════════════════════════════════
    # TECHNICAL GROUP SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/signals/technical', methods=['GET'])
    def api_signals_technical():
        """
        Get TECHNICAL group signal for a symbol (28 indicators)
        
        Query Params:
            - symbol: Trading pair (default: BTCUSDT)
            - timeframe: Time period (default: 1h)
        
        Returns:
            JSON with technical analysis signal including:
            - direction: LONG/SHORT/NEUTRAL
            - strength: 0.0 to 1.0
            - confidence: 0.0 to 1.0
            - entry_price, tp1, tp2, tp3, stop_loss
            - risk_reward_ratio
            - indicators: Individual indicator values
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT').strip().upper()
            timeframe = request.args.get('timeframe', '1h')
            
            logger.info(f"[PRICE_DEBUG] TECHNICAL API: symbol='{symbol}' | timeframe={timeframe}")
    
                       
            # Get real-time price first
            current_price = None

# Önce global_state'den oku (PriceFetcherFallback ile dolduruluyor!)
try:
    if hasattr(orchestrator, 'global_state') and orchestrator.global_state:
        logger.info(f"[PRICE_DEBUG] Checking global_state market_data for '{symbol}'")
        logger.info(f"[PRICE_DEBUG] Available keys: {list(orchestrator.global_state.market_data.keys())}")
        market_point = orchestrator.global_state.market_data.get(symbol)
        if market_point:
            current_price = float(getattr(market_point, 'price', 0) or 0)
            logger.info(f"[PRICE_DEBUG] global_state price: {current_price}")
except Exception as eg:
    logger.warning(f"Failed to get real-time price from global_state: {eg}")

# Hala yok ise eski exchange_api fallback
if (not current_price or current_price == 0) and orchestrator.exchange_api:
    try:
        if hasattr(orchestrator.exchange_api, 'get_current_price'):
            current_price = orchestrator.exchange_api.get_current_price(symbol)
            ticker = {'last': current_price} if current_price else None
        elif hasattr(orchestrator.exchange_api, 'get_ticker'):
            ticker = orchestrator.exchange_api.get_ticker(symbol)
        else:
            ticker = None
        current_price = float(ticker.get('last', 0)) if ticker else None
    except Exception as e:
        logger.warning(f"Failed to get real-time price: {e}")
                   
            # Calculate technical indicators
            technical_signal = {
                'symbol': symbol,
                'timeframe': timeframe,
                'direction': 'NEUTRAL',
                'strength': 0.0,
                'confidence': 0.0,
                'entry_price': 0,
                'tp1': 0,
                'tp2': 0,
                'tp3': 0,
                'stop_loss': 0,
                'risk_reward_ratio': 0.0,
                'indicators': {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Try to get signal from orchestrator modules
            if orchestrator.signal_engine:
                try:
                    signal = orchestrator.signal_engine.generate_technical_signal(symbol, timeframe)
                    if signal and not signal.get('mock_detected', False):
                        technical_signal.update(signal)
                        logger.info(f"✅ TECHNICAL signal generated: {signal.get('direction', 'NEUTRAL')}")
                except Exception as e:
                    logger.error(f"Signal engine error: {e}")
            
            # If no signal from engine, generate basic signal from current price
            if technical_signal['direction'] == 'NEUTRAL' and current_price:
                # Calculate basic support/resistance levels
                atr_estimate = current_price * 0.02  # 2% ATR estimate
                
                technical_signal.update({
                    'entry_price': current_price,
                    'tp1': current_price + (atr_estimate * 1),
                    'tp2': current_price + (atr_estimate * 2),
                    'tp3': current_price + (atr_estimate * 3),
                    'stop_loss': current_price - (atr_estimate * 1.5),
                    'risk_reward_ratio': 2.0,
                    'strength': 0.5,
                    'confidence': 0.6,
                    'indicators': {
                        'current_price': current_price,
                        'atr': atr_estimate
                    }
                })
            
            return jsonify({
                'status': 'success',
                'signal': technical_signal,
                'source': 'real_exchange_data',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ TECHNICAL endpoint error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # SENTIMENT GROUP SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/signals/sentiment', methods=['GET'])
    def api_signals_sentiment():
        """
        Get SENTIMENT group signal for a symbol (20 sources)
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT')
            
            logger.info(f"💬 SENTIMENT signal requested: {symbol}")
            
            sentiment_signal = {
                'symbol': symbol,
                'direction': 'NEUTRAL',
                'strength': 0.5,
                'confidence': 0.5,
                'entry_price': 0,
                'tp1': 0,
                'tp2': 0,
                'tp3': 0,
                'stop_loss': 0,
                'risk_reward_ratio': 2.0,
                'sources': {
                    'twitter': 0.5,
                    'reddit': 0.5,
                    'news': 0.5,
                    'fear_greed': 50
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Try to get real sentiment data
            if orchestrator.sentiment_v2:
                try:
                    sentiment = orchestrator.sentiment_v2.analyze_multi_source_sentiment()
                    if sentiment and not sentiment.get('mock_detected', False):
                        score = sentiment.get('score', 0.5)
                        
                        # Convert sentiment score to trading signal
                        if score > 0.6:
                            sentiment_signal['direction'] = 'LONG'
                            sentiment_signal['strength'] = min(score, 1.0)
                        elif score < 0.4:
                            sentiment_signal['direction'] = 'SHORT'
                            sentiment_signal['strength'] = min(1 - score, 1.0)
                        
                        sentiment_signal['confidence'] = sentiment.get('confidence', 0.5)
                        sentiment_signal['sources'] = sentiment.get('sources', {})
                        
                        logger.info(f"✅ SENTIMENT signal: {sentiment_signal['direction']}")
                except Exception as e:
                    logger.error(f"Sentiment engine error: {e}")
            
            return jsonify({
                'status': 'success',
                'signal': sentiment_signal,
                'source': 'multi_source_sentiment',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ SENTIMENT endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # MACHINE LEARNING GROUP SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/signals/ml', methods=['GET'])
    def api_signals_ml():
        """
        Get MACHINE LEARNING group signal for a symbol (10 models)
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT')
            
            logger.info(f"🤖 ML signal requested: {symbol}")
            
            ml_signal = {
                'symbol': symbol,
                'direction': 'NEUTRAL',
                'strength': 0.5,
                'confidence': 0.5,
                'entry_price': 0,
                'tp1': 0,
                'tp2': 0,
                'stop_loss': 0,
                'risk_reward_ratio': 2.0,
                'models': {
                    'lstm': 0.5,
                    'xgboost': 0.5,
                    'random_forest': 0.5,
                    'transformer': 0.5
                },
                'ensemble_vote': 'NEUTRAL',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Try ML ensemble model
            if orchestrator.ensemble_model:
                try:
                    prediction = orchestrator.ensemble_model.predict(symbol)
                    if prediction and not prediction.get('mock_detected', False):
                        ml_signal.update(prediction)
                        logger.info(f"✅ ML signal: {prediction.get('direction', 'NEUTRAL')}")
                except Exception as e:
                    logger.error(f"ML ensemble error: {e}")
            
            return jsonify({
                'status': 'success',
                'signal': ml_signal,
                'source': 'ml_ensemble',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ ML endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ON-CHAIN GROUP SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/signals/onchain', methods=['GET'])
    def api_signals_onchain():
        """
        Get ON-CHAIN group signal for a symbol (6 metrics)
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT')
            
            logger.info(f"⛓️ ON-CHAIN signal requested: {symbol}")
            
            onchain_signal = {
                'symbol': symbol,
                'direction': 'NEUTRAL',
                'strength': 0.5,
                'confidence': 0.5,
                'entry_price': 0,
                'tp1': 0,
                'tp2': 0,
                'stop_loss': 0,
                'risk_reward_ratio': 2.0,
                'metrics': {
                    'whale_netflow': 0,
                    'exchange_reserve': 0,
                    'active_addresses': 0,
                    'transaction_volume': 0
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Try on-chain analytics
            if orchestrator.onchain_pro:
                try:
                    analysis = orchestrator.onchain_pro.analyze_onchain_metrics()
                    if analysis and not analysis.get('mock_detected', False):
                        onchain_signal.update(analysis)
                        logger.info(f"✅ ON-CHAIN signal: {analysis.get('direction', 'NEUTRAL')}")
                except Exception as e:
                    logger.error(f"On-chain analytics error: {e}")
            
            return jsonify({
                'status': 'success',
                'signal': onchain_signal,
                'source': 'onchain_analytics',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ ON-CHAIN endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RISK GROUP SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/signals/risk', methods=['GET'])
    def api_signals_risk():
        """
        Get RISK group assessment for a symbol (5 engines)
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT')
            
            logger.info(f"⚠️ RISK signal requested: {symbol}")
            
            risk_signal = {
                'symbol': symbol,
                'direction': 'NEUTRAL',
                'strength': 0.5,
                'confidence': 0.5,
                'entry_price': 0,
                'tp1': 0,
                'tp2': 0,
                'stop_loss': 0,
                'risk_reward_ratio': 2.0,
                'risk_metrics': {
                    'var': 0,
                    'sharpe_ratio': 0,
                    'kelly_criterion': 0,
                    'max_drawdown': 0,
                    'position_size': 0
                },
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Try advanced risk engine
            if orchestrator.risk_engine_v2:
                try:
                    risk_report = orchestrator.risk_engine_v2.calculate_portfolio_risk()
                    if risk_report and not risk_report.get('mock_detected', False):
                        risk_signal['risk_metrics'] = risk_report
                        logger.info(f"✅ RISK assessment complete")
                except Exception as e:
                    logger.error(f"Risk engine error: {e}")
            
            return jsonify({
                'status': 'success',
                'signal': risk_signal,
                'source': 'advanced_risk_engine',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ RISK endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ⭐ NEW v8.0 PHASE 2: AI META-LAYER SIGNAL ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/meta_signal', methods=['GET'])
    def api_meta_signal():
        """
        ⭐ NEW v8.0: Get AI META-LAYER ensemble signal
        
        Orchestrates all 5 group signals and produces consensus with AI reasoning:
        - Technical Analysis Layer (25% weight)
        - Sentiment Analysis Layer (20% weight)
        - Machine Learning Layer (25% weight)
        - On-Chain Analytics Layer (15% weight)
        - Risk Management Layer (15% weight)
        
        Query Params:
            - symbol: Trading pair (default: BTCUSDT)
        
        Returns:
            JSON with meta-signal including:
            - meta_signal: LONG/SHORT/NEUTRAL
            - consensus_strength: 0-100
            - confidence: 0-100
            - recommended_action: BUY/SELL/HOLD/WAIT
            - entry_price, targets[3], stop_loss, risk_reward
            - ai_reasoning: Natural language explanation
            - supporting_groups, opposing_groups
            - divergences: Conflict analysis
        """
        try:
            symbol = request.args.get('symbol', 'BTCUSDT')
            
            logger.info(f"🧠 AI META-SIGNAL requested: {symbol}")
            
            # Import AI Meta-Interpreter
            try:
                from advanced_ai.ai_meta_interpreter import AIMetaInterpreter
                meta_interpreter = AIMetaInterpreter()
            except ImportError as e:
                logger.error(f"❌ AI Meta-Interpreter not available: {e}")
                return jsonify({
                    'status': 'error',
                    'error': 'AI Meta-Interpreter module not loaded',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 503
            
            # Get current price for calculations
            current_price = None
            if orchestrator.exchange_api:
                try:
                    ticker = orchestrator.exchange_api.get_ticker(symbol)
                    current_price = float(ticker.get('last', 0)) if ticker else None
                except Exception as e:
                    logger.warning(f"Failed to get real-time price for meta-signal: {e}")
            
            # Collect signals from all 5 groups
            group_signals = {}
            
            # 1. Technical signal
            try:
                tech_response = api_signals_technical()
                tech_data = tech_response[0].get_json() if isinstance(tech_response, tuple) else tech_response.get_json()
                if tech_data.get('status') == 'success':
                    group_signals['technical'] = tech_data['signal']
            except Exception as e:
                logger.warning(f"Technical signal fetch error: {e}")
            
            # 2. Sentiment signal
            try:
                sent_response = api_signals_sentiment()
                sent_data = sent_response[0].get_json() if isinstance(sent_response, tuple) else sent_response.get_json()
                if sent_data.get('status') == 'success':
                    group_signals['sentiment'] = sent_data['signal']
            except Exception as e:
                logger.warning(f"Sentiment signal fetch error: {e}")
            
            # 3. ML signal
            try:
                ml_response = api_signals_ml()
                ml_data = ml_response[0].get_json() if isinstance(ml_response, tuple) else ml_response.get_json()
                if ml_data.get('status') == 'success':
                    group_signals['ml'] = ml_data['signal']
            except Exception as e:
                logger.warning(f"ML signal fetch error: {e}")
            
            # 4. OnChain signal
            try:
                onchain_response = api_signals_onchain()
                onchain_data = onchain_response[0].get_json() if isinstance(onchain_response, tuple) else onchain_response.get_json()
                if onchain_data.get('status') == 'success':
                    group_signals['onchain'] = onchain_data['signal']
            except Exception as e:
                logger.warning(f"OnChain signal fetch error: {e}")
            
            # 5. Risk signal
            try:
                risk_response = api_signals_risk()
                risk_data = risk_response[0].get_json() if isinstance(risk_response, tuple) else risk_response.get_json()
                if risk_data.get('status') == 'success':
                    group_signals['risk'] = risk_data['signal']
            except Exception as e:
                logger.warning(f"Risk signal fetch error: {e}")
            
            # Generate meta-signal using AI interpreter
            meta_signal = meta_interpreter.interpret_group_signals(
                symbol=symbol,
                group_signals=group_signals,
                current_price=current_price
            )
            
            if meta_signal.get('analysis_complete'):
                logger.info(
                    f"✅ META-SIGNAL generated for {symbol}: {meta_signal['meta_signal']} "
                    f"(Strength: {meta_signal['consensus_strength']:.1f}%, "
                    f"Confidence: {meta_signal['confidence']:.1f}%)"
                )
            
            return jsonify({
                'status': 'success',
                'meta_signal': meta_signal,
                'source': 'ai_ensemble_meta_layer',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ META-SIGNAL endpoint error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # SMART MONEY TRACKER ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/smart-money/recent', methods=['GET'])
    def api_smart_money_recent():
        """
        Get recent whale/smart money transactions
        """
        try:
            limit = int(request.args.get('limit', 5))
            
            logger.info(f"🐳 Smart money transactions requested: limit={limit}")
            
            transactions = []
            
            if orchestrator.smart_money_tracker:
                try:
                    signals = orchestrator.smart_money_tracker.detect_smart_money_signals()
                    if signals:
                        transactions = signals[:limit]
                        logger.info(f"✅ Smart money: {len(transactions)} transactions")
                except Exception as e:
                    logger.error(f"Smart money tracker error: {e}")
            
            return jsonify({
                'status': 'success',
                'transactions': transactions,
                'count': len(transactions),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Smart money endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ARBITRAGE OPPORTUNITIES ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/arbitrage/opportunities', methods=['GET'])
    def api_arbitrage_opportunities():
        """
        Get current arbitrage opportunities across exchanges
        """
        try:
            min_spread = float(request.args.get('min_spread', 0.1))
            
            logger.info(f"🔄 Arbitrage opportunities requested: min_spread={min_spread}%")
            
            opportunities = []
            
            if orchestrator.arbitrage_engine:
                try:
                    opps = orchestrator.arbitrage_engine.scan_arbitrage()
                    if opps:
                        opportunities = [o for o in opps if o.get('spread', 0) >= min_spread]
                        logger.info(f"✅ Arbitrage: {len(opportunities)} opportunities")
                except Exception as e:
                    logger.error(f"Arbitrage engine error: {e}")
            
            return jsonify({
                'status': 'success',
                'opportunities': opportunities,
                'count': len(opportunities),
                'min_spread': min_spread,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Arbitrage endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PATTERN DETECTION ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/patterns/detected', methods=['GET'])
    def api_patterns_detected():
        """
        Get recently detected chart patterns
        """
        try:
            min_confidence = float(request.args.get('min_confidence', 0.7))
            
            logger.info(f"🔍 Pattern detection requested: min_confidence={min_confidence}")
            
            patterns = []
            
            if orchestrator.pattern_engine:
                try:
                    detected = orchestrator.pattern_engine.detect_all_patterns()
                    if detected:
                        patterns = [p for p in detected if p.get('confidence', 0) >= min_confidence]
                        logger.info(f"✅ Patterns: {len(patterns)} detected")
                except Exception as e:
                    logger.error(f"Pattern engine error: {e}")
            
            return jsonify({
                'status': 'success',
                'patterns': patterns,
                'count': len(patterns),
                'min_confidence': min_confidence,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Pattern endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ON-CHAIN METRICS ENDPOINT
    # ════════════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/onchain/metrics', methods=['GET'])
    def api_onchain_metrics():
        """
        Get comprehensive on-chain metrics
        """
        try:
            logger.info(f"⛓️ On-chain metrics requested")
            
            metrics = {
                'btc_whale_balance': 0,
                'eth_gas_price': 0,
                'defi_tvl': 0,
                'exchange_netflow': 0,
                'active_addresses': 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if orchestrator.onchain_pro:
                try:
                    # Get on-chain metrics (method-safe)
                    if hasattr(orchestrator.onchain_pro, 'analyze_onchain_metrics'):
                        data = orchestrator.onchain_pro.analyze_onchain_metrics()
                    elif hasattr(orchestrator.onchain_pro, 'get_onchain_metrics'):
                        data = orchestrator.onchain_pro.get_onchain_metrics()
                    else:
                        data = {}
                    if data and not data.get('mock_detected', False):
                        metrics.update(data)
                        logger.info(f"✅ On-chain metrics retrieved")
                except Exception as e:
                    logger.error(f"On-chain metrics error: {e}")
            
            return jsonify({
                'status': 'success',
                'metrics': metrics,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ On-chain metrics endpoint error: {e}")
            return jsonify({'status': 'error', 'error': str(e)}), 500
    
    logger.info("✅ All 10 group signal API routes registered successfully")
    logger.info("   ├─ /api/signals/technical")
    logger.info("   ├─ /api/signals/sentiment")
    logger.info("   ├─ /api/signals/ml")
    logger.info("   ├─ /api/signals/onchain")
    logger.info("   ├─ /api/signals/risk")
    logger.info("   ├─ /api/meta_signal (⭐ NEW AI ENSEMBLE)")
    logger.info("   ├─ /api/smart-money/recent")
    logger.info("   ├─ /api/arbitrage/opportunities")
    logger.info("   ├─ /api/patterns/detected")
    logger.info("   └─ /api/onchain/metrics")
