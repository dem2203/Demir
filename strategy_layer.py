# strategy_layer.py
#! v68.0: KRİTİK DÜZELTME: driving_factors kapsam hatası düzeltildi.
#         - generate_signal fonksiyonu içindeki driving_factors listesi doğru şekilde tanımlanmıştır.
# v67.0: SÖZDİZİMİ HATASI DÜZELTİLDİ. (name 'driving_factors' is not defined)

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from math import sqrt
import streamlit as st
import json

# ML Kütüphaneleri
try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.exceptions import NotFittedError
    ML_LOADED = True
except ImportError:
    print("Uyarı: 'scikit-learn' kütüphanesi yüklü değil. ML modeli çalışmayacak.")
    StandardScaler = MinMaxScaler = RandomForestClassifier = NotFittedError = None
    ML_LOADED = False

# Diğer modüllerden ve config'den importlar
try:
    from config import (
        RISK_PER_TRADE_PERCENT, MAX_HOLD_BARS, BINANCE_FEE_RATE,
        EMA_FAST, EMA_SLOW, model_cache, scaler_cache,
        TRAILING_SL_ENABLED, TRAILING_SL_ACTIVATION_R, TRAILING_SL_ATR_MULTIPLIER
    )
except ImportError:
    print("Uyarı: config.py bulunamadı.")
    RISK_PER_TRADE_PERCENT, MAX_HOLD_BARS, BINANCE_FEE_RATE = 0.01, 5, 0.0004
    EMA_FAST, EMA_SLOW = 12, 26
    model_cache, scaler_cache = {}, {}
    TRAILING_SL_ENABLED, TRAILING_SL_ACTIVATION_R, TRAILING_SL_ATR_MULTIPLIER = True, 1.0, 2.0


try:
    from db_layer import load_factor_performance_from_db, save_kpis_to_db, save_factor_performance_to_db
except ImportError:
    print("Uyarı: db_layer.py bulunamadı.")
    load_factor_performance_from_db = save_kpis_to_db = save_factor_performance_to_db = None

try:
    from analysis_layer import detect_market_regime
except ImportError:
     print("Uyarı: analysis_layer.py bulunamadı.")
     detect_market_regime = None

# ----------------------------
# Finansal Zeka Metrikleri
# ----------------------------
def calculate_kelly_criterion(win_rate: float, avg_payout_ratio: float) -> float:
    if avg_payout_ratio <= 0 or win_rate <= 0 or win_rate >= 1: return 0.0
    p = win_rate; q = 1.0 - p; R = avg_payout_ratio
    f = p - (q / R)
    return round(max(0, f), 4)

def calculate_risk_of_ruin(win_rate: float, avg_payout_ratio: float, risk_per_trade: float) -> float:
    if win_rate <= 0 or risk_per_trade <= 0: return 1.0
    if win_rate >= 1: return 0.0
    if avg_payout_ratio <= 0: return 1.0
    edge = win_rate * avg_payout_ratio - (1.0 - win_rate)
    if edge <= 0: return 1.0
    p = win_rate; q = 1.0 - p
    try: ror = (q / p) ** (10 * risk_per_trade)
    except (OverflowError, ZeroDivisionError): ror = 1.0
    return round(np.clip(ror, 0.0, 1.0), 4)

def determine_risk_mode(ror: float, kelly: float) -> str:
    if pd.isna(ror) or pd.isna(kelly): return "⚪ Hesaplanıyor..."
    if ror < 0.02 and kelly > 0.10: return "🔥 AGRESİF"
    elif ror < 0.10 and kelly > 0.05: return "⚖️ DENGELİ"
    else: return "🛡️ SAVUNMA"

# ----------------------------
# Makine Öğrenimi Modeli (v53.3 - RandomForest)
# ----------------------------
@st.cache_resource(ttl=3600)
def train_predictive_model(df: pd.DataFrame) -> Tuple[Any, Any, float]:
    if not ML_LOADED: return None, None, 0.5
    features = ['Close', 'Volume', 'RSI', 'MACDh_12_26_9', 'ADX', 'BBW', 'KAMA',
                'quantum_score', 'prob_trending', 'cvd', 'vwap',
                'fractal_dimension', 'shannon_entropy', 'prob_ranging']
    available_features = [f for f in features if f in df.columns and not df[f].isnull().all()]
    if not available_features or 'Close' not in available_features:
        print("Uyarı: ML için yeterli özellik veya 'Close' sütunu bulunamadı.")
        return None, None, 0.5
    df_model = df[available_features].copy().dropna()
    n_future = 5
    df_model['future_price'] = df_model['Close'].shift(-n_future)
    df_model['target'] = np.where(df_model['future_price'] > df_model['Close'], 1, 0)
    df_model = df_model.dropna(subset=['target', 'future_price'])
    if len(df_model) < 50:
        print(f"Uyarı: ML eğitimi için yetersiz veri ({len(df_model)} satır).")
        return None, None, 0.5
    X = df_model.drop(columns=['target', 'future_price'])
    y = df_model['target']
    scaler_key = 'ml_scaler'
    if scaler_key in scaler_cache: scaler = scaler_cache[scaler_key]
    else: scaler = StandardScaler(); scaler_cache[scaler_key] = scaler
    try: X_scaled = scaler.fit_transform(X)
    except Exception as e: print(f"ML Scaler hatası: {e}"); return None, None, 0.5
    model_key = 'ml_model'
    model = None
    if model_key in model_cache: model = model_cache[model_key]
    else:
        print("Yeni RandomForest modeli oluşturuluyor...");
        model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
        model_cache[model_key] = model
    try: model.fit(X_scaled, y); model_cache[model_key] = model
    except Exception as e: print(f"ML Model oluşturma/eğitim hatası: {e}"); return scaler, None, 0.5
    prediction_probability = 0.5
    if model:
        try:
            last_row_features = df[available_features].iloc[-1].values.reshape(1, -1)
            last_features_scaled = scaler.transform(last_row_features)
            prediction_probability = model.predict_proba(last_features_scaled)[0][1]
        except Exception as e: print(f"ML Tahmin hatası: {e}")
    return model_cache.get(model_key), scaler_cache.get(scaler_key), prediction_probability


# ----------------------------
# Sinyal Üretme Motoru (v68.0 - Hibrit Canlı Analiz)
# ----------------------------
def calculate_weight_multiplier(kpi_data: Optional[Dict[str, Any]]) -> float:
    if not kpi_data or kpi_data.get('total_trades', 0) < 10: return 1.0
    r_multiple = kpi_data.get('avg_r_multiple', 1.0) if kpi_data.get('avg_r_multiple') is not None else 1.0
    win_rate = kpi_data.get('win_rate_pct', 50.0) if kpi_data.get('win_rate_pct') is not None else 50.0
    if r_multiple > 1.5 and win_rate > 55.0: return 1.5
    elif r_multiple < 0.9 or win_rate < 45.0: return 0.5
    elif win_rate > 53.0: return 1.1
    elif r_multiple < 1.0 or win_rate < 48.0: return 0.9
    else: return 1.0

