"""
DEMIR AI Trading Bot - AI Brain ENHANCED
Phase 3A + Phase 3B + TP1/TP2/TP3 + SL
Fibonacci tabanlı çoklu take profit seviyeleri
Tarih: 31 Ekim 2025

YENİ ÖZELLİKLER:
✅ TP1, TP2, TP3 (Fibonacci seviyeleri)
✅ Partial close önerileri
✅ Risk/Reward her TP için ayrı
✅ Trailing stop önerisi
"""

def calculate_multiple_take_profits(entry_price, stop_loss, atr, signal_direction):
    """
    Fibonacci tabanlı çoklu TP seviyeleri
    
    Args:
        entry_price: Giriş fiyatı
        stop_loss: Stop loss fiyatı
        atr: Average True Range
        signal_direction: 'LONG' | 'SHORT'
    
    Returns:
        dict: {
            'tp1': {'price': float, 'pct': float, 'partial_close': str, 'rr': float},
            'tp2': {...},
            'tp3': {...},
            'trailing_stop': str
        }
    """
    
    if signal_direction == 'LONG':
        # LONG pozisyon
        risk = entry_price - stop_loss
        
        # Fibonacci multipliers
        tp1_price = entry_price + (risk * 1.0)   # 1:1 R/R (38.2% Fib)
        tp2_price = entry_price + (risk * 1.618) # 1:1.618 R/R (61.8% Golden Ratio)
        tp3_price = entry_price + (risk * 2.618) # 1:2.618 R/R (161.8% Extension)
        
        # Percentage gains
        tp1_pct = ((tp1_price - entry_price) / entry_price) * 100
        tp2_pct = ((tp2_price - entry_price) / entry_price) * 100
        tp3_pct = ((tp3_price - entry_price) / entry_price) * 100
        
        # Risk/Reward ratios
        tp1_rr = 1.0
        tp2_rr = 1.618
        tp3_rr = 2.618
        
        # Trailing stop recommendation
        trailing_suggestion = f"After TP1 hit: Move SL to entry (breakeven). After TP2: Trail SL to TP1 level."
    
    else:  # SHORT
        # SHORT pozisyon
        risk = stop_loss - entry_price
        
        # Fibonacci multipliers
        tp1_price = entry_price - (risk * 1.0)
        tp2_price = entry_price - (risk * 1.618)
        tp3_price = entry_price - (risk * 2.618)
        
        # Percentage gains
        tp1_pct = ((entry_price - tp1_price) / entry_price) * 100
        tp2_pct = ((entry_price - tp2_price) / entry_price) * 100
        tp3_pct = ((entry_price - tp3_price) / entry_price) * 100
        
        # Risk/Reward ratios
        tp1_rr = 1.0
        tp2_rr = 1.618
        tp3_rr = 2.618
        
        # Trailing stop recommendation
        trailing_suggestion = f"After TP1 hit: Move SL to entry (breakeven). After TP2: Trail SL to TP1 level."
    
    return {
        'tp1': {
            'price': round(tp1_price, 2),
            'pct': round(tp1_pct, 2),
            'partial_close': '50% position',
            'rr': round(tp1_rr, 2),
            'description': f'TP1 (1:1 R/R) - Close 50% of position, move SL to entry'
        },
        'tp2': {
            'price': round(tp2_price, 2),
            'pct': round(tp2_pct, 2),
            'partial_close': '30% position',
            'rr': round(tp2_rr, 2),
            'description': f'TP2 (1:1.618 Golden Ratio) - Close 30%, trail SL to TP1'
        },
        'tp3': {
            'price': round(tp3_price, 2),
            'pct': round(tp3_pct, 2),
            'partial_close': '20% position',
            'rr': round(tp3_rr, 2),
            'description': f'TP3 (1:2.618 Extension) - Close remaining 20%'
        },
        'trailing_stop': trailing_suggestion,
        'total_rr': round(tp3_rr, 2)  # En yüksek R/R
    }


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Multiple Take Profit Calculator Test")
    print("=" * 80)
    
    # LONG örnek
    entry = 69500
    sl = 68200
    atr = 850
    
    print("\n📈 LONG Position:")
    print(f"   Entry: ${entry:,.2f}")
    print(f"   SL: ${sl:,.2f}")
    print(f"   ATR: ${atr:,.2f}")
    
    tp_levels = calculate_multiple_take_profits(entry, sl, atr, 'LONG')
    
    print(f"\n🎯 Take Profit Levels:")
    print(f"   TP1: ${tp_levels['tp1']['price']:,.2f} (+{tp_levels['tp1']['pct']:.2f}%) [R/R: 1:{tp_levels['tp1']['rr']:.2f}]")
    print(f"        → {tp_levels['tp1']['partial_close']}")
    
    print(f"   TP2: ${tp_levels['tp2']['price']:,.2f} (+{tp_levels['tp2']['pct']:.2f}%) [R/R: 1:{tp_levels['tp2']['rr']:.2f}]")
    print(f"        → {tp_levels['tp2']['partial_close']}")
    
    print(f"   TP3: ${tp_levels['tp3']['price']:,.2f} (+{tp_levels['tp3']['pct']:.2f}%) [R/R: 1:{tp_levels['tp3']['rr']:.2f}]")
    print(f"        → {tp_levels['tp3']['partial_close']}")
    
    print(f"\n📊 Trailing Stop Strategy:")
    print(f"   {tp_levels['trailing_stop']}")
    
    # SHORT örnek
    print("\n" + "=" * 80)
    entry = 3850
    sl = 3970
    atr = 95
    
    print("\n📉 SHORT Position:")
    print(f"   Entry: ${entry:,.2f}")
    print(f"   SL: ${sl:,.2f}")
    print(f"   ATR: ${atr:,.2f}")
    
    tp_levels = calculate_multiple_take_profits(entry, sl, atr, 'SHORT')
    
    print(f"\n🎯 Take Profit Levels:")
    print(f"   TP1: ${tp_levels['tp1']['price']:,.2f} (+{tp_levels['tp1']['pct']:.2f}%) [R/R: 1:{tp_levels['tp1']['rr']:.2f}]")
    print(f"   TP2: ${tp_levels['tp2']['price']:,.2f} (+{tp_levels['tp2']['pct']:.2f}%) [R/R: 1:{tp_levels['tp2']['rr']:.2f}]")
    print(f"   TP3: ${tp_levels['tp3']['price']:,.2f} (+{tp_levels['tp3']['pct']:.2f}%) [R/R: 1:{tp_levels['tp3']['rr']:.2f}]")
    
    print("\n" + "=" * 80)
