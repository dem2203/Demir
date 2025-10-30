# external_data.py
#! v68.0: KRİTİK DÜZELTME: Tüm kritik TTL'ler 1 saniyeye düşürüldü.
# v67.0: KRİTİK DÜZELTME: Agresif TTL 1 saniyeye düşürüldü.

import os
import requests
import json
import numpy as np
import pandas as pd
import yfinance as yf
import ccxt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List 
import streamlit as st 

# Ana config dosyasından gerekli API anahtarları ve URL'leri al
try:
    from config import (
        TELEGRAM_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
        HYPERLIQUID_API_URL, COINGLASS_API_KEY, CRYPTOPANIC_KEY,
        API_KEY, API_SECRET, WHALE_ADDRESS
    )
    CONFIG_LOADED = True
except ImportError:
    print("Uyarı: config.py bulunamadı, external_data.py varsayılan değerleri kullanıyor.")
    CONFIG_LOADED = False
    TELEGRAM_ENABLED = False; TELEGRAM_BOT_TOKEN = ""; TELEGRAM_CHAT_ID = ""
    HYPERLIQUID_API_URL = "https://api.hyperliquid.xyz/info"
    COINGLASS_API_KEY = ""; CRYPTOPANIC_KEY = ""
    API_KEY = ""; API_SECRET = ""
    WHALE_ADDRESS = "0xc2a30212a8DdAc9e123944d6e29FADdCe994E5f2" # Varsayılan

# --- KRİTİK TTL: 1 SANİYE ---
ONE_SECOND_TTL = 1
# -----------------------------


# ----------------------------
# 🚨 Fiyat Çekme (Anlık Ticker)
# ----------------------------
@st.cache_data(ttl=ONE_SECOND_TTL) #! v68.0: 1s TTL
def fetch_latest_ticker_price(symbol: str, _exchange: ccxt.Exchange) -> float:
    """Anlık ticker fiyatını çeker (Futures/Perpetual)."""
    try:
        if _exchange is None: return np.nan
        ticker = _exchange.fetch_ticker(symbol)
        last_price = ticker.get('last')
        if last_price is not None:
             return float(last_price)
    except Exception as e:
        print(f"Uyarı: Anlık ticker fiyatı çekilemedi ({symbol}): {e}")
    return np.nan


# ----------------------------
# 📊 Makro Veri Çekme (yfinance) - 5 Dk TTL
# ----------------------------
# Makro verisi daha az kritiktir, ancak 300 saniye (5 dk) TTL korundu.
@st.cache_data(ttl=300) 
def fetch_macro_data() -> Dict[str, float]:
    """Makro verilerini (VIX, DXY, SPX, NASDAQ) çeker."""
    data = {"VIX": np.nan, "DXY": np.nan, "SPX": np.nan, "NASDAQ": np.nan}
    tickers = { "VIX": "^VIX", "DXY": "DX-Y.NYB", "SPX": "^GSPC",
                "NASDAQ": "^IXIC", "EURUSD": "EURUSD=X" }
    try:
        yf_data = yf.download(list(tickers.values()), period="1d", progress=False)
        if not yf_data.empty and 'Close' in yf_data:
            last_closes = yf_data['Close'].iloc[-1]
            for key, ticker_symbol in tickers.items():
                if key == "EURUSD": continue
                value = last_closes.get(ticker_symbol)
                if value is not None and not np.isnan(value): data[key] = round(value, 2)
            if np.isnan(data["DXY"]):
                 eur_usd_val = last_closes.get(tickers["EURUSD"])
                 if eur_usd_val is not None and not np.isnan(eur_usd_val) and eur_usd_val != 0:
                     data["DXY"] = round(100 / eur_usd_val, 2)
    except Exception as e: print(f"yfinance makro veri hatası: {e}")
    return data

