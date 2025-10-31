"""
DEMIR AI Trading Bot - Win Rate Calculator & Performance Tracker
Real-time performance metrics calculation
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ Win rate hesaplama
✅ Average win/loss
✅ Max drawdown
✅ Profit factor
✅ Sharpe ratio
✅ Real-time statistics
"""

import trade_history_db as db
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_win_rate():
    """
    Win rate hesapla
    
    Returns:
        dict: {
            'win_rate': float,
            'total_trades': int,
            'winning_trades': int,
            'losing_trades': int
        }
    """
    trades_df = db.get_all_trades()
    
    if trades_df.empty:
        return {
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
    
    closed_trades = trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])]
    
    if closed_trades.empty:
        return {
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
    
    total_trades = len(closed_trades)
    winning_trades = len(closed_trades[closed_trades['status'] == 'WIN'])
    losing_trades = len(closed_trades[closed_trades['status'] == 'LOSS'])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    return {
        'win_rate': round(win_rate, 2),
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades
    }


def calculate_pnl_metrics():
    """
    PNL metrikleri hesapla
    
    Returns:
        dict: {
            'total_pnl_usd': float,
            'total_pnl_pct': float,
            'avg_win_usd': float,
            'avg_loss_usd': float,
            'max_win_usd': float,
            'max_loss_usd': float,
            'profit_factor': float
        }
    """
    trades_df = db.get_all_trades()
    
    if trades_df.empty:
        return {
            'total_pnl_usd': 0.0,
            'total_pnl_pct': 0.0,
            'avg_win_usd': 0.0,
            'avg_loss_usd': 0.0,
            'max_win_usd': 0.0,
            'max_loss_usd': 0.0,
            'profit_factor': 0.0
        }
    
    closed_trades = trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])]
    
    if closed_trades.empty:
        return {
            'total_pnl_usd': 0.0,
            'total_pnl_pct': 0.0,
            'avg_win_usd': 0.0,
            'avg_loss_usd': 0.0,
            'max_win_usd': 0.0,
            'max_loss_usd': 0.0,
            'profit_factor': 0.0
        }
    
    # Total PNL
    total_pnl_usd = closed_trades['pnl_usd'].sum()
    total_pnl_pct = closed_trades['pnl_pct'].mean()
    
    # Wins
    wins = closed_trades[closed_trades['status'] == 'WIN']
    avg_win_usd = wins['pnl_usd'].mean() if not wins.empty else 0.0
    max_win_usd = wins['pnl_usd'].max() if not wins.empty else 0.0
    gross_profit = wins['pnl_usd'].sum() if not wins.empty else 0.0
    
    # Losses
    losses = closed_trades[closed_trades['status'] == 'LOSS']
    avg_loss_usd = losses['pnl_usd'].mean() if not losses.empty else 0.0
    max_loss_usd = losses['pnl_usd'].min() if not losses.empty else 0.0
    gross_loss = abs(losses['pnl_usd'].sum()) if not losses.empty else 0.0
    
    # Profit factor
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0
    
    return {
        'total_pnl_usd': round(total_pnl_usd, 2),
        'total_pnl_pct': round(total_pnl_pct, 2),
        'avg_win_usd': round(avg_win_usd, 2),
        'avg_loss_usd': round(avg_loss_usd, 2),
        'max_win_usd': round(max_win_usd, 2),
        'max_loss_usd': round(max_loss_usd, 2),
        'profit_factor': round(profit_factor, 2)
    }


def calculate_drawdown():
    """
    Maximum drawdown hesapla
    
    Returns:
        dict: {
            'max_drawdown_pct': float,
            'max_drawdown_usd': float,
            'current_drawdown_pct': float
        }
    """
    trades_df = db.get_all_trades()
    
    if trades_df.empty:
        return {
            'max_drawdown_pct': 0.0,
            'max_drawdown_usd': 0.0,
            'current_drawdown_pct': 0.0
        }
    
    closed_trades = trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])]
    
    if closed_trades.empty or len(closed_trades) < 2:
        return {
            'max_drawdown_pct': 0.0,
            'max_drawdown_usd': 0.0,
            'current_drawdown_pct': 0.0
        }
    
    # Cumulative PNL
    closed_trades = closed_trades.sort_values('timestamp')
    cumulative_pnl = closed_trades['pnl_usd'].cumsum()
    
    # Running maximum
    running_max = cumulative_pnl.cummax()
    
    # Drawdown
    drawdown = cumulative_pnl - running_max
    
    # Max drawdown
    max_dd_usd = drawdown.min()
    max_dd_pct = (max_dd_usd / running_max.max() * 100) if running_max.max() > 0 else 0.0
    
    # Current drawdown
    current_dd_pct = (drawdown.iloc[-1] / running_max.iloc[-1] * 100) if running_max.iloc[-1] > 0 else 0.0
    
    return {
        'max_drawdown_pct': round(max_dd_pct, 2),
        'max_drawdown_usd': round(max_dd_usd, 2),
        'current_drawdown_pct': round(current_dd_pct, 2)
    }


