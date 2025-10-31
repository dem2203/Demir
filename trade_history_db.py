"""
DEMIR AI Trading Bot - Trade History Database
SQLite database for trade logging and performance tracking
Tarih: 31 Ekim 2025

ÖZELLİKLER:
✅ SQLite database (local file)
✅ Her analizi kaydet
✅ Win/Loss tracking
✅ Export to Excel
✅ Performance metrics
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

# Database file path
DB_PATH = 'demir_ai_trades.db'


def init_database():
    """Database ve tabloları oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trades table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        symbol TEXT NOT NULL,
        interval TEXT NOT NULL,
        signal TEXT NOT NULL,
        confidence REAL NOT NULL,
        final_score REAL NOT NULL,
        entry_price REAL,
        stop_loss REAL,
        tp1 REAL,
        tp2 REAL,
        tp3 REAL,
        position_size_usd REAL,
        risk_amount_usd REAL,
        risk_reward REAL,
        reason TEXT,
        status TEXT DEFAULT 'PENDING',
        close_price REAL,
        pnl_usd REAL,
        pnl_pct REAL,
        closed_at TEXT
    )
    ''')
    
    # Performance summary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        total_trades INTEGER DEFAULT 0,
        winning_trades INTEGER DEFAULT 0,
        losing_trades INTEGER DEFAULT 0,
        win_rate REAL DEFAULT 0.0,
        total_pnl_usd REAL DEFAULT 0.0,
        avg_win_usd REAL DEFAULT 0.0,
        avg_loss_usd REAL DEFAULT 0.0,
        max_win_usd REAL DEFAULT 0.0,
        max_loss_usd REAL DEFAULT 0.0,
        sharpe_ratio REAL DEFAULT 0.0,
        updated_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def log_trade(decision):
    """
    AI kararını database'e kaydet
    
    Args:
        decision (dict): ai_brain.make_trading_decision() sonucu
    
    Returns:
        int: trade_id
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract data
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    symbol = decision.get('signal', 'UNKNOWN')
    interval = decision.get('interval', '1h')
    signal = decision.get('decision', 'NEUTRAL')
    confidence = decision.get('confidence', 0.0)
    final_score = decision.get('final_score', 0.0)
    entry_price = decision.get('entry_price', 0.0)
    stop_loss = decision.get('stop_loss', 0.0)
    position_size_usd = decision.get('position_size_usd', 0.0)
    risk_amount_usd = decision.get('risk_amount_usd', 0.0)
    risk_reward = decision.get('risk_reward', 0.0)
    reason = decision.get('reason', '')
    
    # Calculate TP levels
    if entry_price and stop_loss:
        risk = abs(entry_price - stop_loss)
        if signal == 'LONG':
            tp1 = entry_price + (risk * 1.0)
            tp2 = entry_price + (risk * 1.618)
            tp3 = entry_price + (risk * 2.618)
        else:
            tp1 = entry_price - (risk * 1.0)
            tp2 = entry_price - (risk * 1.618)
            tp3 = entry_price - (risk * 2.618)
    else:
        tp1 = tp2 = tp3 = 0.0
    
    # Insert trade
    cursor.execute('''
    INSERT INTO trades (
        timestamp, symbol, interval, signal, confidence, final_score,
        entry_price, stop_loss, tp1, tp2, tp3,
        position_size_usd, risk_amount_usd, risk_reward, reason, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp, symbol, interval, signal, confidence, final_score,
        entry_price, stop_loss, tp1, tp2, tp3,
        position_size_usd, risk_amount_usd, risk_reward, reason, 'PENDING'
    ))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Trade logged: ID={trade_id}, {signal} {symbol}")
    return trade_id


