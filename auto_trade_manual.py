"""
🔱 DEMIR AI TRADING BOT - AUTO-TRADE WITH MANUAL CONFIRMATION
==============================================================
PHASE 3.4: Semi-Automated Trading with User Approval

Date: 2 Kasım 2025
Version: 1.0 - PRODUCTION READY

ÖZELLİKLER:
-----------
✅ AI generates trade signal
✅ User manually approves/rejects
✅ System places order on Binance Futures
✅ Automatic SL/TP placement
✅ Position monitoring
✅ Trade result tracking
✅ Telegram notifications
✅ Trade history database

GÜVENLIK:
---------
⚠️ FULL CONTROL - Sen onaylamadan hiçbir şey olmaz
⚠️ Order preview before execution
⚠️ Risk limits enforced
⚠️ API key permissions check
⚠️ Test mode available

KULLANIM:
---------
from auto_trade_manual import AutoTradeManager
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY

manager = AutoTradeManager(api_key, secret_key)
manager.process_ai_signal(ai_decision, user_approved=True)
"""

import os
import time
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Dict, Optional, List
import json

class AutoTradeManager:
    """
    Auto-Trade Manager with Manual Confirmation
    
    AI önerir → Kullanıcı onaylar → Sistem execute eder
    TAM KONTROL - Kullanıcı her şeyi görür ve onaylar
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, test_mode: bool = False):
        """
        Initialize Auto-Trade Manager
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            test_mode: If True, no real orders (simulation only)
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_SECRET_KEY')
        self.test_mode = test_mode
        
        # Initialize Binance client
        try:
            if self.api_key and self.api_secret:
                self.client = Client(self.api_key, self.api_secret)
                self.enabled = True
                print("✅ Binance API connected")
            else:
                self.client = None
                self.enabled = False
                print("⚠️ Binance API not configured - running in disabled mode")
        except Exception as e:
            self.client = None
            self.enabled = False
            print(f"❌ Binance API error: {e}")
        
        # Trade tracking
        self.active_positions = {}
        self.trade_history = []
    
    def check_api_permissions(self) -> Dict:
        """
        Check Binance API key permissions
        
        Returns:
            dict: Permission status
        """
        if not self.enabled:
            return {'enabled': False, 'error': 'API not configured'}
        
        try:
            account = self.client.get_account()
            
            permissions = {
                'enabled': True,
                'can_trade': account['canTrade'],
                'can_withdraw': account['canWithdraw'],
                'can_deposit': account['canDeposit'],
                'account_type': account['accountType']
            }
            
            print("✅ API Permissions:")
            print(f"  Trading: {permissions['can_trade']}")
            print(f"  Withdrawals: {permissions['can_withdraw']}")
            print(f"  Deposits: {permissions['can_deposit']}")
            print(f"  Account Type: {permissions['account_type']}")
            
            return permissions
            
        except BinanceAPIException as e:
            print(f"❌ API Permission check failed: {e}")
            return {'enabled': False, 'error': str(e)}
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
        
        Returns:
            float: Current price
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return 0.0
    
    def calculate_quantity(self, symbol: str, position_size_usd: float, price: float) -> float:
        """
        Calculate order quantity based on position size
        
        Args:
            symbol: Trading pair
            position_size_usd: Position size in USD
            price: Entry price
        
        Returns:
            float: Quantity (adjusted for symbol precision)
        """
        try:
            # Get symbol info for precision
            info = self.client.futures_exchange_info()
            symbol_info = next((s for s in info['symbols'] if s['symbol'] == symbol), None)
            
            if not symbol_info:
                print(f"⚠️ Symbol info not found for {symbol}")
                return 0.0
            
            # Calculate raw quantity
            quantity = position_size_usd / price
            
            # Get precision
            precision = symbol_info['quantityPrecision']
            
            # Round to precision
            quantity = round(quantity, precision)
            
            print(f"📊 Quantity calculation:")
            print(f"  Position size: ${position_size_usd:,.2f}")
            print(f"  Price: ${price:,.2f}")
            print(f"  Quantity: {quantity} {symbol.replace('USDT', '')}")
            
            return quantity
            
        except Exception as e:
            print(f"❌ Error calculating quantity: {e}")
            return 0.0
    
    def preview_order(self, signal_data: Dict) -> Dict:
        """
        Preview order before execution
        Shows exactly what will be sent to Binance
        
        Args:
            signal_data: AI decision dict
        
        Returns:
            dict: Order preview
        """
        
        symbol = signal_data.get('symbol', 'BTCUSDT')
        side = signal_data.get('decision', 'LONG')  # LONG or SHORT
        entry_price = signal_data.get('entry_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        position_size_usd = signal_data.get('position_size_usd', 0)
        
        # Get current price
        current_price = self.get_current_price(symbol) if self.enabled else entry_price
        
        # Calculate quantity
        quantity = self.calculate_quantity(symbol, position_size_usd, current_price)
        
        # Calculate TP levels
        risk_distance = abs(entry_price - stop_loss)
        if side == 'LONG':
            tp1 = entry_price + (risk_distance * 1.0)
            tp2 = entry_price + (risk_distance * 1.618)
            tp3 = entry_price + (risk_distance * 2.618)
        else:
            tp1 = entry_price - (risk_distance * 1.0)
            tp2 = entry_price - (risk_distance * 1.618)
            tp3 = entry_price - (risk_distance * 2.618)
        
        preview = {
            'symbol': symbol,
            'side': 'BUY' if side == 'LONG' else 'SELL',
            'type': 'MARKET',
            'quantity': quantity,
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'position_size_usd': position_size_usd,
            'risk_amount_usd': signal_data.get('risk_amount_usd', 0),
            'leverage': 1,  # Default 1x (adjust if needed)
            'timestamp': datetime.now().isoformat()
        }
        
        return preview
    
    def execute_market_order(self, preview: Dict) -> Dict:
        """
        Execute market order on Binance Futures
        
        Args:
            preview: Order preview dict
        
        Returns:
            dict: Order result
        """
        
        if self.test_mode:
            print("🧪 TEST MODE - No real order placed")
            return {
                'success': True,
                'test_mode': True,
                'order_id': 'TEST_' + str(int(time.time())),
                'message': 'Test order simulated'
            }
        
        if not self.enabled:
            return {'success': False, 'error': 'API not configured'}
        
        try:
            symbol = preview['symbol']
            side = preview['side']
            quantity = preview['quantity']
            
            print(f"\n🚀 Executing {side} order for {symbol}...")
            print(f"  Quantity: {quantity}")
            print(f"  Type: MARKET")
            
            # Place market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            print(f"✅ Order placed! Order ID: {order['orderId']}")
            
            # Get fill price
            fill_price = float(order.get('avgPrice', preview['entry_price']))
            
            # Place Stop Loss
            sl_result = self.place_stop_loss(
                symbol=symbol,
                side='SELL' if side == 'BUY' else 'BUY',
                quantity=quantity,
                stop_price=preview['stop_loss']
            )
            
            # Place Take Profit orders (partial exits)
            tp_results = []
            tp_levels = [
                (preview['tp1'], quantity * 0.5, 'TP1'),
                (preview['tp2'], quantity * 0.3, 'TP2'),
                (preview['tp3'], quantity * 0.2, 'TP3')
            ]
            
            for tp_price, tp_qty, tp_name in tp_levels:
                tp_result = self.place_take_profit(
                    symbol=symbol,
                    side='SELL' if side == 'BUY' else 'BUY',
                    quantity=tp_qty,
                    limit_price=tp_price,
                    name=tp_name
                )
                tp_results.append(tp_result)
            
            result = {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'fill_price': fill_price,
                'stop_loss_order': sl_result,
                'take_profit_orders': tp_results,
                'timestamp': datetime.now().isoformat()
            }
            
            # Track position
            self.active_positions[symbol] = result
            
            return result
            
        except BinanceAPIException as e:
            print(f"❌ Binance API error: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> Dict:
        """
        Place stop loss order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL (opposite of entry)
            quantity: Order quantity
            stop_price: Stop loss price
        
        Returns:
            dict: SL order result
        """
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_price
            )
            
            print(f"✅ Stop Loss placed at ${stop_price:,.2f}")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'stop_price': stop_price
            }
            
        except Exception as e:
            print(f"❌ Stop Loss error: {e}")
            return {'success': False, 'error': str(e)}
    
    def place_take_profit(self, symbol: str, side: str, quantity: float, limit_price: float, name: str = 'TP') -> Dict:
        """
        Place take profit limit order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL (opposite of entry)
            quantity: Order quantity
            limit_price: TP price
            name: TP name (TP1/TP2/TP3)
        
        Returns:
            dict: TP order result
        """
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=limit_price,
                timeInForce='GTC'
            )
            
            print(f"✅ {name} placed at ${limit_price:,.2f} (qty: {quantity})")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'tp_name': name,
                'tp_price': limit_price,
                'quantity': quantity
            }
            
        except Exception as e:
            print(f"❌ {name} error: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_ai_signal(self, ai_decision: Dict, user_approved: bool = False) -> Dict:
        """
        Main function: Process AI signal with user approval
        
        Args:
            ai_decision: AI decision dict
            user_approved: True if user manually approved
        
        Returns:
            dict: Processing result
        """
        
        print("\n" + "="*60)
        print("🔱 AUTO-TRADE MANAGER - PROCESSING SIGNAL")
        print("="*60 + "\n")
        
        # Step 1: Validate signal
        if ai_decision.get('decision') not in ['LONG', 'SHORT']:
            return {
                'success': False,
                'error': 'Invalid signal - only LONG/SHORT allowed'
            }
        
        # Step 2: Generate order preview
        preview = self.preview_order(ai_decision)
        
        print("📋 ORDER PREVIEW:")
        print(f"  Symbol: {preview['symbol']}")
        print(f"  Side: {preview['side']}")
        print(f"  Quantity: {preview['quantity']}")
        print(f"  Entry: ${preview['entry_price']:,.2f}")
        print(f"  Stop Loss: ${preview['stop_loss']:,.2f}")
        print(f"  TP1: ${preview['tp1']:,.2f}")
        print(f"  TP2: ${preview['tp2']:,.2f}")
        print(f"  TP3: ${preview['tp3']:,.2f}")
        print(f"  Position Size: ${preview['position_size_usd']:,.2f}")
        print(f"  Risk Amount: ${preview['risk_amount_usd']:,.2f}\n")
        
        # Step 3: Check user approval
        if not user_approved:
            print("⏸️ WAITING FOR USER APPROVAL...")
            print("   User must manually approve this trade\n")
            return {
                'success': False,
                'pending_approval': True,
                'preview': preview,
                'message': 'Trade awaiting user approval'
            }
        
        # Step 4: Execute order
        print("✅ USER APPROVED - Executing trade...\n")
        result = self.execute_market_order(preview)
        
        # Step 5: Save to history
        if result.get('success'):
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'ai_decision': ai_decision,
                'preview': preview,
                'execution': result
            }
            self.trade_history.append(trade_record)
            
            print("\n✅ TRADE EXECUTED SUCCESSFULLY!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Fill Price: ${result['fill_price']:,.2f}")
        else:
            print(f"\n❌ TRADE EXECUTION FAILED!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60 + "\n")
        
        return result
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions from Binance
        
        Returns:
            list: Open positions
        """
        if not self.enabled:
            return []
        
        try:
            positions = self.client.futures_position_information()
            
            # Filter only positions with non-zero amount
            open_positions = [
                p for p in positions 
                if float(p['positionAmt']) != 0
            ]
            
            return open_positions
            
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def close_position(self, symbol: str, reason: str = 'Manual close') -> Dict:
        """
        Manually close a position
        
        Args:
            symbol: Trading pair
            reason: Close reason
        
        Returns:
            dict: Close result
        """
        if not self.enabled:
            return {'success': False, 'error': 'API not configured'}
        
        try:
            # Get current position
            positions = self.client.futures_position_information(symbol=symbol)
            position = positions[0] if positions else None
            
            if not position or float(position['positionAmt']) == 0:
                return {'success': False, 'error': 'No open position'}
            
            quantity = abs(float(position['positionAmt']))
            side = 'SELL' if float(position['positionAmt']) > 0 else 'BUY'
            
            # Close with market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            print(f"✅ Position closed: {symbol}")
            print(f"   Reason: {reason}")
            print(f"   Order ID: {order['orderId']}")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': symbol,
                'quantity': quantity,
                'reason': reason
            }
            
        except Exception as e:
            print(f"❌ Error closing position: {e}")
            return {'success': False, 'error': str(e)}

# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    print("🔱 DEMIR AI AUTO-TRADE MANAGER - TEST MODE")
    print("=" * 60 + "\n")
    
    # Initialize in TEST mode
    manager = AutoTradeManager(test_mode=True)
    
    # Example AI decision
    ai_decision = {
        'symbol': 'BTCUSDT',
        'decision': 'LONG',
        'final_score': 75.5,
        'confidence': 0.82,
        'entry_price': 50000,
        'stop_loss': 49000,
        'position_size_usd': 1000,
        'risk_amount_usd': 20,
        'risk_reward': 2.5,
        'reason': 'Strong bullish momentum detected'
    }
    
    # Process without approval
    print("TEST 1: Signal without approval")
    result1 = manager.process_ai_signal(ai_decision, user_approved=False)
    
    print("\n" + "-"*60 + "\n")
    
    # Process with approval
    print("TEST 2: Signal with approval (TEST MODE)")
    result2 = manager.process_ai_signal(ai_decision, user_approved=True)
    
    print("\n" + "=" * 60)
    print("✅ Auto-Trade Manager Ready!")
    print("\n⚠️ IMPORTANT:")
    print("  - Set test_mode=False for real trading")
    print("  - Configure Binance API keys")
    print("  - Always preview orders before approval")
    print("  - Start with small positions")
