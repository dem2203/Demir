"""
📊 TRADE PERFORMANCE LOGGER - Trade Analiz ve Gelişme Önerileri
Version: 3.0 - Otomatik Log, Stats ve Recommendations
Date: 11 Kasım 2025, 00:20 CET

ÖZELLİKLER:
- Her trade'i otomatik takip et
- TP/SL durumunu kontrol et
- Performance metrikleri hesapla
- Başarı/Hata oranı
- Gelişme önerileri ver
- Streamlit session içinde çalışır
"""

import streamlit as st
from datetime import datetime
import json

class TradeLogger:
    """Trade tracking ve performance analytics"""
    
    def __init__(self):
        """Initialize trade logger"""
        if 'trades_log' not in st.session_state:
            st.session_state.trades_log = []
        if 'performance_stats' not in st.session_state:
            st.session_state.performance_stats = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'breakeven_trades': 0,
                'total_profit': 0,
                'total_loss': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'risk_reward_ratio': 0
            }
    
    def add_trade(self, trade):
        """Trade ekle ve log'a kaydet"""
        trade_entry = {
            'id': len(st.session_state.trades_log) + 1,
            'timestamp': datetime.now().isoformat(),
            'symbol': trade['symbol'],
            'direction': trade['direction'],
            'entry_price': trade['entry_price'],
            'tp_target': trade['tp_target'],
            'sl_stop': trade['sl_stop'],
            'confidence': trade['confidence'],
            'status': 'AÇIK',
            'exit_price': None,
            'result': None,
            'pnl': None,
            'pnl_pct': None
        }
        
        st.session_state.trades_log.append(trade_entry)
        return trade_entry
    
    def update_trade(self, trade_id, current_price):
        """Trade'in durumunu güncelle"""
        if trade_id < 1 or trade_id > len(st.session_state.trades_log):
            return None
        
        trade = st.session_state.trades_log[trade_id - 1]
        
        # Durum kontrolü
        if trade['direction'] == "LONG (YUKARIŞ)":
            if current_price >= trade['tp_target']:
                trade['exit_price'] = trade['tp_target']
                trade['result'] = 'TP'
                trade['status'] = 'KAPATILDI'
            elif current_price <= trade['sl_stop']:
                trade['exit_price'] = trade['sl_stop']
                trade['result'] = 'SL'
                trade['status'] = 'KAPATILDI'
            else:
                trade['status'] = 'AÇIK'
                return trade
        else:  # SHORT
            if current_price <= trade['tp_target']:
                trade['exit_price'] = trade['tp_target']
                trade['result'] = 'TP'
                trade['status'] = 'KAPATILDI'
            elif current_price >= trade['sl_stop']:
                trade['exit_price'] = trade['sl_stop']
                trade['result'] = 'SL'
                trade['status'] = 'KAPATILDI'
            else:
                trade['status'] = 'AÇIK'
                return trade
        
        # PnL hesapla
        if trade['exit_price']:
            if trade['direction'] == "LONG (YUKARIŞ)":
                pnl = trade['exit_price'] - trade['entry_price']
                pnl_pct = (pnl / trade['entry_price']) * 100
            else:
                pnl = trade['entry_price'] - trade['exit_price']
                pnl_pct = (pnl / trade['entry_price']) * 100
            
            trade['pnl'] = pnl
            trade['pnl_pct'] = pnl_pct
            
            # Stats güncelle
            self.update_stats(trade)
        
        return trade
    
    def update_stats(self, trade):
        """Performance istatistiklerini güncelle"""
        stats = st.session_state.performance_stats
        
        stats['total_trades'] += 1
        
        if trade['pnl'] > 0:
            stats['winning_trades'] += 1
            stats['total_profit'] += trade['pnl']
        elif trade['pnl'] < 0:
            stats['losing_trades'] += 1
            stats['total_loss'] += abs(trade['pnl'])
        else:
            stats['breakeven_trades'] += 1
        
        # Oranlar
        if stats['total_trades'] > 0:
            stats['win_rate'] = (stats['winning_trades'] / stats['total_trades']) * 100
        
        if stats['winning_trades'] > 0:
            stats['avg_profit'] = stats['total_profit'] / stats['winning_trades']
        
        if stats['losing_trades'] > 0:
            stats['avg_loss'] = stats['total_loss'] / stats['losing_trades']
        
        if stats['avg_loss'] > 0:
            stats['risk_reward_ratio'] = stats['avg_profit'] / stats['avg_loss']
    
    def get_performance_report(self):
        """Performance raporu oluştur"""
        stats = st.session_state.performance_stats
        
        report = f"""
        📊 TRADE PERFORMANCE RAPORU
        
        ✅ Başarıyla Kapatılan Trades:
        • Toplam İşlem: {stats['total_trades']}
        • Kazanan: {stats['winning_trades']}
        • Kaybeden: {stats['losing_trades']}
        • Eşit: {stats['breakeven_trades']}
        • Kazanma Oranı: {stats['win_rate']:.1f}%
        
        💰 Finansal Özet:
        • Toplam Kar: ${stats['total_profit']:.2f}
        • Toplam Zarar: -${stats['total_loss']:.2f}
        • Net Kar/Zarar: ${stats['total_profit'] - stats['total_loss']:.2f}
        • Ortalama Kazanç: ${stats['avg_profit']:.2f}
        • Ortalama Kayıp: -${stats['avg_loss']:.2f}
        
        📈 Oran Metrikleri:
        • Risk/Reward Oranı: 1:{stats['risk_reward_ratio']:.2f}
        • ROI: {((stats['total_profit'] - stats['total_loss']) / (stats['total_profit'] + stats['total_loss']) * 100) if (stats['total_profit'] + stats['total_loss']) > 0 else 0:.1f}%
        """
        
        return report
    
    def get_improvement_suggestions(self):
        """Gelişme önerileri ver"""
        stats = st.session_state.performance_stats
        suggestions = []
        
        # Win Rate analiz
        if stats['win_rate'] < 50:
            suggestions.append("❌ Win rate %50 altında - Signal kalitesi iyileştir")
        elif stats['win_rate'] < 60:
            suggestions.append("⚠️ Win rate %60 altında - Daha seçici trade aç")
        else:
            suggestions.append("✅ Win rate iyi - Şu anki strateji etkili")
        
        # Risk/Reward
        if stats['risk_reward_ratio'] < 1:
            suggestions.append("⚠️ Risk/Reward < 1 - TP hedeflerini yükselt")
        elif stats['risk_reward_ratio'] < 1.5:
            suggestions.append("⚠️ Risk/Reward 1.5 altında - Daha iyi TP seç")
        else:
            suggestions.append("✅ Risk/Reward sağlıklı")
        
        # Loss streak
        closing_trades = [t for t in st.session_state.trades_log if t['status'] == 'KAPATILDI']
        if len(closing_trades) >= 3:
            last_3 = closing_trades[-3:]
            losses = sum(1 for t in last_3 if t['pnl'] < 0)
            if losses == 3:
                suggestions.append("🔴 3 art arda kayıp - Break al, strateji gözden geçir")
        
        # Confidence ve result korelasyonu
        high_confidence = [t for t in closing_trades if t['confidence'] > 70]
        low_confidence = [t for t in closing_trades if t['confidence'] <= 70]
        
        if high_confidence:
            high_winrate = sum(1 for t in high_confidence if t['pnl'] > 0) / len(high_confidence) * 100
            if high_winrate > 60:
                suggestions.append("✅ Yüksek confidence sinyalleri daha iyi - Buna fokus et")
        
        if low_confidence:
            low_winrate = sum(1 for t in low_confidence if t['pnl'] > 0) / len(low_confidence) * 100
            if low_winrate < 40:
                suggestions.append("❌ Düşük confidence sinyallerini skip et - %70+ confidence'de trade aç")
        
        # TP/SL analiz
        tp_hits = sum(1 for t in closing_trades if t['result'] == 'TP')
        sl_hits = sum(1 for t in closing_trades if t['result'] == 'SL')
        
        if len(closing_trades) >= 5:
            if sl_hits > tp_hits:
                suggestions.append("📍 SL daha sık triggered - TP hedeflerini optimize et")
            else:
                suggestions.append("✅ TP hedefleri iyi ayarlanmış")
        
        # Symbol performance
        symbol_stats = {}
        for trade in closing_trades:
            symbol = trade['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'wins': 0, 'losses': 0}
            
            if trade['pnl'] > 0:
                symbol_stats[symbol]['wins'] += 1
            else:
                symbol_stats[symbol]['losses'] += 1
        
        for symbol, counts in symbol_stats.items():
            total = counts['wins'] + counts['losses']
            if total > 0:
                winrate = (counts['wins'] / total) * 100
                if winrate > 70:
                    suggestions.append(f"✅ {symbol} strong performer - Daha fazla trade aç")
                elif winrate < 40:
                    suggestions.append(f"❌ {symbol} weak performer - Daha az trade aç")
        
        return suggestions

# Streamlit Display Functions
def display_trade_logger():
    """Streamlit'te trade logger göster"""
    
    st.subheader("📊 TRADELERİM")
    
    logger = TradeLogger()
    
    # Performance özeti
    col1, col2, col3, col4 = st.columns(4)
    
    stats = st.session_state.performance_stats
    
    with col1:
        st.metric("Toplam İşlem", stats['total_trades'])
    
    with col2:
        st.metric("Kazanan", f"{stats['winning_trades']}", delta=f"{stats['win_rate']:.1f}%")
    
    with col3:
        st.metric("Net P&L", f"${stats['total_profit'] - stats['total_loss']:.2f}")
    
    with col4:
        st.metric("R/R Oranı", f"1:{stats['risk_reward_ratio']:.2f}")
    
    st.divider()
    
    # Trade tablosu
    if st.session_state.trades_log:
        st.markdown("### 📋 Trade Geçmişi")
        
        # Table için data hazırla
        table_data = []
        for trade in st.session_state.trades_log:
            table_data.append({
                'ID': trade['id'],
                'Coin': trade['symbol'].replace('USDT', ''),
                'Yön': trade['direction'].split('(')[0].strip(),
                'GİRİŞ': f"${trade['entry_price']:,.2f}",
                'HEDEF': f"${trade['tp_target']:,.2f}",
                'STOP': f"${trade['sl_stop']:,.2f}",
                'Durum': trade['status'],
                'P&L': f"${trade['pnl']:.2f}" if trade['pnl'] else '-',
                '% Değişim': f"{trade['pnl_pct']:.2f}%" if trade['pnl_pct'] else '-'
            })
        
        df = __import__('pandas').DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Gelişme önerileri
    st.markdown("### 💡 GELİŞME ÖNERİLERİ")
    
    suggestions = logger.get_improvement_suggestions()
    
    for suggestion in suggestions:
        if suggestion.startswith("✅"):
            st.success(suggestion)
        elif suggestion.startswith("⚠️"):
            st.warning(suggestion)
        elif suggestion.startswith("❌") or suggestion.startswith("🔴"):
            st.error(suggestion)
        else:
            st.info(suggestion)

def show_performance_report():
    """Performance raporu göster"""
    st.subheader("📊 PERFORMANCE RAPORU")
    
    logger = TradeLogger()
    report = logger.get_performance_report()
    
    st.text(report)

if __name__ == "__main__":
    display_trade_logger()