def generate_signal(
    df: pd.DataFrame, i: int, macro: Dict, derivatives: Dict, on_chain: Dict,
    sentiment_data: Dict, liq_data: Dict, prediction_probability: float,
    factor_weights_data: Dict[str, Dict[str, Any]], live_price: float, prev_close: float
) -> Tuple[str, Dict[str, float], List[str], Dict[str, float], float]:
    
    signal = "NEUTRAL"; report_multipliers = {}; factor_contributions = {}; final_strength = 0.0
    
    #! v68.0: KRİTİK DÜZELTME: driving_factors'ı doğru kapsamda tanımla (Önceki hatayı düzeltir)
    driving_factors: List[str] = []
    
    if df.empty or i < 0 or i >= len(df): return signal, report_multipliers, driving_factors, factor_contributions, 0.0
    
    current = df.iloc[i]; prev = df.iloc[i-1] if i > 0 else current
    current_close = current['Close']; atr = current.get('ATR', 0)
    
    # ---------------------------------------------
    # Tick Reactivity Score
    # ---------------------------------------------
    tick_reaction_signal = 0
    tick_reaction_weight = 3.0 # Çok yüksek ağırlık
    price_change_live = live_price - prev_close
    
    if atr > 0:
         # Anlık fiyat, son kapanıştan 0.5 ATR fazla/eksikse tepki ver
         if price_change_live > (atr * 0.5):
              tick_reaction_signal = 1
              driving_factors.append("tick_reaction(B)")
         elif price_change_live < -(atr * 0.5):
              tick_reaction_signal = -1
              driving_factors.append("tick_reaction(S)")
              
    
    known_factors = ["ta_trend", "ta_momentum", "on_chain_l2", "macro", "sentiment", "ml_predict",
                     "liq_filter", "quantum", "ichimoku", "squeeze", "cvd", "fibonacci",
                     "volume_profile", "vwap", "oi_delta", "tick_reactivity"]
    
    multipliers = {f: calculate_weight_multiplier(factor_weights_data.get(f)) for f in known_factors}
    
    base_weights = {"ta_trend": 1.0, "ta_momentum": 1.0, "on_chain_l2": 1.0, "macro": 1.0, "sentiment": 1.5,
                    "ml_predict": 2.0, "liq_filter": 2.0, "quantum": 2.5, "ichimoku": 1.5, "squeeze": 0.5,
                    "cvd": 1.5, "fibonacci": 1.0, "volume_profile": 1.8, "vwap": 1.6, "oi_delta": 1.7,
                    "tick_reactivity": tick_reaction_weight }
    
    weights = {f: base_weights.get(f, 0) * multipliers.get(f, 1.0) for f in base_weights}
    driving_factors_ta: List[str] = []; factor_contributions = {f: 0.0 for f in known_factors} 
    
    # --- Sabit Faktörler (Mum Kapanışına Dayalı) ---
    is_kama_bullish = current_close > current.get('KAMA', current_close + 1)
    is_ema_bullish = current.get(f'EMA_{EMA_FAST}', 0) > current.get(f'EMA_{EMA_SLOW}', 1)
    ta_trend_signal = 1 if is_kama_bullish or is_ema_bullish else -1 if not is_kama_bullish or not is_ema_bullish else 0
    factor_contributions["ta_trend"] = ta_trend_signal * weights.get("ta_trend", 0)
    if ta_trend_signal != 0: driving_factors_ta.append(f"ta_trend({'B' if ta_trend_signal > 0 else 'S'})")
    rsi = current.get('RSI', 50); is_rsi_oversold = rsi < 30; is_rsi_overbought = rsi > 70
    is_rsi_bullish = rsi > 55; is_rsi_bearish = rsi < 45
    ta_momentum_signal = 1 if is_rsi_bullish or is_rsi_oversold else -1 if is_rsi_bearish or is_rsi_overbought else 0
    factor_contributions["ta_momentum"] = ta_momentum_signal * weights.get("ta_momentum", 0)
    if ta_momentum_signal != 0: driving_factors_ta.append(f"ta_momentum({'B' if ta_momentum_signal > 0 else 'S'})")
    is_above_cloud = current_close > current.get('ichimoku_a', -1) and current_close > current.get('ichimoku_b', -1)
    is_below_cloud = current_close < current.get('ichimoku_a', 9e9) and current_close < current.get('ichimoku_b', 9e9)
    ichimoku_signal = 1 if is_above_cloud else -1 if is_below_cloud else 0
    factor_contributions["ichimoku"] = ichimoku_signal * weights.get("ichimoku", 0)
    if ichimoku_signal != 0: driving_factors_ta.append(f"ichimoku({'B' if ichimoku_signal > 0 else 'S'})")
    squeeze_signal = 0
    if current.get('squeeze_on', False):
        if is_rsi_bullish: squeeze_signal = 1; driving_factors_ta.append("squeeze(B)")
        elif is_rsi_bearish: squeeze_signal = -1; driving_factors_ta.append("squeeze(S)")
    factor_contributions["squeeze"] = squeeze_signal * weights.get("squeeze", 0)
    cvd_now = current.get('cvd', 0); cvd_prev = prev.get('cvd', 0); cvd_signal = 1 if cvd_now > cvd_prev else -1
    factor_contributions["cvd"] = cvd_signal * weights.get("cvd", 0)
    driving_factors_ta.append(f"cvd({'B' if cvd_signal > 0 else 'S'})")
    fib_signal = 0; dist_to_fib618 = abs(current_close - current.get('fib_618', current_close)) / (atr + 1e-9)
    dist_to_fib382 = abs(current_close - current.get('fib_382', current_close)) / (atr + 1e-9)
    if dist_to_fib618 < 0.5 and is_rsi_oversold: fib_signal = 1; driving_factors_ta.append("fibonacci(B)")
    elif dist_to_fib382 < 0.5 and is_rsi_overbought: fib_signal = -1; driving_factors_ta.append("fibonacci(S)")
    factor_contributions["fibonacci"] = fib_signal * weights.get("fibonacci", 0)
    is_macro_risk_off = (macro.get("VIX", 20) > 28) or (macro.get("DXY", 100) > 106)
    is_macro_risk_on = (macro.get("VIX", 20) < 15) and (macro.get("DXY", 100) < 103)
    macro_signal = 1 if is_macro_risk_on else -1 if is_macro_risk_off else 0
    factor_contributions["macro"] = macro_signal * weights.get("macro", 0)
    if macro_signal != 0: driving_factors_ta.append(f"macro({'B' if macro_signal > 0 else 'S'})")
    sentiment_score = sentiment_data.get('score', 0.0); sentiment_signal = 1 if sentiment_score > 0.8 else -1 if sentiment_score < -0.8 else 0
    factor_contributions["sentiment"] = sentiment_signal * weights.get("sentiment", 0)
    if sentiment_signal != 0: driving_factors_ta.append(f"sentiment({'B' if sentiment_signal > 0 else 'S'})")
    oir = on_chain.get("OIR", 0.0); on_chain_signal = 1 if oir > 0.15 else -1 if oir < -0.15 else 0
    factor_contributions["on_chain_l2"] = on_chain_signal * weights.get("on_chain_l2", 0)
    if on_chain_signal != 0: driving_factors_ta.append(f"on_chain_l2({'B' if on_chain_signal > 0 else 'S'})")
    ml_signal = 1 if prediction_probability > 0.60 else -1 if prediction_probability < 0.40 else 0
    factor_contributions["ml_predict"] = ml_signal * weights.get("ml_predict", 0)
    if ml_signal != 0: driving_factors_ta.append(f"ml_predict({'B' if ml_signal > 0 else 'S'})")
    q_score = current.get('quantum_score', 0); quantum_signal = 1 if q_score > 30 else -1 if q_score < -30 else 0
    factor_contributions["quantum"] = quantum_signal * weights.get("quantum", 0)
    if quantum_signal != 0: driving_factors_ta.append(f"quantum({'B' if quantum_signal > 0 else 'S'})")
    poc = current.get('vp_poc'); vah = current.get('vp_vah'); val = current.get('vp_val'); vp_signal_poc = 0; vp_signal_mr = 0
    if pd.notna(poc):
        dist_to_poc = abs(current_close - poc) / (atr + 1e-9)
        if current_close > poc and dist_to_poc < 0.5: vp_signal_poc = 0.7; driving_factors_ta.append("volume_profile(PoC_Sup)")
        elif current_close < poc and dist_to_poc < 0.5: vp_signal_poc = -0.7; driving_factors_ta.append("volume_profile(PoC_Res)")
        elif current_close > poc and (current_close - prev['Close'] > 0): vp_signal_poc = 0.3; driving_factors_ta.append("volume_profile(PoC_TrendB)")
        elif current_close < poc and (current_close - prev['Close'] < 0): vp_signal_poc = -0.3; driving_factors_ta.append("volume_profile(PoC_TrendS)")
    if pd.notna(val) and pd.notna(vah):
        dist_to_val = abs(current_close - val) / (atr + 1e-9); dist_to_vah = abs(current_close - vah) / (atr + 1e-9)
        if dist_to_val < 0.3 and is_rsi_oversold: vp_signal_mr = 1.0; driving_factors_ta.append("volume_profile(VAL_MR_B)")
        elif dist_to_vah < 0.3 and is_rsi_overbought: vp_signal_mr = -1.0; driving_factors_ta.append("volume_profile(VAH_MR_S)")
    factor_contributions["volume_profile"] = (vp_signal_poc + vp_signal_mr) * weights.get("volume_profile", 0)
    vwap = current.get('vwap'); vwap_signal = 0; vwap_lower2 = current.get('vwap_lower2'); vwap_upper2 = current.get('vwap_upper2')
    if pd.notna(vwap):
        vwap_trend = 0.5 if current_close > vwap else -0.5; driving_factors_ta.append(f"vwap({'TrendB' if vwap_trend > 0 else 'S'})")
        vwap_mr = 0
        if pd.notna(vwap_lower2) and current_close < vwap_lower2 and is_rsi_oversold: vwap_mr = 1.0; driving_factors_ta.append("vwap(MR_B)")
        if pd.notna(vwap_upper2) and current_close > vwap_upper2 and is_rsi_overbought: vwap_mr = -1.0; driving_factors_ta.append("vwap(MR_S)")
        dist_to_vwap = abs(current_close - vwap) / (atr + 1e-9)
        if dist_to_vwap < 0.3: driving_factors_ta.append(f"vwap({'Sup' if current_close > vwap else 'Res'})")
        vwap_signal = vwap_trend + vwap_mr
    factor_contributions["vwap"] = vwap_signal * weights.get("vwap", 0)
    oi_delta_usd = derivatives.get("oi_delta_usd", 0); oi_signal = 0; oi_value = derivatives.get("oi_value_usd", 1e9)
    oi_delta_pct_threshold = 0.01
    price_change_candle = current_close - prev['Close'] if i > 0 else 0
    if price_change_candle > atr * 0.1:
        if oi_delta_usd > oi_delta_pct_threshold * oi_value: oi_signal = 1; driving_factors_ta.append("oi_delta(PriceUp_OIUp)")
        elif oi_delta_usd < -oi_delta_pct_threshold * oi_value: oi_signal = -0.5; driving_factors_ta.append("oi_delta(PriceUp_OIDown)")
    elif price_change_candle < -atr * 0.1:
        if oi_delta_usd > oi_delta_pct_threshold * oi_value: oi_signal = -1; driving_factors_ta.append("oi_delta(PriceDown_OIUp)")
        elif oi_delta_usd < -oi_delta_pct_threshold * oi_value: oi_signal = 0.5; driving_factors_ta.append("oi_delta(PriceDown_OIDown)")
    factor_contributions["oi_delta"] = oi_signal * weights.get("oi_delta", 0)

    # Rejim Filtresi
    prob_trending = current.get('prob_trending', 0.5); trending_multiplier = 1.0 + prob_trending; ranging_multiplier = 1.0 + (1.0 - prob_trending)
    trend_factors = ["ta_trend", "ichimoku", "quantum", "cvd", "vwap", "oi_delta"]
    ranging_factors = ["ta_momentum", "fibonacci", "squeeze", "volume_profile"]
    for factor in trend_factors:
         if factor in factor_contributions: factor_contributions[factor] *= trending_multiplier
    for factor in ranging_factors:
         if factor in factor_contributions: factor_contributions[factor] *= ranging_multiplier
         
    # Likidasyon Filtresi
    long_liq = liq_data.get('long_liq_price'); short_liq = liq_data.get('short_liq_price'); liq_penalty = 0.0
    if atr and atr > 0:
         if long_liq and pd.notna(long_liq) and (current_close - long_liq) / atr < 1.0:
             liq_penalty = weights.get("liq_filter", 0); driving_factors_ta.append("liq_filter(S)")
         elif short_liq and pd.notna(short_liq) and (short_liq - current_close) / atr < 1.0:
             liq_penalty = -weights.get("liq_filter", 0); driving_factors_ta.append("liq_filter(B)")
    factor_contributions["liq_filter"] = liq_penalty
    
    # ADIM 2: Tick Reactivity Score'u ekle
    factor_contributions["tick_reactivity"] = tick_reaction_signal * weights.get("tick_reactivity", 0)
    
    # Toplam Güç ve Sinyal Kararı
    signal_strength = sum(c for c in factor_contributions.values() if pd.notna(c))
    
    strong_th = 4.0; normal_th = 2.0
    if signal_strength >= strong_th: signal = "STRONG BUY"
    elif signal_strength <= -strong_th: signal = "STRONG SELL"
    elif signal_strength >= normal_th: signal = "BUY"
    elif signal_strength <= -normal_th: signal = "SELL"
    else: signal = "NEUTRAL"
    
    report_multipliers = multipliers
    
    # Tüm driving factors'ları birleştir (Tick Reaction da dahil)
    all_driving_factors = driving_factors_ta
    if tick_reaction_signal != 0: all_driving_factors.append(f"tick_reactivity({'B' if tick_reaction_signal > 0 else 'S'})")
    
    # KRİTİK DÜZELTME v68.0: driving_factors, all_driving_factors ile güncellenmeli (Scope düzeltmesi)
    driving_factors = list(set([f for f in all_driving_factors if abs(factor_contributions.get(f.split('(')[0], 0)) > 0.01]))
    
    return signal, report_multipliers, driving_factors, factor_contributions, signal_strength