# ----------------------------
# 📰 Duygu Verisi Çekme (Fear&Greed, CryptoPanic) - 5 Dk TTL
# ----------------------------
@st.cache_data(ttl=300) 
def fetch_sentiment_data() -> Dict[str, Any]:
    """Piyasa Duygusunu (F&G, Haberler) çeker."""
    sentiment_data = {"score": 0.0, "label": "🟡 Nötr", "source": "N/A"}
    # Fear & Greed
    try:
        fng_res = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        fng_res.raise_for_status()
        fng_data = fng_res.json()['data'][0]
        fng_value = int(fng_data['value'])
        fng_label = fng_data['value_classification']
        sentiment_data['score'] = (50.0 - fng_value) / 50.0
        sentiment_data['source'] = f"F&G: {fng_value} ({fng_label})"
        if fng_value <= 25: sentiment_data['label'] = "🔥 Aşırı Korku"
        elif fng_value >= 75: sentiment_data['label'] = "🚫 Aşırı Açgözlülük"
    except Exception as e: print(f"Fear&Greed hatası: {e}")
    # CryptoPanic
    if CRYPTOPANIC_KEY:
        try:
            panic_res = requests.get(f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_KEY}&public=true&kind=news", timeout=10)
            panic_res.raise_for_status()
            panic_data = panic_res.json().get('results', [])
            if panic_data:
                pos = sum(p.get('votes', {}).get('positive', 0) for p in panic_data[:5])
                neg = sum(p.get('votes', {}).get('negative', 0) + p.get('votes', {}).get('toxic', 0) + p.get('votes', {}).get('disliked', 0) for p in panic_data[:5])
                total = pos + neg
                if total > 5:
                    news_score = (pos - neg) / total
                    sentiment_data['score'] = round((sentiment_data['score'] * 0.7) + (news_score * 0.3), 3)
                    news_label = " (Haberler Pozitif)" if news_score > 0.4 else " (Haberler Negatif)" if news_score < -0.4 else ""
                    sentiment_data['label'] += news_label
                    sentiment_data['source'] += f" / CP: {pos}P/{neg}N"
        except Exception as e: print(f"CryptoPanic hatası: {e}")
    return sentiment_data

# ----------------------------
# 📈 Türev Verisi Çekme (CCXT)
# ----------------------------
@st.cache_data(ttl=ONE_SECOND_TTL) #! v68.0: 1s TTL
def get_derivatives_data(symbol: str, _exchange: ccxt.Exchange) -> Dict[str, Any]:
    """Türev piyasa metriklerini (Funding Rate, OI Amount, OI Value) çeker."""
    data = {"funding_rate": np.nan, "open_interest": np.nan, "oi_value_usd": np.nan, "oi_amount": np.nan}
    # Funding Rate
    try:
        if _exchange.has['fetchFundingRate']:
            funding_data = _exchange.fetch_funding_rate(symbol)
            rate = funding_data.get('fundingRate', funding_data.get('info', {}).get('lastFundingRate'))
            if rate is not None:
                 data["funding_rate"] = round(float(rate) * 100, 4)
    except (ccxt.NotSupported, ccxt.ExchangeError): pass
    except Exception as e: print(f"Funding rate hatası ({symbol}): {e}")
    # Open Interest
    try:
        if _exchange.has['fetchOpenInterest']:
            oi_data = _exchange.fetch_open_interest(symbol)
            oi_amount_keys = ['openInterestAmount', 'info.open_interest', 'info.size']
            oi_value_keys = ['openInterestValue', 'info.open_interest_value', 'info.turnover24h', 'quoteVolume']
            oi_amount = None
            for key in oi_amount_keys:
                try: oi_amount = oi_data.get(key.split('.')[0], {}).get(key.split('.')[1]) if '.' in key else oi_data.get(key); break
                except: pass
            if oi_amount is not None: data["oi_amount"] = round(float(oi_amount), 4)
            oi_value = None
            for key in oi_value_keys:
                try: oi_value = oi_data.get(key.split('.')[0], {}).get(key.split('.')[1]) if '.' in key else oi_data.get(key); break
                except: pass
            if oi_value is not None: data["oi_value_usd"] = round(float(oi_value), 2)
            if data["oi_value_usd"] is not None and not np.isnan(data["oi_value_usd"]):
                data["open_interest"] = data["oi_value_usd"]
            elif data["oi_amount"] is not None and not np.isnan(data["oi_amount"]):
                 try:
                     ticker = _exchange.fetch_ticker(symbol) 
                     last_price = ticker.get('last')
                     if last_price:
                         estimated_value = data["oi_amount"] * last_price
                         data["oi_value_usd"] = round(estimated_value, 2)
                         data["open_interest"] = data["oi_value_usd"]
                     else: data["open_interest"] = data["oi_amount"]
                 except Exception: data["open_interest"] = data["oi_amount"]
    except (ccxt.NotSupported, ccxt.ExchangeError): pass
    except Exception as e: print(f"Open interest hatası ({symbol}): {e}")
    return data