def calculate_sharpe_ratio(risk_free_rate=0.02):
    """
    Sharpe ratio hesapla
    
    Args:
        risk_free_rate (float): Risk-free rate (annual, e.g., 0.02 = 2%)
    
    Returns:
        float: Sharpe ratio
    """
    trades_df = db.get_all_trades()
    
    if trades_df.empty:
        return 0.0
    
    closed_trades = trades_df[trades_df['status'].isin(['WIN', 'LOSS', 'BREAKEVEN'])]
    
    if closed_trades.empty or len(closed_trades) < 2:
        return 0.0
    
    # Returns as percentage
    returns = closed_trades['pnl_pct'].values
    
    # Mean return
    mean_return = returns.mean()
    
    # Standard deviation
    std_return = returns.std()
    
    if std_return == 0:
        return 0.0
    
    # Sharpe ratio (annualized)
    sharpe = (mean_return - risk_free_rate) / std_return
    
    return round(sharpe, 2)


def get_performance_dashboard():
    """
    Tüm performance metrics'i toplu getir
    
    Returns:
        dict: Complete performance dashboard
    """
    win_rate_metrics = calculate_win_rate()
    pnl_metrics = calculate_pnl_metrics()
    drawdown_metrics = calculate_drawdown()
    sharpe = calculate_sharpe_ratio()
    
    return {
        **win_rate_metrics,
        **pnl_metrics,
        **drawdown_metrics,
        'sharpe_ratio': sharpe,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def get_trade_history_summary(days=7):
    """
    Son N günün trade özeti
    
    Args:
        days (int): Kaç günlük geçmiş
    
    Returns:
        pd.DataFrame: Summary by day
    """
    trades_df = db.get_all_trades()
    
    if trades_df.empty:
        return pd.DataFrame()
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
    recent_trades = trades_df[trades_df['timestamp'] >= cutoff_date]
    
    if recent_trades.empty:
        return pd.DataFrame()
    
    # Group by date
    recent_trades['date'] = recent_trades['timestamp'].dt.date
    
    summary = recent_trades.groupby('date').agg({
        'id': 'count',
        'pnl_usd': 'sum',
        'pnl_pct': 'mean',
        'status': lambda x: (x == 'WIN').sum() / len(x) * 100 if len(x) > 0 else 0
    }).rename(columns={
        'id': 'trades',
        'pnl_usd': 'total_pnl_usd',
        'pnl_pct': 'avg_pnl_pct',
        'status': 'win_rate'
    })
    
    return summary


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Win Rate Calculator Test")
    print("=" * 80)
    
    # Get dashboard
    dashboard = get_performance_dashboard()
    
    print("\n📊 PERFORMANCE DASHBOARD:")
    print(f"\n✅ Win Rate:")
    print(f"   Win Rate: {dashboard['win_rate']:.1f}%")
    print(f"   Total Trades: {dashboard['total_trades']}")
    print(f"   Winning: {dashboard['winning_trades']} | Losing: {dashboard['losing_trades']}")
    
    print(f"\n💰 PNL Metrics:")
    print(f"   Total PNL: ${dashboard['total_pnl_usd']:,.2f}")
    print(f"   Avg Win: ${dashboard['avg_win_usd']:,.2f}")
    print(f"   Avg Loss: ${dashboard['avg_loss_usd']:,.2f}")
    print(f"   Profit Factor: {dashboard['profit_factor']:.2f}")
    
    print(f"\n📉 Risk Metrics:")
    print(f"   Max Drawdown: {dashboard['max_drawdown_pct']:.2f}% (${dashboard['max_drawdown_usd']:,.2f})")
    print(f"   Sharpe Ratio: {dashboard['sharpe_ratio']:.2f}")
    
    print("\n" + "=" * 80)