# ----------------------------
# İşlem Parametre Hesaplayıcı (v65.0 - Entry'yi Canlı Fiyat Yap)
# ----------------------------
def calculate_trade_parameters(df: pd.DataFrame, signal: str, live_price: float) -> Dict[str, Any]:
    # ... (Kod v65.0 ile aynı) ...
    params = {"Entry": np.nan, "TP1": np.nan, "TP2": np.nan, "TP3": np.nan, "SL": np.nan}
    if df.empty or 'ATR' not in df.columns or df['ATR'].isnull().all() or pd.isna(live_price): return params
    window_size = 20; window_df = df.iloc[-window_size:] if len(df) >= window_size else df
    current = df.iloc[-1]; atr = current.get('ATR', 0)
    entry = live_price
    poc = current.get('vp_poc'); val = current.get('vp_val'); vah = current.get('vp_vah')
    vwap_lower1 = current.get('vwap_lower1'); vwap_upper1 = current.get('vwap_upper1')
    vwap_lower2 = current.get('vwap_lower2'); vwap_upper2 = current.get('vwap_upper2')
    pivot_s1 = current.get('pivot_s1'); pivot_r1 = current.get('pivot_r1')
    rolling_low = window_df['Low'].min(); rolling_high = window_df['High'].max()
    if pd.isna(entry) or pd.isna(atr) or atr <= 0: return params
    params["Entry"] = round(entry, 4); sl_atr_multiplier = 1.5
    base_sl = entry - (atr * sl_atr_multiplier) if "BUY" in signal else entry + (atr * sl_atr_multiplier)
    final_sl = base_sl; sl_buffer = atr * 0.2
    if "BUY" in signal:
        potential_supports = [poc, val, vwap_lower1, pivot_s1, rolling_low]
        valid_supports = [s for s in potential_supports if pd.notna(s) and s < entry - atr*0.1]
        if valid_supports: adjusted_sl = max(valid_supports) - sl_buffer; final_sl = min(base_sl, adjusted_sl)
    elif "SELL" in signal:
        potential_resistances = [poc, vah, vwap_upper1, pivot_r1, rolling_high]
        valid_resistances = [r for r in potential_resistances if pd.notna(r) and r > entry + atr*0.1]
        if valid_resistances: adjusted_sl = min(valid_resistances) + sl_buffer; final_sl = max(base_sl, adjusted_sl)
    min_sl_distance = atr * 0.7
    if "BUY" in signal and entry - final_sl < min_sl_distance: final_sl = entry - min_sl_distance
    elif "SELL" in signal and final_sl - entry < min_sl_distance: final_sl = entry + min_sl_distance
    params["SL"] = round(final_sl, 4)
    risk_r = abs(entry - params["SL"]) if pd.notna(params["SL"]) and params["SL"] != entry else atr * sl_atr_multiplier
    if risk_r <= 1e-6: risk_r = atr * sl_atr_multiplier
    tp_levels = {}
    if "BUY" in signal:
        potential_targets = [poc, vah, vwap_upper1, vwap_upper2, pivot_r1, rolling_high]
        valid_targets = sorted([t for t in potential_targets if pd.notna(t) and t > entry + risk_r * 0.3])
        r_targets = { "TP1": entry + risk_r * 1.5, "TP2": entry + risk_r * 2.5, "TP3": entry + risk_r * 4.0 }
        last_tp = entry; target_idx = 0
        for i in range(1, 4):
            tp_key = f"TP{i}"; r_target_level = r_targets[tp_key]; best_candidate = None; min_diff = float('inf')
            temp_target_idx = target_idx
            while temp_target_idx < len(valid_targets):
                 candidate = valid_targets[temp_target_idx]
                 if candidate > last_tp + risk_r * 0.5 and candidate > params["SL"] + risk_r*0.5: 
                      diff = abs(candidate - r_target_level)
                      if diff < min_diff:
                           min_diff = diff; best_candidate = candidate
                           if diff > atr * 1.5 : best_candidate = None; break
                 temp_target_idx += 1
            if best_candidate is not None:
                 tp_levels[tp_key] = best_candidate
                 try: target_idx = valid_targets.index(best_candidate) + 1
                 except ValueError: pass
            else:
                 tp_levels[tp_key] = r_target_level
                 while target_idx < len(valid_targets) and valid_targets[target_idx] <= r_target_level + atr*0.1: target_idx += 1
            last_tp = tp_levels[tp_key]
    elif "SELL" in signal:
        potential_targets = [poc, val, vwap_lower1, vwap_lower2, pivot_s1, rolling_low]
        valid_targets = sorted([t for t in potential_targets if pd.notna(t) and t < entry - risk_r * 0.3], reverse=True)
        r_targets = { "TP1": entry - risk_r * 1.5, "TP2": entry - risk_r * 2.5, "TP3": entry - risk_r * 4.0 }
        last_tp = entry; target_idx = 0
        for i in range(1, 4):
            tp_key = f"TP{i}"; r_target_level = r_targets[tp_key]; best_candidate = None; min_diff = float('inf')
            temp_target_idx = target_idx
            while temp_target_idx < len(valid_targets):
                 candidate = valid_targets[temp_target_idx]
                 if candidate < last_tp - risk_r * 0.5 and candidate < params["SL"] - risk_r*0.5:
                      diff = abs(candidate - r_target_level)
                      if diff < min_diff:
                           min_diff = diff; best_candidate = candidate
                           if diff > atr * 1.5: best_candidate = None; break
                 temp_target_idx += 1
            if best_candidate is not None:
                 tp_levels[tp_key] = best_candidate
                 try: target_idx = valid_targets.index(best_candidate) + 1
                 except ValueError: pass
            else:
                 tp_levels[tp_key] = r_target_level
                 while target_idx < len(valid_targets) and valid_targets[target_idx] >= r_target_level - atr*0.1: target_idx += 1
            last_tp = tp_levels[tp_key]
    for i in range(1, 4):
        tp_key = f"TP{i}"; level = tp_levels.get(tp_key, np.nan)
        if pd.notna(level) and pd.notna(params["SL"]):
             if ("BUY" in signal and level < params["SL"]) or ("SELL" in signal and level > params["SL"]): level = np.nan
        params[tp_key] = round(level, 4) if pd.notna(level) else np.nan
    return params

