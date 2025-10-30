# analysis_layer.py
# v49.4: calculate_vwap_bands içindeki KeyError düzeltildi (v59.0 için stabil)
# v49.0: VWAP ve Sapma Bantları eklendi
# v48.0: Hacim Profili (PoC, VAH, VAL)
# v47.0: Modüler yapı

import numpy as np
import pandas as pd
from scipy.fft import fft
from math import sqrt, log, log2
from typing import Tuple, Dict, Optional

# Gerekli kütüphaneler
try:
    from arch import arch_model
except ImportError:
    print("Uyarı: 'arch' kütüphanesi yüklü değil. GARCH hesaplamaları yapılamayacak.")
    arch_model = None

try:
    import statsmodels.api as sm
except ImportError:
    print("Uyarı: 'statsmodels' kütüphanesi yüklü değil. MRSM hesaplamaları yapılamayacak.")
    sm = None

try:
    from ta.trend import EMAIndicator, MACD, ADXIndicator, IchimokuIndicator
    try: from ta.trend import KAMAIndicator
    except ImportError:
        try: from ta.momentum import KAMAIndicator
        except ImportError:
            try: from ta.volatility import KAMAIndicator
            except ImportError: KAMAIndicator = None

    from ta.volatility import KeltnerChannel, AverageTrueRange, BollingerBands
    from ta.momentum import RSIIndicator
    TA_LOADED = True
except ImportError:
    print("Kritik Hata: 'ta' kütüphanesi bulunamadı veya eksik.")
    TA_LOADED = False
    EMAIndicator = MACD = ADXIndicator = IchimokuIndicator = KAMAIndicator = None
    KeltnerChannel = AverageTrueRange = BollingerBands = RSIIndicator = None

# Ana config dosyasından sabitler
try:
    from config import EMA_FAST, EMA_SLOW, EMA_MED, EMA_LONG
except ImportError:
    print("Uyarı: config.py bulunamadı, analysis_layer.py varsayılan EMA değerlerini kullanıyor.")
    EMA_FAST, EMA_SLOW, EMA_MED, EMA_LONG = 12, 26, 50, 200

# ----------------------------
# Yardımcı Fonksiyonlar (VWAP için)
# ----------------------------
def typical_price(df: pd.DataFrame) -> pd.Series:
    """Tipik Fiyatı (HLC/3) hesaplar."""
    if all(c in df.columns for c in ['High', 'Low', 'Close']):
        return (df['High'] + df['Low'] + df['Close']) / 3
    elif 'Close' in df.columns:
         print("Uyarı: VWAP için H/L eksik, sadece Close kullanılıyor.")
         return df['Close']
    else:
         return pd.Series(index=df.index, dtype=float) # Boş Seri döndür

# ----------------------------
# Kuantum Matematik Fonksiyonları (v41.0)
# ----------------------------
def calculate_fourier_cycle(df: pd.DataFrame, min_cycle: int = 8, max_cycle: int = 60) -> float:
    """FFT ile baskın döngüyü bulur."""
    # ... (Kod v47.0 ile aynı) ...
    try:
        prices = df['Close'].dropna().values
        if len(prices) < max(min_cycle, 20): return 0.0
        time_index = np.arange(len(prices))
        coeffs = np.polyfit(time_index, prices, 1)
        detrended_prices = prices - (coeffs[0] * time_index + coeffs[1])
        fft_result = fft(detrended_prices)
        frequencies = np.fft.fftfreq(len(detrended_prices))
        positive_freq_mask = frequencies > 1e-9
        if not np.any(positive_freq_mask): return 0.0
        fft_result = fft_result[positive_freq_mask]
        frequencies = frequencies[positive_freq_mask]
        power_spectrum = np.abs(fft_result) ** 2
        periods = 1 / frequencies
        if len(periods) == 0: return 0.0
        valid_period_mask = (periods >= min_cycle) & (periods <= max_cycle)
        if not np.any(valid_period_mask): return 0.0
        valid_powers = power_spectrum[valid_period_mask]
        valid_periods = periods[valid_period_mask]
        dominant_power_index = valid_powers.argmax()
        dominant_period = valid_periods[dominant_power_index]
        return dominant_period
    except Exception: return 0.0

