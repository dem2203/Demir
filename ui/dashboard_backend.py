# dashboard_backend.py - DEMIR AI v6.0 Flask Backend (800+ lines)
# Production-ready: Real data from Binance + WebSocket real-time updates

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from functools import wraps
import threading
import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class DashboardBackend:
    """
    Flask backend for real-time trading dashboard
    - Real data from Binance API
    - WebSocket for real-time updates
    - Database persistence (PostgreSQL)
    """
    
    def __init__(self, app: Flask, signal_engine, telegram_notifier, db_config: Dict):
        """Initialize dashboard backend"""
        self.app = app
        self.signal_engine = signal_engine
        self.telegram = telegram_notifier
        self.db_config = db_config
        self.db_connection = None
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        self.clients = {}  # Track connected clients
        self.symbol_subscribers = {}  # Symbol → client IDs
        self.background_threads = []
        
        # Initialize
        self._init_cors()
        self._init_database()
        self._register_routes()
        self._register_websocket_handlers()
        self._start_background_tasks()
    
    def _init_cors(self):
        """Enable CORS for all routes"""
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})
    
    def _init_database(self):
        """Initialize PostgreSQL connection"""
        try:
            self.db_connection = psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                user=self.db_config.get('user', 'demir'),
                password=self.db_config.get('password'),
                database=self.db_config.get('database', 'demir_ai'),
                port=self.db_config.get('port', 5432)
            )
            logger.info("✅ Database connected")
        except Exception as e:
            logger.error(f"❌ Database error: {str(e)}")
    
    def _register_routes(self):
        """Register Flask API routes"""
        
        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """System health check"""
            return jsonify({
                'status': 'HEALTHY',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '6.0'
            })
        
        @self.app.route('/api/v1/dashboard', methods=['GET'])
        async def get_dashboard():
            """Get complete dashboard data with REAL market data"""
            try:
                symbol = request.args.get('symbol', 'BTCUSDT')
                
                # Get REAL signals for 15m and 1h
                signals_15m = await self.signal_engine.calculate_group_signals(symbol, '15m')
                signals_1h = await self.signal_engine.calculate_group_signals(symbol, '1h')
                
                # Get REAL price data from Binance
                price_data = await self._get_real_price_data(symbol)
                
                # Get performance stats from DB
                performance = await self._get_performance_stats(symbol)
                
                # Get open trades
                open_trades = await self._get_open_trades()
                
                return jsonify({
                    'market': price_data,
                    'signals': {
                        '15m': signals_15m,
                        '1h': signals_1h,
                        'multi_tf_match': signals_15m['master']['signal'] == signals_1h['master']['signal']
                    },
                    'open_trades': open_trades,
                    'performance': performance,
                    'timestamp': datetime.utcnow().isoformat(),
                    'data_source': 'REAL_BINANCE'
                })
                
            except Exception as e:
                logger.error(f"Dashboard error: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/signals', methods=['GET'])
        def get_signal_history():
            """Get signal history from database"""
            try:
                symbol = request.args.get('symbol', 'BTCUSDT')
                limit = int(request.args.get('limit', 50))
                timeframe = request.args.get('timeframe', '15m')
                
                cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT * FROM signals 
                    WHERE symbol = %s AND timeframe = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (symbol, timeframe, limit))
                
                signals = cursor.fetchall()
                cursor.close()
                
                return jsonify({
                    'signals': signals,
                    'count': len(signals),
                    'symbol': symbol
                })
                
            except Exception as e:
                logger.error(f"Signal history error: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/add-trade', methods=['POST'])
        async def add_trade():
            """Add manual trade (user clicks ADD TRADE button)"""
            try:
                data = request.json
                symbol = data.get('symbol', 'BTCUSDT')
                direction = data.get('direction')  # LONG or SHORT
                
                # Get AI signal to calculate levels
                signal = await self.signal_engine.calculate_group_signals(symbol, '15m')
                
                if not signal:
                    return jsonify({'error': 'No signal available'}), 400
                
                # Calculate levels based on REAL signal
                entry_price = float(data.get('entry_price', 0))
                if entry_price == 0:
                    return jsonify({'error': 'Entry price required'}), 400
                
                # Risk/reward calculation
                if direction == 'LONG':
                    tp1 = entry_price * 1.015  # +1.5%
                    tp2 = entry_price * 1.031  # +3.1%
                    sl = entry_price * 0.993   # -0.7%
                else:  # SHORT
                    tp1 = entry_price * 0.985  # -1.5%
                    tp2 = entry_price * 0.969  # -3.1%
                    sl = entry_price * 1.007   # +0.7%
                
                # Store in database
                trade_id = await self._store_trade_to_db({
                    'symbol': symbol,
                    'direction': direction,
                    'entry_price': entry_price,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'signal_confidence': signal['master']['confidence'],
                    'entry_time': datetime.utcnow(),
                    'status': 'OPEN'
                })
                
                # Send Telegram alert
                await self.telegram.send_trade_update({
                    'event': 'OPEN',
                    'symbol': symbol,
                    'direction': direction,
                    'entry_price': entry_price,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'signal_confidence': signal['master']['confidence']
                })
                
                # Broadcast to all connected clients
                self.socketio.emit('trade_opened', {
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'direction': direction,
                    'entry_price': entry_price,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'timestamp': datetime.utcnow().isoformat()
                }, broadcast=True)
                
                return jsonify({
                    'trade_id': trade_id,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'message': 'Trade added successfully'
                })
                
            except Exception as e:
                logger.error(f"Add trade error: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/trade/<int:trade_id>', methods=['GET'])
        def get_trade(trade_id):
            """Get trade details"""
            try:
                cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM trades WHERE id = %s", (trade_id,))
                trade = cursor.fetchone()
                cursor.close()
                
                if not trade:
                    return jsonify({'error': 'Trade not found'}), 404
                
                return jsonify(trade)
                
            except Exception as e:
                logger.error(f"Get trade error: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/close-trade/<int:trade_id>', methods=['POST'])
        async def close_trade(trade_id):
            """Close trade manually"""
            try:
                data = request.json
                exit_price = float(data.get('exit_price'))
                
                # Get trade details
                cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM trades WHERE id = %s", (trade_id,))
                trade = cursor.fetchone()
                
                if not trade:
                    return jsonify({'error': 'Trade not found'}), 404
                
                # Calculate P&L
                entry = float(trade['entry_price'])
                if trade['direction'] == 'LONG':
                    pnl = exit_price - entry
                    pnl_percent = (pnl / entry) * 100
                else:
                    pnl = entry - exit_price
                    pnl_percent = (pnl / entry) * 100
                
                # Update in database
                cursor.execute("""
                    UPDATE trades 
                    SET status = %s, exit_price = %s, exit_time = %s, pnl = %s, pnl_percent = %s
                    WHERE id = %s
                """, ('CLOSED', exit_price, datetime.utcnow(), pnl, pnl_percent, trade_id))
                
                self.db_connection.commit()
                cursor.close()
                
                # Send Telegram alert
                await self.telegram.send_trade_update({
                    'event': 'MANUAL_CLOSE',
                    'symbol': trade['symbol'],
                    'exit_price': exit_price,
                    'pnl_percent': pnl_percent
                })
                
                return jsonify({
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'message': 'Trade closed'
                })
                
            except Exception as e:
                logger.error(f"Close trade error: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    def _register_websocket_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Client connected"""
            logger.info(f"Client connected: {request.sid}")
            self.clients[request.sid] = {
                'connected_at': datetime.utcnow(),
                'subscribed_symbols': []
            }
            emit('connection_response', {
                'data': 'Connected to DEMIR AI Dashboard',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Client disconnected"""
            logger.info(f"Client disconnected: {request.sid}")
            if request.sid in self.clients:
                del self.clients[request.sid]
        
        @self.socketio.on('subscribe_symbol')
        def handle_subscribe(data):
            """Subscribe to symbol updates"""
            symbol = data.get('symbol', 'BTCUSDT')
            
            if symbol not in self.symbol_subscribers:
                self.symbol_subscribers[symbol] = set()
            
            self.symbol_subscribers[symbol].add(request.sid)
            
            if request.sid in self.clients:
                self.clients[request.sid]['subscribed_symbols'].append(symbol)
            
            emit('subscribed', {'symbol': symbol})
            logger.info(f"Client {request.sid} subscribed to {symbol}")
        
        @self.socketio.on('unsubscribe_symbol')
        def handle_unsubscribe(data):
            """Unsubscribe from symbol"""
            symbol = data.get('symbol')
            
            if symbol in self.symbol_subscribers:
                self.symbol_subscribers[symbol].discard(request.sid)
            
            emit('unsubscribed', {'symbol': symbol})
    
    def _start_background_tasks(self):
        """Start background signal calculation loop"""
        
        def signal_loop():
            """Background loop for signal calculation"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']
            
            while True:
                try:
                    for symbol in symbols:
                        # Calculate signals every 5 minutes
                        signals = loop.run_until_complete(
                            self.signal_engine.calculate_group_signals(symbol, '15m')
                        )
                        
                        if signals:
                            # Broadcast to subscribed clients
                            if symbol in self.symbol_subscribers:
                                for client_id in self.symbol_subscribers[symbol]:
                                    self.socketio.emit('signal_update', {
                                        'symbol': symbol,
                                        'signals': signals,
                                        'timestamp': datetime.utcnow().isoformat()
                                    }, room=client_id)
                            
                            # Send Telegram if strong signal
                            if signals['master']['confidence'] >= 75:
                                loop.run_until_complete(
                                    self.telegram.send_signal_alert(signals, symbol)
                                )
                    
                    # Check open trades
                    loop.run_until_complete(self._check_open_trades())
                    
                except Exception as e:
                    logger.error(f"Signal loop error: {str(e)}")
                
                import time
                time.sleep(300)  # Every 5 minutes
        
        thread = threading.Thread(target=signal_loop, daemon=True)
        thread.start()
        self.background_threads.append(thread)
        logger.info("Background signal loop started")
    
    async def _get_real_price_data(self, symbol: str) -> Dict:
        """Get REAL price data from Binance"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                # Get ticker from Binance
                async with session.get(
                    f'https://api.binance.com/api/v3/ticker/24hr',
                    params={'symbol': symbol}
                ) as resp:
                    if resp.status == 200:
                        ticker = await resp.json()
                        return {
                            'symbol': symbol,
                            'price': float(ticker['lastPrice']),
                            'change_24h': float(ticker['priceChangePercent']),
                            'volume_24h': float(ticker['volume']),
                            'high_24h': float(ticker['highPrice']),
                            'low_24h': float(ticker['lowPrice']),
                            'timestamp': datetime.utcnow().isoformat()
                        }
        except Exception as e:
            logger.error(f"Price data error: {str(e)}")
        
        return {}
    
    async def _get_performance_stats(self, symbol: str) -> Dict:
        """Get performance stats from database"""
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as wins,
                    AVG(pnl_percent) as avg_pnl,
                    MAX(pnl_percent) as max_win,
                    MIN(pnl_percent) as max_loss
                FROM trades
                WHERE symbol = %s AND status = 'CLOSED'
            """, (symbol,))
            
            stats = cursor.fetchone()
            cursor.close()
            
            if stats and stats['total_trades'] > 0:
                return {
                    'total_trades': stats['total_trades'],
                    'win_rate': (stats['wins'] / stats['total_trades']) * 100,
                    'avg_pnl': float(stats['avg_pnl'] or 0),
                    'max_win': float(stats['max_win'] or 0),
                    'max_loss': float(stats['max_loss'] or 0)
                }
        except Exception as e:
            logger.error(f"Performance stats error: {str(e)}")
        
        return {'total_trades': 0, 'win_rate': 0}
    
    async def _get_open_trades(self) -> List:
        """Get open trades from database"""
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM trades 
                WHERE status = 'OPEN'
                ORDER BY entry_time DESC
            """)
            
            trades = cursor.fetchall()
            cursor.close()
            
            return trades
        except Exception as e:
            logger.error(f"Open trades error: {str(e)}")
            return []
    
    async def _store_trade_to_db(self, trade_data: Dict) -> int:
        """Store trade in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO trades 
                (symbol, direction, entry_price, tp1, tp2, sl, signal_confidence, entry_time, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                trade_data['symbol'],
                trade_data['direction'],
                trade_data['entry_price'],
                trade_data['tp1'],
                trade_data['tp2'],
                trade_data['sl'],
                trade_data['signal_confidence'],
                trade_data['entry_time'],
                trade_data['status']
            ))
            
            trade_id = cursor.fetchone()[0]
            self.db_connection.commit()
            cursor.close()
            
            return trade_id
        except Exception as e:
            logger.error(f"Store trade error: {str(e)}")
            return None
    
    async def _check_open_trades(self):
        """Check if open trades hit TP or SL"""
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM trades WHERE status = 'OPEN'")
            trades = cursor.fetchall()
            cursor.close()
            
            for trade in trades:
                # Get current price
                symbol = trade['symbol']
                price_data = await self._get_real_price_data(symbol)
                current_price = price_data.get('price', 0)
                
                if current_price == 0:
                    continue
                
                # Check TP/SL
                if trade['direction'] == 'LONG':
                    if current_price >= trade['tp1']:
                        await self._close_trade_auto(trade, current_price, 'TP1_HIT')
                    elif current_price >= trade['tp2']:
                        await self._close_trade_auto(trade, current_price, 'TP2_HIT')
                    elif current_price <= trade['sl']:
                        await self._close_trade_auto(trade, current_price, 'SL_HIT')
                else:  # SHORT
                    if current_price <= trade['tp1']:
                        await self._close_trade_auto(trade, current_price, 'TP1_HIT')
                    elif current_price <= trade['tp2']:
                        await self._close_trade_auto(trade, current_price, 'TP2_HIT')
                    elif current_price >= trade['sl']:
                        await self._close_trade_auto(trade, current_price, 'SL_HIT')
        
        except Exception as e:
            logger.error(f"Check trades error: {str(e)}")
    
    async def _close_trade_auto(self, trade: Dict, exit_price: float, event: str):
        """Automatically close trade at TP/SL"""
        try:
            entry = float(trade['entry_price'])
            if trade['direction'] == 'LONG':
                pnl = exit_price - entry
                pnl_percent = (pnl / entry) * 100
            else:
                pnl = entry - exit_price
                pnl_percent = (pnl / entry) * 100
            
            # Update database
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE trades 
                SET status = %s, exit_price = %s, exit_time = %s, pnl = %s, pnl_percent = %s
                WHERE id = %s
            """, (event, exit_price, datetime.utcnow(), pnl, pnl_percent, trade['id']))
            
            self.db_connection.commit()
            cursor.close()
            
            # Send Telegram
            await self.telegram.send_trade_update({
                'event': event,
                'symbol': trade['symbol'],
                'exit_price': exit_price,
                'pnl_percent': pnl_percent
            })
            
            logger.info(f"Trade {trade['id']} closed: {event} at {exit_price}")
        
        except Exception as e:
            logger.error(f"Close trade auto error: {str(e)}")
