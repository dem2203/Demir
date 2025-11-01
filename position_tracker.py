"""
🔱 DEMIR AI TRADING BOT - POSITION TRACKER v1.0
PHASE 3.4: Manuel Trade Tracking + Real-time PNL
Date: 1 Kasım 2025

ÖZELLİKLER:
✅ Manuel trade tracking (Futures positions)
✅ Real-time PNL calculation (Binance price API)
✅ Open/Close position updates
✅ Win/Loss automatic calculation
✅ Position status management
"""

import sqlite3
from datetime import datetime
import requests


class PositionTracker:
    """
    Position Tracker - Manuel trade tracking for Futures
    
    Tracks open positions and calculates real-time PNL
    No API Key required - uses public Binance price API
    """
    
    def __init__(self, db_path='trades.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize position tracking table"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Position tracker table
        c.execute('''
            CREATE TABLE IF NOT EXISTS position_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                position_size REAL,
                stop_loss REAL,
                take_profit REAL,
                opened_at TEXT,
                closed_at TEXT,
                exit_price REAL,
                pnl_usd REAL,
                pnl_pct REAL,
                status TEXT,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def mark_position_opened(self, trade_id):
        """
        Mark AI trade as opened in Binance
        
        Args:
            trade_id: Trade ID from trades table
            
        Returns:
            Success boolean
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get trade details
            c.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
            trade = c.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
            
            if not trade:
                print(f"⚠️ Trade ID {trade_id} not found!")
                conn.close()
                return False
            
            # Parse trade details (assuming trade table structure)
            # Adjust indices based on your actual trades table schema
            symbol = trade[2]  # Assuming symbol is at index 2
            signal = trade[3]  # Assuming signal is at index 3
            entry_price = trade[7]  # Assuming entry_price at index 7
            stop_loss = trade[8]  # Assuming stop_loss at index 8
            position_size_usd = trade[10]  # Assuming position_size_usd at index 10
            
            # Insert into position tracker
            c.execute("""
                INSERT INTO position_tracker 
                (trade_id, symbol, side, entry_price, position_size, stop_loss, opened_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id,
                symbol,
                signal,  # LONG or SHORT
                entry_price,
                position_size_usd,
                stop_loss,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'OPEN'
            ))
            
            # Update trade status to OPENED
            c.execute("UPDATE trades SET status = ? WHERE id = ?", ('OPENED', trade_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Position opened! Trade ID #{trade_id} | {symbol} {signal}")
            return True
            
        except Exception as e:
            print(f"❌ Error marking position opened: {str(e)}")
            return False
    
    def get_open_positions(self):
        """
        Get all open positions with real-time PNL
        
        Returns:
            List of dicts with position details + current PNL
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("SELECT * FROM position_tracker WHERE status = 'OPEN'")
            positions = c.fetchall()
            conn.close()
            
            if not positions:
                return []
            
            # Calculate real-time PNL for each position
            position_list = []
            
            for pos in positions:
                pos_id, trade_id, symbol, side, entry_price, position_size, stop_loss, take_profit, opened_at, closed_at, exit_price, pnl_usd, pnl_pct, status = pos
                
                # Get current price from Binance
                current_price = self._get_current_price(symbol)
                
                if current_price > 0:
                    # Calculate real-time PNL
                    if side == 'LONG':
                        pnl_pct_rt = ((current_price - entry_price) / entry_price) * 100
                        pnl_usd_rt = (current_price - entry_price) * (position_size / entry_price)
                    else:  # SHORT
                        pnl_pct_rt = ((entry_price - current_price) / entry_price) * 100
                        pnl_usd_rt = (entry_price - current_price) * (position_size / entry_price)
                    
                    # Distance to SL/TP
                    if side == 'LONG':
                        sl_distance = ((current_price - stop_loss) / current_price) * 100
                    else:
                        sl_distance = ((stop_loss - current_price) / current_price) * 100
                    
                    position_list.append({
                        'id': pos_id,
                        'trade_id': trade_id,
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'position_size': position_size,
                        'stop_loss': stop_loss,
                        'pnl_usd': pnl_usd_rt,
                        'pnl_pct': pnl_pct_rt,
                        'sl_distance_pct': sl_distance,
                        'opened_at': opened_at,
                        'status': 'OPEN'
                    })
            
            return position_list
            
        except Exception as e:
            print(f"❌ Error getting open positions: {str(e)}")
            return []
    
    def close_position(self, position_id, exit_price):
        """
        Close position and calculate final PNL
        
        Args:
            position_id: Position tracker ID
            exit_price: Exit price (manual input)
            
        Returns:
            Success boolean
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get position details
            c.execute("SELECT * FROM position_tracker WHERE id = ?", (position_id,))
            pos = c.fetchone()
            
            if not pos:
                print(f"⚠️ Position ID {position_id} not found!")
                conn.close()
                return False
            
            pos_id, trade_id, symbol, side, entry_price, position_size, stop_loss, take_profit, opened_at, closed_at, old_exit_price, old_pnl_usd, old_pnl_pct, status = pos
            
            # Calculate final PNL
            if side == 'LONG':
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                pnl_usd = (exit_price - entry_price) * (position_size / entry_price)
            else:  # SHORT
                pnl_pct = ((entry_price - exit_price) / entry_price) * 100
                pnl_usd = (entry_price - exit_price) * (position_size / entry_price)
            
            # Determine Win/Loss/Breakeven
            if pnl_usd > 1:
                result = 'WIN'
            elif pnl_usd < -1:
                result = 'LOSS'
            else:
                result = 'BREAKEVEN'
            
            # Update position tracker
            c.execute("""
                UPDATE position_tracker 
                SET exit_price = ?, pnl_usd = ?, pnl_pct = ?, 
                    closed_at = ?, status = ?
                WHERE id = ?
            """, (
                exit_price,
                pnl_usd,
                pnl_pct,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'CLOSED',
                position_id
            ))
            
            # Update corresponding trade in trades table
            c.execute("""
                UPDATE trades 
                SET status = ?, pnl_usd = ?, pnl_pct = ?
                WHERE id = ?
            """, (result, pnl_usd, pnl_pct, trade_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Position closed! {symbol} {side} | PNL: ${pnl_usd:.2f} ({pnl_pct:.2f}%) | {result}")
            return True
            
        except Exception as e:
            print(f"❌ Error closing position: {str(e)}")
            return False
    
    def get_pending_signals(self):
        """
        Get AI trades that haven't been opened yet
        
        Returns:
            List of pending trades (PENDING status)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT id, symbol, signal, confidence, final_score, 
                       entry_price, stop_loss, position_size_usd, timestamp
                FROM trades 
                WHERE status = 'PENDING' AND signal IN ('LONG', 'SHORT')
                ORDER BY timestamp DESC
            """)
            
            pending = c.fetchall()
            conn.close()
            
            if not pending:
                return []
            
            pending_list = []
            for trade in pending:
                trade_id, symbol, signal, confidence, final_score, entry_price, stop_loss, position_size_usd, timestamp = trade
                
                pending_list.append({
                    'id': trade_id,
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': confidence * 100,
                    'score': final_score,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'position_size': position_size_usd,
                    'timestamp': timestamp
                })
            
            return pending_list
            
        except Exception as e:
            print(f"❌ Error getting pending signals: {str(e)}")
            return []
    
    def _get_current_price(self, symbol):
        """
        Get current price from Binance public API
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            
        Returns:
            Current price (float)
        """
        try:
            url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            else:
                return 0.0
                
        except Exception as e:
            print(f"⚠️ Error fetching price for {symbol}: {str(e)}")
            return 0.0
    
    def get_position_summary(self):
        """
        Get summary of all positions
        
        Returns:
            Dict with summary stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Open positions
            c.execute("SELECT COUNT(*) FROM position_tracker WHERE status = 'OPEN'")
            open_count = c.fetchone()[0]
            
            # Closed positions
            c.execute("SELECT COUNT(*) FROM position_tracker WHERE status = 'CLOSED'")
            closed_count = c.fetchone()[0]
            
            # Total PNL (closed positions only)
            c.execute("SELECT SUM(pnl_usd) FROM position_tracker WHERE status = 'CLOSED'")
            total_pnl = c.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'open_positions': open_count,
                'closed_positions': closed_count,
                'total_pnl': total_pnl
            }
            
        except Exception as e:
            print(f"❌ Error getting position summary: {str(e)}")
            return {'open_positions': 0, 'closed_positions': 0, 'total_pnl': 0.0}


# TEST
if __name__ == "__main__":
    print("🔱 DEMIR AI POSITION TRACKER - Test Mode")
    
    tracker = PositionTracker()
    
    # Test: Get pending signals
    pending = tracker.get_pending_signals()
    print(f"\n📊 Pending Signals: {len(pending)}")
    
    # Test: Get open positions
    open_pos = tracker.get_open_positions()
    print(f"\n📊 Open Positions: {len(open_pos)}")
    
    # Test: Get summary
    summary = tracker.get_position_summary()
    print(f"\n📊 Summary: {summary}")
