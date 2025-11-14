#!/usr/bin/env python3
"""
🔱 DEMIR AI - Position Tracker v1.0
HAFTA 10: Real-time Position Monitoring & Management

KURALLAR:
✅ Track all open positions
✅ Monitor profit/loss in real-time
✅ Alert on SL/TP hits
✅ Update position status
✅ Database sync
✅ Error loud - all positions logged
"""

import os
import psycopg2
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

# ============================================================================
# POSITION MONITOR
# ============================================================================

class PositionMonitor:
    """Monitor open positions"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            query = """
                SELECT 
                    id,
                    symbol,
                    entry_time,
                    entry_price,
                    quantity,
                    tp_price,
                    sl_price,
                    status
                FROM manual_trades
                WHERE status = 'OPEN'
                ORDER BY entry_time DESC
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            positions = []
            for _, row in df.iterrows():
                positions.append({
                    'id': row['id'],
                    'symbol': row['symbol'],
                    'entry_time': row['entry_time'],
                    'entry_price': float(row['entry_price']),
                    'quantity': float(row['quantity']),
                    'tp_price': float(row['tp_price']),
                    'sl_price': float(row['sl_price']),
                    'status': row['status']
                })
            
            logger.info(f"✅ Found {len(positions)} open positions")
            return positions
        
        except Exception as e:
            logger.error(f"❌ Failed to get open positions: {e}")
            return []
    
    def calculate_position_pnl(self, position: Dict, current_price: float) -> Dict:
        """Calculate P&L for position"""
        try:
            entry_price = position['entry_price']
            quantity = position['quantity']
            tp_price = position['tp_price']
            sl_price = position['sl_price']
            
            # P&L calculation
            pnl = (current_price - entry_price) * quantity
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
            
            # Distance to targets
            dist_to_tp = (tp_price - current_price) / tp_price * 100
            dist_to_sl = (current_price - sl_price) / sl_price * 100
            
            # Status
            if current_price >= tp_price:
                status = 'TP_HIT'
                alert = f"🎯 {position['symbol']} TP hit at ${current_price:.2f}"
            elif current_price <= sl_price:
                status = 'SL_HIT'
                alert = f"🛑 {position['symbol']} SL hit at ${current_price:.2f}"
            else:
                status = 'ACTIVE'
                alert = None
            
            logger.info(f"📊 {position['symbol']}: ${pnl:.2f} ({pnl_percent:.2f}%) | TP: {dist_to_tp:.2f}% | SL: {dist_to_sl:.2f}%")
            
            return {
                'position_id': position['id'],
                'symbol': position['symbol'],
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'dist_to_tp': dist_to_tp,
                'dist_to_sl': dist_to_sl,
                'status': status,
                'alert': alert
            }
        
        except Exception as e:
            logger.error(f"❌ P&L calculation failed: {e}")
            return {}
    
    def update_position_price(self, position_id: int, current_price: float):
        """Update position with current price"""
        try:
            cur = self.db_conn.cursor()
            
            update_query = """
                UPDATE manual_trades
                SET last_price = %s, last_update = %s
                WHERE id = %s
            """
            
            cur.execute(update_query, (current_price, datetime.now(), position_id))
            self.db_conn.commit()
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to update position: {e}")
    
    def close_position_on_target(self, position_id: int, close_reason: str, exit_price: float, pnl: float):
        """Close position when SL/TP hit"""
        try:
            cur = self.db_conn.cursor()
            
            update_query = """
                UPDATE manual_trades
                SET 
                    exit_time = %s,
                    exit_price = %s,
                    pnl = %s,
                    status = 'CLOSED',
                    close_reason = %s
                WHERE id = %s
            """
            
            cur.execute(update_query, (
                datetime.now(),
                exit_price,
                pnl,
                close_reason,
                position_id
            ))
            
            self.db_conn.commit()
            logger.info(f"✅ Position {position_id} closed: {close_reason}")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to close position: {e}")

# ============================================================================
# PRICE FETCHER
# ============================================================================

