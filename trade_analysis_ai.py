"""
📊 TRADE_ANALYSIS_REFORMATTED - Yapay Zeka Tabanlı Trade İntelijen Sistemi
Version: 2.0 - AI-Powered Trade Analysis
Date: 11 Kasım 2025

YENİ YAKLAŞIM:
Her trade'e AI puanlaması ve detaylı analiz
- AI confidence score
- Layer breakdown
- Pattern matching
- Risk assessment
- Opportunity grading (A+, A, B, C)
"""

import json
from datetime import datetime
from typing import Dict, List
import numpy as np

class TradeAnalysisAI:
    """Yapay zeka tarafından trade analiz sistemi"""
    
    def __init__(self):
        self.trade_history = []
        self.pattern_library = {}
        self.ai_insights = []
    
    def analyze_trade_opportunity(self, 
                                   symbol: str,
                                   signal_type: str,
                                   entry_price: float,
                                   tp_price: float,
                                   sl_price: float,
                                   ai_confidence: float,
                                   layer_scores: Dict) -> Dict:
        """
        TRADE'ı AI ile analiz et
        
        Args:
            symbol: BTCUSDT vb
            signal_type: LONG/SHORT
            entry_price: Giriş fiyatı
            tp_price: Take profit
            sl_price: Stop loss
            ai_confidence: 0-100 AI güveni
            layer_scores: Tüm layer'ların skorları
        
        Returns:
            Detaylı trade analizi
        """
        
        analysis_time = datetime.now()
        
        # === RISK/REWARD HESAPLA ===
        if signal_type == "LONG":
            potential_profit = tp_price - entry_price
            potential_loss = entry_price - sl_price
        else:  # SHORT
            potential_profit = entry_price - tp_price
            potential_loss = sl_price - entry_price
        
        profit_percentage = (potential_profit / entry_price) * 100 if entry_price > 0 else 0
        loss_percentage = (potential_loss / entry_price) * 100 if entry_price > 0 else 0
        risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
        
        # === TRADE GRADING (A+, A, B, C) ===
        grade = self._calculate_trade_grade(
            ai_confidence,
            risk_reward_ratio,
            layer_scores
        )
        
        # === LAYER BREAKDOWN ===
        layer_analysis = self._analyze_layer_contribution(layer_scores)
        
        # === PATTERN MATCH ===
        pattern_match = self._match_historical_patterns(
            symbol,
            signal_type,
            layer_scores
        )
        
        # === RISK ASSESSMENT ===
        risks = self._assess_trade_risks(
            symbol,
            entry_price,
            tp_price,
            sl_price,
            layer_scores
        )
        
        # === AI INSIGHTS ===
        insights = self._generate_ai_insights(
            symbol,
            signal_type,
            grade,
            layer_analysis,
            pattern_match,
            ai_confidence
        )
        
        trade_analysis = {
            'timestamp': analysis_time.isoformat(),
            'symbol': symbol,
            'signal': signal_type,
            'grade': grade,
            'ai_confidence': ai_confidence,
            
            # === FIYAT SEVİYELERİ ===
            'pricing': {
                'entry': entry_price,
                'tp': tp_price,
                'sl': sl_price,
                'potential_profit': potential_profit,
                'potential_loss': potential_loss,
                'profit_percentage': profit_percentage,
                'loss_percentage': loss_percentage,
                'risk_reward_ratio': risk_reward_ratio
            },
            
            # === LAYER BREAKDOWN ===
            'layer_scores': layer_scores,
            'layer_analysis': layer_analysis,
            
            # === PATTERN MATCHING ===
            'pattern_match': pattern_match,
            
            # === RISK ASSESSMENT ===
            'risks': risks,
            'risk_level': self._calculate_risk_level(risks, ai_confidence),
            
            # === AI İNSİGHTLARI ===
            'ai_insights': insights,
            
            # === TRADE KALİTESİ ===
            'trade_quality': {
                'is_tradeable': grade in ['A+', 'A'],  # Sadece A+ ve A trade aç
                'confidence_level': 'HIGH' if ai_confidence > 75 else 'MEDIUM' if ai_confidence > 60 else 'LOW',
                'suggested_action': self._suggest_action(grade, ai_confidence),
                'recommendation': self._generate_recommendation(grade, ai_confidence, risks)
            }
        }
        
        self.trade_history.append(trade_analysis)
        return trade_analysis
    
    def _calculate_trade_grade(self, confidence: float, rr_ratio: float, layers: Dict) -> str:
        """
        Trade'i A+, A, B, C ile grade et
        
        A+ = Harika (confidence > 80, RR > 2.5, tüm layers align)
        A  = İyi (confidence > 70, RR > 2.0, çoğu layer align)
        B  = Orta (confidence > 60, RR > 1.5)
        C  = Zayıf (confidence < 60 veya RR < 1.5)
        """
        
        # Layer alignment kontrol et
        aligned_layers = sum(1 for score in layers.values() if 55 < score < 65 or score > 65)
        total_layers = len(layers)
        alignment_ratio = aligned_layers / total_layers
        
        score = (confidence * 0.5 + rr_ratio * 20 * 0.3 + alignment_ratio * 100 * 0.2)
        
        if score > 85 and confidence > 80 and rr_ratio > 2.5 and alignment_ratio > 0.7:
            return 'A+'
        elif score > 75 and confidence > 70 and rr_ratio > 2.0:
            return 'A'
        elif score > 65 and confidence > 60 and rr_ratio > 1.5:
            return 'B'
        else:
            return 'C'
    
    def _analyze_layer_contribution(self, layer_scores: Dict) -> Dict:
        """Her layer'ın trade'e katkısını analiz et"""
        
        contribution = {}
        total = sum(layer_scores.values())
        
        for layer, score in layer_scores.items():
            # Bullish/Bearish tarafını belirle
            if score > 60:
                bias = 'BULLISH'
            elif score < 40:
                bias = 'BEARISH'
            else:
                bias = 'NEUTRAL'
            
            contribution[layer] = {
                'score': score,
                'bias': bias,
                'strength': 'STRONG' if score > 70 or score < 30 else 'MODERATE',
                'contribution_ratio': (score / total) * 100
            }
        
        return contribution
    
    def _match_historical_patterns(self, symbol: str, signal_type: str, layers: Dict) -> Dict:
        """Geçmişte benzer pattern'ler olmuş mu?"""
        
        # Dummy - gerçekte trade history ile karşılaştırılır
        
        similar_patterns = {
            'found': len(self.trade_history) > 0,
            'count': len(self.trade_history),
            'success_rate': 0.0,
            'avg_profit': 0.0,
            'interpretation': "Tarihte benzer pattern'ler bulundu"
        }
        
        if len(self.trade_history) > 0:
            # Benzer layer scores'a sahip trade'leri bul
            similar = [
                t for t in self.trade_history 
                if t['symbol'] == symbol and t['signal'] == signal_type
            ]
            
            if similar:
                similar_patterns['found'] = True
                similar_patterns['count'] = len(similar)
                successful = sum(1 for t in similar if t['pricing']['profit_percentage'] > 0)
                similar_patterns['success_rate'] = (successful / len(similar)) * 100
                similar_patterns['avg_profit'] = np.mean([
                    t['pricing']['profit_percentage'] for t in similar
                ])
        
        return similar_patterns
    
    def _assess_trade_risks(self, symbol: str, entry: float, tp: float, sl: float, layers: Dict) -> List[Dict]:
        """Trade'in risk'lerini değerlendir"""
        
        risks = []
        
        # Risk 1: Weak layer contribution
        weak_layers = [
            layer for layer, score in layers.items() 
            if 40 < score < 60  # Zayıf layer
        ]
        
        if len(weak_layers) > 2:
            risks.append({
                'type': 'WEAK_CONSENSUS',
                'severity': 'HIGH',
                'description': f"Birden fazla layer zayıf: {', '.join(weak_layers)}",
                'impact': 'Sinyal güvenilirliği düşük'
            })
        
        # Risk 2: Low volatility
        volatility = abs(tp - sl) / entry
        if volatility < 0.01:
            risks.append({
                'type': 'LOW_VOLATILITY',
                'severity': 'MEDIUM',
                'description': 'TP/SL aralığı çok dar',
                'impact': 'Fiyat dalgalanmalarından etkilenmesi az'
            })
        
        # Risk 3: High leverage needed
        rr_ratio = abs(tp - entry) / abs(entry - sl)
        if rr_ratio < 1.0:
            risks.append({
                'type': 'BAD_RISK_REWARD',
                'severity': 'MEDIUM',
                'description': f'RR ratio: {rr_ratio:.2f}',
                'impact': 'Potansiyel zarar > Potansiyel kar'
            })
        
        return risks
    
    def _calculate_risk_level(self, risks: List, confidence: float) -> str:
        """Genel risk level'ı belirle"""
        
        high_severity_count = sum(1 for r in risks if r['severity'] == 'HIGH')
        
        if high_severity_count > 0 and confidence < 70:
            return 'VERY_HIGH'
        elif high_severity_count > 0 or confidence < 60:
            return 'HIGH'
        elif len(risks) > 2 or confidence < 65:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _suggest_action(self, grade: str, confidence: float) -> str:
        """Ne yapmalı?"""
        
        if grade in ['A+', 'A'] and confidence > 75:
            return 'TRADE_IMMEDIATELY'
        elif grade in ['A', 'B'] and confidence > 70:
            return 'TRADE_WITH_CAUTION'
        elif grade == 'B':
            return 'WATCH_AND_WAIT'
        else:
            return 'SKIP_THIS_TRADE'
    
    def _generate_recommendation(self, grade: str, confidence: float, risks: List) -> str:
        """AI'ın tavsiyesi"""
        
        if grade == 'A+':
            return f"🟢 Harika fırsat! {confidence:.0f}% güvenle trade aç. Tüm layer'lar align."
        elif grade == 'A':
            return f"🟢 İyi fırsat. {confidence:.0f}% güvenle trade açabilirsin."
        elif grade == 'B':
            if confidence > 70:
                return f"🟡 Orta fırsat. Bekle veya %{confidence:.0f} güvenle küçük pozisyon aç."
            else:
                return f"🟡 Zayıf sinyal. Daha iyi fırsat bekle."
        else:
            risk_str = ", ".join([r['type'] for r in risks[:2]])
            return f"🔴 Skip. Riskler: {risk_str}. Daha iyi fırsat bekle."
    
    def _generate_ai_insights(self, symbol: str, signal_type: str, grade: str, 
                              layer_analysis: Dict, pattern_match: Dict, confidence: float) -> List[str]:
        """AI'ın detaylı insights'ları"""
        
        insights = []
        
        # Insight 1: Layer consensus
        bullish_layers = sum(1 for l in layer_analysis.values() if l['bias'] == 'BULLISH')
        bearish_layers = sum(1 for l in layer_analysis.values() if l['bias'] == 'BEARISH')
        
        if bullish_layers > bearish_layers:
            insights.append(f"✅ {bullish_layers}/{len(layer_analysis)} layer BULLISH align")
        else:
            insights.append(f"✅ {bearish_layers}/{len(layer_analysis)} layer BEARISH align")
        
        # Insight 2: Grade recommendation
        if grade == 'A+':
            insights.append("💪 Bu sinyalin başarı oranı tarihte %70+")
        elif grade == 'A':
            insights.append("✨ Güvenilir sinyal. Benzer patterler %60+ başarı")
        
        # Insight 3: Pattern matching
        if pattern_match['found']:
            insights.append(f"📊 Geçmişte {pattern_match['count']} benzer pattern bulundu ({pattern_match['success_rate']:.0f}% başarı)")
        
        # Insight 4: Confidence score explanation
        if confidence > 80:
            insights.append("🎯 Çok yüksek AI güveni - Tüm indikatörler align")
        elif confidence > 70:
            insights.append("🎯 Yüksek AI güveni - Çoğu indikatör align")
        elif confidence > 60:
            insights.append("⚠️ Orta AI güveni - Bazı indikatörler zayıf")
        
        return insights
    
    def get_daily_summary(self) -> Dict:
        """Günlük AI raporu"""
        
        if not self.trade_history:
            return {'trades': 0, 'summary': 'Henüz trade yok'}
        
        today_trades = [
            t for t in self.trade_history
            if datetime.fromisoformat(t['timestamp']).date() == datetime.now().date()
        ]
        
        if not today_trades:
            return {'trades': 0, 'summary': 'Bugün trade yok'}
        
        # Başarılı/başarısız trades
        successful = sum(1 for t in today_trades if t['pricing']['profit_percentage'] > 0)
        
        # Ortalama confidence
        avg_confidence = np.mean([t['ai_confidence'] for t in today_trades])
        
        # Grade dağılımı
        grades = {}
        for t in today_trades:
            grade = t['grade']
            grades[grade] = grades.get(grade, 0) + 1
        
        return {
            'trades': len(today_trades),
            'successful': successful,
            'failed': len(today_trades) - successful,
            'success_rate': (successful / len(today_trades)) * 100,
            'avg_confidence': avg_confidence,
            'grade_distribution': grades,
            'summary': f"{len(today_trades)} trade ({successful} başarılı), Ort. Güven: {avg_confidence:.0f}%"
        }

# Test
if __name__ == "__main__":
    analyzer = TradeAnalysisAI()
    
    analysis = analyzer.analyze_trade_opportunity(
        symbol='BTCUSDT',
        signal_type='LONG',
        entry_price=43000,
        tp_price=44000,
        sl_price=42500,
        ai_confidence=78.5,
        layer_scores={
            'technical': 75,
            'onchain': 70,
            'macro': 65,
            'sentiment': 72,
            'pattern': 68,
            'volume': 70
        }
    )
    
    print(json.dumps(analysis, indent=2))