def update_trade_result(trade_id, close_price, status='WIN'):
    """
    Trade sonucunu güncelle (manuel olarak)
    
    Args:
        trade_id (int): Trade ID
        close_price (float): Kapanış fiyatı
        status (str): 'WIN' | 'LOSS' | 'BREAKEVEN'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get trade info
    cursor.execute('SELECT entry_price, position_size_usd, signal FROM trades WHERE id = ?', (trade_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"❌ Trade ID {trade_id} not found")
        conn.close()
        return
    
    entry_price, position_size_usd, signal = row
    
    # Calculate PNL
    if signal == 'LONG':
        pnl_pct = ((close_price - entry_price) / entry_price) * 100
    else:
        pnl_pct = ((entry_price - close_price) / entry_price) * 100
    
    pnl_usd = position_size_usd * (pnl_pct / 100)
    
    # Update trade
    closed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
    UPDATE trades
    SET status = ?, close_price = ?, pnl_usd = ?, pnl_pct = ?, closed_at = ?
    WHERE id = ?
    ''', (status, close_price, pnl_usd, pnl_pct, closed_at, trade_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Trade {trade_id} updated: {status}, PNL: ${pnl_usd:.2f} ({pnl_pct:+.2f}%)")
    
    # Update performance summary
    update_performance_summary()


def update_performance_summary():
    """Performance metrics'i güncelle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all closed trades
    cursor.execute('''
    SELECT pnl_usd, status FROM trades
    WHERE status IN ('WIN', 'LOSS', 'BREAKEVEN')
    ''')
    
    trades = cursor.fetchall()
    
    if not trades:
        conn.close()
        return
    
    total_trades = len(trades)
    winning_trades = sum(1 for _, status in trades if status == 'WIN')
    losing_trades = sum(1 for _, status in trades if status == 'LOSS')
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    pnls = [pnl for pnl, _ in trades]
    total_pnl_usd = sum(pnls)
    
    wins = [pnl for pnl, status in trades if status == 'WIN']
    losses = [pnl for pnl, status in trades if status == 'LOSS']
    
    avg_win_usd = sum(wins) / len(wins) if wins else 0.0
    avg_loss_usd = sum(losses) / len(losses) if losses else 0.0
    max_win_usd = max(wins) if wins else 0.0
    max_loss_usd = min(losses) if losses else 0.0
    
    # Sharpe ratio (simplified)
    if pnls:
        import numpy as np
        returns = np.array(pnls)
        sharpe_ratio = (returns.mean() / returns.std()) if returns.std() > 0 else 0.0
    else:
        sharpe_ratio = 0.0
    
    # Insert or update performance
    date = datetime.now().strftime('%Y-%m-%d')
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('SELECT id FROM performance WHERE date = ?', (date,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
        UPDATE performance
        SET total_trades = ?, winning_trades = ?, losing_trades = ?,
            win_rate = ?, total_pnl_usd = ?, avg_win_usd = ?, avg_loss_usd = ?,
            max_win_usd = ?, max_loss_usd = ?, sharpe_ratio = ?, updated_at = ?
        WHERE date = ?
        ''', (
            total_trades, winning_trades, losing_trades, win_rate, total_pnl_usd,
            avg_win_usd, avg_loss_usd, max_win_usd, max_loss_usd, sharpe_ratio,
            updated_at, date
        ))
    else:
        cursor.execute('''
        INSERT INTO performance (
            date, total_trades, winning_trades, losing_trades, win_rate,
            total_pnl_usd, avg_win_usd, avg_loss_usd, max_win_usd, max_loss_usd,
            sharpe_ratio, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date, total_trades, winning_trades, losing_trades, win_rate,
            total_pnl_usd, avg_win_usd, avg_loss_usd, max_win_usd, max_loss_usd,
            sharpe_ratio, updated_at
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Performance updated: Win Rate: {win_rate:.1f}%, Total PNL: ${total_pnl_usd:.2f}")


def get_all_trades():
    """Tüm trade'leri getir"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM trades ORDER BY timestamp DESC', conn)
    conn.close()
    return df


def get_performance_summary():
    """Performance summary getir"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM performance ORDER BY date DESC', conn)
    conn.close()
    
    if df.empty:
        return None
    
    return df.iloc[0].to_dict()


def export_to_excel(filename='demir_ai_trades.xlsx'):
    """Excel'e export et"""
    trades_df = get_all_trades()
    
    conn = sqlite3.connect(DB_PATH)
    perf_df = pd.read_sql_query('SELECT * FROM performance ORDER BY date DESC', conn)
    conn.close()
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        trades_df.to_excel(writer, sheet_name='Trades', index=False)
        perf_df.to_excel(writer, sheet_name='Performance', index=False)
    
    print(f"✅ Exported to {filename}")
    return filename


# Initialize database on import
if not os.path.exists(DB_PATH):
    init_database()


# Test
if __name__ == "__main__":
    print("=" * 80)
    print("🔱 Trade History Database Test")
    print("=" * 80)
    
    # Initialize
    init_database()
    
    # Test trade
    test_decision = {
        'signal': 'BTCUSDT',
        'interval': '1h',
        'decision': 'LONG',
        'confidence': 0.75,
        'final_score': 68.5,
        'entry_price': 69500,
        'stop_loss': 68200,
        'position_size_usd': 485,
        'risk_amount_usd': 9.36,
        'risk_reward': 2.62,
        'reason': 'Fibonacci 0.618 + Markov BULLISH'
    }
    
    trade_id = log_trade(test_decision)
    print(f"\n✅ Test trade logged: ID={trade_id}")
    
    # Simulate closing
    update_trade_result(trade_id, 71200, 'WIN')
    
    # Get summary
    perf = get_performance_summary()
    if perf:
        print(f"\n📊 Performance Summary:")
        print(f"   Total Trades: {perf['total_trades']}")
        print(f"   Win Rate: {perf['win_rate']:.1f}%")
        print(f"   Total PNL: ${perf['total_pnl_usd']:.2f}")
    
    print("\n" + "=" * 80)
