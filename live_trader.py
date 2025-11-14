#!/usr/bin/env python3
"""
🔱 DEMIR AI - Live Trader v1.0
Real Binance Futures Trading Execution

KURALLAR:
✅ Binance Futures API integration
✅ Market order execution
✅ Position management
✅ Real P&L tracking
✅ Error loud - all trades logged
✅ ZERO MOCK - real trades on testnet
"""

import os
import psycopg2
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
USE_TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'

SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
MAX_LEVERAGE = 10
POSITION_SIZE_PERCENT = 1.0

# ============================================================================
# LIVE TRADER
# ============================================================================

class LiveTrader:
    """Execute trades on Binance Futures"""
    
    def __init__(self):
        logger.info("🔄 Initializing Live Trader...")
        
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=USE_TESTNET)
            self.client.ping()
            
            logger.info("✅ Connected to Binance Futures")
            
            if USE_TESTNET:
                logger.warning("⚠️ Using TESTNET - no real money at risk")
            else:
                logger.critical("🚨 USING MAINNET - REAL MONEY AT RISK!")
            
            self.db_conn = psycopg2.connect(DATABASE_URL)
            self.open_orders = {}
            
        except Exception as e:
            logger.critical(f"❌ Initialization failed: {e}")
            raise
    
    def get_account_balance(self) -> Dict:
        """Get account balance and margin info"""
        try:
            account = self.client.futures_account()
            
            total_balance = float(account['totalWalletBalance'])
            available_balance = float(account['availableBalance'])
            
            return {
                'total': total_balance,
                'available': available_balance,
                'used': total_balance - available_balance
            }
        
        except Exception as e:
            logger.error(f"❌ Balance fetch failed: {e}")
            return {}
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                                stop_loss: float) -> Tuple[float, float]:
        """Calculate position size based on risk"""
        try:
            balance = self.get_account_balance()
            available = balance.get('available', 0)
            
            if available <= 0:
                logger.warning("⚠️ Insufficient balance")
                return 0, 0
            
            # Risk amount (1% of available)
            risk_amount = available * (POSITION_SIZE_PERCENT / 100)
            
            # Distance to stop loss
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                logger.warning("⚠️ Invalid stop loss")
                return 0, 0
            
            # Position size in contracts
            position_size = risk_amount / price_diff
            
            # Respect max leverage
            max_position = available / entry_price * MAX_LEVERAGE
            position_size = min(position_size, max_position)
            
            # Minimum position size (0.001 BTC for BTCUSDT, etc.)
            min_size = 0.001
            
            if position_size < min_size:
                logger.warning(f"⚠️ Position size too small: {position_size}")
                return 0, 0
            
            # Round to exchange precision
            position_size = round(position_size, 4)
            
            logger.info(f"📍 Calculated position size: {position_size}")
            return position_size, risk_amount
        
        except Exception as e:
            logger.error(f"❌ Position size calculation failed: {e}")
            return 0, 0
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """Place market order"""
        try:
            logger.info(f"⚡ Placing {side} order: {symbol} x{quantity}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            logger.info(f"✅ Order placed: Order ID {order['orderId']}")
            
            return order
        
        except BinanceAPIException as e:
            logger.error(f"❌ Order failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    def set_stop_loss(self, symbol: str, quantity: float, 
                     stop_price: float) -> Optional[Dict]:
        """Set stop loss order"""
        try:
            logger.info(f"🛑 Setting SL for {symbol} at {stop_price}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price,
                timeInForce='GTC'
            )
            
            logger.info(f"✅ Stop loss set: Order ID {order['orderId']}")
            return order
        
        except Exception as e:
            logger.error(f"❌ Stop loss failed: {e}")
            return None
    
    def set_take_profit(self, symbol: str, quantity: float, 
                       price: float) -> Optional[Dict]:
        """Set take profit order"""
        try:
            logger.info(f"🎯 Setting TP for {symbol} at {price}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='TAKE_PROFIT_MARKET',
                quantity=quantity,
                stopPrice=price,
                timeInForce='GTC'
            )
            
            logger.info(f"✅ Take profit set: Order ID {order['orderId']}")
            return order
        
        except Exception as e:
            logger.error(f"❌ Take profit failed: {e}")
            return None
    
    def get_open_positions(self) -> list:
        """Get all open positions"""
        try:
            positions = self.client.futures_position_information()
            
            open_positions = [p for p in positions if float(p['positionAmt']) != 0]
            
            logger.info(f"✅ Found {len(open_positions)} open positions")
            return open_positions
        
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            return []
    
    def close_position(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Close an open position"""
        try:
            logger.info(f"🔴 Closing {symbol} position x{quantity}")
            
            # Get current position
            positions = self.get_open_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position:
                logger.warning(f"⚠️ No open position for {symbol}")
                return None
            
            # Close with opposite side
            side = 'SELL' if float(position['positionAmt']) > 0 else 'BUY'
            
            order = self.place_market_order(symbol, side, abs(quantity))
            
            if order:
                logger.info(f"✅ Position closed: {symbol}")
            
            return order
        
        except Exception as e:
            logger.error(f"❌ Close position failed: {e}")
            return None
    
    def execute_trade_from_signal(self, symbol: str, signal: int, 
                                  entry_price: float) -> Dict:
        """
        Execute trade based on signal
        signal: 1=BUY, 0=SELL
        """
        try:
            side = 'BUY' if signal == 1 else 'SELL'
            
            logger.info(f"🚀 Executing {side} trade for {symbol}...")
            
            # Calculate SL/TP
            sl_price = entry_price * 0.99 if signal == 1 else entry_price * 1.01
            tp_price = entry_price * 1.02 if signal == 1 else entry_price * 0.98
            
            # Calculate position size
            position_size, risk_amount = self.calculate_position_size(
                symbol, entry_price, sl_price
            )
            
            if position_size <= 0:
                logger.warning(f"⚠️ Invalid position size")
                return {'status': 'failed', 'reason': 'Invalid position size'}
            
            # Place market order
            order = self.place_market_order(symbol, side, position_size)
            
            if not order:
                return {'status': 'failed', 'reason': 'Order execution failed'}
            
            # Set SL/TP
            self.set_stop_loss(symbol, position_size, sl_price)
            self.set_take_profit(symbol, position_size, tp_price)
            
            # Save to database
            cur = self.db_conn.cursor()
            
            insert_query = """
                INSERT INTO manual_trades
                (entry_time, symbol, entry_price, quantity, tp_price, sl_price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cur.execute(insert_query, (
                datetime.now(),
                symbol,
                entry_price,
                position_size,
                tp_price,
                sl_price,
                'OPEN'
            ))
            
            self.db_conn.commit()
            cur.close()
            
            logger.info(f"✅ Trade executed: {side} {symbol} x{position_size}")
            
            return {
                'status': 'success',
                'side': side,
                'symbol': symbol,
                'quantity': position_size,
                'entry_price': entry_price,
                'stop_loss': sl_price,
                'take_profit': tp_price,
                'order_id': order['orderId']
            }
        
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            return {'status': 'failed', 'reason': str(e)}
    
    def close(self):
        """Close connections"""
        if self.db_conn:
            self.db_conn.close()
        logger.info("✅ Trader closed")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        logger.info("=" * 80)
        logger.info("🚀 DEMIR AI - LIVE TRADER v1.0")
        logger.info("=" * 80)
        
        trader = LiveTrader()
        
        # Show account info
        balance = trader.get_account_balance()
        logger.info(f"📊 Account Balance: ${balance.get('total', 0):.2f}")
        
        # Get open positions
        positions = trader.get_open_positions()
        logger.info(f"📍 Open Positions: {len(positions)}")
        
        logger.info("✅ Trader ready for trading")
        
        trader.close()
    
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
