import os
from binance.client import Client
from binance.exceptions import BinanceAPIException

class LiveOrderExecutionLayer:
    """Execute live orders on Binance"""
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.test_mode = True  # START IN TEST MODE!
        
    def place_limit_order(self, symbol, side, quantity, price):
        """Place limit order (TEST MODE by default)"""
        try:
            if self.test_mode:
                # Test order
                order = self.client.create_test_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
                return {'test': True, 'status': 'test_success', 'order': order}
            else:
                # LIVE order - CAUTION!
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
                return {'test': False, 'status': 'order_placed', 'order': order}
        except BinanceAPIException as e:
            return {'error': str(e), 'status': 'error'}
    
    def place_market_order(self, symbol, side, quantity):
        """Place market order (TEST MODE by default)"""
        try:
            if self.test_mode:
                order = self.client.create_test_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=quantity
                )
                return {'test': True, 'status': 'test_success'}
            else:
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=quantity
                )
                return {'test': False, 'status': 'order_placed', 'order_id': order['orderId']}
        except Exception as e:
            return {'error': str(e), 'status': 'error'}
    
    def get_open_orders(self, symbol=None):
        """Get all open orders"""
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            return {'open_orders': len(orders), 'orders': orders}
        except Exception as e:
            return {'error': str(e)}
    
    def cancel_order(self, symbol, order_id):
        """Cancel order"""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return {'status': 'cancelled', 'result': result}
        except Exception as e:
            return {'error': str(e)}
    
    def analyze(self, action='check', symbol='BTCUSDT'):
        """Analyze and execute orders"""
        if action == 'check':
            return self.get_open_orders(symbol)
        return {'status': 'ready', 'test_mode': self.test_mode}

execution_layer = LiveOrderExecutionLayer()
```
