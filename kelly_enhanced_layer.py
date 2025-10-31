"""
DEMIR AI Trading Bot - Kelly Enhanced Layer
Phase 3A: Advanced Position Sizing
Tarih: 31 Ekim 2025

Kelly Criterion (Enhanced):
- Full Kelly: f* = (bp - q) / b
- Fractional Kelly: 0.25 * Full Kelly (güvenli)
- Confidence-based adjustment
- Max position size: 10% (risk management)

Kullanım:
- High confidence (0.8+) → 0.25 Fractional Kelly
- Medium confidence (0.5-0.8) → 0.15 Fractional Kelly
- Low confidence (<0.5) → Skip trade or 0.05
- Never exceed 10% of portfolio per trade
"""

from datetime import datetime
import numpy as np


def calculate_full_kelly(win_rate, avg_win, avg_loss):
    """
    Full Kelly Criterion hesaplar
    
    Formula: f* = (bp - q) / b
        f* = optimal position size (fraction of bankroll)
        b = odds (net win/net loss ratio) = avg_win / avg_loss
        p = win probability
        q = loss probability = 1 - p
    
    Args:
        win_rate (float): Kazanma olasılığı (0.55 = %55)
        avg_win (float): Ortalama kazanç oranı (%2.0 = %2)
        avg_loss (float): Ortalama kayıp oranı (%1.0 = %1)
    
    Returns:
        float: Full Kelly fraction (0.0-1.0)
    """
    
    if win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    if avg_win <= 0 or avg_loss <= 0:
        return 0.0
    
    # Odds (b)
    b = avg_win / avg_loss
    
    # Probabilities
    p = win_rate
    q = 1 - p
    
    # Full Kelly
    full_kelly = (b * p - q) / b
    
    # Kelly negatif ise edge yok, trade yapma
    if full_kelly < 0:
        return 0.0
    
    return full_kelly