def calculate_fractal_dimension(df: pd.DataFrame, window: int = 100) -> float:
    """Higuchi fraktal boyutunu hesaplar."""
    # ... (Kod v47.0 ile aynı) ...
    try:
        prices = df['Close'].dropna().values[-window:]
        n = len(prices)
        if n < 20: return 1.5
        k_max = int(n / 2)
        lk = np.zeros(k_max)
        for k in range(1, k_max + 1):
            lmk = []
            for m in range(k):
                indices = np.arange(m, n, k)
                if len(indices) < 2: continue
                series_k_m = prices[indices]
                l_m_k = np.sum(np.abs(np.diff(series_k_m))) * (n - 1) / ((len(series_k_m) -1) * k) if (len(series_k_m) > 1 and k > 0) else 0
                lmk.append(l_m_k)
            lk[k-1] = np.mean(lmk) if lmk else 0
        valid_mask = lk > 0
        if np.sum(valid_mask) < 2: return 1.5
        log_lk = np.log(lk[valid_mask])
        log_k = np.log(1.0 / np.arange(1, k_max + 1)[valid_mask])
        coeffs = np.polyfit(log_k, log_lk, 1)
        D = coeffs[0]
        return np.clip(D, 1.0, 2.0)
    except Exception: return 1.5

def calculate_shannon_entropy(df: pd.DataFrame, window: int = 50, bins: int = 10) -> float:
    """Shannon Entropisini hesaplar."""
    # ... (Kod v47.0 ile aynı) ...
    try:
        returns = df['Close'].pct_change().dropna().values[-window:]
        if len(returns) < 2: return 0.0
        hist, bin_edges = np.histogram(returns, bins=bins, density=False)
        probabilities = hist / len(returns)
        non_zero_probs = probabilities[probabilities > 1e-9]
        if len(non_zero_probs) == 0: return 0.0
        entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))
        return entropy
    except Exception: return 0.0

def calculate_quantum_score(df: pd.DataFrame) -> float:
    """Kuantum Skorunu hesaplar."""
    # ... (Kod v47.0 ile aynı) ...
    required_cols = ['fourier_cycle', 'fractal_dimension', 'shannon_entropy']
    if not all(col in df.columns for col in required_cols) or df[required_cols].iloc[-1].isnull().any():
        return 0.0
    fourier_cycle = df['fourier_cycle'].iloc[-1]
    fractal_dim = df['fractal_dimension'].iloc[-1]
    entropy = df['shannon_entropy'].iloc[-1]
    trend_score = (1.5 - fractal_dim) * 50
    cycle_score = 15 if fourier_cycle > 0 else -15
    max_entropy = log2(10)
    noise_score = (max_entropy - entropy) * 10
    quantum_score = trend_score + cycle_score + noise_score
    return round(quantum_score, 2)

# ----------------------------
# İleri Düzey İstatistik (v42.0, v46.0)
# ----------------------------
def calculate_garch_volatility(df: pd.DataFrame) -> float:
    """GARCH(1,1) ile yıllık volatiliteyi tahmin eder."""
    # ... (Kod v47.0 ile aynı) ...
    if arch_model is None or df.empty or len(df) < 50: return np.nan
    returns = 100 * df['Close'].pct_change().dropna()
    if returns.empty or len(returns) < 30: return np.nan
    try:
        model = arch_model(returns, vol='Garch', p=1, q=1, mean='Constant', dist='Normal')
        res = model.fit(update_freq=0, disp='off', show_warning=False)
        forecast = res.forecast(horizon=1, reindex=False)
        daily_vol_percent = sqrt(forecast.variance.iloc[-1, 0])
        annualized_vol = daily_vol_percent * sqrt(365)
        return round(annualized_vol, 2)
    except Exception:
        return round(returns.std() * sqrt(365), 2) if len(returns) > 1 else np.nan

