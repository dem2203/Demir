"""
🔱 DEMIR AI TRADING BOT - PORTFOLIO OPTIMIZER v1.0
PHASE 3.3: Kelly Criterion + Correlation + Multi-Coin Allocation
Date: 1 Kasım 2025

ÖZELLİKLER:
✅ Kelly Criterion Enhanced - Optimal position sizing
✅ Correlation Analysis - Coin'ler arası korelasyon matrisi
✅ Portfolio Allocation - Risk-balanced dağılım
✅ Multi-Coin Balancing - 3-5 coin optimal mix
✅ Diversification Score - Çeşitlendirme skoru
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta


class PortfolioOptimizer:
    """
    Portfolio Optimizer - Multi-coin portfolio için optimal allocation
    
    Kelly Criterion kullanarak position size optimize eder
    Correlation analysis ile diversification sağlar
    """
    
    def __init__(self, total_capital=10000, risk_per_trade=200):
        """
        Args:
            total_capital: Toplam portfolio sermayesi ($)
            risk_per_trade: Trade başına maksimum risk ($)
        """
        self.total_capital = total_capital
        self.risk_per_trade = risk_per_trade
        self.correlation_matrix = None
        
    def calculate_kelly_size(self, win_rate, avg_win, avg_loss):
        """
        Kelly Criterion ile optimal position size hesapla
        
        Formula: Kelly% = W - [(1-W) / R]
        W = Win rate (0-1)
        R = Win/Loss ratio
        
        Args:
            win_rate: Kazanma oranı (0-1)
            avg_win: Ortalama kazanç ($)
            avg_loss: Ortalama kayıp ($)
            
        Returns:
            Optimal position size as fraction of capital (0-1)
        """
        if avg_loss == 0 or win_rate == 0:
            return 0.02  # Default 2% conservative
        
        # Win/Loss ratio
        win_loss_ratio = avg_win / avg_loss
        
        # Kelly%
        kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Kelly fraction (clamp between 0-1)
        kelly_fraction = max(0, min(kelly_pct, 1.0))
        
        # Fractional Kelly (use 0.25-0.5 of full Kelly for safety)
        # Full Kelly can be too aggressive
        safe_kelly = kelly_fraction * 0.25  # 1/4 Kelly (conservative)
        
        return safe_kelly
    
    def get_historical_correlation(self, symbols, days=30):
        """
        Coin'ler arası korelasyon matrisi hesapla
        
        Args:
            symbols: List of coin pairs ['BTCUSDT', 'ETHUSDT', ...]
            days: Kaç günlük veri kullanılacak
            
        Returns:
            Correlation matrix (DataFrame)
        """
        print(f"📊 Calculating correlation matrix for {len(symbols)} coins ({days} days)...")
        
        price_data = {}
        
        for symbol in symbols:
            try:
                # Binance Klines API
                url = "https://fapi.binance.com/fapi/v1/klines"
                
                end_time = int(datetime.now().timestamp() * 1000)
                start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                
                params = {
                    'symbol': symbol,
                    'interval': '1h',
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': min(days * 24, 1000)  # Max 1000
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Close prices
                    closes = [float(candle[4]) for candle in data]
                    
                    # Price changes (returns)
                    returns = np.diff(closes) / closes[:-1]
                    
                    price_data[symbol.replace('USDT', '')] = returns
                else:
                    print(f"⚠️ Could not fetch data for {symbol}")
            except Exception as e:
                print(f"❌ Error fetching {symbol}: {str(e)}")
        
        if len(price_data) < 2:
            print("⚠️ Not enough data for correlation")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(price_data)
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        self.correlation_matrix = corr_matrix
        
        print(f"✅ Correlation matrix calculated!")
        return corr_matrix
    
    def calculate_diversification_score(self, allocations, corr_matrix):
        """
        Portfolio diversification skoru hesapla
        
        Lower correlation = Better diversification
        
        Args:
            allocations: Dict of {symbol: weight}
            corr_matrix: Correlation matrix
            
        Returns:
            Diversification score (0-100, higher is better)
        """
        if corr_matrix.empty or len(allocations) < 2:
            return 50  # Neutral score
        
        # Portfolio variance (weighted correlation)
        total_corr = 0
        count = 0
        
        symbols = list(allocations.keys())
        
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                if sym1 in corr_matrix.index and sym2 in corr_matrix.columns:
                    corr_val = corr_matrix.loc[sym1, sym2]
                    weight = allocations[sym1] * allocations[sym2]
                    total_corr += abs(corr_val) * weight
                    count += 1
        
        if count == 0:
            return 50
        
        avg_corr = total_corr / count
        
        # Score: 100 = perfectly uncorrelated (0)
        #        0 = perfectly correlated (1)
        score = (1 - avg_corr) * 100
        
        return max(0, min(score, 100))
    
    def optimize_portfolio(self, coin_signals, historical_performance=None):
        """
        Multi-coin portfolio için optimal allocation hesapla
        
        Args:
            coin_signals: List of dicts with AI decisions
                [{
                    'symbol': 'BTCUSDT',
                    'signal': 'LONG',
                    'confidence': 0.75,
                    'score': 68.5
                }, ...]
            
            historical_performance: Dict with past performance
                {
                    'win_rate': 0.58,
                    'avg_win': 150,
                    'avg_loss': 100
                }
                
        Returns:
            Optimal allocations dict
        """
        print(f"\n{'='*60}")
        print(f"🎯 PORTFOLIO OPTIMIZER")
        print(f"{'='*60}\n")
        print(f"Total Capital: ${self.total_capital:,.2f}")
        print(f"Risk/Trade: ${self.risk_per_trade:,.2f}")
        print(f"Coins to analyze: {len(coin_signals)}")
        
        # Filter only tradable signals (LONG/SHORT)
        tradable = [s for s in coin_signals if s.get('signal') in ['LONG', 'SHORT']]
        
        if len(tradable) == 0:
            print("⚠️ No tradable signals!")
            return {}
        
        print(f"Tradable signals: {len(tradable)}\n")
        
        # Kelly Criterion calculation
        if historical_performance:
            kelly_fraction = self.calculate_kelly_size(
                historical_performance.get('win_rate', 0.5),
                historical_performance.get('avg_win', 100),
                historical_performance.get('avg_loss', 100)
            )
            print(f"📊 Kelly Fraction: {kelly_fraction:.2%}")
        else:
            kelly_fraction = 0.05  # Default 5% conservative
            print(f"📊 Kelly Fraction: {kelly_fraction:.2%} (default - no history)")
        
        # Score-weighted allocation
        total_score = sum([s.get('score', 50) * s.get('confidence', 0.5) for s in tradable])
        
        allocations = {}
        position_sizes = {}
        
        print(f"\n{'Coin':<10} {'Signal':<8} {'Conf':<8} {'Score':<8} {'Weight':<10} {'Position $'}")
        print("-" * 70)
        
        for sig in tradable:
            symbol = sig['symbol']
            coin_name = symbol.replace('USDT', '')
            signal = sig.get('signal', 'NEUTRAL')
            confidence = sig.get('confidence', 0.5)
            score = sig.get('score', 50)
            
            # Weight = (score * confidence) / total_score
            weighted_score = score * confidence
            weight = weighted_score / total_score if total_score > 0 else 0
            
            # Position size = total_capital * kelly_fraction * weight
            position_size = self.total_capital * kelly_fraction * weight
            
            allocations[coin_name] = weight
            position_sizes[symbol] = position_size
            
            print(f"{coin_name:<10} {signal:<8} {confidence:.2f}   {score:.1f}   {weight:.2%}      ${position_size:,.2f}")
        
        # Correlation analysis
        symbols_list = [s['symbol'] for s in tradable]
        if len(symbols_list) >= 2:
            print(f"\n📊 Correlation Analysis...")
            corr_matrix = self.get_historical_correlation(symbols_list, days=30)
            
            if not corr_matrix.empty:
                div_score = self.calculate_diversification_score(allocations, corr_matrix)
                print(f"✅ Diversification Score: {div_score:.1f}/100")
                
                # Show correlation matrix
                print(f"\n📊 Correlation Matrix:")
                print(corr_matrix.round(2))
        else:
            div_score = 100  # Single coin = perfectly diversified (no correlation)
        
        print(f"\n{'='*60}")
        print(f"✅ OPTIMIZATION COMPLETE")
        print(f"{'='*60}\n")
        
        result = {
            'allocations': allocations,
            'position_sizes': position_sizes,
            'kelly_fraction': kelly_fraction,
            'diversification_score': div_score if len(symbols_list) >= 2 else 100,
            'total_allocated': sum(position_sizes.values()),
            'correlation_matrix': corr_matrix if len(symbols_list) >= 2 else pd.DataFrame()
        }
        
        return result
    
    def calculate_optimal_risk_per_coin(self, allocations, total_risk):
        """
        Her coin için optimal risk miktarı hesapla
        
        Args:
            allocations: Weight dict {coin: weight}
            total_risk: Toplam risk limiti ($)
            
        Returns:
            Risk dict {coin: risk_amount}
        """
        risk_per_coin = {}
        
        for coin, weight in allocations.items():
            risk_per_coin[coin] = total_risk * weight
        
        return risk_per_coin


# TEST EXAMPLE
if __name__ == "__main__":
    print("🔱 DEMIR AI PORTFOLIO OPTIMIZER - Test Mode")
    
    # Example usage
    optimizer = PortfolioOptimizer(total_capital=10000, risk_per_trade=200)
    
    # Example signals
    signals = [
        {'symbol': 'BTCUSDT', 'signal': 'LONG', 'confidence': 0.75, 'score': 68.5},
        {'symbol': 'ETHUSDT', 'signal': 'LONG', 'confidence': 0.60, 'score': 55.0},
        {'symbol': 'SOLUSDT', 'signal': 'SHORT', 'confidence': 0.65, 'score': 58.2},
        {'symbol': 'BNBUSDT', 'signal': 'NEUTRAL', 'confidence': 0.40, 'score': 45.0},  # Won't trade
    ]
    
    # Example historical performance
    perf = {
        'win_rate': 0.58,
        'avg_win': 180,
        'avg_loss': 120
    }
    
    # Optimize
    result = optimizer.optimize_portfolio(signals, perf)
    
    print(f"\n📊 Results:")
    print(f"Total Allocated: ${result['total_allocated']:,.2f}")
    print(f"Kelly Fraction: {result['kelly_fraction']:.2%}")
    print(f"Diversification Score: {result['diversification_score']:.1f}/100")