def calculate_fractional_kelly(
    win_rate,
    avg_win,
    avg_loss,
    fraction=0.25,
    max_kelly=0.10
):
    """
    Fractional Kelly (güvenli versiyon)
    
    Args:
        win_rate (float): Kazanma olasılığı
        avg_win (float): Ortalama kazanç %
        avg_loss (float): Ortalama kayıp %
        fraction (float): Kelly fraksiyonu (0.25 = %25 of full Kelly)
        max_kelly (float): Maximum position size (0.10 = %10 of portfolio)
    
    Returns:
        dict: {
            'full_kelly': float,
            'fractional_kelly': float,
            'recommended': float,
            'position_size_pct': float,
            'edge': float
        }
    """
    
    # Full Kelly hesapla
    full_kelly = calculate_full_kelly(win_rate, avg_win, avg_loss)
    
    # Fractional Kelly
    fractional_kelly = full_kelly * fraction
    
    # Max kelly constraint
    recommended = min(fractional_kelly, max_kelly)
    
    # Edge hesapla (expected value)
    edge = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    return {
        'full_kelly': round(full_kelly, 4),
        'fractional_kelly': round(fractional_kelly, 4),
        'fraction_used': fraction,
        'max_kelly_constraint': max_kelly,
        'recommended': round(recommended, 4),
        'position_size_pct': round(recommended * 100, 2),  # % of portfolio
        'edge': round(edge, 4),  # Expected value per $1 risked
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def calculate_dynamic_kelly(
    win_rate,
    avg_win,
    avg_loss,
    confidence=0.7,
    portfolio_value=10000
):
    """
    Confidence-based Dynamic Kelly
    
    Args:
        win_rate (float): Kazanma olasılığı
        avg_win (float): Ortalama kazanç %
        avg_loss (float): Ortalama kayıp %
        confidence (float): AI confidence (0.0-1.0)
        portfolio_value (float): Current portfolio value
    
    Returns:
        dict: Detailed Kelly calculation with confidence adjustment
    """
    
    # Base fractional Kelly
    if confidence >= 0.8:
        fraction = 0.25  # High confidence: %25 of full Kelly
        max_kelly = 0.10  # Max %10 of portfolio
    elif confidence >= 0.5:
        fraction = 0.15  # Medium confidence: %15 of full Kelly
        max_kelly = 0.05  # Max %5 of portfolio
    else:
        fraction = 0.05  # Low confidence: %5 of full Kelly
        max_kelly = 0.02  # Max %2 of portfolio
    
    # Calculate Kelly
    kelly_result = calculate_fractional_kelly(
        win_rate,
        avg_win,
        avg_loss,
        fraction=fraction,
        max_kelly=max_kelly
    )
    
    # Position size in USD
    position_size_usd = portfolio_value * kelly_result['recommended']
    
    # Risk amount (what you're willing to lose)
    risk_amount = position_size_usd * (avg_loss / 100)
    
    # Signal strength based on Kelly
    if kelly_result['recommended'] >= 0.05:
        signal_strength = 'STRONG'
    elif kelly_result['recommended'] >= 0.02:
        signal_strength = 'MODERATE'
    elif kelly_result['recommended'] > 0:
        signal_strength = 'WEAK'
    else:
        signal_strength = 'SKIP'
    
    return {
        'confidence': confidence,
        'kelly_data': kelly_result,
        'portfolio_value': portfolio_value,
        'position_size_usd': round(position_size_usd, 2),
        'position_size_pct': kelly_result['position_size_pct'],
        'risk_amount_usd': round(risk_amount, 2),
        'signal_strength': signal_strength,
        'recommendation': {
            'action': 'ENTER' if kelly_result['recommended'] > 0 else 'SKIP',
            'size': f"${position_size_usd:,.2f} ({kelly_result['position_size_pct']}% of portfolio)",
            'risk': f"${risk_amount:,.2f}",
            'reason': f"Confidence: {confidence:.0%}, Kelly: {kelly_result['position_size_pct']:.2f}%"
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def kelly_position_sizing_guide(win_rate, avg_win, avg_loss):
    """
    Kelly position sizing kılavuzu (farklı confidence seviyeleri için)
    
    Returns:
        dict: Confidence-based position sizing guide
    """
    
    guide = {}
    
    for confidence in [0.9, 0.7, 0.5, 0.3]:
        result = calculate_dynamic_kelly(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            confidence=confidence,
            portfolio_value=10000  # Reference $10k portfolio
        )
        
        guide[f"confidence_{int(confidence*100)}"] = {
            'confidence': confidence,
            'position_size_pct': result['position_size_pct'],
            'position_size_usd': result['position_size_usd'],
            'risk_usd': result['risk_amount_usd'],
            'signal_strength': result['signal_strength']
        }
    
    return {
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'sizing_guide': guide,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - Kelly Enhanced Layer Test")
    print("=" * 80)
    
    # Test parameters
    win_rate = 0.55  # %55 win rate
    avg_win = 2.0    # %2 average win
    avg_loss = 1.0   # %1 average loss
    confidence = 0.75  # %75 AI confidence
    portfolio = 10000  # $10k portfolio
    
    print(f"\n📊 Input Parameters:")
    print(f"   Win Rate: {win_rate*100}%")
    print(f"   Avg Win: {avg_win}%")
    print(f"   Avg Loss: {avg_loss}%")
    print(f"   AI Confidence: {confidence*100}%")
    print(f"   Portfolio: ${portfolio:,.0f}")
    
    # Full Kelly
    full_kelly = calculate_full_kelly(win_rate, avg_win, avg_loss)
    print(f"\n✅ FULL KELLY:")
    print(f"   Kelly Fraction: {full_kelly:.4f} ({full_kelly*100:.2f}% of portfolio)")
    print(f"   ⚠️ WARNING: Full Kelly is aggressive! Use fractional instead.")
    
    # Fractional Kelly (25%)
    frac_kelly = calculate_fractional_kelly(win_rate, avg_win, avg_loss, fraction=0.25)
    print(f"\n✅ FRACTIONAL KELLY (25%):")
    print(f"   Recommended: {frac_kelly['recommended']:.4f} ({frac_kelly['position_size_pct']}%)")
    print(f"   Edge: {frac_kelly['edge']:.4f} (expected value per $1)")
    
    # Dynamic Kelly with confidence
    dyn_kelly = calculate_dynamic_kelly(win_rate, avg_win, avg_loss, confidence, portfolio)
    print(f"\n✅ DYNAMIC KELLY (Confidence-based):")
    print(f"   Confidence: {dyn_kelly['confidence']*100}%")
    print(f"   Signal Strength: {dyn_kelly['signal_strength']}")
    print(f"   Position Size: ${dyn_kelly['position_size_usd']:,.2f} ({dyn_kelly['position_size_pct']}%)")
    print(f"   Risk Amount: ${dyn_kelly['risk_amount_usd']:,.2f}")
    print(f"\n   Recommendation:")
    print(f"   Action: {dyn_kelly['recommendation']['action']}")
    print(f"   Size: {dyn_kelly['recommendation']['size']}")
    print(f"   Risk: {dyn_kelly['recommendation']['risk']}")
    print(f"   Reason: {dyn_kelly['recommendation']['reason']}")
    
    # Position sizing guide
    print(f"\n✅ POSITION SIZING GUIDE (for $10k portfolio):")
    guide = kelly_position_sizing_guide(win_rate, avg_win, avg_loss)
    
    for key, val in guide['sizing_guide'].items():
        print(f"\n   Confidence {val['confidence']*100:.0f}%:")
        print(f"      Position: ${val['position_size_usd']:,.2f} ({val['position_size_pct']}%)")
        print(f"      Risk: ${val['risk_usd']:,.2f}")
        print(f"      Strength: {val['signal_strength']}")
    
    print("\n" + "=" * 80)