class CurrentPriceFetcher:
    """Fetch current prices"""
    
    def __init__(self):
        from binance.client import Client
        
        self.client = Client()
    
    def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for symbols"""
        try:
            prices = {}
            
            for symbol in symbols:
                try:
                    ticker = self.client.get_symbol_ticker(symbol=symbol)
                    prices[symbol] = float(ticker['price'])
                    logger.info(f"💹 {symbol}: ${prices[symbol]:.2f}")
                except Exception as e:
                    logger.error(f"❌ Failed to get price for {symbol}: {e}")
            
            return prices
        
        except Exception as e:
            logger.error(f"❌ Price fetching failed: {e}")
            return {}

# ============================================================================
# ALERT MANAGER
# ============================================================================

class AlertManager:
    """Manage position alerts"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def create_alert(self, position_id: int, alert_type: str, message: str):
        """Create alert for position"""
        try:
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO position_alerts
                (position_id, alert_type, message, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            
            cur.execute(insert_query, (
                position_id,
                alert_type,
                message,
                datetime.now()
            ))
            
            self.db_conn.commit()
            logger.info(f"🚨 Alert created: {message}")
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to create alert: {e}")
    
    def get_pending_alerts(self) -> List[Dict]:
        """Get unacknowledged alerts"""
        try:
            query = """
                SELECT 
                    id, position_id, alert_type, message, timestamp
                FROM position_alerts
                WHERE acknowledged = FALSE
                ORDER BY timestamp DESC
                LIMIT 10
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            
            alerts = []
            for _, row in df.iterrows():
                alerts.append({
                    'id': row['id'],
                    'position_id': row['position_id'],
                    'alert_type': row['alert_type'],
                    'message': row['message'],
                    'timestamp': row['timestamp']
                })
            
            return alerts
        
        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: int):
        """Mark alert as acknowledged"""
        try:
            cur = self.db_conn.cursor()
            
            update_query = """
                UPDATE position_alerts
                SET acknowledged = TRUE, acknowledged_at = %s
                WHERE id = %s
            """
            
            cur.execute(update_query, (datetime.now(), alert_id))
            self.db_conn.commit()
            cur.close()
        
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"❌ Failed to acknowledge alert: {e}")

# ============================================================================
# POSITION STATISTICS
# ============================================================================

class PositionStatistics:
    """Calculate position statistics"""
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def get_position_stats(self) -> Dict:
        """Get overall position statistics"""
        try:
            query = """
                SELECT
                    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open_positions,
                    SUM(CASE WHEN status = 'OPEN' THEN (last_price - entry_price) * quantity ELSE 0 END) as unrealized_pnl,
                    AVG(CASE WHEN status = 'CLOSED' AND pnl > 0 THEN pnl ELSE NULL END) as avg_win,
                    AVG(CASE WHEN status = 'CLOSED' AND pnl < 0 THEN pnl ELSE NULL END) as avg_loss
                FROM manual_trades
            """
            
            df = pd.read_sql_query(query, self.db_conn)
            row = df.iloc[0]
            
            stats = {
                'open_positions': int(row['open_positions']),
                'unrealized_pnl': float(row['unrealized_pnl']) if row['unrealized_pnl'] else 0,
                'avg_win': float(row['avg_win']) if row['avg_win'] else 0,
                'avg_loss': float(row['avg_loss']) if row['avg_loss'] else 0
            }
            
            logger.info(f"📊 Position Stats: Open={stats['open_positions']}, Unrealized=${stats['unrealized_pnl']:.2f}")
            
            return stats
        
        except Exception as e:
            logger.error(f"❌ Stats calculation failed: {e}")
            return {}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - POSITION TRACKER (HAFTA 10)")
        logger.info("=" * 80)
        
        db_conn = psycopg2.connect(DATABASE_URL)
        
        monitor = PositionMonitor(db_conn)
        price_fetcher = CurrentPriceFetcher()
        alert_mgr = AlertManager(db_conn)
        stats = PositionStatistics(db_conn)
        
        # Get open positions
        positions = monitor.get_open_positions()
        
        if not positions:
            logger.info("✅ No open positions")
            db_conn.close()
            return
        
        # Get current prices
        logger.info("\n💹 Fetching current prices...")
        prices = price_fetcher.get_prices(SYMBOLS)
        
        # Monitor each position
        logger.info("\n📊 Monitoring positions...")
        for position in positions:
            symbol = position['symbol']
            
            if symbol not in prices:
                logger.warning(f"⚠️ No price for {symbol}")
                continue
            
            current_price = prices[symbol]
            pnl_data = monitor.calculate_position_pnl(position, current_price)
            
            # Update position
            monitor.update_position_price(position['id'], current_price)
            
            # Check alerts
            if pnl_data['status'] == 'TP_HIT':
                monitor.close_position_on_target(
                    position['id'],
                    'TP_HIT',
                    current_price,
                    pnl_data['pnl']
                )
                alert_mgr.create_alert(position['id'], 'TP_HIT', pnl_data['alert'])
            
            elif pnl_data['status'] == 'SL_HIT':
                monitor.close_position_on_target(
                    position['id'],
                    'SL_HIT',
                    current_price,
                    pnl_data['pnl']
                )
                alert_mgr.create_alert(position['id'], 'SL_HIT', pnl_data['alert'])
        
        # Get statistics
        logger.info("\n📈 Position statistics...")
        position_stats = stats.get_position_stats()
        
        # Get pending alerts
        logger.info("\n🚨 Pending alerts...")
        pending_alerts = alert_mgr.get_pending_alerts()
        logger.info(f"✅ {len(pending_alerts)} pending alerts")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ POSITION TRACKING COMPLETED")
        logger.info("=" * 80)
        
        db_conn.close()
    
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: {e}")
        raise

if __name__ == "__main__":
    main()
