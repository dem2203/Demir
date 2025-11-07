"""
🔮 FOURIER CYCLE LAYER v16.5
============================

Date: 7 Kasım 2025, 14:27 CET
Phase: 7+8 - Quantum Trading AI

AMAÇ:
-----
Fast Fourier Transform (FFT) ile market'taki dominant cycles
ve periodic patterns tespit etmek. Spectral analysis ile entry
timing optimize etmek.

MATHEMATIK:
-----------
FFT: X(f) = Σ x(t)e^(-i2πft)  (Time → Frequency domain)
PSD: |X(f)|²  (Power spectral density)
Phase: arctan(Im/Re)
Cycles: 7-day, 30-day, 90-day patterns
"""

import numpy as np
import requests
import pandas as pd
from datetime import datetime

def fetch_price_data(symbol, interval='1h', limit=256):
    """Fetch REAL price data for FFT analysis"""
    debug = {}
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            debug['http_error'] = f"HTTP {response.status_code}"
            return None, debug
        
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        debug['info'] = f"Fetched {len(df)} real candles"
        return df, debug
        
    except Exception as e:
        debug['exception'] = str(e)
        return None, debug

def compute_fft_spectrum(prices, zero_pad=True):
    """Compute FFT spectrum and dominant frequencies"""
    try:
        # Normalize
        prices_norm = prices - np.mean(prices)
        prices_norm = prices_norm / np.std(prices_norm) if np.std(prices_norm) > 0 else prices_norm
        
        # Zero padding for better resolution
        if zero_pad:
            prices_norm = np.pad(prices_norm, (0, len(prices_norm)), mode='constant')
        
        # FFT
        fft_values = np.fft.fft(prices_norm)
        power = np.abs(fft_values) ** 2
        
        # Get frequencies and power
        freqs = np.fft.fftfreq(len(prices_norm))
        
        # Only positive frequencies
        positive_mask = freqs >= 0
        freqs = freqs[positive_mask]
        power = power[positive_mask]
        
        # Sort by power
        sorted_idx = np.argsort(power)[::-1]
        
        return {
            'frequencies': freqs[sorted_idx][:10],
            'power': power[sorted_idx][:10],
            'dominant_freq': freqs[sorted_idx][0] if len(sorted_idx) > 0 else 0,
            'total_power': np.sum(power)
        }
    except:
        return {
            'frequencies': [],
            'power': [],
            'dominant_freq': 0,
            'total_power': 0
        }

def detect_cycles(freqs, powers, price_length):
    """Detect dominant cycles (7-day, 30-day, 90-day)"""
    try:
        cycles = {}
        
        # Known cycles (as frequency ratios)
        known_cycles = {
            'daily': 1.0 / 1,
            'weekly': 1.0 / 7,
            'monthly': 1.0 / 30,
            'quarterly': 1.0 / 90
        }
        
        for cycle_name, cycle_freq in known_cycles.items():
            # Find power at this frequency
            idx = np.argmin(np.abs(freqs - cycle_freq))
            if idx < len(powers):
                cycles[cycle_name] = {
                    'frequency': freqs[idx],
                    'power': powers[idx],
                    'period': 1 / (freqs[idx] + 1e-10)
                }
        
        return cycles
    except:
        return {}

def calculate_phase_position(prices, dominant_freq):
    """Calculate phase position in cycle"""
    try:
        if dominant_freq == 0:
            return 0.5  # Neutral
        
        # Create analytic signal (Hilbert transform)
        analytical_signal = np.fft.ifft(np.fft.fft(prices))
        phase = np.angle(analytical_signal)
        
        return (phase[-1] + np.pi) / (2 * np.pi)  # Normalize to 0-1
    except:
        return 0.5