def calculate_regime_probabilities(df: pd.DataFrame, window: int = 100) -> Tuple[float, float, int]:
    """MRSM ile rejim olasılıklarını hesaplar."""
    # ... (Kod v47.0 ile aynı) ...
    if sm is None or len(df) < window: return 0.5, 0.5, 0
    returns = 100 * np.log(df['Close'] / df['Close'].shift(1)).dropna().iloc[-window:]
    if returns.empty or len(returns) < 50: return 0.5, 0.5, 0
    try:
        model = sm.tsa.MarkovRegression(returns, k_regimes=2, trend='c', switching_variance=True)
        res = model.fit(method='powell', disp=False)
        prob_regime_0 = res.filtered_marginal_probabilities[0].iloc[-1]
        prob_regime_1 = 1.0 - prob_regime_0
        params = res.params
        sigma2_0, sigma2_1 = np.nan, np.nan
        for key in params.index:
            if 'sigma2' in key:
                 if key.endswith('[0]') or key.endswith('_0'): sigma2_0 = params[key]
                 elif key.endswith('[1]') or key.endswith('_1'): sigma2_1 = params[key]
        if pd.isna(sigma2_0) or pd.isna(sigma2_1): return 0.5, 0.5, 0
        if sigma2_0 < sigma2_1:
            prob_ranging, prob_trending_volatile = prob_regime_0, prob_regime_1
            current_regime_index = 1 if prob_trending_volatile > 0.5 else 0
        else:
            prob_ranging, prob_trending_volatile = prob_regime_1, prob_regime_0
            current_regime_index = 0 if prob_trending_volatile > 0.5 else 1
        return round(prob_ranging, 4), round(prob_trending_volatile, 4), current_regime_index
    except Exception: return 0.5, 0.5, 0

# ----------------------------
# Diğer Analiz Fonksiyonları (v44.4, v48.0)
# ----------------------------
def calculate_cvd_manual(df: pd.DataFrame) -> pd.Series:
    """Manuel CVD hesaplar."""
    # ... (Kod v47.0 ile aynı) ...
    price_diff = df['Close'].diff()
    direction = np.sign(price_diff).fillna(0)
    directional_volume = df['Volume'] * direction
    cvd = directional_volume.cumsum().fillna(0)
    return cvd

def calculate_volume_profile(
    df_window: pd.DataFrame, volume_col: str = 'Volume', bins: int = 30, value_area_pct: float = 0.70
) -> Dict[str, Optional[float]]:
    """Hacim Profili (PoC, VAH, VAL) hesaplar."""
    # ... (Kod v48.0 ile aynı) ...
    results: Dict[str, Optional[float]] = {"vp_poc": None, "vp_vah": None, "vp_val": None}
    if df_window.empty or volume_col not in df_window.columns or df_window[volume_col].sum() <= 0: return results
    price_data = typical_price(df_window).dropna()
    volume_data = df_window.loc[price_data.index, volume_col].fillna(0).clip(lower=0)
    if price_data.empty: return results
    try:
        min_price, max_price = price_data.min(), price_data.max()
        if min_price == max_price: return results
        bin_edges = np.linspace(min_price, max_price, bins + 1)
        bin_indices = np.digitize(price_data, bin_edges) - 1
        bin_indices[price_data == max_price] = bins - 1
        valid_mask = (bin_indices >= 0) & (bin_indices < bins)
        if not np.any(valid_mask): return results
        volume_per_bin = volume_data[valid_mask].groupby(bin_indices[valid_mask]).sum()
        if volume_per_bin.empty: return results
        poc_bin_index = volume_per_bin.idxmax()
        results["vp_poc"] = round((bin_edges[poc_bin_index] + bin_edges[poc_bin_index + 1]) / 2, 4)
        total_volume = volume_per_bin.sum()
        if total_volume <= 0: return results
        target_volume = total_volume * value_area_pct
        sorted_bins = volume_per_bin.sort_values(ascending=False)
        cumulative_volume = 0.0
        va_indices = set()
        for idx, vol in sorted_bins.items():
            cumulative_volume += vol
            va_indices.add(idx)
            if cumulative_volume >= target_volume: break
        if not va_indices: return results
        val_bin_index, vah_bin_index = min(va_indices), max(va_indices)
        if vah_bin_index + 1 < len(bin_edges) and val_bin_index >= 0:
             results["vp_vah"] = round(bin_edges[vah_bin_index + 1], 4)
             results["vp_val"] = round(bin_edges[val_bin_index], 4)
    except Exception: pass
    return results

