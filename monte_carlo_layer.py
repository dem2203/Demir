"""
DEMIR AI Trading Bot - Monte Carlo Layer
Phase 3A: Risk Management & Portfolio Simulation
Tarih: 31 Ekim 2025

Monte Carlo Simulations:
- 10,000+ trade simülasyonu
- Risk of Ruin (iflas olasılığı)
- Maximum Drawdown (en kötü düşüş)
- Sharpe Ratio (risk-adjusted return)
- Win/Loss Streak Probability

Kullanım:
- Risk of Ruin > 10% → Position size azalt
- Max Drawdown > 30% → Trading'i durdur
- Sharpe < 1.0 → Strategy optimization gerekli
- 95th percentile streak → Psychological hazırlık
"""

import numpy as np
from datetime import datetime
import random


def monte_carlo_simulation(
    win_rate=0.55,
    avg_win=2.0,
    avg_loss=1.0,
    num_trades=100,
    simulations=10000,
    starting_capital=1000
):
    """
    Monte Carlo risk simülasyonu
    
    Args:
        win_rate (float): Kazanma olasılığı (0.55 = %55)
        avg_win (float): Ortalama kazanç (%2.0 = %2)
        avg_loss (float): Ortalama kayıp (%1.0 = %1)
        num_trades (int): Simüle edilecek trade sayısı
        simulations (int): Monte Carlo iterasyon sayısı
        starting_capital (float): Başlangıç sermayesi
    
    Returns:
        dict: Detaylı risk analizi
    """
    
    results = []
    equity_curves = []
    
    for sim in range(simulations):
        equity = starting_capital
        equity_curve = [equity]
        peak = equity
        max_drawdown = 0
        
        for trade in range(num_trades):
            # Random trade outcome
            if random.random() < win_rate:
                # Win
                profit = equity * (avg_win / 100)
                equity += profit
            else:
                # Loss
                loss = equity * (avg_loss / 100)
                equity -= loss
            
            # Track drawdown
            if equity > peak:
                peak = equity
            
            drawdown = ((peak - equity) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
            
            equity_curve.append(equity)
        
        # Calculate returns
        total_return = ((equity - starting_capital) / starting_capital) * 100
        
        results.append({
            'final_equity': equity,
            'total_return': total_return,
            'max_drawdown': max_drawdown
        })
        
        equity_curves.append(equity_curve)
    
    # Analyze results
    final_equities = [r['final_equity'] for r in results]
    total_returns = [r['total_return'] for r in results]
    max_drawdowns = [r['max_drawdown'] for r in results]
    
    # Risk of Ruin (equity < 50% of starting capital)
    ruin_threshold = starting_capital * 0.5
    risk_of_ruin = sum(1 for eq in final_equities if eq < ruin_threshold) / simulations
    
    # Percentiles
    percentile_5 = np.percentile(total_returns, 5)
    percentile_25 = np.percentile(total_returns, 25)
    percentile_50 = np.percentile(total_returns, 50)  # Median
    percentile_75 = np.percentile(total_returns, 75)
    percentile_95 = np.percentile(total_returns, 95)
    
    # Drawdown statistics
    avg_drawdown = np.mean(max_drawdowns)
    worst_drawdown = np.max(max_drawdowns)
    percentile_95_drawdown = np.percentile(max_drawdowns, 95)
    
    # Sharpe Ratio estimation
    returns_std = np.std(total_returns)
    sharpe_ratio = (percentile_50 / returns_std) if returns_std > 0 else 0
    
    return {
        'simulations': simulations,
        'num_trades': num_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'starting_capital': starting_capital,
        'risk_of_ruin': round(risk_of_ruin * 100, 2),  # %
        'expected_return_median': round(percentile_50, 2),  # %
        'expected_return_5th': round(percentile_5, 2),  # Worst case (5%)
        'expected_return_95th': round(percentile_95, 2),  # Best case (95%)
        'avg_drawdown': round(avg_drawdown, 2),  # %
        'worst_drawdown': round(worst_drawdown, 2),  # %
        'percentile_95_drawdown': round(percentile_95_drawdown, 2),  # %
        'sharpe_ratio': round(sharpe_ratio, 2),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def calculate_streak_probability(win_rate=0.55, streak_length=5):
    """
    Win/Loss streak olasılığını hesaplar
    
    Args:
        win_rate (float): Kazanma olasılığı
        streak_length (int): Streak uzunluğu
    
    Returns:
        dict: {
            'win_streak_prob': float,
            'loss_streak_prob': float
        }
    """
    
    win_streak_prob = win_rate ** streak_length
    loss_streak_prob = (1 - win_rate) ** streak_length
    
    return {
        'streak_length': streak_length,
        'win_streak_prob': round(win_streak_prob * 100, 4),  # %
        'loss_streak_prob': round(loss_streak_prob * 100, 4)  # %
    }


def find_95th_percentile_streaks(win_rate=0.55, simulations=10000, max_trades=100):
    """
    %95 olasılıkla karşılaşılacak en uzun streak'leri bulur
    
    Returns:
        dict: {
            'win_streak_95': int,
            'loss_streak_95': int
        }
    """
    
    win_streaks = []
    loss_streaks = []
    
    for _ in range(simulations):
        current_win_streak = 0
        current_loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for trade in range(max_trades):
            if random.random() < win_rate:
                # Win
                current_win_streak += 1
                current_loss_streak = 0
                if current_win_streak > max_win_streak:
                    max_win_streak = current_win_streak
            else:
                # Loss
                current_loss_streak += 1
                current_win_streak = 0
                if current_loss_streak > max_loss_streak:
                    max_loss_streak = current_loss_streak
        
        win_streaks.append(max_win_streak)
        loss_streaks.append(max_loss_streak)
    
    # 95th percentile
    win_streak_95 = int(np.percentile(win_streaks, 95))
    loss_streak_95 = int(np.percentile(loss_streaks, 95))
    
    return {
        'win_streak_95': win_streak_95,
        'loss_streak_95': loss_streak_95,
        'description': f"%95 olasılıkla: {win_streak_95} kazanç streak veya {loss_streak_95} kayıp streak görebilirsiniz"
    }


def get_monte_carlo_risk_assessment(win_rate, avg_win, avg_loss, num_trades=100):
    """
    Kapsamlı risk değerlendirmesi
    
    Returns:
        dict: Tüm Monte Carlo metrikleri + yorumlar
    """
    
    # Ana simülasyon
    mc_results = monte_carlo_simulation(
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        num_trades=num_trades,
        simulations=10000,
        starting_capital=1000
    )
    
    # Streak analizi
    streaks = find_95th_percentile_streaks(win_rate=win_rate, simulations=5000, max_trades=num_trades)
    
    # Risk seviyesi belirleme
    risk_of_ruin = mc_results['risk_of_ruin']
    if risk_of_ruin > 10:
        risk_level = 'HIGH'
        risk_color = '🔴'
        risk_action = 'Position size azaltın! Ruin riski çok yüksek.'
    elif risk_of_ruin > 5:
        risk_level = 'MEDIUM'
        risk_color = '🟡'
        risk_action = 'Dikkatli olun. Ruin riski kabul edilebilir ama yüksek.'
    else:
        risk_level = 'LOW'
        risk_color = '🟢'
        risk_action = 'Risk seviyesi düşük. Position size uygun.'
    
    # Drawdown değerlendirmesi
    worst_dd = mc_results['worst_drawdown']
    if worst_dd > 30:
        dd_level = 'EXTREME'
        dd_action = 'En kötü senaryo: -%{:.1f} düşüş! Trading'i durdurmayı düşünün.'.format(worst_dd)
    elif worst_dd > 20:
        dd_level = 'HIGH'
        dd_action = 'En kötü senaryo: -%{:.1f} düşüş. Psychological hazırlık gerekli.'.format(worst_dd)
    else:
        dd_level = 'ACCEPTABLE'
        dd_action = 'Drawdown kabul edilebilir: -%{:.1f}'.format(worst_dd)
    
    # Sharpe Ratio değerlendirmesi
    sharpe = mc_results['sharpe_ratio']
    if sharpe > 2.0:
        sharpe_level = 'EXCELLENT'
        sharpe_action = 'Mükemmel risk-adjusted returns!'
    elif sharpe > 1.0:
        sharpe_level = 'GOOD'
        sharpe_action = 'İyi risk-adjusted returns.'
    elif sharpe > 0.5:
        sharpe_level = 'FAIR'
        sharpe_action = 'Orta seviye risk-adjusted returns.'
    else:
        sharpe_level = 'POOR'
        sharpe_action = 'Zayıf risk-adjusted returns. Strategy optimization gerekli!'
    
    return {
        'monte_carlo_results': mc_results,
        'streak_analysis': streaks,
        'risk_assessment': {
            'level': risk_level,
            'color': risk_color,
            'risk_of_ruin_pct': risk_of_ruin,
            'action': risk_action
        },
        'drawdown_assessment': {
            'level': dd_level,
            'worst_case_pct': worst_dd,
            'action': dd_action
        },
        'sharpe_assessment': {
            'level': sharpe_level,
            'ratio': sharpe,
            'action': sharpe_action
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Monte Carlo Layer Test")
    print("=" * 80)
    
    # Test parameters
    win_rate = 0.55  # %55 win rate
    avg_win = 2.0    # %2 average win
    avg_loss = 1.0   # %1 average loss
    
    print(f"\n📊 Running Monte Carlo Simulation...")
    print(f"   Win Rate: {win_rate*100}%")
    print(f"   Avg Win: {avg_win}%")
    print(f"   Avg Loss: {avg_loss}%")
    print(f"   Simulations: 10,000")
    print(f"   Trades per simulation: 100")
    
    assessment = get_monte_carlo_risk_assessment(win_rate, avg_win, avg_loss, num_trades=100)
    
    mc = assessment['monte_carlo_results']
    risk = assessment['risk_assessment']
    dd = assessment['drawdown_assessment']
    sharpe = assessment['sharpe_assessment']
    streaks = assessment['streak_analysis']
    
    print(f"\n✅ RESULTS:")
    print(f"\n{risk['color']} RISK OF RUIN:")
    print(f"   Level: {risk['level']}")
    print(f"   Probability: {risk['risk_of_ruin_pct']}%")
    print(f"   Action: {risk['action']}")
    
    print(f"\n📉 DRAWDOWN ANALYSIS:")
    print(f"   Level: {dd['level']}")
    print(f"   Average Drawdown: -{mc['avg_drawdown']}%")
    print(f"   Worst Case (95th): -{mc['percentile_95_drawdown']}%")
    print(f"   Absolute Worst: -{dd['worst_case_pct']}%")
    print(f"   Action: {dd['action']}")
    
    print(f"\n💰 EXPECTED RETURNS:")
    print(f"   Worst Case (5th): {mc['expected_return_5th']:+.2f}%")
    print(f"   Median (50th): {mc['expected_return_median']:+.2f}%")
    print(f"   Best Case (95th): {mc['expected_return_95th']:+.2f}%")
    
    print(f"\n📊 SHARPE RATIO:")
    print(f"   Level: {sharpe['level']}")
    print(f"   Ratio: {sharpe['ratio']:.2f}")
    print(f"   Action: {sharpe['action']}")
    
    print(f"\n🔄 STREAK ANALYSIS:")
    print(f"   Win Streak (95th): {streaks['win_streak_95']} consecutive wins")
    print(f"   Loss Streak (95th): {streaks['loss_streak_95']} consecutive losses")
    print(f"   Description: {streaks['description']}")
    
    print("\n" + "=" * 80)
