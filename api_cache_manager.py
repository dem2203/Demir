# ===========================================
# api_cache_manager.py v1.0 - RATE LIMIT SAFE CACHE SYSTEM
# ===========================================
# ✅ ÖZELLİKLER:
# 1. 15 dakika cache (her endpoint için ayrı)
# 2. Multi-API fallback (API1 → API2 → API3 → yfinance)
# 3. Rate limit tracking
# 4. Automatic retry
# 5. Health monitoring
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - API Cache Manager v1.0
====================================================================
Tarih: 3 Kasım 2025, 12:40 CET
Versiyon: 1.0 - RATE LIMIT SAFE + MULTI-SOURCE CACHE

ÖZELLİKLER:
-----------
✅ 15 dakika veri cache
✅ Multi-API rotation (limit aşınca otomatik geçiş)
✅ yfinance fallback (tüm API'ler başarısız olursa)
✅ Health monitoring
✅ Graceful degradation
"""

import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# ============================================================================
# GLOBAL CACHE STORE
# ============================================================================
_CACHE = {}
_API_HEALTH = {
    'alpha_vantage': {'status': 'UNKNOWN', 'last_success': None, 'fail_count': 0},
    'twelve_data': {'status': 'UNKNOWN', 'last_success': None, 'fail_count': 0},
    'yfinance': {'status': 'UNKNOWN', 'last_success': None, 'fail_count': 0}
}

CACHE_DURATION = 15 * 60  # 15 dakika (saniye)

# ============================================================================
# API KEY LOADING
# ============================================================================
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')

# ============================================================================
# HELPER: CACHE KONTROL
# ============================================================================


def get_cached_data(cache_key: str) -> Optional[Any]:
    """
    Cache'den veri çek (15dk expire)

    Args:
        cache_key: Cache anahtarı

    Returns:
        Cached data veya None
    """
    if cache_key in _CACHE:
        entry = _CACHE[cache_key]
        if time.time() - entry['timestamp'] < CACHE_DURATION:
            print(f"📦 Cache hit: {cache_key} (Son güncellenme: {datetime.fromtimestamp(entry['timestamp']).strftime('%H:%M:%S')})")
            return entry['data']
        else:
            print(f"⏰ Cache expired: {cache_key}")
            del _CACHE[cache_key]
    return None


def set_cached_data(cache_key: str, data: Any):
    """
    Veriyi cache'e kaydet

    Args:
        cache_key: Cache anahtarı
        data: Kaydedilecek veri
    """
    _CACHE[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }
    print(f"💾 Cache saved: {cache_key}")


def update_api_health(api_name: str, success: bool):
    """
    API sağlık durumunu güncelle

    Args:
        api_name: API adı
        success: Başarılı mı?
    """
    if success:
        _API_HEALTH[api_name]['status'] = 'HEALTHY'
        _API_HEALTH[api_name]['last_success'] = time.time()
        _API_HEALTH[api_name]['fail_count'] = 0
    else:
        _API_HEALTH[api_name]['fail_count'] += 1
        if _API_HEALTH[api_name]['fail_count'] >= 3:
            _API_HEALTH[api_name]['status'] = 'UNHEALTHY'
        else:
            _API_HEALTH[api_name]['status'] = 'WARNING'


def get_api_health() -> Dict[str, Any]:
    """API sağlık durumlarını döndür"""
    return _API_HEALTH.copy()


# ============================================================================
# MULTI-SOURCE DATA FETCHER (SPY, QQQ, DXY, VIX, GLD, SLV)
# ============================================================================


def fetch_market_data(
    symbol: str,
    source_priority: List[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Multi-source market data fetcher (cache + fallback)

    Args:
        symbol: Market symbol (SPY, QQQ, DXY, ^VIX, GLD, SLV)
        source_priority: API priority listesi ['alpha_vantage', 'twelve_data', 'yfinance']
        days: Veri günü

    Returns:
        dict: {'success': bool, 'data': list, 'source': str, 'price': float}
    """
    if source_priority is None:
        source_priority = ['alpha_vantage', 'twelve_data', 'yfinance']

    cache_key = f"market_{symbol}_{days}d"

    # 1. Cache kontrolü
    cached = get_cached_data(cache_key)
    if cached:
        return {'success': True, **cached}

    # 2. API rotation
    for api_name in source_priority:
        try:
            if api_name == 'alpha_vantage' and ALPHA_VANTAGE_API_KEY:
                result = _fetch_alpha_vantage(symbol, days)
                if result['success']:
                    update_api_health('alpha_vantage', True)
                    set_cached_data(cache_key, result)
                    return result
                else:
                    update_api_health('alpha_vantage', False)

            elif api_name == 'twelve_data' and TWELVE_DATA_API_KEY:
                result = _fetch_twelve_data(symbol, days)
                if result['success']:
                    update_api_health('twelve_data', True)
                    set_cached_data(cache_key, result)
                    return result
                else:
                    update_api_health('twelve_data', False)

            elif api_name == 'yfinance':
                result = _fetch_yfinance(symbol, days)
                if result['success']:
                    update_api_health('yfinance', True)
                    set_cached_data(cache_key, result)
                    return result
                else:
                    update_api_health('yfinance', False)

        except Exception as e:
            print(f"⚠️ {api_name} fetch hatası ({symbol}): {e}")
            update_api_health(api_name, False)
            continue

    # 3. Tüm kaynaklar başarısız
    print(f"❌ Tüm kaynaklar başarısız: {symbol}")
    return {'success': False, 'data': [], 'source': 'NONE', 'price': 0}


# ============================================================================
# SOURCE 1: ALPHA VANTAGE
# ============================================================================


def _fetch_alpha_vantage(symbol: str, days: int) -> Dict[str, Any]:
    """
    Alpha Vantage API data fetch

    Returns:
        dict: {'success': bool, 'data': list, 'source': str, 'price': float}
    """
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'compact'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {'success': False}

        data = response.json()
        if 'Time Series (Daily)' not in data:
            return {'success': False}

        time_series = data['Time Series (Daily)']
        bars = []
        for date_str, values in sorted(time_series.items(), reverse=True)[:days]:
            bars.append({
                'date': date_str,
                'close': float(values['4. close']),
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'volume': float(values['5. volume'])
            })

        latest_price = bars[0]['close'] if bars else 0
        return {
            'success': True,
            'data': bars,
            'source': 'Alpha Vantage',
            'price': latest_price
        }

    except Exception as e:
        print(f"Alpha Vantage error ({symbol}): {e}")
        return {'success': False}


# ============================================================================
# SOURCE 2: TWELVE DATA
# ============================================================================


def _fetch_twelve_data(symbol: str, days: int) -> Dict[str, Any]:
    """
    Twelve Data API data fetch

    Returns:
        dict: {'success': bool, 'data': list, 'source': str, 'price': float}
    """
    try:
        # Symbol mapping
        symbol_map = {
            'SPY': 'SPY',
            'QQQ': 'QQQ',
            'DXY': 'DXY',
            '^VIX': 'VIX',
            'VIX': 'VIX',
            'GLD': 'GLD',
            'SLV': 'SLV',
            'XAU/USD': 'XAU/USD',
            'XAG/USD': 'XAG/USD'
        }
        mapped_symbol = symbol_map.get(symbol, symbol)

        url = f"https://api.twelvedata.com/time_series"
        params = {
            'symbol': mapped_symbol,
            'interval': '1day',
            'apikey': TWELVE_DATA_API_KEY,
            'outputsize': days
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return {'success': False}

        data = response.json()
        if 'values' not in data or not data['values']:
            return {'success': False}

        bars = []
        for bar in data['values']:
            bars.append({
                'date': bar['datetime'],
                'close': float(bar['close']),
                'open': float(bar['open']),
                'high': float(bar['high']),
                'low': float(bar['low']),
                'volume': float(bar.get('volume', 0))
            })

        latest_price = bars[0]['close'] if bars else 0
        return {
            'success': True,
            'data': bars,
            'source': 'Twelve Data',
            'price': latest_price
        }

    except Exception as e:
        print(f"Twelve Data error ({symbol}): {e}")
        return {'success': False}


# ============================================================================
# SOURCE 3: YFINANCE (FALLBACK)
# ============================================================================


def _fetch_yfinance(symbol: str, days: int) -> Dict[str, Any]:
    """
    yfinance fallback data fetch

    Returns:
        dict: {'success': bool, 'data': list, 'source': str, 'price': float}
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")

        if hist.empty:
            return {'success': False}

        bars = []
        for date_idx, row in hist.iterrows():
            bars.append({
                'date': date_idx.strftime('%Y-%m-%d'),
                'close': float(row['Close']),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': float(row['Volume'])
            })

        latest_price = bars[-1]['close'] if bars else 0
        return {
            'success': True,
            'data': bars,
            'source': 'yfinance',
            'price': latest_price
        }

    except Exception as e:
        print(f"yfinance error ({symbol}): {e}")
        return {'success': False}


# ============================================================================
# QUICK PRICE FETCH (CACHE + FALLBACK)
# ============================================================================


def fetch_quick_price(symbol: str, source_priority: List[str] = None) -> float:
    """
    Sadece fiyat çek (cache + fallback)

    Args:
        symbol: Market symbol
        source_priority: API priority listesi

    Returns:
        float: Fiyat (0 = başarısız)
    """
    result = fetch_market_data(symbol, source_priority, days=1)
    return result.get('price', 0)


# ============================================================================
# CACHE CLEAR
# ============================================================================


def clear_cache():
    """Tüm cache'i temizle"""
    global _CACHE
    _CACHE = {}
    print("🗑️ Cache temizlendi!")


def clear_old_cache():
    """Eski cache'leri temizle (15dk+)"""
    current_time = time.time()
    keys_to_delete = []

    for key, entry in _CACHE.items():
        if current_time - entry['timestamp'] > CACHE_DURATION:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del _CACHE[key]

    if keys_to_delete:
        print(f"🗑️ {len(keys_to_delete)} eski cache silindi!")


# ============================================================================
# SON: API_CACHE_MANAGER.PY v1.0
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🔱 API CACHE MANAGER v1.0 - RATE LIMIT SAFE!")
    print("=" * 80)
    print()
    print("ÖZELLİKLER:")
    print("  ✅ 15 dakika cache")
    print("  ✅ Multi-API rotation")
    print("  ✅ yfinance fallback")
    print("  ✅ Health monitoring")
    print("=" * 80)