# ----------------------------
# v49.4: VWAP ve Sapma Bantları (KeyError Düzeltmesi)
# ----------------------------
def calculate_vwap_bands(df: pd.DataFrame, window: int = 0, reset_on: str = 'D') -> pd.DataFrame:
    """VWAP ve standart sapma bantlarını hesaplar."""
    # ... (Kod v49.4 ile aynı) ...
    if df.empty or 'Volume' not in df.columns or df['Volume'].sum() <= 0 or not any(c in df.columns for c in ['Close', 'High', 'Low']):
         df['vwap'] = np.nan
         for i in range(1, 4): df[f'vwap_upper{i}'], df[f'vwap_lower{i}'] = np.nan, np.nan
         return df
    tp = typical_price(df).fillna(method='ffill')
    volume = df['Volume'].fillna(0)
    if window > 0:
        tp_vol = tp * volume
        cum_tp_vol = tp_vol.rolling(window=window, min_periods=1).sum()
        cum_vol = volume.rolling(window=window, min_periods=1).sum()
        vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
        tp_squared_vol = (tp**2) * volume
        cum_tp_squared_vol = tp_squared_vol.rolling(window=window, min_periods=1).sum()
        variance = (cum_tp_squared_vol / cum_vol.replace(0, np.nan)) - (vwap**2)
        std_dev = np.sqrt(variance.clip(lower=0))
    else:
        df['tp_vol_temp'] = tp * volume
        df['tp_sq_vol_temp'] = (tp**2) * volume
        try:
            grouped = df.groupby(pd.Grouper(freq=reset_on))
            cum_tp_vol = grouped['tp_vol_temp'].cumsum()
            cum_vol = grouped['Volume'].cumsum()
            cum_tp_squared_vol = grouped['tp_sq_vol_temp'].cumsum()
            vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
            variance = (cum_tp_squared_vol / cum_vol.replace(0, np.nan)) - (vwap**2)
            std_dev = np.sqrt(variance.clip(lower=0))
        except Exception as e:
            print(f"Hata: Periyodik VWAP hesaplanamadı ({e}). Kayan pencereye dönülüyor.")
            window = 20
            tp_vol = tp * volume
            cum_tp_vol = tp_vol.rolling(window=window, min_periods=1).sum()
            cum_vol = volume.rolling(window=window, min_periods=1).sum()
            vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
            tp_squared_vol = (tp**2) * volume
            cum_tp_squared_vol = tp_squared_vol.rolling(window=window, min_periods=1).sum()
            variance = (cum_tp_squared_vol / cum_vol.replace(0, np.nan)) - (vwap**2)
            std_dev = np.sqrt(variance.clip(lower=0))
        df.drop(columns=['tp_vol_temp', 'tp_sq_vol_temp'], inplace=True)
    df['vwap'] = vwap
    for i in range(1, 4):
        df[f'vwap_upper{i}'] = vwap + (std_dev * i)
        df[f'vwap_lower{i}'] = vwap - (std_dev * i)
    df['vwap'].fillna(method='bfill', inplace=True)
    for i in range(1, 4):
         df[f'vwap_upper{i}'].fillna(method='bfill', inplace=True)
         df[f'vwap_lower{i}'].fillna(method='bfill', inplace=True)
    return df

