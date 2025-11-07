"""
🔮 COPULA CORRELATION LAYER v16.5
=================================

Date: 7 Kasım 2025, 14:27 CET
Phase: 7+8 - Quantum Trading AI

AMAÇ:
-----
Copula theory ile asset'ler arasındaki tail dependencies
ve extreme event correlations tespit etmek. Normal correlation'ın
yakalayamadığı non-linear dependencies'i modellemek.

MATHEMATIK:
-----------
Gaussian Copula: C(u,v) = Φ_ρ(Φ^(-1)(u), Φ^(-1)(v))
t-Copula: Heavy tails için daha robust
Tail Dependence: λ_U = lim P(Y>y|X>x) as x,y→∞ (upper)
Lambda Lower: λ_L = lim P(Y lower_thresh_x
        upper_y = returns_y > upper_thresh_y
        upper_both = upper_x & upper_y
        
        lambda_upper = np.sum(upper_both) / max(np.sum(upper_x), 1) if np.sum(upper_x) > 0 else 0
        
        # Lower tail
        lower_thresh_x = np.percentile(returns_x, (1 - threshold) * 100)
        lower_thresh_y = np.percentile(returns_y, (1 - threshold) * 100)
        lower_x = returns_x < lower_thresh_x
        lower_y = returns_y < lower_thresh_y
        lower_both = lower_x & lower_y
        
        lambda_lower = np.sum(lower_both) / max(np.sum(lower_x), 1) if np.sum(lower_x) > 0 else 0
        
        return {'lambda_upper': lambda_upper, 'lambda_lower': lambda_lower}
    
    except:
        return {'lambda_upper': 0.5, 'lambda_lower': 0.5}

def get_copula_correlation_signal(symbol_1='BTCUSDT', symbol_2='ETHUSDT', interval='1h'):
    """
    Copula Correlation Layer ana fonksiyonu
    
    MANTIK:
    1. Fetch REAL data for both assets
    2. Calculate log returns
    3. Compute Pearson correlation
    4. Estimate tail dependencies
    5. Calculate copula-based score
    """
    debug = {}
    
    try:
        print(f"🔮 Copula analyzing {symbol_1} vs {symbol_2}...")
        
        # 1. Get REAL data
        df1, debug1 = fetch_pair_data(symbol_1, interval, 200)
        df2, debug2 = fetch_pair_data(symbol_2, interval, 200)
        
        debug.update({'symbol_1': debug1, 'symbol_2': debug2})
        
        if df1 is None or df2 is None:
            print(f"❌ Data fetch failed")
            return {
                'available': False,
                'score': 50.0,
                'signal': 'NEUTRAL',
                'error_message': 'Data fetch failed',
                'data_debug': debug
            }
        
        # 2. Calculate returns
        prices_1 = df1['close'].values
        prices_2 = df2['close'].values
        
        returns_1 = np.diff(np.log(prices_1))
        returns_2 = np.diff(np.log(prices_2))
        
        print(f" 📊 Returns: {len(returns_1)} observations for each")
        
        # 3. Pearson correlation
        corr_pearson = np.corrcoef(returns_1, returns_2)[0, 1]
        print(f" 📈 Pearson Correlation: {corr_pearson:.3f}")
        
        # 4. Tail dependencies
        tails = calculate_tail_dependence(returns_1, returns_2, threshold=0.1)
        lambda_upper = tails['lambda_upper']
        lambda_lower = tails['lambda_lower']
        
        print(f" 🔴 Upper Tail Dep: {lambda_upper:.3f}")
        print(f" 🟢 Lower Tail Dep: {lambda_lower:.3f}")
        
        # 5. Asymmetry index
        asymmetry = abs(lambda_upper - lambda_lower)
        print(f" ⚖️  Tail Asymmetry: {asymmetry:.3f}")
        
        # 6. Rank correlation (Spearman)
        rank_1 = np.argsort(np.argsort(returns_1))
        rank_2 = np.argsort(np.argsort(returns_2))
        corr_rank = np.corrcoef(rank_1, rank_2)[0, 1]
        print(f" 📊 Spearman Correlation: {corr_rank:.3f}")
        
        # 7. Score calculation
        score = 50.0
        
        # Correlation component
        if abs(corr_pearson) < 0.3:
            # Low correlation = good diversification
            score += 20
            correlation_signal = "DECORRELATED"
            print(f" ✅ Low correlation (diversification +20)")
        elif abs(corr_pearson) > 0.8:
            # High correlation = avoid pair
            score -= 20
            correlation_signal = "HIGHLY CORRELATED"
            print(f" ⚠️  High correlation (-20)")
        else:
            # Medium correlation = moderate
            score += 0
            correlation_signal = "MODERATE"
            print(f" ⚖️  Moderate correlation (0)")
        
        # Tail dependency component
        if lambda_upper > 0.3:
            # Strong upper tail = risk during rallies
            score -= min(lambda_upper * 20, 15)
            print(f" 🔴 Strong upper tail risk (-{min(lambda_upper * 20, 15):.1f})")
        
        if lambda_lower > 0.3:
            # Strong lower tail = risk during crashes
            score -= min(lambda_lower * 20, 15)
            print(f" 🟢 Strong lower tail risk (-{min(lambda_lower * 20, 15):.1f})")
        
        # Asymmetry component
        if asymmetry > 0.3:
            # Asymmetric tails = unpredictable behavior
            score = score * 0.9 + 50 * 0.1
            print(f" ⚡ Asymmetric tails (penalty)")
        
        # Rank correlation vs Pearson (copula structure)
        copula_distortion = abs(corr_rank - corr_pearson)
        if copula_distortion > 0.2:
            score += 10
            print(f" 🔄 Non-linear copula structure (+10)")
        
        score = max(0, min(100, score))
        
        print(f"✅ Copula Score: {score:.1f}/100")
        
        # Signal
        if score >= 65:
            signal = "DIVERSIFY"  # Good diversification
        elif score <= 35:
            signal = "AVOID"  # Avoid this pair
        else:
            signal = "MONITOR"  # Monitor carefully
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal,
            'pearson_correlation': round(corr_pearson, 3),
            'spearman_correlation': round(corr_rank, 3),
            'upper_tail_dependence': round(lambda_upper, 3),
            'lower_tail_dependence': round(lambda_lower, 3),
            'tail_asymmetry': round(asymmetry, 3),
            'copula_distortion': round(copula_distortion, 3),
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
        
    except Exception as e:
        print(f"❌ Copula Correlation error: {e}")
        debug['exception'] = str(e)
        return {
            'available': False,
            'score': 50.0,
            'signal': 'NEUTRAL',
            'error_message': str(e),
            'data_debug': debug
        }


if __name__ == "__main__":
    print("="*80)
    print("🔮 COPULA CORRELATION LAYER TEST")
    print("="*80)
    
    pairs = [('BTCUSDT', 'ETHUSDT'), ('BTCUSDT', 'XRPUSDT')]
    for symbol_1, symbol_2 in pairs:
        print(f"\n📊 Testing {symbol_1} vs {symbol_2}:")
        result = get_copula_correlation_signal(symbol_1, symbol_2)
        print(f" Score: {result['score']}, Signal: {result['signal']}\n")
