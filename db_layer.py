# db_layer.py
# v47.0: Tüm veritabanı işlemleri ve kalıcı hafıza yönetimi (v59.0 için stabil)

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import ccxt
import streamlit as st # st.cache_data için gerekli

# Ana config dosyasından DB adını al
try:
    from config import DB_NAME
except ImportError:
    # Eğer config.py bulunamazsa varsayılanı kullan (test/yerel çalıştırma için)
    DB_NAME = "demir_memory.db"

# ----------------------------
# 💾 Veritabanı Başlatma ve Tablo Oluşturma
# ----------------------------

def init_db():
    """Veritabanını ve gerekli tabloları (learning_kpis, factor_performance, live_signal_tracker) oluşturur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # v39.0: Ana strateji KPI'ları
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_kpis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        win_rate_pct REAL,
        avg_r_multiple REAL,
        total_trades INTEGER,
        expected_value REAL,
        risk_of_ruin REAL,
        UNIQUE(symbol, timeframe)
    )
    """)

    # v39.0: Parçacıklı (Granular) Faktör Performansı
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS factor_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factor_name TEXT NOT NULL UNIQUE,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        win_rate_pct REAL,
        avg_r_multiple REAL,
        total_trades INTEGER
    )
    """)

    # v40.0: Canlı Sinyal Takibi
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS live_signal_tracker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        signal_type TEXT,
        entry_price REAL,
        tp1_price REAL,
        sl_price REAL,
        status TEXT DEFAULT 'ACTIVE',
        outcome TEXT,
        closed_timestamp DATETIME,
        driving_factors TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Veritabanı tabloları kontrol edildi/oluşturuldu.")

# ----------------------------
# 💾 Veritabanı Yazma Fonksiyonları
# ----------------------------

def save_kpis_to_db(kpis: Dict[str, Any], symbol: str, timeframe: str):
    """Backtest ana KPI'larını veritabanına kaydeder."""
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO learning_kpis
    (symbol, timeframe, win_rate_pct, avg_r_multiple, total_trades, expected_value, risk_of_ruin, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol, timeframe,
        kpis.get('win_rate_pct'), kpis.get('avg_r_multiple'),
        kpis.get('total_trades'),
        kpis.get('expected_value'), kpis.get('risk_of_ruin'),
        datetime.now()
    ))
    conn.commit()
    conn.close()