# ----------------------------
# Ana Teknik Analiz Motoru
# ----------------------------
def run_technical_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame'e tüm göstergeleri, metrikleri ve analiz sonuçlarını ekler."""
    # ... (Kod v49.4 ile aynı) ...
    if df.empty: return df
    min_len = EMA_LONG if 'EMA_LONG' in globals() else 200
    if len(df) < min_len:
        print(f"Uyarı: run_technical_analysis için yetersiz veri ({len(df)} < {min_len}).")
        required_cols = ['ADX', 'ATR', 'quantum_score', 'prob_trending', 'prob_ranging',
                         'vp_poc', 'vp_vah', 'vp_val', 'vwap']
        for col in required_cols: df[col] = np.nan
        if not all(c in df.columns for c in ['Close', 'High', 'Low', 'Volume']):
             print("Kritik: Temel OHLCV sütunları eksik!")
             return pd.DataFrame()
        return df.ffill().bfill().fillna(0)
    if TA_LOADED:
        df[f'EMA_{EMA_FAST}'] = EMAIndicator(close=df['Close'], window=EMA_FAST, fillna=True).ema_indicator()
        df[f'EMA_{EMA_SLOW}'] = EMAIndicator(close=df['Close'], window=EMA_SLOW, fillna=True).ema_indicator()
        df[f'EMA_{EMA_MED}'] = EMAIndicator(close=df['Close'], window=EMA_MED, fillna=True).ema_indicator()
        df[f'EMA_{EMA_LONG}'] = EMAIndicator(close=df['Close'], window=EMA_LONG, fillna=True).ema_indicator()
        df['RSI'] = RSIIndicator(close=df['Close'], window=14, fillna=True).rsi()
        macd = MACD(close=df['Close'], window_fast=12, window_slow=26, window_sign=9, fillna=True)
        df['MACDh_12_26_9'] = macd.macd_diff()
        df['ATR'] = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14, fillna=True).average_true_range()
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2, fillna=True)
        df['BB_High'] = bb.bollinger_hband(); df['BB_Low'] = bb.bollinger_lband(); df['BB_Mid'] = bb.bollinger_mavg()
        df['BBW'] = (df['BB_High'] - df['BB_Low']) / (df['BB_Mid'] + 1e-9)
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14, fillna=True)
        df['ADX'] = adx.adx()
        if KAMAIndicator: df['KAMA'] = KAMAIndicator(close=df['Close'], window=10, fillna=True).kama()
        else: df['KAMA'] = df['Close'].rolling(window=10, min_periods=1).mean()
        ichimoku = IchimokuIndicator(high=df['High'], low=df['Low'], window1=9, window2=26, window3=52, fillna=True)
        df['ichimoku_a'] = ichimoku.ichimoku_a(); df['ichimoku_b'] = ichimoku.ichimoku_b()
        kc = KeltnerChannel(high=df['High'], low=df['Low'], close=df['Close'], window=20, window_atr=10, fillna=True)
        df['kc_h'] = kc.keltner_channel_hband(); df['kc_l'] = kc.keltner_channel_lband()
        df['squeeze_on'] = (df['BB_High'] < df['kc_h']) & (df['BB_Low'] > df['kc_l'])
        high_roll = df['High'].rolling(window=96, min_periods=1).max().shift(1)
        low_roll = df['Low'].rolling(window=96, min_periods=1).min().shift(1)
        close_roll = df['Close'].shift(1)
        P = (high_roll + low_roll + close_roll) / 3
        df['pivot_s1'] = (P * 2) - high_roll; df['pivot_r1'] = (P * 2) - low_roll
        window_fib = 100
        high_fib = df['High'].rolling(window=window_fib, min_periods=2).max()
        low_fib = df['Low'].rolling(window=window_fib, min_periods=2).min()
        diff_fib = high_fib - low_fib
        if isinstance(diff_fib, pd.Series): diff_fib = diff_fib.replace(0, np.nan)
        elif diff_fib == 0: diff_fib = np.nan
        df['fib_236'] = high_fib - diff_fib * 0.236
        df['fib_382'] = high_fib - diff_fib * 0.382
        df['fib_618'] = high_fib - diff_fib * 0.618
    else:
         cols_to_nan = [f'EMA_{EMA_FAST}', f'EMA_{EMA_SLOW}', f'EMA_{EMA_MED}', f'EMA_{EMA_LONG}', 'RSI', 'MACDh_12_26_9', 'ATR',
                        'BB_High', 'BB_Low', 'BB_Mid', 'BBW', 'ADX', 'KAMA', 'ichimoku_a', 'ichimoku_b', 'kc_h', 'kc_l',
                        'squeeze_on', 'pivot_s1', 'pivot_r1', 'fib_236', 'fib_382', 'fib_618']
         for col in cols_to_nan: df[col] = np.nan
    df = calculate_vwap_bands(df, reset_on='D') # Günlük sıfırlanan
    df['cvd'] = calculate_cvd_manual(df)
    df['fourier_cycle'] = calculate_fourier_cycle(df)
    df['fractal_dimension'] = calculate_fractal_dimension(df)
    df['shannon_entropy'] = calculate_shannon_entropy(df)
    df['quantum_score'] = calculate_quantum_score(df)
    df['GARCH_Volatility'] = calculate_garch_volatility(df)
    prob_ranging, prob_trending, _ = calculate_regime_probabilities(df)
    df['prob_ranging'] = prob_ranging
    df['prob_trending'] = prob_trending
    vp_window = 200; vp_bins = 30
    vp_poc_last, vp_vah_last, vp_val_last = None, None, None
    if len(df) >= max(50, vp_bins):
        last_window_df = df.iloc[-vp_window:]
        vp_data_last = calculate_volume_profile(last_window_df, bins=vp_bins)
        vp_poc_last = vp_data_last.get('vp_poc')
        vp_vah_last = vp_data_last.get('vp_vah')
        vp_val_last = vp_data_last.get('vp_val')
    df['vp_poc'] = vp_poc_last; df['vp_vah'] = vp_vah_last; df['vp_val'] = vp_val_last
    df['vp_poc'].fillna(method='ffill', inplace=True)
    df['vp_vah'].fillna(method='ffill', inplace=True)
    df['vp_val'].fillna(method='ffill', inplace=True)
    base_critical_cols = ['Close', 'Volume']
    ta_critical_cols = ['ADX', 'ATR', 'RSI'] if TA_LOADED else []
    vp_critical_cols = ['vp_poc']
    vwap_critical_cols = ['vwap']
    all_critical_cols = base_critical_cols + ta_critical_cols + vp_critical_cols + vwap_critical_cols
    missing_critical = [col for col in all_critical_cols if col not in df.columns]
    if missing_critical:
        print(f"Kritik: Temizleme öncesi eksik sütunlar: {missing_critical}")
        for col in missing_critical: df[col] = np.nan
    df_cleaned = df.dropna(subset=all_critical_cols)
    if df_cleaned.empty and not df.empty:
         print(f"Uyarı: Analiz sonrası ({len(df)} satır) dropna kritiği boş DataFrame döndürdü. NaN'lar dolduruluyor.")
         df = df.ffill().bfill().fillna(0)
         df_cleaned = df.dropna(subset=all_critical_cols)
         if df_cleaned.empty:
             print("Kritik: NaN doldurma sonrası bile kritik sütunlar eksik.")
             return pd.DataFrame()
    df_cleaned = df_cleaned.ffill().bfill() # fillna(0) yerine ffill/bfill daha iyi
    return df_cleaned


