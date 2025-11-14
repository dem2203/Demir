#!/usr/bin/env python3
"""
🔱 DEMIR AI - trader.py (HAFTA 10)
REAL BINANCE FUTURES TRADING - STRICT, ZERO MOCK
"""

import logging
import os
from typing import Dict, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException
import psycopg2

logger = logging.getLogger(__name__)

class FuturesTrader:
    """Live Binance Futures trading - STRICT"""
    
    def __init__(self, api_key: str, api_secret: str, db_url: str, testnet: bool = True):
        if not api_key or not api_secret:
            raise ValueError("❌ Missing Binance keys")
        
        self.client = Client(api_key, api_secret)
        self.testnet = testnet
        self.db_url = db_url
        self.position_size_pct = 0.02  # 2% per trade
        self.max_daily_loss = 0.05  # 5% daily loss limit
        
        logger.info(f"✅ FuturesTrader initialized (testnet={testnet})")
    
    def get_account_balance(self) -> float:
        """Get account balance - STRICT"""
        try:
            account = self.client.futures_account()
            if not account or 'totalWalletBalance' not in account:
                raise ValueError("❌ Failed to fetch account")
            
            balance = float(account['totalWalletBalance'])
            if balance <= 0:
                raise ValueError(f"❌ Invalid balance: {balance}")
            
            logger.info(f"✅ Balance: ${balance:.2f}")
            return balance
        except Exception as e:
            logger.critical(f"❌ Balance fetch failed: {e}")
            raise
    
    def calculate_position_size(self, entry_price: float, sl_price: float) -> float:
        """Calculate position size - STRICT"""
        try:
            balance = self.get_account_balance()
            risk_amount = balance * self.position_size_pct
            
            sl_distance = abs(entry_price - sl_price)
            if sl_distance <= 0:
                raise ValueError(f"❌ Invalid SL distance: {sl_distance}")
            
            position_size = risk_amount / sl_distance
            
            logger.info(f"✅ Position size: {position_size:.4f}")
            return position_size
        except Exception as e:
            logger.critical(f"❌ Position size calculation failed: {e}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place market order - STRICT"""
        try:
            if side not in ['BUY', 'SELL']:
                raise ValueError(f"❌ Invalid side: {side}")
            if quantity <= 0:
                raise ValueError(f"❌ Invalid quantity: {quantity}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            if not order or 'orderId' not in order:
                raise ValueError("❌ Order creation failed")
            
            logger.info(f"✅ Order placed: {side} {quantity} {symbol}")
            return order
        except Exception as e:
            logger.critical(f"❌ Market order failed: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float) -> Dict:
        """Place limit order (TP/SL) - STRICT"""
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=price
            )
            
            logger.info(f"✅ Limit order: {side} {quantity} @ {price}")
            return order
        except Exception as e:
            logger.critical(f"❌ Limit order failed: {e}")
            raise
    
    def execute_trade(self, symbol: str, entry_price: float, tp1: float, 
                     tp2: float, sl: float) -> Dict:
        """Execute full trade: market entry + TP + SL - STRICT"""
        try:
            logger.info(f"🚀 Executing trade: {symbol}")
            
            # Calculate position size
            position_size = self.calculate_position_size(entry_price, sl)
            tp1_size = position_size * 0.5
            tp2_size = position_size * 0.5
            
            # Market entry
            entry_order = self.place_market_order(symbol, 'BUY', position_size)
            
            # TP1 order
            tp1_order = self.place_limit_order(symbol, 'SELL', tp1_size, tp1)
            
            # TP2 order
            tp2_order = self.place_limit_order(symbol, 'SELL', tp2_size, tp2)
            
            # SL order
            sl_order = self.place_limit_order(symbol, 'SELL', position_size, sl)
            
            # Store to database
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO manual_trades (symbol, entry_price, entry_time, 
                    tp1_price, tp2_price, sl_price, position_size, status)
                VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
            """, (symbol, entry_price, tp1, tp2, sl, position_size, 'open'))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Trade executed: {symbol}")
            return {
                'entry': entry_order,
                'tp1': tp1_order,
                'tp2': tp2_order,
                'sl': sl_order
            }
        except Exception as e:
            logger.critical(f"❌ Trade execution failed: {e}")
            raise
    
    def monitor_position(self, symbol: str) -> Dict:
        """Monitor open position - STRICT"""
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            if not positions:
                raise ValueError(f"❌ No position data for {symbol}")
            
            position = positions[0]
            
            pnl = float(position.get('unRealizedProfit', 0))
            logger.info(f"📊 {symbol} P&L: ${pnl:.2f}")
            
            return {
                'symbol': symbol,
                'size': float(position['positionAmt']),
                'entry_price': float(position['entryPrice']),
                'pnl': pnl
            }
        except Exception as e:
            logger.error(f"❌ Position monitoring failed: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("✅ Futures Trader ready")
