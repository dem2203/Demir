"""🔮 FOURIER CYCLE - v16.5 COMPATIBLE"""
import numpy as np
import requests
import pandas as pd

def fetch_price_data(symbol, interval='1h', limit=256):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200: return None
        data = response.json()
        df = pd.DataFrame(data, columns=['t','o','h','l','c','v','ct','qv','tr','tbb','tbq','ig'])
        df['close'] = df['c'].astype(float)
        return df
    except: return None

def compute_fft_spectrum(prices):
    try:
        prices_norm = prices - np.mean(prices)
        prices_norm = prices_norm / np.std(prices_norm) if np.std(prices_norm) > 0 else prices_norm
        prices_norm = np.pad(prices_norm, (0, len(prices_norm)), mode='constant')
        fft_values = np.fft.fft(prices_norm)
        power = np.abs(fft_values) ** 2
        freqs = np.fft.fftfreq(len(prices_norm))
        positive_mask = freqs >= 0
        freqs = freqs[positive_mask]
        power = power[positive_mask]
        sorted_idx = np.argsort(power)[::-1]
        return {'frequencies': freqs[sorted_idx][:10], 'power': power[sorted_idx][:10], 
                'dominant_freq': freqs[sorted_idx][0] if len(sorted_idx) > 0 else 0}
    except: return {'frequencies': [], 'power': [], 'dominant_freq': 0}

def analyze_fourier_cycles(symbol='BTCUSDT'):
    """COMPATIBLE FUNCTION"""
    try:
        df = fetch_price_data(symbol, '1h', 256)
        if df is None or len(df) < 100:
            return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
        
        prices = df['close'].values
        spectrum = compute_fft_spectrum(prices)
        dominant_freq = spectrum['dominant_freq']
        
        # Phase
        try:
            analytical_signal = np.fft.ifft(np.fft.fft(prices))
            phase = np.angle(analytical_signal)
            phase_norm = (phase[-1] + np.pi) / (2 * np.pi)
        except:
            phase_norm = 0.5
        
        phase_deg = phase_norm * 360
        score = 50.0
        
        if 0 <= phase_norm <= 0.25:
            signal = "LONG"
            score = 50 + (phase_norm / 0.25) * 40
        elif 0.25 < phase_norm <= 0.5:
            signal = "LONG"
            score = 50 + (1 - (phase_norm - 0.25) / 0.25) * 30
        elif 0.5 < phase_norm <= 0.75:
            signal = "SHORT"
            score = 50 - ((phase_norm - 0.5) / 0.25) * 40
        else:
            signal = "SHORT"
            score = 50 - (1 - (phase_norm - 0.75) / 0.25) * 30
        
        return {'available': True, 'score': round(max(0, min(100, score)), 2), 'signal': signal}
    except:
        return {'available': False, 'score': 50.0, 'signal': 'NEUTRAL'}
