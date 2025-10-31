"""
DEMIR - Strategy Layer FIXED
Multi-Factor Signal Generation
"""

from typing import Dict, Any
import numpy as np

# ============================================
# FAKTÖR AĞIRLIKLARI
# ============================================

FACTOR_WEIGHTS = {
    # Teknik göstergeler
    'rsi': 1.0,
    'macd': 1.0,
    'bollinger': 0.8,
    'ema_trend': 1.2,
    'volume_profile': 1.0,
    'rsi_divergence': 1.5,
    'fibonacci': 0.8,
    # Dış faktörler
    'fear_greed': 0.7,
    'funding_rate': 0.6,
    'traditional_markets': 0.5,
    'news_sentiment': 0.4
}


# ============================================
# FAKTÖR HESAPLAYICILAR
# ============================================

def calculate_rsi_score(rsi_value: float) -> float:
    """RSI skoru: 0-30 oversold (pozitif), 70-100 overbought (negatif)"""
    if rsi_value < 30:
        return (30 - rsi_value) / 30 * 100  # 0-100 arası pozitif
    elif rsi_value > 70:
        return -(rsi_value - 70) / 30 * 100  # 0-100 arası negatif
    else:
        return 0


def calculate_macd_score(macd: float, signal: float, histogram: float) -> float:
    """MACD skoru: Histogram momentum"""
    if histogram > 0:
        return min(100, abs(histogram) * 50)
    else:
        return max(-100, -abs(histogram) * 50)


def calculate_bollinger_score(price: float, upper: float, lower: float, middle: float) -> float:
    """Bollinger Bands skoru"""
    band_width = upper - lower
    
    if price < lower:
        # Alt bandın altında - oversold
        distance = (lower - price) / band_width
        return min(100, distance * 100)
    elif price > upper:
        # Üst bandın üstünde - overbought
        distance = (price - upper) / band_width
        return max(-100, -distance * 100)
    else:
        return 0


def calculate_ema_trend_score(price: float, ema_9: float, ema_21: float, ema_50: float) -> float:
    """EMA trend skoru: Fiyat EMAlerin üstünde mi?"""
    score = 0
    
    if price > ema_9:
        score += 30
    if price > ema_21:
        score += 30
    if price > ema_50:
        score += 40
    
    # EMA alignment (golden cross benzeri)
    if ema_9 > ema_21 > ema_50:
        score += 20  # Bullish alignment
    elif ema_9 < ema_21 < ema_50:
        score -= 20  # Bearish alignment
    
    return score - 50  # -50 ile +50 arası normalize


def calculate_volume_profile_score(price: float, vp_data: Dict) -> float:
    """Volume Profile skoru: Fiyat POC'a yakın mı?"""
    if not vp_data or 'poc' not in vp_data:
        return 0
    
    poc = vp_data['poc']
    vah = vp_data.get('vah', poc)
    val = vp_data.get('val', poc)
    
    # POC çevresinde güçlü destek/direnç
    if val <= price <= vah:
        return 20  # Value area içinde (güvenli)
    elif price < val:
        return -30  # Value area altında (zayıf)
    else:
        return 30  # Value area üstünde (güçlü)


def calculate_divergence_score(div_data: Dict) -> float:
    """RSI Divergence skoru"""
    if not div_data:
        return 0
    
    if div_data.get('bullish_divergence'):
        return div_data.get('strength', 50)
    elif div_data.get('bearish_divergence'):
        return -div_data.get('strength', 50)
    else:
        return 0


def calculate_fibonacci_score(fib_data: Dict, price: float) -> float:
    """Fibonacci skoru: Hangi seviyede?"""
    if not fib_data:
        return 0
    
    level = fib_data.get('current_level', '')
    
    if 'below' in level or '23.6' in level:
        return 40  # Oversold bölge
    elif '38.2' in level or '50' in level:
        return 20  # Potansiyel destek
    elif '61.8' in level or '78.6' in level:
        return -20  # Potansiyel direnç
    elif 'above 100%' in level:
        return -40  # Overbought
    else:
        return 0


