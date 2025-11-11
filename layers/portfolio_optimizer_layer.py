import numpy as np
import pandas as pd
import os
from binance.client import Client
from scipy.optimize import minimize

class PortfolioOptimizerLayer:
    """Kelly Criterion + Sharpe Ratio portfolio optimization"""
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.risk_free_rate = 0.02 / 252  # Annual to daily
        
    def get_real_data(self, symbols=['BTCUSDT', 'ETHUSDT'], interval='1d', limit=100):
        """Fetch REAL historical data"""
        data = {}
        try:
            for symbol in symbols:
                klines = self.client.get_historical_klines(symbol, interval, limit=limit)
                closes = np.array([float(k[4]) for k in klines])
                returns = np.diff(closes) / closes[:-1]
                data[symbol] = returns
        except Exception as e:
            print(f"Portfolio: Data error: {e}")
        return data
    
    def kelly_criterion(self, win_rate, avg_win, avg_loss):
        """Calculate Kelly Criterion for position sizing"""
        if avg_loss == 0:
            return 0.0
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_loss
        # Cap at 25% (for safety)
        return min(max(kelly, 0), 0.25)
    
    def calculate_sharpe_ratio(self, returns, portfolio_weight):
        """Calculate Sharpe Ratio"""
        portfolio_return = np.mean(returns) * np.dot(portfolio_weight, 1)
        portfolio_std = np.std(returns) * np.sum(portfolio_weight ** 2) ** 0.5
        sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_std + 1e-8)
        return sharpe
    
    def optimize_weights(self, returns_dict):
        """Optimize portfolio weights"""
        symbols = list(returns_dict.keys())
        n_assets = len(symbols)
        
        if n_assets == 0:
            return {}
        
        # Calculate correlation matrix
        returns_matrix = np.column_stack([returns_dict[s] for s in symbols])
        cov_matrix = np.cov(returns_matrix.T)
        mean_returns = np.mean(returns_matrix, axis=0)
        
        # Objective: minimize negative Sharpe
        def neg_sharpe(weights):
            return -self.calculate_sharpe_ratio(returns_matrix, weights)
        
        # Constraints
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Optimize
        result = minimize(neg_sharpe, np.array([1/n_assets]*n_assets), 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        optimal_weights = {}
        for i, symbol in enumerate(symbols):
            optimal_weights[symbol] = float(result.x[i])
        
        return optimal_weights
    
    def analyze(self, symbols=['BTCUSDT', 'ETHUSDT']):
        """Analyze portfolio optimization"""
        try:
            # Get REAL data
            returns_dict = self.get_real_data(symbols)
            
            if not returns_dict:
                return {'status': 'error', 'message': 'No data'}
            
            # Optimize weights
            optimal_weights = self.optimize_weights(returns_dict)
            
            # Calculate metrics
            kelly_estimates = {}
            for symbol in symbols:
                # Simulate: 55% win rate, 1% avg win, 1% avg loss
                kelly = self.kelly_criterion(0.55, 0.01, 0.01)
                kelly_estimates[symbol] = kelly
            
            return {
                'optimal_weights': optimal_weights,
                'kelly_estimates': kelly_estimates,
                'allocation_method': 'Sharpe Ratio Optimized',
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Portfolio optimizer error: {e}")
            return {'status': 'error', 'message': str(e)[:50]}

# Global instance
portfolio_layer = PortfolioOptimizerLayer()
