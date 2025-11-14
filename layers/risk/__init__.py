# ============================================================================
# RISK LAYERS (5) - Advanced Risk Management
# File: layers/risk/__init__.py
# ============================================================================

class GarchVolatilityLayer:
    def analyze(self, returns):
        try:
            if len(returns) < 20:
                return 0.5
            
            # GARCH(1,1) model
            mean_return = np.mean(returns)
            variance = np.var(returns)
            
            # Conditional variance
            omega = 0.0001
            alpha = 0.1
            beta = 0.85
            
            cond_var = omega + alpha * (returns[-1] ** 2) + beta * variance
            return np.clip(0.5 - (cond_var * 10), 0, 1)
        except:
            return 0.5

class HistoricalVolatilityLayer:
    def analyze(self, prices):
        try:
            returns = np.diff(prices[-50:]) / prices[-50:-1]
            hist_vol = np.std(returns)
            return np.clip(0.5 - (hist_vol * 5), 0, 1)
        except:
            return 0.5

class MonteCarloLayer:
    def analyze(self, prices):
        try:
            simulations = []
            for _ in range(1000):
                future_price = prices[-1] * (1 + np.random.normal(0, 0.01))
                simulations.append(future_price)
            
            percentile_95 = np.percentile(simulations, 95)
            return 0.8 if percentile_95 > prices[-1] else 0.2
        except:
            return 0.5

class KellyCriterionLayer:
    def analyze(self, winrate, avg_win, avg_loss):
        try:
            if avg_loss == 0:
                return 0.5
            
            kelly_pct = (winrate * avg_win - (1 - winrate) * avg_loss) / avg_win
            kelly_pct = max(0, min(kelly_pct, 0.25))
            
            return np.clip(0.5 + kelly_pct, 0, 1)
        except:
            return 0.5

class DrawdownLayer:
    def analyze(self, equity):
        try:
            cummax = np.maximum.accumulate(equity)
            drawdown = (cummax - equity) / cummax
            max_dd = np.max(drawdown)
            
            return np.clip(1 - max_dd, 0, 1)
        except:
            return 0.5