# ----------------------------
# AI Yorumlayıcı (XAI - v65.0 Metin Güncellemesi)
# ----------------------------
def generate_live_ai_commentary(
    df_analyzed: pd.DataFrame, symbol: str, signal: str,
    factor_contributions: Dict[str, float], driving_factors: List[str],
    macro_data: Dict, sentiment_data: Dict, derivatives_data: Dict, on_chain_data: Dict,
    regime: str, liq_data: Dict, prediction_probability: float, quantum_score: float,
    live_feedback: Dict, trade_params: Dict, backtest_kpis: Optional[Dict[str, Any]],
    final_strength: float 
) -> str:
    
    current_price = trade_params.get('Entry', df_analyzed['Close'].iloc[-1] if not df_analyzed.empty else np.nan)
    poc = df_analyzed['vp_poc'].iloc[-1] if 'vp_poc' in df_analyzed.columns and not df_analyzed.empty else np.nan
    vah = df_analyzed['vp_vah'].iloc[-1] if 'vp_vah' in df_analyzed.columns and not df_analyzed.empty else np.nan
    val = df_analyzed['vp_val'].iloc[-1] if 'vp_val' in df_analyzed.columns and not df_analyzed.empty else np.nan
    vwap = df_analyzed['vwap'].iloc[-1] if 'vwap' in df_analyzed.columns and not df_analyzed.empty else np.nan
    
    risk_mode = "⚪ Bilgi Yok"; ror_comment = "N/A"
    if backtest_kpis and backtest_kpis.get('total_trades', 0) > 5:
        win_rate = backtest_kpis.get('win_rate_pct', 50.0) / 100.0; r_multiple = backtest_kpis.get('avg_r_multiple', 1.0)
        ror = calculate_risk_of_ruin(win_rate, r_multiple, RISK_PER_TRADE_PERCENT)
        kelly = calculate_kelly_criterion(win_rate, r_multiple)
        risk_mode = determine_risk_mode(ror, kelly); ror_comment = f"{ror*100:.1f}%"
    
    tsl_status = f"Takip Eden SL Aktif ({TRAILING_SL_ATR_MULTIPLIER}x ATR, {TRAILING_SL_ACTIVATION_R}R Kârda)" if TRAILING_SL_ENABLED else "Takip Eden SL Kapalı"
    risk_comment = f"Strateji Risk: **{risk_mode}** (RoR: {ror_comment}) / **{tsl_status}**"

    xai_parts = []
    factor_groups = { "Trend": ["ta_trend", "ichimoku", "vwap", "cvd", "oi_delta"], "Momentum/MR": ["ta_momentum", "fibonacci", "squeeze", "volume_profile"],
                      "Quant": ["quantum", "tick_reactivity"], "Dış Etkenler": ["macro", "sentiment", "on_chain_l2"], "Tahmin": ["ml_predict"], "Filtreler": ["liq_filter"] }
    group_contributions = {group: 0.0 for group in factor_groups}
    valid_contributions = {f:c for f, c in factor_contributions.items() if pd.notna(c)}
    for factor, contribution in valid_contributions.items():
        for group, members in factor_groups.items():
            if factor in members: group_contributions[group] += contribution; break
            
    positive_groups = {g: f"{c:+.1f}" for g, c in group_contributions.items() if c > 0.01} # Düşük katkıları filtrele
    negative_groups = {g: f"{c:+.1f}" for g, c in group_contributions.items() if c < -0.01} # Düşük katkıları filtrele
    
    if positive_groups: xai_parts.append(f"🟢 Destekleyenler (AL): `{positive_groups}`")
    if negative_groups: xai_parts.append(f"🔴 Karşı Çıkanlar (SAT): `{negative_groups}`")
    if not positive_groups and not negative_groups: xai_parts.append("⚪ Belirgin bir grup etkisi yok.")
    
    sorted_contributions = sorted(valid_contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    top_factors_str = ", ".join([f"{f.split('(')[0]}{'(B)' if c > 0 else '(S)' if c < 0 else ''} ({c:+.1f})" for f, c in sorted_contributions[:3] if abs(c) > 0.01]) 
    if top_factors_str: xai_parts.append(f"✨ Öne Çıkanlar: {top_factors_str}")
    
    xai_comment = "\n".join(xai_parts)
    
    verdict_map = {"STRONG BUY": "🔥 GÜÇLÜ AL", "BUY": "🟢 AL", "STRONG SELL": "🚨 GÜÇLÜ SAT", "SELL": "🔴 SAT", "NEUTRAL": "⚪ NÖTR"}
    verdict_text = verdict_map.get(signal, "⚪ NÖTR")
    
    pos_total = sum(c for c in valid_contributions.values() if c > 0); neg_total = sum(c for c in valid_contributions.values() if c < 0)

    summary = f"**NİHAİ KARAR: {verdict_text} (Net Sinyal Gücü: {final_strength:+.2f})**"
    if signal == "NEUTRAL":
        summary += f"\n*Sebep: Pozitif faktörler (Toplam: {pos_total:+.1f}) ve Negatif faktörler (Toplam: {neg_total:+.1f}) birbirini dengelemiştir.*"
    else:
         verdict = "Pozitif faktörler baskın geldi." if "BUY" in signal else "Negatif faktörler baskın geldi."
         summary += f"\n*Sebep: {verdict} (Poz: {pos_total:+.1f}, Neg: {neg_total:+.1f})*"

    regime_note = ""
    if "KARARSIZ" in regime and abs(final_strength) > 4.0:
         regime_note = " (Ancak Quant/Makro faktörleri bu rejime rağmen yüksek sinyal üretti.)"
    
    predictive_comment = f"Tahminler: Nöral Net (RF) **{prediction_probability * 100:.0f}% Yükseliş**, Kuantum Skor **{quantum_score:.1f}** ({'Pozitif' if quantum_score > 30 else 'Negatif' if quantum_score < -30 else 'Nötr'})."
    
    vix = macro_data.get("VIX", np.nan); dxy = macro_data.get("DXY", np.nan); risk_appetite = "Nötr"
    if not pd.isna(vix) and not pd.isna(dxy):
        if vix < 15 and dxy < 103: risk_appetite = "Yüksek (Risk-On)"
        elif vix > 28 or dxy > 106: risk_appetite = "Düşük (Risk-Off)"
        
    sentiment_label = sentiment_data.get('label', 'Nötr')
    conditions_comment = f"Piyasa: Risk İştahı **{risk_appetite}**, Duygu **{sentiment_label}**, Rejim **{regime}**."
    
    funding_rate = derivatives_data.get('funding_rate', np.nan)
    fr_display = f"{funding_rate:.4f}%" if pd.notna(funding_rate) else "N/A"
    
    oir = on_chain_data.get('OIR', 0.0); oir_label = "Alış Baskısı" if oir > 0.15 else "Satış Baskısı" if oir < -0.15 else "Dengeli"
    liq_comment = liq_data.get('liq_comment', 'Yok')
    
    vwap_status = "Bilinmiyor"; vwap_display = "N/A"
    if pd.notna(vwap) and pd.notna(current_price):
        vwap_status = "VWAP Üstü" if current_price > vwap else "VWAP Altı"
        vwap_display = f"${vwap:.2f}"
        
    oi_delta_usd = derivatives.get("oi_delta_usd", 0); oi_value = derivatives.get("oi_value_usd", 0)
    oi_comment = ""
    if oi_value and pd.notna(oi_value) and oi_value != 0:
        oi_delta_pct = (oi_delta_usd / oi_value) * 100
        if oi_delta_pct > 1.0: oi_comment = f"📈 OI Artıyor ({oi_delta_pct:.1f}%)"
        elif oi_delta_pct < -1.0: oi_comment = f"📉 OI Azalıyor ({oi_delta_pct:.1f}%)"
        else: oi_comment = "➖ OI Stabil"
    else: oi_comment = "➖ OI Verisi Yok"
    
    local_flow_comment = f"Akış: Funding {fr_display}, **{oi_comment}**, **{vwap_status}** ({vwap_display}), Emir Dft. **{oir_label}** ({oir:.2f}), Likidasyon **{liq_comment}**."
    
    poc_status = "Bilinmiyor"; vp_comment = ""
    if not pd.isna(poc):
        poc_status = "PoC Üstü" if current_price > poc else "PoC Altı"
        vp_comment = f"Hacim: **{poc_status}** (PoC ${poc:.2f})"
        if pd.notna(vah) and pd.notna(val):
             vp_comment += f", VA [${val:.2f} - ${vah:.2f}]"
             if current_price > vah: vp_comment += " (Üstü)"
             elif current_price < val: vp_comment += " (Altı)"
             else: vp_comment += " (İçinde)"
    else: vp_comment = "Hacim: Profili Hesaplanamadı."
    
    live_perf_comment = f"Performans (24s): {live_feedback.get('wins_24h', 0)}K / {live_feedback.get('losses_24h', 0)}Z ({live_feedback.get('active_count',0)} Aktif)."
    
    final_commentary = ( f"**🤖 DemirAI Analizi (v68.0 - {symbol} | {verdict_text})**\n\n"
                         f"**1. Gerekçe (XAI):**\n{summary}\n"
                         f"--- (Detaylar) ---\n"
                         f"{xai_comment}\n\n"
                         f"**2. Risk:** {risk_comment}\n"
                         f"**3. Tahmin:** {predictive_comment}\n"
                         f"**4. Piyasa:** {conditions_comment}\n"
                         f"**5. Akış:** {local_flow_comment}\n"
                         f"**6. Hacim:** {vp_comment}\n"
                         f"**7. Performans:** {live_perf_comment}" )
    return final_commentary

# ----------------------------
# Backtest Motorları ve KPI
# ----------------------------
# ... (Kod v65.0 ile aynı) ...
def calculate_backtest_kpis(equity_curve: List[float], trade_log: List[Dict[str, Any]], initial_capital: float, timeframe: str) -> Dict[str, Any]:
    # ... (Kod v65.0 ile aynı) ...
    kpis = { "total_return_pct": 0.0, "max_drawdown_pct": 0.0, "win_rate_pct": 0.0, "total_trades": 0,
             "sharpe_ratio": 0.0, "cagr": 0.0, "expected_value": 0.0, "avg_r_multiple": 0.0,
             "risk_of_ruin": 100.0, "symbol_tested": "" }
    if not trade_log or len(equity_curve) < 2: return kpis
    df_log = pd.DataFrame(trade_log); total_trades = len(df_log)
    kpis["total_trades"] = total_trades; kpis["symbol_tested"] = df_log['symbol'].iloc[0] if not df_log.empty else ""
    winning_trades_df = df_log[df_log['pnl_usd'] > 0]; losing_trades_df = df_log[df_log['pnl_usd'] <= 0]
    wins = len(winning_trades_df); losses = total_trades - wins
    win_rate = wins / total_trades if total_trades > 0 else 0.0
    kpis["win_rate_pct"] = win_rate * 100
    avg_win_usd = winning_trades_df['pnl_usd'].mean() if wins > 0 else 0.0
    avg_loss_usd = abs(losing_trades_df['pnl_usd'].mean()) if losses > 0 else 0.0
    kpis["expected_value"] = (win_rate * avg_win_usd) - ((1.0 - win_rate) * avg_loss_usd)
    kpis["avg_r_multiple"] = avg_win_usd / avg_loss_usd if avg_loss_usd > 0 else 0.0
    kpis["risk_of_ruin"] = calculate_risk_of_ruin(win_rate, kpis["avg_r_multiple"], RISK_PER_TRADE_PERCENT) * 100
    equity_series = pd.Series(equity_curve)
    kpis["total_return_pct"] = (equity_series.iloc[-1] / initial_capital - 1) * 100 if initial_capital > 0 else 0
    peak = equity_series.expanding(min_periods=1).max(); drawdown = (equity_series - peak) / peak.replace(0, np.nan)
    kpis["max_drawdown_pct"] = abs(drawdown.min()) * 100 if not drawdown.empty and pd.notna(drawdown.min()) else 0.0
    if 'entry_time' in df_log.columns and 'exit_time' in df_log.columns:
         try:
             start_time = pd.to_datetime(df_log['entry_time'].min()); end_time = pd.to_datetime(df_log['exit_time'].max())
             years = max((end_time - start_time).days / 365.25, 1.0/365.25)
             final_equity = equity_series.iloc[-1]
             if final_equity > 0 and initial_capital > 0:
                 kpis["cagr"] = ((final_equity / initial_capital) ** (1 / years) - 1) * 100
             returns = equity_series.pct_change().dropna()
             if len(returns) > 1 and returns.std() > 0:
                 tf_minutes = 15
                 try:
                     if 'm' in timeframe: tf_minutes = int(timeframe.replace('m', ''))
                     elif 'h' in timeframe: tf_minutes = int(timeframe.replace('h', '')) * 60
                     elif 'd' in timeframe: tf_minutes = int(timeframe.replace('d', '')) * 1440
                 except: pass
                 bars_per_year = (365 * 24 * 60) / tf_minutes if tf_minutes > 0 else 0
                 if bars_per_year > 0:
                     sharpe = (returns.mean() / returns.std()) * sqrt(bars_per_year)
                     kpis["sharpe_ratio"] = round(sharpe, 2)
         except Exception as e: print(f"Uyarı: Yıllık metrik hesaplama hatası: {e}")
    for key in kpis:
        if isinstance(kpis[key], (float, np.float64)) and key != "symbol_tested": kpis[key] = round(kpis[key], 2)
    return kpis

def run_hypothetical_backtest(
    df: pd.DataFrame, symbol: str, initial_capital: float, risk_per_trade: float, factor_name: str
) -> Tuple[List[Dict[str, Any]], List[float]]:
    # ... (Kod v65.0 ile aynı, trade_log.append düzeltmesi uygulandı) ...
    trade_log = []; equity_curve = [initial_capital]; current_capital = initial_capital
    open_trade: Optional[Dict[str, Any]] = None
    start_index = max(200, df.index.get_loc(df.first_valid_index()) if df.first_valid_index() is not None else 0)
    FEE = BINANCE_FEE_RATE; mock_oi_delta_usd = 0
    trailing_sl_active = TRAILING_SL_ENABLED
    tsl_multiplier = TRAILING_SL_ATR_MULTIPLIER
    tsl_activation_r = TRAILING_SL_ACTIVATION_R
    for i in range(start_index, len(df) - 1):
        current_bar = df.iloc[i]; next_bar = df.iloc[i+1]; signal = "NEUTRAL"
        current_price = current_bar['Close']; atr = current_bar.get('ATR', 0.01)
        price_change = current_price - df.iloc[i-1]['Close'] if i > 0 else 0
        try:
            if factor_name == "ta_trend":
                if current_price > current_bar.get('KAMA', current_price + 1): signal = "BUY"
                elif current_price < current_bar.get('KAMA', current_price - 1): signal = "SELL"
            elif factor_name == "ta_momentum":
                rsi = current_bar.get('RSI', 50)
                if rsi < 30: signal = "BUY"
                elif rsi > 70: signal = "SELL"
            elif factor_name == "quantum":
                 q_score = current_bar.get('quantum_score', 0)
                 if q_score > 30: signal = "BUY"
                 elif q_score < -30: signal = "SELL"
            elif factor_name == "ichimoku":
                 is_above = current_price > current_bar.get('ichimoku_a', -1) and current_price > current_bar.get('ichimoku_b', -1)
                 is_below = current_price < current_bar.get('ichimoku_a', 9e9) and current_price < current_bar.get('ichimoku_b', 9e9)
                 if is_above: signal = "BUY"
                 elif is_below: signal = "SELL"
            elif factor_name == "cvd":
                 if current_bar.get('cvd', 0) > df.iloc[i-1].get('cvd', 0): signal = "BUY"
                 else: signal = "SELL"
            elif factor_name == "volume_profile":
                 poc = current_bar.get('vp_poc')
                 if pd.notna(poc):
                      if current_price > poc: signal = "BUY"
                      elif current_price < poc: signal = "SELL"
            elif factor_name == "vwap":
                 vwap = current_bar.get('vwap')
                 if pd.notna(vwap):
                      if current_price > vwap: signal = "BUY"
                      elif current_price < vwap: signal = "SELL"
            elif factor_name == "oi_delta":
                 if price_change > atr * 0.1 and mock_oi_delta_usd > 0: signal = "BUY"
                 elif price_change < -atr * 0.1 and mock_oi_delta_usd > 0: signal = "SELL"
            elif factor_name == "ml_predict": pass
        except Exception: signal = "NEUTRAL"
        if open_trade:
            entry_price = open_trade['entry_price']; is_long = open_trade['direction'] == 'LONG'
            risk_amount = RISK_PER_TRADE_PERCENT * current_capital 
            sl_price_static = entry_price * (1 - RISK_PER_TRADE_PERCENT if is_long else 1 + RISK_PER_TRADE_PERCENT)
            tp_price = entry_price * (1 + (RISK_PER_TRADE_PERCENT * 2) if is_long else 1 - (RISK_PER_TRADE_PERCENT * 2))
            if trailing_sl_active and open_trade['initial_sl'] is None:
                 risk_r_dist = abs(entry_price - sl_price_static)
                 open_trade['initial_sl'] = sl_price_static
                 open_trade['risk_r_dist'] = risk_r_dist
                 open_trade['trailing_sl'] = sl_price_static
            exit_reason = None; exit_price = entry_price
            if trailing_sl_active and open_trade.get('initial_sl') is not None and open_trade.get('risk_r_dist', 0) > 0:
                 current_price = current_bar['Close']
                 risk_r_dist = open_trade['risk_r_dist']
                 unrealized_pnl_r = ((current_price - entry_price) / risk_r_dist) * (1 if is_long else -1)
                 if unrealized_pnl_r >= tsl_activation_r:
                      if is_long:
                          new_tsl = current_price - (atr * tsl_multiplier)
                          open_trade['trailing_sl'] = max(open_trade['trailing_sl'], new_tsl)
                      else:
                          new_tsl = current_price + (atr * tsl_multiplier)
                          open_trade['trailing_sl'] = min(open_trade['trailing_sl'], new_tsl)
                 sl_price_current = open_trade['trailing_sl']
            else: sl_price_current = sl_price_static
            if is_long:
                if next_bar['Low'] <= sl_price_current: exit_reason = "SL Hit"; exit_price = sl_price_current
                elif next_bar['High'] >= tp_price: exit_reason = "TP Hit"; exit_price = tp_price
            else:
                if next_bar['High'] >= sl_price_current: exit_reason = "SL Hit"; exit_price = sl_price_current
                elif next_bar['Low'] <= tp_price: exit_reason = "TP Hit"; exit_price = tp_price
            if not exit_reason and ((is_long and signal == 'SELL') or (not is_long and signal == 'BUY')):
                exit_reason = "Reverse Signal"; exit_price = next_bar['Open']
            open_trade['hold_bars'] += 1
            if not exit_reason and open_trade['hold_bars'] >= MAX_HOLD_BARS:
                exit_reason = "Max Hold Time"; exit_price = next_bar['Open']
            if exit_reason:
                pnl_percent = (exit_price / entry_price - 1) * (1 if is_long else -1) if entry_price != 0 else 0
                pos_size = open_trade['pos_size']; opening_cost = open_trade['opening_cost']
                closing_cost = pos_size * exit_price * FEE; total_fees = opening_cost + closing_cost
                pnl_usd_gross = (exit_price - entry_price) * pos_size * (1 if is_long else -1)
                pnl_usd_net = pnl_usd_gross - total_fees
                current_capital += pnl_usd_net; equity_curve.append(current_capital)
                
                trade_log.append({ "symbol": symbol, "entry_time": open_trade['entry_time'], "exit_time": next_bar.name,
                                   "direction": open_trade['direction'], "entry_price": round(entry_price, 4),
                                   "exit_price": round(exit_price, 4), "exit_reason": exit_reason,
                                   "pnl_usd": round(pnl_usd_net, 2), "pnl_percent": round(pnl_percent * 100, 2),
                                   "fees_usd": round(total_fees, 2), "current_capital": round(current_capital, 2),
                                   "tsl_hit": trailing_sl_active and exit_reason == "SL Hit" and abs(exit_price - open_trade.get('initial_sl', 0)) > 1e-5 })
                
                open_trade = None
        if not open_trade and ("BUY" in signal or "SELL" in signal):
             entry_price = current_bar['Close']
             risk_amount_per_coin = entry_price * RISK_PER_TRADE_PERCENT
             pos_size = 0; opening_cost = 0
             if risk_amount_per_coin > 0:
                 pos_size = (current_capital * risk_per_trade) / risk_amount_per_coin
                 opening_cost = pos_size * entry_price * FEE
                 if current_capital > opening_cost: current_capital -= opening_cost
                 else: continue
             open_trade = { "entry_time": current_bar.name, "direction": "LONG" if "BUY" in signal else "SHORT",
                            "entry_price": entry_price, "hold_bars": 0, "pos_size": pos_size, 
                            "opening_cost": opening_cost, 'initial_sl': None, 'trailing_sl': None, 'risk_r_dist': 0 }
    if open_trade:
        exit_price = df.iloc[-1]['Close']; is_long = open_trade['direction'] == 'LONG'
        pnl_percent = (exit_price / open_trade['entry_price'] - 1) * (1 if is_long else -1) if open_trade['entry_price'] != 0 else 0
        pos_size = open_trade['pos_size']; opening_cost = open_trade['opening_cost']
        closing_cost = pos_size * exit_price * FEE; total_fees = opening_cost + closing_cost
        pnl_usd_gross = (exit_price - open_trade['entry_price']) * pos_size * (1 if is_long else -1)
        pnl_usd_net = pnl_usd_gross - total_fees
        current_capital += pnl_usd_net; equity_curve.append(current_capital)
        
        trade_log.append({ "symbol": symbol, "entry_time": open_trade['entry_time'], "exit_time": df.iloc[-1].name,
                           "direction": open_trade['direction'], "entry_price": round(open_trade['entry_price'], 4),
                           "exit_price": round(exit_price, 4), "exit_reason": "Close End",
                           "pnl_usd": round(pnl_usd_net, 2), "pnl_percent": round(pnl_percent * 100, 2),
                           "fees_usd": round(total_fees, 2), "current_capital": round(current_capital, 2),
                           "tsl_hit": False })
                           
    return trade_log, equity_curve

def run_main_backtest(
    df: pd.DataFrame, symbol: str, initial_capital: float, risk_per_trade: float
) -> Tuple[List[Dict[str, Any]], List[float]]:
    # ... (Kod v65.0 ile aynı, trade_log.append düzeltmesi uygulandı) ...
    trade_log = []; equity_curve = [initial_capital]; current_capital = initial_capital
    open_trade: Optional[Dict[str, Any]] = None
    start_index = max(200, df.index.get_loc(df.first_valid_index()) if df.first_valid_index() is not None else 0)
    FEE = BINANCE_FEE_RATE
    mock_macro = {"VIX": 20, "DXY": 104};
    mock_derivatives = {"funding_rate": 0.01, "oi_value_usd": np.nan, "oi_delta_usd": 0}
    mock_on_chain = {"OIR": 0.0}; mock_sentiment = {"score": 0.0, "label": "Nötr"}
    mock_liq_data = {"long_liq_price": np.nan, "short_liq_price": np.nan, "liq_comment": "Backtest Mock"}
    factor_weights_data = load_factor_performance_from_db() if load_factor_performance_from_db else {}
    mock_prediction_prob = 0.5
    trailing_sl_active = TRAILING_SL_ENABLED
    tsl_multiplier = TRAILING_SL_ATR_MULTIPLIER
    tsl_activation_r = TRAILING_SL_ACTIVATION_R
    for i in range(start_index, len(df) - 1):
        current_bar = df.iloc[i]; next_bar = df.iloc[i+1]; atr = current_bar.get('ATR', 0.01)
        mock_live_price = current_bar['Close']
        mock_prev_close = df.iloc[i-1]['Close']
        
        signal, _, _, _, _ = generate_signal( 
            df, i, mock_macro, mock_derivatives, mock_on_chain, mock_sentiment,
            mock_liq_data, mock_prediction_prob, factor_weights_data, 
            live_price=mock_live_price, prev_close=mock_prev_close
        )
        if open_trade:
            entry_price = open_trade['entry_price']; is_long = open_trade['direction'] == 'LONG'
            risk_r_dist = open_trade.get('risk_r_dist', atr * 1.5)
            sl_price_static = entry_price * (1 - RISK_PER_TRADE_PERCENT if is_long else 1 + RISK_PER_TRADE_PERCENT)
            tp_price = entry_price * (1 + (RISK_PER_TRADE_PERCENT * 2) if is_long else 1 - (RISK_PER_TRADE_PERCENT * 2))
            if trailing_sl_active and open_trade['initial_sl'] is None:
                 risk_r_dist = abs(entry_price - sl_price_static)
                 open_trade['initial_sl'] = sl_price_static
                 open_trade['risk_r_dist'] = risk_r_dist
                 open_trade['trailing_sl'] = sl_price_static
            exit_reason = None; exit_price = entry_price
            if trailing_sl_active and open_trade.get('initial_sl') is not None and open_trade.get('risk_r_dist', 0) > 0:
                 current_price = current_bar['Close']
                 risk_r_dist = open_trade['risk_r_dist']
                 unrealized_pnl_r = ((current_price - entry_price) / risk_r_dist) * (1 if is_long else -1)
                 if unrealized_pnl_r >= tsl_activation_r:
                      if is_long:
                          new_tsl = current_price - (atr * tsl_multiplier)
                          open_trade['trailing_sl'] = max(open_trade['trailing_sl'], new_tsl)
                      else:
                          new_tsl = current_price + (atr * tsl_multiplier)
                          open_trade['trailing_sl'] = min(open_trade['trailing_sl'], new_tsl)
                 sl_price_current = open_trade['trailing_sl']
            else: sl_price_current = sl_price_static
            if is_long:
                if next_bar['Low'] <= sl_price_current: exit_reason = "SL Hit"; exit_price = sl_price_current
                elif next_bar['High'] >= tp_price: exit_reason = "TP Hit"; exit_price = tp_price
            else:
                if next_bar['High'] >= sl_price_current: exit_reason = "SL Hit"; exit_price = sl_price_current
                elif next_bar['Low'] <= tp_price: exit_reason = "TP Hit"; exit_price = tp_price
            if not exit_reason and ( (is_long and ("SELL" in signal)) or (not is_long and ("BUY" in signal)) ):
                 exit_reason = "Reverse Signal"; exit_price = next_bar['Open']
            open_trade['hold_bars'] += 1
            if not exit_reason and open_trade['hold_bars'] >= MAX_HOLD_BARS:
                exit_reason = "Max Hold Time"; exit_price = next_bar['Open']
            if exit_reason:
                pnl_percent = (exit_price / entry_price - 1) * (1 if is_long else -1) if entry_price != 0 else 0
                pos_size = open_trade['pos_size']; opening_cost = open_trade['opening_cost']
                closing_cost = pos_size * exit_price * FEE; total_fees = opening_cost + closing_cost
                pnl_usd_gross = (exit_price - entry_price) * pos_size * (1 if is_long else -1)
                pnl_usd_net = pnl_usd_gross - total_fees
                current_capital += pnl_usd_net; equity_curve.append(current_capital)
                
                trade_log.append({ "symbol": symbol, "entry_time": open_trade['entry_time'], "exit_time": next_bar.name,
                                   "direction": open_trade['direction'], "entry_price": round(entry_price, 4),
                                   "exit_price": round(exit_price, 4), "exit_reason": exit_reason,
                                   "pnl_usd": round(pnl_usd_net, 2), "pnl_percent": round(pnl_percent * 100, 2),
                                   "fees_usd": round(total_fees, 2), "current_capital": round(current_capital, 2),
                                   "tsl_hit": trailing_sl_active and exit_reason == "SL Hit" and abs(exit_price - open_trade.get('initial_sl', 0)) > 1e-5 })
                
                open_trade = None
        if not open_trade and ("BUY" in signal or "SELL" in signal):
             entry_price = current_bar['Close']; risk_amount_per_coin = entry_price * RISK_PER_TRADE_PERCENT
             pos_size = 0; opening_cost = 0
             if risk_amount_per_coin > 0:
                 pos_size = (current_capital * risk_per_trade) / risk_amount_per_coin
                 opening_cost = pos_size * entry_price * FEE
                 if current_capital > opening_cost: current_capital -= opening_cost
                 else: continue
             open_trade = { "entry_time": current_bar.name, "direction": "LONG" if "BUY" in signal else "SHORT",
                            "entry_price": entry_price, "hold_bars": 0, "pos_size": pos_size, 
                            "opening_cost": opening_cost, 'initial_sl': None, 'trailing_sl': None, 'risk_r_dist': 0 }
    if open_trade:
        exit_price = df.iloc[-1]['Close']; is_long = open_trade['direction'] == 'LONG'
        pnl_percent = (exit_price / open_trade['entry_price'] - 1) * (1 if is_long else -1) if open_trade['entry_price'] != 0 else 0
        pos_size = open_trade['pos_size']; opening_cost = open_trade['opening_cost']
        closing_cost = pos_size * exit_price * FEE; total_fees = opening_cost + closing_cost
        pnl_usd_gross = (exit_price - open_trade['entry_price']) * pos_size * (1 if is_long else -1)
        pnl_usd_net = pnl_usd_gross - total_fees
        current_capital += pnl_usd_net; equity_curve.append(current_capital)
        
        trade_log.append({ "symbol": symbol, "entry_time": open_trade['entry_time'], "exit_time": df.iloc[-1].name,
                           "direction": open_trade['direction'], "entry_price": round(open_trade['entry_price'], 4),
                           "exit_price": round(exit_price, 4), "exit_reason": "Close End",
                           "pnl_usd": round(pnl_usd_net, 2), "pnl_percent": round(pnl_percent * 100, 2),
                           "fees_usd": round(total_fees, 2), "current_capital": round(current_capital, 2),
                           "tsl_hit": False })
                           
    return trade_log, equity_curve

def run_backtest_and_learn(
    df: pd.DataFrame, symbol: str, initial_capital: float, risk_per_trade: float, timeframe: str
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[float], List[Dict[str, Any]]]:
    # ... (Kod v65.0 ile aynı) ...
    if save_kpis_to_db is None or save_factor_performance_to_db is None:
        print("Hata: DB katmanı yüklenemediği için öğrenme işlemi yapılamıyor."); return {}, [], [], []
    st.info(f"[{symbol}] Ana Strateji backtest ediliyor...")
    trade_log_main, equity_curve_main = run_main_backtest(df, symbol, initial_capital, risk_per_trade)
    kpis_main = calculate_backtest_kpis(equity_curve_main, trade_log_main, initial_capital, timeframe)
    if kpis_main.get('total_trades', 0) > 0: save_kpis_to_db(kpis_main, symbol, timeframe)
    else: st.warning(f"[{symbol}] Ana strateji için hiç işlem bulunamadı.")
    st.info(f"[{symbol}] Hipotetik Faktör backtestleri başlıyor...")
    factor_kpis_list = []
    factors_to_test = ["ta_trend", "ta_momentum", "quantum", "ichimoku", "squeeze",
                       "cvd", "fibonacci", "volume_profile", "vwap", "oi_delta", "ml_predict"]
    for factor in factors_to_test:
        trade_log_factor, equity_curve_factor = run_hypothetical_backtest(df, symbol, initial_capital, risk_per_trade, factor)
        kpis_factor = calculate_backtest_kpis(equity_curve_factor, trade_log_factor, initial_capital, timeframe)
        kpis_factor['factor_name'] = factor
        factor_kpis_list.append(kpis_factor)
    if factor_kpis_list: save_factor_performance_to_db(factor_kpis_list)
    st.success(f"[{symbol}] Backtest ve Öğrenme tamamlandı. Ana: {kpis_main.get('total_trades', 0)} işl. Faktörler: {len(factor_kpis_list)} adet.")
    return kpis_main, factor_kpis_list, equity_curve_main, trade_log_main

print("✅ strategy_layer.py v68.0 (Sözdizimi Düzeltmesi) yüklendi.")