def calculate_fear_greed_score(fg_value: int) -> float:
    """Fear & Greed skoru (Contrarian yaklaşım)"""
    if fg_value < 25:
        return 50  # Extreme fear = alış fırsatı
    elif fg_value < 45:
        return 20  # Fear = olumlu
    elif fg_value > 75:
        return -50  # Extreme greed = satış sinyali
    elif fg_value > 55:
        return -20  # Greed = olumsuz
    else:
        return 0


def calculate_funding_rate_score(funding_rate: float) -> float:
    """Funding rate skoru"""
    # Pozitif funding = long ağırlıklı (overbought)
    # Negatif funding = short ağırlıklı (oversold)
    
    if funding_rate > 0.05:
        return -40  # Çok yüksek long pozisyonu
    elif funding_rate > 0.01:
        return -20
    elif funding_rate < -0.05:
        return 40  # Çok yüksek short pozisyonu
    elif funding_rate < -0.01:
        return 20
    else:
        return 0


# ============================================
# ANA SİNYAL ÜRETME FONKSİYONU
# ============================================

def generate_signal(symbol: str, tech_data: Dict, external_data: Dict) -> Dict[str, Any]:
    """
    Multi-factor scoring ile sinyal üret
    
    Returns:
    {
        'signal': 'BUY' | 'SELL' | 'HOLD',
        'confidence': float (0-100),
        'factors': {faktör: skor}
    }
    """
    factors = {}
    
    # Teknik faktörler
    if 'rsi' in tech_data:
        factors['rsi'] = calculate_rsi_score(tech_data['rsi'])
    
    if 'macd' in tech_data:
        factors['macd'] = calculate_macd_score(
            tech_data.get('macd', 0),
            tech_data.get('macd_signal', 0),
            tech_data.get('macd_histogram', 0)
        )
    
    # FIXED: Bollinger Bands key names
    if all(k in tech_data for k in ['price', 'BB_High', 'BB_Low', 'BB_Mid']):
        factors['bollinger'] = calculate_bollinger_score(
            tech_data['price'],
            tech_data['BB_High'],
            tech_data['BB_Low'],
            tech_data['BB_Mid']
        )
    
    if all(k in tech_data for k in ['price', 'ema_9', 'ema_21', 'ema_50']):
        factors['ema_trend'] = calculate_ema_trend_score(
            tech_data['price'],
            tech_data['ema_9'],
            tech_data['ema_21'],
            tech_data['ema_50']
        )
    
    if 'volume_profile' in tech_data and tech_data['volume_profile']:
        factors['volume_profile'] = calculate_volume_profile_score(
            tech_data.get('price', 0),
            tech_data['volume_profile']
        )
    
    if 'rsi_divergence' in tech_data:
        factors['rsi_divergence'] = calculate_divergence_score(tech_data['rsi_divergence'])
    
    if 'fibonacci' in tech_data and tech_data['fibonacci']:
        factors['fibonacci'] = calculate_fibonacci_score(
            tech_data['fibonacci'],
            tech_data.get('price', 0)
        )
    
    # Dış faktörler
    if 'fear_greed' in external_data:
        fg_value = external_data['fear_greed'].get('value', 50)
        factors['fear_greed'] = calculate_fear_greed_score(fg_value)
    
    if 'funding_rate' in external_data:
        factors['funding_rate'] = calculate_funding_rate_score(external_data['funding_rate'])
    
    # Ağırlıklı toplam skor
    weighted_score = 0
    total_weight = 0
    
    for factor, score in factors.items():
        weight = FACTOR_WEIGHTS.get(factor, 1.0)
        weighted_score += score * weight
        total_weight += weight
    
    # Normalize et (-100 ile +100 arası)
    if total_weight > 0:
        final_score = weighted_score / total_weight
    else:
        final_score = 0
    
    # Sinyal belirle
    if final_score > 30:
        signal = 'BUY'
        confidence = min(100, abs(final_score))
    elif final_score < -30:
        signal = 'SELL'
        confidence = min(100, abs(final_score))
    else:
        signal = 'HOLD'
        confidence = 50 - abs(final_score)
    
    return {
        'signal': signal,
        'confidence': confidence,
        'final_score': final_score,
        'factors': factors,
        'symbol': symbol
    }
