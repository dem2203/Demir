"""
DEMIR AI Trading Bot - GARCH Volatility Layer
Phase 3B Module 1: Volatility Forecasting
Tarih: 31 Ekim 2025

GARCH(1,1) - Generalized Autoregressive Conditional Heteroskedasticity
Gelecek volatilite tahminleri için
"""

import numpy as np
import pandas as pd
from datetime import datetime
import requests


def fetch_ohlcv_data(symbol, interval='1h', limit=100):
    """
    Binance'den OHLCV verilerini çek
    """
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            
            print(f"✅ GARCH: Fetched {len(df)} bars for {symbol} {interval}")
            return df
        else:
            print(f"⚠️ GARCH: API error {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ GARCH: Data fetch error: {e}")
        return None


def calculate_log_returns(df):
    """
    Log returns hesapla (volatilite modelleme için)
    """
    df['returns'] = np.log(df['close'] / df['close'].shift(1))
    df = df.dropna()
    return df


def fit_garch_model(returns, p=1, q=1):
    """
    Basitleştirilmiş GARCH(1,1) modeli
    
    GARCH formülü:
    σ²(t) = ω + α·r²(t-1) + β·σ²(t-1)
    
    Burada:
    - σ²(t): Zamana bağlı varyans (volatility)
    - r(t-1): Önceki dönem return
    - α: ARCH etkisi (kısa dönem şok)
    - β: GARCH etkisi (volatilite persistence)
    - ω: Sabit terim
    """
    
    print(f"🎲 GARCH: Fitting GARCH({p},{q}) model...")
    
    # Basitleştirilmiş parametre tahmini
    # Gerçek uygulamada Maximum Likelihood Estimation kullanılır
    
    # Returns squared (ARCH component)
    returns_sq = returns ** 2
    
    # Rolling volatility (proxy for conditional variance)
    rolling_vol = returns_sq.rolling(window=20).mean()
    
    # Parametreler (simplified estimation)
    alpha = 0.15  # ARCH parameter (kısa dönem)
    beta = 0.80   # GARCH parameter (uzun dönem)
    omega = rolling_vol.mean() * (1 - alpha - beta)  # Long-run variance
    
    print(f"   ω (omega): {omega:.6f}")
    print(f"   α (alpha): {alpha:.6f}")
    print(f"   β (beta): {beta:.6f}")
    print(f"   Persistence (α+β): {alpha + beta:.6f}")
    
    return {
        'omega': omega,
        'alpha': alpha,
        'beta': beta,
        'returns_sq': returns_sq,
        'conditional_variance': rolling_vol
    }


def forecast_volatility(model, returns, horizon=24):
    """
    Gelecek volatilite tahmin et
    
    GARCH forecast:
    σ²(t+h) = E[σ²(∞)] + (α+β)^h · (σ²(t) - E[σ²(∞)])
    
    Burada:
    - E[σ²(∞)] = ω / (1 - α - β): Long-run variance
    - h: Forecast horizon
    """
    
    omega = model['omega']
    alpha = model['alpha']
    beta = model['beta']
    
    # Son gözlemlenen variance
    current_variance = model['conditional_variance'].iloc[-1]
    
    # Long-run variance
    long_run_var = omega / (1 - alpha - beta)
    
    # Forecast (h-step ahead)
    persistence = alpha + beta
    forecasted_variances = []
    
    for h in range(1, horizon + 1):
        # Mean reversion to long-run variance
        var_forecast = long_run_var + (persistence ** h) * (current_variance - long_run_var)
        forecasted_variances.append(var_forecast)
    
    # Convert variance to volatility (annualized %)
    # σ = √(variance) * √(periods_per_year) * 100
    
    # Periods per year based on interval
    periods_per_year = {
        '1m': 525600,
        '5m': 105120,
        '15m': 35040,
        '1h': 8760,
        '4h': 2190,
        '1d': 365
    }
    
    # Average forecast
    avg_forecast_var = np.mean(forecasted_variances)
    avg_forecast_vol = np.sqrt(avg_forecast_var) * 100  # Convert to %
    
    # Next period forecast
    next_period_var = forecasted_variances[0]
    next_period_vol = np.sqrt(next_period_var) * 100
    
    print(f"\n📊 GARCH Forecast Results:")
    print(f"   Current Vol: {np.sqrt(current_variance) * 100:.2f}%")
    print(f"   Next Period Vol: {next_period_vol:.2f}%")
    print(f"   Avg {horizon}h Vol: {avg_forecast_vol:.2f}%")
    print(f"   Long-run Vol: {np.sqrt(long_run_var) * 100:.2f}%")
    
    return {
        'current_volatility': float(np.sqrt(current_variance) * 100),
        'next_period_volatility': float(next_period_vol),
        'avg_forecast_volatility': float(avg_forecast_vol),
        'long_run_volatility': float(np.sqrt(long_run_var) * 100),
        'forecast_horizon': horizon,
        'forecasted_variances': forecasted_variances
    }


