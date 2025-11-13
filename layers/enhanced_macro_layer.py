"""
ENHANCED MACRO LAYER - v2.0
Makroekonomik göstergeler analizi
⚠️ REAL data only - gerçek ekonomik veriler

Bu layer şunu yapar:
1. Fed kararlarını analiz et
2. Enflasyon, GDP, Faiz oranlarını kontrol et
3. Ekonomik ortamın Crypto'ya etkisini ölç
"""

from utils.base_layer import BaseLayer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnhancedMacroLayer(BaseLayer):
    """Makroekonomik Analiz Layer"""
    
    def __init__(self):
        """Initialize"""
        super().__init__('EnhancedMacro_Layer')
        self.macro_history = []
    
    async def get_signal(self, macro_data):
        """Get macro economic signal
        
        Args:
            macro_data: Dict with:
            {
                'fed_decision': 'HAWKISH' veya 'DOVISH' veya None,
                'inflation': 3.5,              # Current inflation rate (%)
                'target_inflation': 2.0,       # Fed's target inflation
                'interest_rate': 5.25,         # Current Fed rate (%)
                'gdp_growth': 2.1,             # GDP growth rate (%)
                'unemployment': 3.8,           # Unemployment rate (%)
                'fomc_date': '2025-12-18'      # Next FOMC meeting
            }
        
        Returns:
            Macro signal with score and recommendation
        """
        return await self.execute_with_retry(
            self._analyze_macro,
            macro_data
        )
    
    async def _analyze_macro(self, macro_data):
        """Analyze macro indicators - GERÇEK VERİ İLE"""
        
        if not macro_data:
            raise ValueError("No macro data provided")
        
        try:
            # Extract REAL macro data
            fed_decision = macro_data.get('fed_decision')  # HAWKISH/DOVISH/None
            inflation = macro_data.get('inflation', 0)     # % rate
            target_inf = macro_data.get('target_inflation', 2.0)
            int_rate = macro_data.get('interest_rate', 0)  # %
            gdp = macro_data.get('gdp_growth', 0)          # %
            unemployment = macro_data.get('unemployment', 0) # %
            
            # Validate
            if inflation < 0 or int_rate < 0:
                raise ValueError("Invalid macro data")
            
            # SCORE CALCULATION
            # =================
            
            score = 50.0  # Neutral start
            reasons = []
            
            # 1. FED DECISION
            # ===============
            # HAWKISH = More hikes = Negative for crypto = -15 points
            # DOVISH = Rate cuts = Positive for crypto = +15 points
            
            if fed_decision == 'HAWKISH':
                score -= 15.0
                reasons.append("Fed hawkish stance (rate hikes expected)")
            elif fed_decision == 'DOVISH':
                score += 15.0
                reasons.append("Fed dovish stance (potential rate cuts)")
            
            # 2. INFLATION ANALYSIS
            # =====================
            # Yüksek enflasyon = Fed sıkı tutum = Negative
            # Düşük enflasyon = Fed rahat = Positive
            
            inflation_gap = inflation - target_inf
            
            if inflation_gap > 2.0:
                # Significant above target
                score -= 10.0
                reasons.append(f"High inflation above target: {inflation}% vs {target_inf}%")
            elif inflation_gap < -1.0:
                # Significant below target
                score += 10.0
                reasons.append(f"Low inflation below target: {inflation}% vs {target_inf}%")
            else:
                reasons.append(f"Inflation near target: {inflation}%")
            
            # 3. INTEREST RATE ENVIRONMENT
            # =============================
            # Yüksek rates = Sabit getiri alanları cazip = Crypto riskli
            # Düşük rates = Likidite çoğu = Crypto cazip
            
            if int_rate > 5.0:
                # High rates
                score -= 8.0
                reasons.append(f"High interest rates: {int_rate}%")
            elif int_rate < 2.0:
                # Low rates
                score += 8.0
                reasons.append(f"Low interest rates: {int_rate}%")
            
            # 4. GDP GROWTH
            # =============
            # Güçlü büyüme = İyi ekonomi = Positive for risk assets
            # Zayıf büyüme = Durgunluk riski = Negative
            
            if gdp > 3.0:
                # Strong growth
                score += 5.0
                reasons.append(f"Strong GDP growth: {gdp}%")
            elif gdp < 0.5:
                # Weak growth / recession
                score -= 8.0
                reasons.append(f"Weak GDP growth: {gdp}% (recession risk)")
            
            # 5. UNEMPLOYMENT
            # ===============
            # Düşük işsizlik = Güçlü labor market = Positive
            # Yüksek işsizlik = Zayıf labor market = Negative
            
            if unemployment < 4.0:
                # Strong labor market
                score += 3.0
                reasons.append(f"Low unemployment: {unemployment}%")
            elif unemployment > 5.0:
                # Weak labor market
                score -= 5.0
                reasons.append(f"High unemployment: {unemployment}%")
            
            # Clamp score to 0-100
            score = max(0, min(100, score))
            
            # FINAL SIGNAL
            # ============
            
            if score >= 65:
                signal = 'BULLISH'
            elif score <= 35:
                signal = 'BEARISH'
            else:
                signal = 'NEUTRAL'
            
            # Store history
            self.macro_history.append({
                'timestamp': datetime.now(),
                'signal': signal,
                'score': score,
                'inflation': inflation,
                'rate': int_rate,
                'gdp': gdp
            })
            
            # Limit history
            if len(self.macro_history) > 500:
                self.macro_history = self.macro_history[-500:]
            
            return {
                'signal': signal,
                'score': score,
                'reasons': reasons,
                'economic_outlook': self._get_outlook(score),
                'inflation': float(inflation),
                'inflation_target': float(target_inf),
                'inflation_gap': float(inflation_gap),
                'interest_rate': float(int_rate),
                'gdp_growth': float(gdp),
                'unemployment': float(unemployment),
                'fed_decision': fed_decision,
                'timestamp': datetime.now().isoformat(),
                'valid': True
            }
        
        except Exception as e:
            logger.error(f"Macro analysis error: {e}")
            raise ValueError(f"Macro error: {e}")
    
    @staticmethod
    def _get_outlook(score):
        """Get economic outlook based on score"""
        
        if score >= 75:
            return "VERY_BULLISH - Strong economic environment"
        elif score >= 65:
            return "BULLISH - Positive economic conditions"
        elif score >= 50:
            return "NEUTRAL - Mixed signals"
        elif score >= 35:
            return "BEARISH - Challenging environment"
        else:
            return "VERY_BEARISH - Harsh economic conditions"
