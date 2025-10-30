"""
DEMIR - AI Brain Module
Self-Learning Adaptive Trading Intelligence
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

# ============================================
# MARKET REGIME DETECTOR
# ============================================

class MarketRegimeDetector:
    """Piyasa rejimini tespit et: Trend / Range / Volatile"""
    
    @staticmethod
    def detect_regime(df: pd.DataFrame) -> Dict[str, Any]:
        """
        ADX, ATR, Bollinger Band width kullanarak regime belirle
        
        Returns:
            {
                'regime': 'TREND' | 'RANGE' | 'VOLATILE',
                'confidence': float (0-100),
                'adx': float,
                'atr_percentile': float
            }
        """
        # ADX hesapla (trend strength)
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        
        # +DM ve -DM
        high_diff = high.diff()
        low_diff = -low.diff()
        
        pos_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        neg_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Smoothed DM
        pos_di = 100 * (pos_dm.rolling(14).mean() / atr)
        neg_di = 100 * (neg_dm.rolling(14).mean() / atr)
        
        # DX ve ADX
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(14).mean().iloc[-1]
        
        # ATR percentile (volatilite)
        atr_current = atr.iloc[-1]
        atr_percentile = (atr.rank(pct=True).iloc[-1]) * 100
        
        # BB width
        bb_width = (df['BB_upper'].iloc[-1] - df['BB_lower'].iloc[-1]) / df['BB_middle'].iloc[-1]
        
        # Karar
        if adx > 25 and atr_percentile < 70:
            regime = 'TREND'
            confidence = min(100, adx * 1.5)
        elif adx < 20 and bb_width < 0.05:
            regime = 'RANGE'
            confidence = 100 - adx * 3
        else:
            regime = 'VOLATILE'
            confidence = atr_percentile
        
        return {
            'regime': regime,
            'confidence': confidence,
            'adx': adx,
            'atr_percentile': atr_percentile,
            'bb_width': bb_width
        }


# ============================================
# MULTI-TIMEFRAME CONFLUENCE
# ============================================

class MultiTimeframeAnalysis:
    """Birden fazla zaman diliminde uyum kontrolü"""
    
    @staticmethod
    def analyze_confluence(symbol: str, timeframes: List[str] = ['15m', '1h', '4h']) -> Dict:
        """
        Farklı timeframe'lerde sinyal uyumu
        
        Returns:
            {
                'confluence_score': float (0-100),
                'timeframe_signals': {tf: signal},
                'aligned': bool
            }
        """
        from analysis_layer import run_full_analysis
        from strategy_layer import generate_signal
        from external_data import get_all_external_data
        
        signals = {}
        ext_data = get_all_external_data()
        
        for tf in timeframes:
            try:
                tech = run_full_analysis(symbol, tf)
                sig = generate_signal(symbol, tech, ext_data)
                signals[tf] = sig.get('signal', 'HOLD')
            except:
                signals[tf] = 'HOLD'
        
        # Uyum skoru
        buy_count = sum(1 for s in signals.values() if s == 'BUY')
        sell_count = sum(1 for s in signals.values() if s == 'SELL')
        
        if buy_count >= 2:
            confluence_score = (buy_count / len(timeframes)) * 100
            aligned_signal = 'BUY'
        elif sell_count >= 2:
            confluence_score = (sell_count / len(timeframes)) * 100
            aligned_signal = 'SELL'
        else:
            confluence_score = 0
            aligned_signal = 'HOLD'
        
        return {
            'confluence_score': confluence_score,
            'timeframe_signals': signals,
            'aligned_signal': aligned_signal,
            'aligned': confluence_score >= 66
        }


# ============================================
# RISK-REWARD CALCULATOR
# ============================================

class RiskRewardCalculator:
    """Hedge fund seviyesinde R/R analizi"""
    
    @staticmethod
    def calculate_rr(entry_price: float, tech_data: Dict) -> Dict[str, float]:
        """
        Fibonacci, support/resistance kullanarak R/R hesapla
        
        Returns:
            {
                'stop_loss': float,
                'take_profit_1': float,
                'take_profit_2': float,
                'risk_reward_ratio': float,
                'trade_quality': str
            }
        """
        fib = tech_data.get('fibonacci', {})
        vp = tech_data.get('volume_profile', {})
        
        # Stop loss: En yakın Fibonacci veya VAL
        stop_candidates = []
        
        if fib:
            stop_candidates.extend([
                fib.get('fib_382', entry_price * 0.97),
                fib.get('fib_236', entry_price * 0.98)
            ])
        
        if vp:
            stop_candidates.append(vp.get('val', entry_price * 0.97))
        
        stop_loss = min(stop_candidates) if stop_candidates else entry_price * 0.97
        
        # Take profit: Üst Fibonacci veya VAH
        tp_candidates = []
        
        if fib:
            tp_candidates.extend([
                fib.get('fib_786', entry_price * 1.03),
                fib.get('fib_100', entry_price * 1.05)
            ])
        
        if vp:
            tp_candidates.append(vp.get('vah', entry_price * 1.03))
        
        take_profit_1 = max(tp_candidates) if tp_candidates else entry_price * 1.03
        take_profit_2 = entry_price * 1.06  # Extension
        
        # R/R hesapla
        risk = abs(entry_price - stop_loss)
        reward_1 = abs(take_profit_1 - entry_price)
        
        rr_ratio = reward_1 / risk if risk > 0 else 0
        
        # Trade quality
        if rr_ratio >= 3:
            quality = 'EXCELLENT'
        elif rr_ratio >= 2:
            quality = 'GOOD'
        elif rr_ratio >= 1.5:
            quality = 'ACCEPTABLE'
        else:
            quality = 'POOR'
        
        return {
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_reward_ratio': rr_ratio,
            'trade_quality': quality
        }


# ============================================
# POSITION SIZING (KELLY CRITERION)
# ============================================

class PositionSizer:
    """Kelly Criterion ile optimal pozisyon boyutu"""
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float, 
                       capital: float, max_risk_pct: float = 2.0) -> float:
        """
        Kelly % = (Win Rate * Avg Win - (1 - Win Rate) * Avg Loss) / Avg Win
        
        Args:
            win_rate: Kazanma oranı (0-1)
            avg_win: Ortalama kazanç
            avg_loss: Ortalama kayıp (pozitif değer)
            capital: Toplam sermaye
            max_risk_pct: Maksimum risk yüzdesi (güvenlik)
        
        Returns:
            position_size: Pozisyon boyutu (USD)
        """
        if win_rate <= 0 or avg_win <= 0 or avg_loss <= 0:
            return capital * (max_risk_pct / 100)
        
        # Kelly formülü
        kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Güvenlik: Kelly'yi yarıya düşür (Half Kelly)
        kelly_pct = kelly_pct / 2
        
        # Max risk limiti
        kelly_pct = min(kelly_pct, max_risk_pct / 100)
        kelly_pct = max(kelly_pct, 0)
        
        position_size = capital * kelly_pct
        
        return position_size


# ============================================
# ADAPTIVE WEIGHT OPTIMIZER
# ============================================

class AdaptiveWeightOptimizer:
    """Performansa göre faktör ağırlıklarını güncelle"""
    
    def __init__(self, db_file='demir_trading.db'):
        self.db_file = db_file
    
    def optimize_weights(self, lookback_days: int = 30) -> Dict[str, float]:
        """
        Son N günün performansına göre ağırlıkları optimize et
        
        Returns:
            optimized_weights: {factor: new_weight}
        """
        import sqlite3
        
        conn = sqlite3.connect(self.db_file)
        
        # Son N günün sinyallerini al
        query = f"""
            SELECT factors, confidence 
            FROM signals 
            WHERE timestamp > datetime('now', '-{lookback_days} days')
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Her faktörün ortalama katkısını hesapla
        factor_scores = {}
        
        for _, row in df.iterrows():
            try:
                factors = json.loads(row['factors'])
                confidence = row['confidence']
                
                for factor, score in factors.items():
                    if factor not in factor_scores:
                        factor_scores[factor] = []
                    
                    # Yüksek confidence'lı sinyallerdeki faktörlere bonus
                    weighted_score = score * (confidence / 100)
                    factor_scores[factor].append(weighted_score)
                    
            except:
                continue
        
        # Ortalama skorları hesapla ve normalize et
        optimized_weights = {}
        
        for factor, scores in factor_scores.items():
            avg_score = np.mean(np.abs(scores))
            optimized_weights[factor] = max(0.5, min(2.0, avg_score / 50))
        
        return optimized_weights


