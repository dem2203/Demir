#============================================================================
# LAYER 2: ANALYTICS DASHBOARD (YENİ DOSYA)
# ============================================================================
# Dosya: Demir/layers/analytics_dashboard_v5.py
# Durum: YENİ (eski mock versiyonu replace et)

class AnalyticsDashboard:
    """
    Real analytics with metrics and KPIs
    - Trading statistics
    - Win/loss ratios
    - Risk metrics
    - Performance analytics
    """
    
    def __init__(self):
        logger.info("✅ AnalyticsDashboard initialized")
        self.trades = []
        self.metrics = {}

    def calculate_trading_metrics(self, trades: list) -> dict:
        """
        Calculate REAL trading metrics
        - NOT hardcoded
        - Based on actual trades
        """
        
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        df_trades = pd.DataFrame(trades)
        
        # Real calculations
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Calculate drawdown
        cumulative_returns = df_trades['pnl'].cumsum()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe ratio
        returns = df_trades['pnl'].values
        sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)
        
        metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_pnl': df_trades['pnl'].sum(),
            'avg_win': df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0,
            'avg_loss': df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        }
        
        logger.info(f"✅ Trading metrics calculated: WR={win_rate:.1f}%, PF={profit_factor:.2f}")
        
        return metrics