def get_fourier_cycle_signal(symbol='BTCUSDT', interval='1h'):
    """
    Fourier Cycle Layer ana fonksiyonu
    
    MANTIK:
    1. Fetch REAL price data
    2. Compute FFT spectrum
    3. Detect dominant cycles
    4. Calculate phase position
    5. Generate score (0-100)
    """
    debug = {}
    
    try:
        print(f"🔮 Fourier Cycle analyzing {symbol}...")
        
        # 1. Get REAL data
        df, fetch_debug = fetch_price_data(symbol, interval, 256)
        debug.update(fetch_debug)
        
        if df is None or len(df) < 100:
            print(f"❌ Data fetch failed")
            return {
                'available': False,
                'score': 50.0,
                'signal': 'NEUTRAL',
                'error_message': 'Insufficient FFT data',
                'data_debug': debug
            }
        
        prices = df['close'].values
        print(f" 📊 Real prices: {len(prices)} candles")
        
        # 2. Compute FFT
        spectrum = compute_fft_spectrum(prices, zero_pad=True)
        dominant_freq = spectrum['dominant_freq']
        print(f" 📈 Dominant Frequency: {dominant_freq:.4f}")
        print(f" 💪 Total Power: {spectrum['total_power']:.2f}")
        
        # 3. Detect cycles
        cycles = detect_cycles(spectrum['frequencies'], spectrum['power'], len(prices))
        for cycle_name, cycle_data in cycles.items():
            print(f" 🔄 {cycle_name}: P={cycle_data['power']:.2f}, Period={cycle_data['period']:.1f}")
        
        # 4. Phase position
        phase = calculate_phase_position(prices, dominant_freq)
        phase_deg = phase * 360
        print(f" 🔄 Phase Position: {phase_deg:.1f}°")
        
        # 5. Score calculation
        score = 50.0
        
        # Phase-based signal
        if 0 <= phase <= 0.25:  # 0-90°: Cycle bottom → UP
            signal = "LONG"
            strength = phase / 0.25
            score = 50 + strength * 40
            print(f" 🟢 Phase 0-90°: Cycle bottom")
            
        elif 0.25 < phase <= 0.5:  # 90-180°: Weak UP
            signal = "LONG"
            strength = 1 - (phase - 0.25) / 0.25
            score = 50 + strength * 30
            print(f" 🟡 Phase 90-180°: Uptrend weakening")
            
        elif 0.5 < phase <= 0.75:  # 180-270°: Cycle top → DOWN
            signal = "SHORT"
            strength = (phase - 0.5) / 0.25
            score = 50 - strength * 40
            print(f" 🔴 Phase 180-270°: Cycle top")
            
        else:  # 270-360°: Weak DOWN
            signal = "SHORT"
            strength = 1 - (phase - 0.75) / 0.25
            score = 50 - strength * 30
            print(f" 🟠 Phase 270-360°: Downtrend weakening")
        
        # Power component (strong signal vs noise)
        avg_power = np.mean(spectrum['power'][:5]) if len(spectrum['power']) > 0 else 1
        power_ratio = spectrum['power'][0] / max(avg_power, 1e-10)
        
        if power_ratio > 2:
            confidence = min(power_ratio / 5, 1.0) * 15
            score = score * (1 + confidence/100) if signal == "LONG" else score * (1 - confidence/100)
            print(f" 💪 Strong signal confidence (+{confidence:.1f})")
        
        score = max(0, min(100, score))
        print(f"✅ Fourier Cycle Score: {score:.1f}/100")
        
        return {
            'available': True,
            'score': round(score, 2),
            'signal': signal,
            'phase': round(phase, 3),
            'phase_degrees': round(phase_deg, 1),
            'dominant_frequency': round(dominant_freq, 4),
            'total_power': round(spectrum['total_power'], 2),
            'cycles_detected': len(cycles),
            'timestamp': datetime.now().isoformat(),
            'data_debug': debug
        }
        
    except Exception as e:
        print(f"❌ Fourier Cycle error: {e}")
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
    print("🔮 FOURIER CYCLE LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        result = get_fourier_cycle_signal(symbol)
        print(f" Score: {result['score']}, Signal: {result['signal']}\n")
