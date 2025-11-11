import os
from binance.client import Client

class PortfolioMonitoringLayer:
    """Monitor portfolio in real-time"""
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        
    def get_account_balance(self):
        """Get account balances"""
        try:
            account = self.client.get_account()
            balances = {}
            for asset in account['balances']:
                if float(asset['free']) > 0 or float(asset['locked']) > 0:
                    balances[asset['asset']] = {
                        'free': float(asset['free']),
                        'locked': float(asset['locked']),
                        'total': float(asset['free']) + float(asset['locked'])
                    }
            return balances
        except Exception as e:
            return {'error': str(e)}
    
    def get_portfolio_value(self):
        """Calculate portfolio value in USDT"""
        try:
            balances = self.get_account_balance()
            total_value = 0
            
            for symbol, balance in balances.items():
                if symbol == 'USDT':
                    total_value += balance['total']
                else:
                    try:
                        ticker = self.client.get_symbol_ticker(symbol=f"{symbol}USDT")
                        price = float(ticker['price'])
                        total_value += balance['total'] * price
                    except:
                        pass
            
            return {'total_value': total_value, 'currency': 'USDT'}
        except Exception as e:
            return {'error': str(e)}
    
    def analyze(self):
        """Full portfolio analysis"""
        try:
            balances = self.get_account_balance()
            portfolio_value = self.get_portfolio_value()
            
            return {
                'balances': balances,
                'portfolio_value': portfolio_value.get('total_value', 0),
                'assets_held': len(balances),
                'status': 'ok'
            }
        except Exception as e:
            return {'error': str(e), 'status': 'error'}

portfolio_layer = PortfolioMonitoringLayer()
```
