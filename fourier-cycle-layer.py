"""
🔮 FOURIER CYCLE LAYER v1.0
===========================
Date: 4 Kasım 2025, 09:15 CET
Phase: 7.4 - Quantum Mathematics

AMAÇ:
-----
Fast Fourier Transform (FFT) kullanarak market'taki dominant
cycle'ları tespit etmek. Spectral analysis ile periodic patterns
bulmak ve cycle phase'ine göre entry timing optimize etmek.

MATEMATİK:
----------
1. FFT (Fast Fourier Transform):
   X(f) = Σ x(t)e^(-i2πft)
   
   Time domain → Frequency domain dönüşümü

2. Power Spectral Density (PSD):
   PSD = |X(f)|²
   
   Her frekansın gücü

3. Dominant Cycles:
   - 7-day cycle (weekly pattern)
   - 30-day cycle (monthly pattern)
   - 90-day cycle (quarterly pattern)

4. Phase Detection:
   - Phase = arctan(Im/Re)
   - Phase 0° = Cycle bottom (BUY)
   - Phase 90° = Uptrend
   - Phase 180° = Cycle top (SELL)
   - Phase 270° = Downtrend

SINYAL LOJİĞİ:
--------------
- Dominant cycle phase 0-90° → LONG (60-90)
- Phase 90-180° → Weak LONG (50-65)
- Phase 180-270° → SHORT (10-40)
- Phase 270-360° → Weak SHORT (35-50)

Multiple cycles: Weighted average

SKOR: 0-100
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

# ============================================================================
# FFT & SPECTRAL ANALYSIS
# ============================================================================

def calculate_fft_spectrum(prices):
    """
    FFT ile frequency spectrum hesapla
    
    Args:
        prices (array): Price series
        
    Returns:
        tuple: (frequencies, power_spectrum, phases)
    """
    try:
        # Detrend (trend'i çıkar)
        detrended = prices - np.linspace(prices[0], prices[-1], len(prices))
        
        # FFT hesapla
        fft_values = fft(detrended)
        
        # Power spectrum
        power = np.abs(fft_values)**2
        
        # Phases
        phases = np.angle(fft_values)
        
        # Frequencies (sampling rate = 1 per candle)
        frequencies = fftfreq(len(prices), d=1)
        
        # Sadece pozitif frekanslar
        positive_freq_idx = frequencies > 0
        frequencies = frequencies[positive_freq_idx]
        power = power[positive_freq_idx]
        phases = phases[positive_freq_idx]
        
        return frequencies, power, phases
        
    except Exception as e:
        print(f"⚠️ FFT calculation error: {e}")
        return np.array([]), np.array([]), np.array([])


def find_dominant_cycles(frequencies, power, min_period=5, max_period=200):
    """
    Dominant cycle'ları bul
    
    Args:
        frequencies (array): Frequency values
        power (array): Power spectrum
        min_period (int): Minimum cycle period (candles)
        max_period (int): Maximum cycle period (candles)
        
    Returns:
        list: [(period, power, frequency), ...]
    """
    try:
        # Period = 1 / frequency
        periods = 1 / frequencies
        
        # Filter by period range
        valid_idx = (periods >= min_period) & (periods <= max_period)
        periods = periods[valid_idx]
        power = power[valid_idx]
        frequencies = frequencies[valid_idx]
        
        if len(power) == 0:
            return []
        
        # Find peaks in power spectrum
        peaks, properties = find_peaks(power, prominence=np.max(power)*0.1)
        
        if len(peaks) == 0:
            # Return top 3 by power
            top_idx = np.argsort(power)[-3:]
            return [(periods[i], power[i], frequencies[i]) for i in top_idx]
        
        # Sort by power
        peak_data = [(periods[i], power[i], frequencies[i]) for i in peaks]
        peak_data.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 5
        return peak_data[:5]
        
    except Exception as e:
        print(f"⚠️ Cycle detection error: {e}")
        return []


def calculate_cycle_phase(prices, period):
    """
    Belirli bir cycle için current phase hesapla
    
    Args:
        prices (array): Price series
        period (float): Cycle period (candles)
        
    Returns:
        float: Phase in degrees (0-360)
    """
    try:
        if period < 2:
            return 180.0  # Neutral
        
        # Last 2 cycle lengths
        lookback = int(period * 2)
        recent_prices = prices[-lookback:] if len(prices) > lookback else prices
        
        # Detrend
        detrended = recent_prices - np.linspace(recent_prices[0], recent_prices[-1], len(recent_prices))
        
        # FFT
        fft_values = fft(detrended)
        
        # Frequency corresponding to period
        freq_idx = int(len(recent_prices) / period)
        if freq_idx >= len(fft_values) // 2:
            freq_idx = len(fft_values) // 2 - 1
        
        # Phase at this frequency
        phase_rad = np.angle(fft_values[freq_idx])
        phase_deg = np.degrees(phase_rad)
        
        # Normalize to 0-360
        if phase_deg < 0:
            phase_deg += 360
        
        return phase_deg
        
    except Exception as e:
        print(f"⚠️ Phase calculation error: {e}")
        return 180.0  # Neutral


def interpret_phase(phase):
    """
    Phase'e göre sinyal yorumla
    
    Args:
        phase (float): Phase in degrees (0-360)
        
    Returns:
        tuple: (signal, strength)
    """
    if 0 <= phase < 90:
        return "STRONG_LONG", 1.0  # Bottom to uptrend
    elif 90 <= phase < 180:
        return "LONG", 0.6  # Uptrend to top
    elif 180 <= phase < 270:
        return "SHORT", 1.0  # Top to downtrend
    else:  # 270 <= phase < 360
        return "WEAK_SHORT", 0.6  # Downtrend to bottom


# ============================================================================
# DATA FETCHING
# ============================================================================

def get_historical_data(symbol, interval='1h', limit=500):
    """
    Binance'den historical data çek (FFT için daha fazla data)
    """
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        
        return df
    except Exception as e:
        print(f"⚠️ Data fetch failed: {e}")
        return None


# ============================================================================
# FOURIER CYCLE SIGNAL GENERATOR
# ============================================================================

def get_fourier_cycle_signal(symbol, interval='1h'):
    """
    Fourier Cycle layer ana fonksiyonu
    
    MANTIK:
    -------
    1. Historical data çek (500 candle - FFT için yeterli)
    2. FFT hesapla, power spectrum
    3. Dominant cycle'ları tespit et
    4. Her cycle için current phase hesapla
    5. Phase'leri weighted average ile skorla
    
    Args:
        symbol (str): Trading pair
        interval (str): Timeframe
        
    Returns:
        float: Score (0-100)
    """
    try:
        print(f"🔮 Fourier Cycle analyzing {symbol}...")
        
        # 1. Data çek
        df = get_historical_data(symbol, interval, limit=500)
        if df is None or len(df) < 100:
            print("⚠️ Insufficient data")
            return 50.0
        
        prices = df['close'].values
        
        # 2. FFT spectrum
        frequencies, power, phases = calculate_fft_spectrum(prices)
        
        if len(frequencies) == 0:
            print("⚠️ FFT failed")
            return 50.0
        
        # 3. Dominant cycle'ları bul
        dominant_cycles = find_dominant_cycles(frequencies, power)
        
        if len(dominant_cycles) == 0:
            print("⚠️ No cycles detected")
            return 50.0
        
        print(f"   Dominant Cycles Detected: {len(dominant_cycles)}")
        
        # 4. Her cycle için phase ve sinyal
        cycle_signals = []
        total_power = sum(c[1] for c in dominant_cycles)
        
        for period, cycle_power, freq in dominant_cycles:
            phase = calculate_cycle_phase(prices, period)
            signal_type, strength = interpret_phase(phase)
            
            # Weight by power
            weight = cycle_power / total_power if total_power > 0 else 0
            
            print(f"   - Period: {period:.1f} candles | Phase: {phase:.1f}° | Signal: {signal_type} | Weight: {weight:.2f}")
            
            cycle_signals.append((signal_type, strength, weight))
        
        # 5. Weighted score hesapla
        score = 50.0  # Baseline
        
        for signal_type, strength, weight in cycle_signals:
            if signal_type == "STRONG_LONG":
                contribution = 40 * strength * weight
            elif signal_type == "LONG":
                contribution = 20 * strength * weight
            elif signal_type == "SHORT":
                contribution = -40 * strength * weight
            elif signal_type == "WEAK_SHORT":
                contribution = -20 * strength * weight
            else:
                contribution = 0
            
            score += contribution
        
        # Skor 0-100 aralığına sınırla
        score = np.clip(score, 0, 100)
        
        print(f"✅ Fourier Cycle Score: {score:.1f}/100")
        
        return score
        
    except Exception as e:
        print(f"❌ Fourier Cycle error: {e}")
        return 50.0


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def analyze_cycles(symbol, interval='1h'):
    """
    Alias for backward compatibility
    """
    return get_fourier_cycle_signal(symbol, interval)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("🔮 FOURIER CYCLE LAYER TEST")
    print("="*80)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        score = get_fourier_cycle_signal(symbol)
        
        if score >= 65:
            signal = "🟢 LONG"
        elif score <= 35:
            signal = "🔴 SHORT"
        else:
            signal = "⚪ NEUTRAL"
        
        print(f"   Signal: {signal}")
        print(f"   Score: {score:.1f}/100")
        print("-"*80)
