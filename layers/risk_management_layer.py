import numpy as np
import os
from binance.client import Client

class RiskManagementLayer:
    """Dynamic risk management and position sizing"""
    
    def __init__(self, max_risk_per_trade=0.02, max_portfolio_risk=0.05):
        self.max_risk_per_trade = max_risk_per_trade  # 2% per trade
        self.max_portfolio_risk = max_portfolio_risk   # 5% max drawdown
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        
    def get_account_balance(self):
        """Get REAL account balance from Binance"""
        try:
            account = self.client.get_account()
            balances = {asset['asset']: float(asset['free']) for asset in account['balances']}
            usdt_balance = balances.get('USDT', 0.0)
            return usdt_balance
        except Exception as e:
            print(f"Risk: Balance error: {e}")
            return 0.0
    
    def calculate_position_size(self, entry_price, stop_loss, account_balance=None):
        """Calculate position size based on risk"""
        if account_balance is None:
            account_balance = self.get_account_balance()
        
        if account_balance <= 0:
            return 0.0
        
        risk_amount = account_balance * self.max_risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0.0
        
        position_size = risk_amount / price_risk
        return position_size
    
    def calculate_stop_loss(self, entry_price, atr_value, direction='long'):
        """Calculate stop loss using ATR"""
        if direction == 'long':
            stop_loss = entry_price - (atr_value * 1.5)
        else:
            stop_loss = entry_price + (atr_value * 1.5)
        return stop_loss
    
    def calculate_take_profit(self, entry_price, stop_loss, risk_reward_ratio=2.0, direction='long'):
        """Calculate take profit based on risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if direction == 'long':
            take_profit = entry_price + reward
        else:
            take_profit = entry_price - reward
        
        return take_profit
    
    def analyze(self, symbol='BTCUSDT', entry_price=None, direction='long'):
        """Analyze risk for a position"""
        try:
            if entry_price is None:
                # Get REAL current price
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                entry_price = float(ticker['price'])
            
            # Estimate ATR (simplified)
            account_balance = self.get_account_balance()
            atr = entry_price * 0.02  # 2% of price as rough ATR
            
            stop_loss = self.calculate_stop_loss(entry_price, atr, direction)
            take_profit = self.calculate_take_profit(entry_price, stop_loss, 2.0, direction)
            position_size = self.calculate_position_size(entry_price, stop_loss, account_balance)
            
            risk_amount = account_balance * self.max_risk_per_trade
            risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss)
            
            return {
                'entry_price': float(entry_price),
                'stop_loss': float(stop_loss),
                'take_profit': float(take_profit),
                'position_size': float(position_size),
                'risk_amount': float(risk_amount),
                'account_balance': float(account_balance),
                'risk_reward_ratio': float(risk_reward),
                'max_drawdown_percent': float(self.max_portfolio_risk * 100)
            }
            
        except Exception as e:
            print(f"Risk management error: {e}")
            return {'error': str(e), 'status': 'error'}

# Global instance
risk_layer = RiskManagementLayer()