# ----------------------------
# ⛓️ On-Chain (Emir Defteri) Verisi Çekme (CCXT)
# ----------------------------
@st.cache_data(ttl=ONE_SECOND_TTL) #! v68.0: 1s TTL
def get_on_chain_data(symbol: str, _exchange: ccxt.Exchange) -> Dict[str, float]:
    """Emir Defteri (L2) verisinden OIR (-1 ile +1 arası) hesaplar."""
    oir_value = 0.0
    try:
        if _exchange.has['fetchL2OrderBook']:
            order_book = _exchange.fetch_l2_order_book(symbol, limit=200)
            bids = pd.DataFrame(order_book['bids'], columns=['price', 'amount'])
            asks = pd.DataFrame(order_book['asks'], columns=['price', 'amount'])
            if not bids.empty and not asks.empty:
                bid_depth = bids['amount'].sum()
                ask_depth = asks['amount'].sum()
                total_depth = bid_depth + ask_depth
                if total_depth > 0:
                     oir = (bid_depth - ask_depth) / total_depth
                     oir_value = round(oir, 4)
    except Exception: pass
    return {"OIR": oir_value}


# ----------------------------
# 🔥 Likidasyon Verisi Çekme (Coinglass) - 5 Dk TTL
# ----------------------------
@st.cache_data(ttl=300) # Likidasyon verisi daha az kritiktir
def fetch_liquidation_data(symbol: str, current_price: float) -> Dict[str, Any]:
    """Coinglass API üzerinden likidasyon ısı haritası alınır."""
    result = {"long_liq_price": np.nan, "short_liq_price": np.nan, "liq_comment": "Veri yok/API Key eksik."}
    if not COINGLASS_API_KEY: return result
    symbol_only = symbol.replace("/USDT", "").replace("-PERP", "")
    headers = {"coinglassSecret": COINGLASS_API_KEY}
    url = f"https://open-api.coinglass.com/api/futures/liquidation_map?symbol={symbol_only}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', {})
        longs = data.get('long', []); shorts = data.get('short', [])
        if not longs or not shorts or pd.isna(current_price):
             result["liq_comment"] = "Likidasyon verisi boş/fiyat geçersiz."; return result
        near_longs_prices = [l[0] for l in longs if l[0] < current_price]
        near_shorts_prices = [s[0] for s in shorts if s[0] > current_price]
        if not near_longs_prices or not near_shorts_prices:
            result["liq_comment"] = "Fiyata yakın lik. havuzu yok."; return result
        long_liq_price = max(near_longs_prices); short_liq_price = min(near_shorts_prices)
        result["long_liq_price"] = long_liq_price; result["short_liq_price"] = short_liq_price
        long_dist = current_price - long_liq_price; short_dist = short_liq_price - current_price
        if long_dist < short_dist: result["liq_comment"] = f"⚠️ Yakın Long Lik. (${long_liq_price:.2f}, {long_dist:.2f}$ alt.)"
        else: result["liq_comment"] = f"🎯 Yakın Short Lik. (${short_liq_price:.2f}, {short_dist:.2f}$ üst.)"
    except requests.exceptions.RequestException as e: result["liq_comment"] = f"Coinglass API hatası."
    except Exception as e: result["liq_comment"] = f"Likidasyon işleme hatası."
    return result

