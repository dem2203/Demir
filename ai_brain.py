"""
DEMIR - AI Brain Module v2.0
Self-Learning Trading Intelligence
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class MarketRegimeDetector:
    """Piyasa rejimi tespiti"""
    
    @staticmethod
    def detect_regime(df: pd.DataFrame) -> Dict[str, Any]:
        try:
            adx = df['ADX'].iloc[-1] if 'ADX' in df.columns else 20
            atr_current = df['ATR'].iloc[-1] if 'ATR' in df.columns else 0
            atr_mean = df['ATR'].mean() if 'ATR' in df.columns else 1
            atr_percentile = (atr_current / atr_mean * 100) if atr_mean > 0 else 50
            
            bb_upper = df.get('BB_High', df.get('BB_Upper', pd.Series([0]))).iloc[-1]
            bb_lower = df.get('BB_Low', df.get('BB_Lower', pd.Series([0]))).iloc[-1]
            bb_mid = df.get('BB_Mid', df.get('BB_Middle', pd.Series([1]))).iloc[-1]
            bb_width = (bb_upper - bb_lower) / max(bb_mid, 1)
            
            if adx > 25 and atr_percentile < 70:
                regime = 'TREND'
                confidence = min(100, adx * 1.5)
                explanation = "Piyasa güçlü bir trend içinde. İşlem yapmak için ideal."
            elif adx < 20 and bb_width < 0.05:
                regime = 'RANGE'
                confidence = 100 - adx * 3
                explanation = "Piyasa yatay seyrediyor. Fiyat dar aralıkta."
            else:
                regime = 'VOLATILE'
                confidence = atr_percentile
                explanation = "Piyasa dalgalı ve tahmin edilemez. Dikkatli ol!"
            
            return {
                'regime': regime,
                'confidence': confidence,
                'adx': adx,
                'explanation': explanation
            }
        except Exception as e:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'explanation': f"Rejim hesaplanamadı: {e}"
            }


class MultiTimeframeAnalysis:
    """Çoklu zaman dilimi analizi"""
    
    @staticmethod
    def analyze_confluence(symbol: str, timeframes: List[str] = ['15m', '1h', '4h']) -> Dict:
        from analysis_layer import run_full_analysis
        from strategy_layer import generate_signal
        from external_data import get_all_external_data
        
        signals = {}
        ext_data = get_all_external_data()
        
        for tf in timeframes:
            try:
                tech = run_full_analysis(symbol, tf)
                if 'error' not in tech:
                    sig = generate_signal(symbol, tech, ext_data)
                    signals[tf] = sig.get('signal', 'HOLD')
                else:
                    signals[tf] = 'HOLD'
            except:
                signals[tf] = 'HOLD'
        
        buy_count = sum(1 for s in signals.values() if s == 'BUY')
        sell_count = sum(1 for s in signals.values() if s == 'SELL')
        
        if buy_count >= 2:
            confluence_score = (buy_count / len(timeframes)) * 100
            aligned_signal = 'BUY'
            explanation = f"{buy_count}/{len(timeframes)} zaman ALIŞ sinyali. Güçlü!"
        elif sell_count >= 2:
            confluence_score = (sell_count / len(timeframes)) * 100
            aligned_signal = 'SELL'
            explanation = f"{sell_count}/{len(timeframes)} zaman SATIŞ sinyali. Güçlü!"
        else:
            confluence_score = 0
            aligned_signal = 'HOLD'
            explanation = "Zaman dilimleri uyumsuz. Bekle!"
        
        return {
            'confluence_score': confluence_score,
            'timeframe_signals': signals,
            'aligned_signal': aligned_signal,
            'aligned': confluence_score >= 66,
            'explanation': explanation
        }


class RiskRewardCalculator:
    """Risk/Ödül hesaplama"""
    
    @staticmethod
    def calculate_rr(entry_price: float, tech_data: Dict) -> Dict[str, float]:
        fib = tech_data.get('fibonacci', {})
        vp = tech_data.get('volume_profile', {})
        
        stop_candidates = []
        if fib:
            stop_candidates.extend([
                fib.get('fib_382', entry_price * 0.97),
                fib.get('fib_236', entry_price * 0.98)
            ])
        if vp:
            stop_candidates.append(vp.get('val', entry_price * 0.97))
        
        stop_loss = min([s for s in stop_candidates if s > 0]) if stop_candidates else entry_price * 0.97
        
        tp_candidates = []
        if fib:
            tp_candidates.append(fib.get('fib_618', entry_price * 1.03))
        if vp:
            tp_candidates.append(vp.get('vah', entry_price * 1.03))
        
        take_profit_1 = max([t for t in tp_candidates if t > 0]) if tp_candidates else entry_price * 1.03
        take_profit_2 = entry_price * 1.06
        
        risk = abs(entry_price - stop_loss)
        reward_1 = abs(take_profit_1 - entry_price)
        rr_ratio = reward_1 / risk if risk > 0 else 0
        
        if rr_ratio >= 3:
            quality = 'MÜTHİŞ'
            explanation = f"Risk/Ödül çok yüksek! {rr_ratio:.1f}x kazanç potansiyeli."
        elif rr_ratio >= 2:
            quality = 'İYİ'
            explanation = f"İyi fırsat. {rr_ratio:.1f}x kazanç hedefi."
        elif rr_ratio >= 1.5:
            quality = 'KABUL EDİLEBİLİR'
            explanation = f"Orta seviye. R/R: {rr_ratio:.1f}"
        else:
            quality = 'ZAYIF'
            explanation = f"Risk ödülü karşılamıyor! R/R: {rr_ratio:.1f}"
        
        return {
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_reward_ratio': rr_ratio,
            'trade_quality': quality,
            'explanation': explanation
        }


class PositionSizer:
    """Kelly Criterion pozisyon hesaplama"""
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                       capital: float, max_risk_pct: float = 2.0) -> Dict:
        if win_rate <= 0 or avg_win <= 0 or avg_loss <= 0:
            return {
                'position_size': capital * (max_risk_pct / 100),
                'explanation': f"Varsayılan: %{max_risk_pct} risk"
            }
        
        kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly_pct = kelly_pct / 2  # Half Kelly
        kelly_pct = min(kelly_pct, max_risk_pct / 100)
        kelly_pct = max(kelly_pct, 0)
        
        position_size = capital * kelly_pct
        explanation = f"Kelly: %{kelly_pct*100:.1f} ({position_size:.0f} USD)"
        
        return {
            'position_size': position_size,
            'kelly_percentage': kelly_pct * 100,
            'explanation': explanation
        }


class AIBrain:
    """Ana AI Brain"""
    
    def __init__(self):
        self.regime_detector = MarketRegimeDetector()
        self.mtf_analyzer = MultiTimeframeAnalysis()
        self.rr_calculator = RiskRewardCalculator()
        self.position_sizer = PositionSizer()
    
    def make_decision(self, symbol: str, capital: float = 10000) -> Dict[str, Any]:
        from analysis_layer import run_full_analysis, get_binance_data
        from strategy_layer import generate_signal
        from external_data import get_all_external_data
        
        tech_data = run_full_analysis(symbol, '1h')
        
        if 'error' in tech_data:
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reasoning': ['❌ Veri çekilemedi'],
                'metadata': {},
                'position_size': 0,
                'stop_loss': 0,
                'take_profit_1': 0,
                'take_profit_2': 0,
                'risk_reward_ratio': 0
            }
        
        ext_data = get_all_external_data()
        base_signal = generate_signal(symbol, tech_data, ext_data)
        
        df = get_binance_data(symbol, '1h', limit=1)
        current_price = float(df['Close'].iloc[-1]) if not df.empty else tech_data.get('price', 0)
        
        df_full = tech_data.get('dataframe')
        regime = self.regime_detector.detect_regime(df_full) if df_full is not None and not df_full.empty else {
            'regime': 'UNKNOWN', 'explanation': 'Hesaplanamadı'
        }
        
        mtf = self.mtf_analyzer.analyze_confluence(symbol)
        rr_data = self.rr_calculator.calculate_rr(current_price, tech_data)
        
        win_rate = 0.55
        avg_win = rr_data['take_profit_1'] - current_price
        avg_loss = current_price - rr_data['stop_loss']
        position_data = self.position_sizer.kelly_criterion(win_rate, avg_win, avg_loss, capital)
        
        final_signal = 'HOLD'
        confidence = 0
        reasoning = []
        
        if mtf['aligned'] and mtf['aligned_signal'] == base_signal['signal']:
            confidence += 40
            reasoning.append(f"✅ {mtf['explanation']}")
        else:
            reasoning.append(f"⚠️ {mtf['explanation']}")
        
        reasoning.append(f"📊 {regime.get('explanation', '')}")
        if regime['regime'] == 'TREND' and base_signal['signal'] != 'HOLD':
            confidence += 30