def interpret_volatility_level(volatility, symbol):
    """
    Volatilite seviyesini yorumla
    """
    # Coin-specific thresholds
    thresholds = {
        'BTCUSDT': {'low': 1.5, 'moderate': 2.5, 'high': 4.0},
        'ETHUSDT': {'low': 2.0, 'moderate': 3.5, 'high': 5.5},
        'LTCUSDT': {'low': 2.5, 'moderate': 4.0, 'high': 6.0},
    }
    
    # Default thresholds
    default = {'low': 2.0, 'moderate': 3.5, 'high': 5.0}
    threshold = thresholds.get(symbol, default)
    
    if volatility < threshold['low']:
        level = 'LOW'
        description = 'Low volatility - Consolidation phase'
    elif volatility < threshold['moderate']:
        level = 'MODERATE'
        description = 'Moderate volatility - Normal trading'
    elif volatility < threshold['high']:
        level = 'HIGH'
        description = 'High volatility - Increased risk'
    else:
        level = 'EXTREME'
        description = 'Extreme volatility - Caution advised'
    
    return level, description


def get_garch_signal(symbol, interval='1h', lookback=100):
    """
    GARCH volatility signal'ı hesapla
    
    Returns:
        dict: {
            'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
            'volatility_level': 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME',
            'forecast': {...},
            'description': str,
            'available': bool
        }
    """
    
    print(f"\n{'='*80}")
    print(f"🎲 GARCH VOLATILITY ANALYSIS: {symbol} {interval}")
    print(f"{'='*80}")
    
    try:
        # 1. Fetch data
        df = fetch_ohlcv_data(symbol, interval, lookback)
        
        if df is None or len(df) < 50:
            print(f"⚠️ GARCH: Insufficient data")
            return {
                'signal': 'NEUTRAL',
                'volatility_level': 'UNKNOWN',
                'forecast': None,
                'description': 'Insufficient data for GARCH modeling',
                'available': False
            }
        
        # 2. Calculate returns
        df = calculate_log_returns(df)
        returns = df['returns'].dropna()
        
        # 3. Fit GARCH model
        model = fit_garch_model(returns)
        
        # 4. Forecast volatility
        forecast = forecast_volatility(model, returns, horizon=24)
        
        # 5. Interpret level
        avg_vol = forecast['avg_forecast_volatility']
        level, level_desc = interpret_volatility_level(avg_vol, symbol)
        
        # 6. Trading signal based on volatility regime
        if level == 'LOW':
            signal = 'NEUTRAL'
            signal_desc = 'Low volatility - Breakout potential'
        elif level == 'MODERATE':
            signal = 'NEUTRAL'
            signal_desc = 'Moderate volatility - Normal conditions'
        elif level == 'HIGH':
            signal = 'SHORT'  # Reduce exposure
            signal_desc = 'High volatility - Reduce position size'
        else:  # EXTREME
            signal = 'SHORT'
            signal_desc = 'Extreme volatility - High risk, consider exit'
        
        description = f"GARCH Forecast: {avg_vol:.2f}% (Next 24h) - {level_desc} [{symbol}][{interval}]"
        
        print(f"\n✅ GARCH Signal: {signal}")
        print(f"   Level: {level}")
        print(f"   {description}")
        print(f"{'='*80}\n")
        
        return {
            'signal': signal,
            'volatility_level': level,
            'current_vol': forecast['current_volatility'],
            'forecast_vol': avg_vol,
            'long_run_vol': forecast['long_run_volatility'],
            'forecast': forecast,
            'description': description,
            'signal_description': signal_desc,
            'available': True
        }
        
    except Exception as e:
        print(f"❌ GARCH: Error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'signal': 'NEUTRAL',
            'volatility_level': 'UNKNOWN',
            'forecast': None,
            'description': f'GARCH error: {str(e)}',
            'available': False
        }


# Test fonksiyonu
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 DEMIR AI - GARCH Volatility Layer Test")
    print("=" * 80)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT']
    
    for symbol in symbols:
        result = get_garch_signal(symbol, interval='1h', lookback=100)
        
        print(f"\n✅ {symbol} GARCH RESULTS:")
        print(f"   Signal: {result['signal']}")
        print(f"   Volatility Level: {result['volatility_level']}")
        print(f"   Available: {result['available']}")
        
        if result['available']:
            print(f"   Current Vol: {result['current_vol']:.2f}%")
            print(f"   Forecast Vol: {result['forecast_vol']:.2f}%")
            print(f"   Description: {result['description']}")
    
    print("\n" + "=" * 80)