# ----------------------------
# Piyasa Rejim Tespiti (v47.0)
# ----------------------------
def detect_market_regime(df: pd.DataFrame) -> str:
    """v47.0: Piyasa Rejimini (MRSM Olasılıklarına ve ADX'e Göre) tespit eder."""
    # ... (Kod v47.0 ile aynı) ...
    required_cols = ['prob_trending', 'prob_ranging', 'ADX']
    last_valid_idx = None
    for i in range(len(df) - 1, -1, -1):
        try:
             row = df.iloc[i]
             if all(col in row.index and pd.notna(row[col]) for col in required_cols):
                  last_valid_idx = i; break
        except IndexError: continue
    if last_valid_idx is None: return " ⚪ Veri Yok/Hesaplanıyor..."
    last_row = df.iloc[last_valid_idx]
    last_adx = last_row['ADX']
    prob_trending = last_row['prob_trending']
    prob_ranging = last_row['prob_ranging']
    confidence_pct = max(prob_trending, prob_ranging) * 100
    dominant_prob = "YüksekVol" if prob_trending > prob_ranging else "DüşükVol"
    if confidence_pct > 70:
        if dominant_prob == "YüksekVol":
            return f"🟢 TREND ({confidence_pct:.0f}%)" if last_adx > 25 else f"🔴 VOLATILE ({confidence_pct:.0f}%)"
        else:
            return f"🟡 RANGING ({confidence_pct:.0f}%)" if last_adx < 20 else f"🔵 KARARSIZ (DüşükVol, ADX Yüksek {last_adx:.0f})"
    else:
        if last_adx > 25: return f"🟢 TREND (ADX {last_adx:.0f})"
        elif last_adx < 20: return f"🟡 RANGING (ADX {last_adx:.0f})"
        else: return f"🔵 KARARSIZ (MRSM <%70, ADX {last_adx:.0f})"

print("✅ analysis_layer.py v49.4 (Stabil) yüklendi.")