def save_factor_performance_to_db(factor_kpis_list: List[Dict[str, Any]]):
    """Hipotetik faktör backtest KPI'larını DB'ye kaydeder."""
    # ... (Kod v47.0 ile aynı) ...
    if not factor_kpis_list:
        return # Boş liste ise işlem yapma
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        for kpis in factor_kpis_list:
            if not all(key in kpis for key in ['factor_name', 'win_rate_pct', 'avg_r_multiple', 'total_trades']):
                 print(f"Uyarı: Eksik anahtar içeren KPI kaydı atlandı: {kpis}")
                 continue
            cursor.execute("""
            INSERT OR REPLACE INTO factor_performance
            (factor_name, timestamp, win_rate_pct, avg_r_multiple, total_trades)
            VALUES (?, ?, ?, ?, ?)
            """, (
                kpis.get('factor_name'),
                datetime.now(),
                kpis.get('win_rate_pct'),
                kpis.get('avg_r_multiple'),
                kpis.get('total_trades')
            ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB Yazma Hatası (save_factor_performance_to_db): {e}")
        conn.rollback()
    finally:
        conn.close()


def save_live_signal(symbol: str, timeframe: str, signal: str, trade_params: Dict, driving_factors_json: str):
    """Canlı sinyali (ve nedenlerini) DB'ye 'ACTIVE' olarak kaydeder."""
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO live_signal_tracker
        (symbol, timeframe, signal_type, entry_price, tp1_price, sl_price, status, driving_factors)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
        """, (
            symbol, timeframe, signal,
            trade_params.get('Entry'), trade_params.get('TP1'), trade_params.get('SL'),
            driving_factors_json
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB Yazma Hatası (save_live_signal): {e}")
        conn.rollback()
    finally:
        conn.close()

# ----------------------------
# 💾 Veritabanı Okuma Fonksiyonları (Streamlit Cache ile)
# ----------------------------

@st.cache_data(ttl=60)
def load_kpis_from_db(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
    """Ana strateji KPI'larını veritabanından okur."""
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT * FROM learning_kpis
        WHERE symbol = ? AND timeframe = ?
        ORDER BY timestamp DESC LIMIT 1
        """, (symbol, timeframe))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"DB Okuma Hatası (load_kpis_from_db): {e}")
        row = None
    finally:
        conn.close()
    if row:
        return dict(row)
    return None

@st.cache_data(ttl=60)
def load_factor_performance_from_db() -> Dict[str, Dict[str, Any]]:
    """Tüm faktörlerin son performansını DB'den yükler."""
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    factor_weights = {}
    try:
        cursor.execute("SELECT * FROM factor_performance")
        rows = cursor.fetchall()
        for row in rows:
            factor_weights[row['factor_name']] = dict(row)
    except sqlite3.Error as e:
        print(f"DB Okuma Hatası (load_factor_performance_from_db): {e}")
    finally:
        conn.close()
    return factor_weights

# ----------------------------
# 📈 Canlı Sinyal Takibi ve Öğrenme Motoru
# ----------------------------

@st.cache_data(ttl=60)
def check_live_signal_outcomes(_exchange: ccxt.binance) -> Dict[str, Any]:
    """DB'deki 'ACTIVE' sinyalleri anlık fiyata göre kontrol eder (TP/SL)."""
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    wins_now = 0; losses_now = 0; active_count_start = 0
    summary = {'wins': 0, 'losses': 0}
    try:
        active_signals = cursor.execute("SELECT * FROM live_signal_tracker WHERE status = 'ACTIVE'").fetchall()
        active_count_start = len(active_signals)
        if not active_signals:
            conn.close()
            return {"active_count": 0, "wins_24h": 0, "losses_24h": 0}
        symbols_to_check = list(set([s['symbol'] for s in active_signals]))
        try: tickers = _exchange.fetch_tickers(symbols=symbols_to_check)
        except Exception as e:
            print(f"Canlı sinyal fiyat çekme hatası: {e}")
            conn.close()
            return {"active_count": active_count_start, "wins_24h": 0, "losses_24h": 0}
        for signal in active_signals:
            try:
                current_price = tickers[signal['symbol']]['last']
                if not current_price: continue
                outcome = None; status = 'ACTIVE'
                if "BUY" in signal['signal_type']:
                    if current_price >= signal['tp1_price']: outcome = 'SUCCESS_TP1'; status = 'CLOSED'; wins_now += 1
                    elif current_price <= signal['sl_price']: outcome = 'FAILED_SL'; status = 'CLOSED'; losses_now += 1
                elif "SELL" in signal['signal_type']:
                    if current_price <= signal['tp1_price']: outcome = 'SUCCESS_TP1'; status = 'CLOSED'; wins_now += 1
                    elif current_price >= signal['sl_price']: outcome = 'FAILED_SL'; status = 'CLOSED'; losses_now += 1
                if status == 'CLOSED':
                    cursor.execute("""
                    UPDATE live_signal_tracker
                    SET status = ?, outcome = ?, closed_timestamp = ?
                    WHERE id = ?
                    """, (status, outcome, datetime.now(), signal['id']))
            except Exception: continue
        conn.commit()
        summary_row = cursor.execute("""
        SELECT
            SUM(CASE WHEN outcome = 'SUCCESS_TP1' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN outcome = 'FAILED_SL' THEN 1 ELSE 0 END) as losses
        FROM live_signal_tracker
        WHERE closed_timestamp >= ?
        """, (datetime.now() - timedelta(hours=24),)).fetchone()
        if summary_row: summary = dict(summary_row)
    except sqlite3.Error as e:
        print(f"DB Hatası (check_live_signal_outcomes): {e}")
        conn.rollback()
    finally:
        conn.close()
    active_count_now = active_count_start - (wins_now + losses_now)
    return { "active_count": active_count_now, "wins_24h": summary.get('wins', 0) if summary else 0, "losses_24h": summary.get('losses', 0) if summary else 0 }


def run_live_learning_optimization():
    """
    v40.0 Motoru: Kapanan canlı işlemleri tarar, sonuçları alır
    ve bu sonuçları kullanarak faktör performansını günceller.
    """
    # ... (Kod v47.0 ile aynı) ...
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    live_trades_count = 0
    try:
        live_trades = cursor.execute("""
            SELECT id, driving_factors, outcome
            FROM live_signal_tracker
            WHERE status = 'CLOSED' AND driving_factors IS NOT NULL AND driving_factors != ''
        """).fetchall()
        live_trades_count = len(live_trades)
        if not live_trades:
            conn.close()
            return
        print(f"v40.0 Canlı Öğrenme: {live_trades_count} adet kapanmış işlem bulundu...")
        live_factor_stats: Dict[str, Dict[str, int]] = {}
        processed_trade_ids = []
        for trade in live_trades:
            try:
                factors = json.loads(trade['driving_factors'])
                is_win = trade['outcome'] == 'SUCCESS_TP1'
                for factor in factors:
                    if factor not in live_factor_stats: live_factor_stats[factor] = {"wins": 0, "losses": 0}
                    if is_win: live_factor_stats[factor]["wins"] += 1
                    else: live_factor_stats[factor]["losses"] += 1
                processed_trade_ids.append(trade['id'])
            except json.JSONDecodeError:
                print(f"Uyarı: Bozuk JSON verisi atlandı (ID: {trade['id']}, Veri: {trade['driving_factors']})")
                processed_trade_ids.append(trade['id'])
            except Exception as e:
                print(f"Canlı öğrenme istatistik hatası (ID: {trade['id']}): {e}")
                processed_trade_ids.append(trade['id'])
        cursor.execute("SELECT * FROM factor_performance")
        backtest_factors_rows = cursor.fetchall()
        backtest_factors: Dict[str, Dict[str, Any]] = {}
        for row in backtest_factors_rows: backtest_factors[row['factor_name']] = dict(row)
        new_kpis_list = []
        all_factors = set(live_factor_stats.keys()) | set(backtest_factors.keys()) | {"quantum", "ichimoku", "squeeze", "cvd", "fibonacci", "liq_filter", "ml_predict", "macro", "sentiment", "on_chain_l2"}
        for factor_name in all_factors:
            live_stats = live_factor_stats.get(factor_name, {"wins": 0, "losses": 0})
            backtest_stats = backtest_factors.get(factor_name, { "win_rate_pct": 50.0, "avg_r_multiple": 1.5, "total_trades": 0 })
            backtest_trades = backtest_stats.get('total_trades', 0) if backtest_stats.get('total_trades') is not None else 0
            backtest_win_rate = backtest_stats.get('win_rate_pct', 50.0) if backtest_stats.get('win_rate_pct') is not None else 50.0
            backtest_wins = (backtest_win_rate / 100.0) * backtest_trades
            backtest_losses = backtest_trades - backtest_wins
            total_wins = backtest_wins + live_stats["wins"]
            total_losses = backtest_losses + live_stats["losses"]
            total_trades = int(round(total_wins + total_losses))
            new_win_rate = (total_wins / total_trades) * 100.0 if total_trades > 0 else 50.0
            new_r_multiple = backtest_stats.get('avg_r_multiple', 1.5) if backtest_stats.get('avg_r_multiple') is not None else 1.5
            new_kpis_list.append({ "factor_name": factor_name, "win_rate_pct": new_win_rate, "avg_r_multiple": new_r_multiple, "total_trades": total_trades })
        save_factor_performance_to_db(new_kpis_list)
        if processed_trade_ids:
            ids_tuple = tuple(processed_trade_ids)
            if len(ids_tuple) == 1: ids_tuple = (ids_tuple[0],)
            update_query = f"""
                UPDATE live_signal_tracker
                SET driving_factors = NULL
                WHERE id IN ({','.join('?' * len(ids_tuple))})
            """
            cursor.execute(update_query, ids_tuple)
            conn.commit()
            print(f"{len(processed_trade_ids)} canlı işlem öğrenildi ve işaretlendi.")
        else: print("İşlenecek geçerli canlı işlem ID'si bulunamadı.")
    except sqlite3.Error as e:
        print(f"DB Hatası (run_live_learning_optimization): {e}")
        conn.rollback()
    except Exception as e:
        print(f"Beklenmedik Hata (run_live_learning_optimization): {e}")
        conn.rollback()
    finally:
        conn.close()
    if live_trades_count > 0:
        st.sidebar.success(f"v40.0 Öğrenme: {live_trades_count} canlı işlemden öğrenildi.")

print("✅ db_layer.py v47.0 (Stabil) yüklendi.") # Yükleme onayı