# ============================================
# MASTER AI BRAIN
# ============================================

class AIBrain:
    """Tüm AI modüllerini yöneten ana beyin"""
    
    def __init__(self):
        self.regime_detector = MarketRegimeDetector()
        self.mtf_analyzer = MultiTimeframeAnalysis()
        self.rr_calculator = RiskRewardCalculator()
        self.position_sizer = PositionSizer()
        self.weight_optimizer = AdaptiveWeightOptimizer()
    
    def make_decision(self, symbol: str, capital: float = 10000) -> Dict[str, Any]:
        """
        Tüm AI modüllerini kullanarak nihai karar ver
        
        Returns:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'confidence': float,
                'position_size': float,
                'stop_loss': float,
                'take_profit': float,
                'reasoning': str,
                'metadata': dict
            }
        """
        from analysis_layer import run_full_analysis
        from strategy_layer import generate_signal
        from external_data import get_all_external_data
        
        # 1. Tek timeframe analiz
        tech_data = run_full_analysis(symbol, '1h')
        ext_data = get_all_external_data()
        base_signal = generate_signal(symbol, tech_data, ext_data)
        
        # 2. Market regime
        df = tech_data.get('dataframe')
        regime = self.regime_detector.detect_regime(df) if df is not None else {'regime': 'UNKNOWN'}
        
        # 3. Multi-timeframe confluence
        mtf = self.mtf_analyzer.analyze_confluence(symbol)
        
        # 4. Risk-Reward
        current_price = tech_data.get('price', 0)
        rr_data = self.rr_calculator.calculate_rr(current_price, tech_data)
        
        # 5. Karar mantığı
        final_signal = 'HOLD'
        confidence = 0
        reasoning = []
        
        # Confluence check
        if mtf['aligned'] and mtf['aligned_signal'] == base_signal['signal']:
            confidence += 40
            reasoning.append(f"✅ Multi-timeframe aligned ({mtf['aligned_signal']})")
        else:
            reasoning.append(f"⚠️ Timeframe conflict")
        
        # Regime check
        if regime['regime'] == 'TREND' and base_signal['signal'] != 'HOLD':
            confidence += 30
            reasoning.append(f"✅ Strong trend detected (ADX: {regime['adx']:.1f})")
        elif regime['regime'] == 'RANGE':
            confidence -= 20
            reasoning.append(f"⚠️ Range-bound market")
        
        # R/R check
        if rr_data['trade_quality'] in ['EXCELLENT', 'GOOD']:
            confidence += 20
            reasoning.append(f"✅ Good R/R ratio: {rr_data['risk_reward_ratio']:.2f}")
        else:
            confidence -= 30
            reasoning.append(f"❌ Poor R/R ratio: {rr_data['risk_reward_ratio']:.2f}")
        
        # Base signal confidence
        confidence += base_signal.get('confidence', 0) * 0.3
        
        # Final decision
        confidence = max(0, min(100, confidence))
        
        if confidence >= 70 and rr_data['risk_reward_ratio'] >= 2:
            final_signal = base_signal['signal']
        else:
            final_signal = 'HOLD'
        
        # Position sizing
        win_rate = 0.55  # Varsayılan (DB'den alınacak)
        avg_win = rr_data['take_profit_1'] - current_price
        avg_loss = current_price - rr_data['stop_loss']
        
        position_size = self.position_sizer.kelly_criterion(
            win_rate, avg_win, avg_loss, capital
        )
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'position_size': position_size,
            'stop_loss': rr_data['stop_loss'],
            'take_profit_1': rr_data['take_profit_1'],
            'take_profit_2': rr_data['take_profit_2'],
            'risk_reward_ratio': rr_data['risk_reward_ratio'],
            'reasoning': reasoning,
            'metadata': {
                'regime': regime,
                'mtf_confluence': mtf,
                'base_signal': base_signal
            }
        }