# ----------------------------
# 🕯️ OHLCV Verisi Çekme (CCXT)
# ----------------------------
@st.cache_data(ttl=ONE_SECOND_TTL) #! v68.0: 1s TTL
def get_crypto_data(symbol: str, timeframe: str, _exchange: ccxt.Exchange, start_date: Optional[datetime] = None, limit: int = 400) -> Optional[pd.DataFrame]:
    """
    OHLCV verisi çeker. _exchange objesi Futures olarak yapılandırılmış olmalıdır.
    """
    limit_to_use = limit if limit is not None else 400
    df = None
    try:
        if _exchange is None:
             print(f"Hata: CCXT Exchange objesi (_exchange) geçersiz.")
             return None
             
        since_ms = int(start_date.timestamp() * 1000) if start_date else None
        
        # CCXT'nin rate limit mekanizması kullanılır
        ohlcv = _exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit_to_use)
        if not ohlcv: print(f"Uyarı: {symbol} - {timeframe} için OHLCV verisi alınamadı."); return None

        df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms', utc=True)
        df.set_index('Timestamp', inplace=True)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        first_valid_idx = df['Close'].first_valid_index()
        if first_valid_idx is not None: df = df.loc[first_valid_idx:]
        else: return None
        
    except (ccxt.NetworkError, ccxt.ExchangeError) as e: print(f"CCXT Hatası ({symbol}): {e}")
    except Exception as e: print(f"Veri Çekme Hatası ({symbol}): {e}")
    return df

def send_telegram_message(message: str):
    """Telegram'a mesaj gönderir."""
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = { "chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown" }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Telegram gönderim hatası: {e}")
    except Exception as e:
        print(f"Bilinmeyen Telegram hatası: {e}")

def track_whale_activity(address: str) -> None:
    """Belirli bir balina adresini Hyperliquid API üzerinden takip eder ve mesaj gönderir."""
    if not address or not TELEGRAM_ENABLED: return
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"type": "clearinghouseState", "user": address})
    try:
        response = requests.post(HYPERLIQUID_API_URL, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        new_positions = {}
        if 'assetPositions' in data:
            for item in data['assetPositions']:
                if 'position' in item and 'coin' in item['position']:
                    symbol = item['position']['coin']
                    size_usd = float(item['position']['szi'])
                    if abs(size_usd) > 1: new_positions[symbol] = size_usd
        if 'whale_positions' not in st.session_state: st.session_state.whale_positions = {}
        old_positions = st.session_state.get('whale_positions', {})
        messages = []
        for symbol, old_size in old_positions.items():
            if symbol not in new_positions:
                messages.append(f"❌ *POZİSYON KAPATILDI* ❌\nBalina ({address[:6]}...) {symbol} pozisyonunu kapattı (Eski: ${old_size:,.0f}).")
            elif new_positions[symbol] != old_size:
                 messages.append(f"🔄 *POZİSYON DEĞİŞTİ* 🔄\nBalina ({address[:6]}...) {symbol} pozisyonunu ${old_size:,.0f} -> ${new_positions[symbol]:,.0f} olarak güncelledi.")
        for symbol, new_size in new_positions.items():
            if symbol not in old_positions:
                direction = "LONG" if new_size > 0 else "SHORT"
                messages.append(f"🔥 *YENİ POZİSYON: {direction}* 🔥\nBalina ({address[:6]}...) ${abs(new_size):,.0f} değerinde {symbol} {direction} pozisyonu açtı!")
        if messages:
            full_message = f"🚨 *DemirAI Balina Takip (v51+)* 🚨\nAdres: `{address}`\n\n" + "\n\n".join(messages)
            send_telegram_message(full_message)
        st.session_state.whale_positions = new_positions
    except requests.exceptions.RequestException as e: print(f"Balina takip API hatası: {e}")
    except Exception as e: print(f"Balina takip bilinmeyen hata: {e}")
    
print("✅ external_data.py v68.0 (Agresif TTL 1s) yüklendi.")
