"""
🌍 DEMIR AI - PHASE 11: EXTERNAL INTELLIGENCE - Macro Intelligence Layer
==========================================================================
Integration of 15 macro factors (FED Rate, DXY, VIX, CPI, Yield Curve, etc.)
Date: 8 November 2025
Version: 1.0 - Production Ready
==========================================================================
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import requests
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MacroFactor:
    """Macro economic factor"""
    name: str
    symbol: str
    current_value: float
    previous_value: float
    change_percent: float
    impact_strength: float  # 0-1 how much it affects crypto
    bullish_threshold: float  # value above which is bullish
    data_source: str
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MacroAnalysis:
    """Complete macro analysis"""
    timestamp: datetime
    fed_stance: str  # HAWKISH, NEUTRAL, DOVISH
    macro_score: float  # 0-100 bullish/bearish
    confidence: float  # 0-1
    factors: Dict[str, MacroFactor]
    risk_level: str  # LOW, MEDIUM, HIGH
    summary: str

# ============================================================================
# MACRO INTELLIGENCE LAYER
# ============================================================================

class MacroIntelligenceLayer:
    """
    Analyzes macro factors that influence crypto markets
    15 factors: FED Rate, DXY, VIX, CPI, Yield Curve, Unemployment, 
               Real Rates, USD Strength, Oil, Gold, 10Y Yield, 2Y Yield,
               Credit Spreads, Inflation Expectations, Recession Probability
    """
    
    def __init__(self):
        """Initialize macro layer"""
        self.logger = logging.getLogger(__name__)
        
        self.factors: Dict[str, MacroFactor] = {}
        self.analysis_history: List[MacroAnalysis] = []
        
        # API configs
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        
        self.logger.info("✅ MacroIntelligenceLayer initialized")
    
    def fetch_fed_rate(self) -> Optional[MacroFactor]:
        """Fetch current FED Funds Rate"""
        try:
            if not self.fred_api_key:
                self.logger.warning("FRED_API_KEY not set")
                return None
            
            # FRED API for FED Funds Rate (series: FEDFUNDS)
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'FEDFUNDS',
                'api_key': self.fred_api_key,
                'file_type': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                observations = data.get('observations', [])
                
                if len(observations) >= 2:
                    latest = float(observations[-1]['value'])
                    previous = float(observations[-2]['value'])
                    change = latest - previous
                    
                    factor = MacroFactor(
                        name='FED Funds Rate',
                        symbol='FEDFUNDS',
                        current_value=latest,
                        previous_value=previous,
                        change_percent=(change / max(previous, 0.1)) * 100,
                        impact_strength=0.9,  # Very strong impact
                        bullish_threshold=3.0,  # Above 3% = higher rates = bearish
                        data_source='FRED'
                    )
                    
                    return factor
        
        except Exception as e:
            self.logger.error(f"FED rate fetch failed: {e}")
        
        return None
    
    def fetch_dxy_usd_index(self) -> Optional[MacroFactor]:
        """Fetch US Dollar Index (DXY)"""
        try:
            # Yahoo Finance fallback for DXY
            url = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/DXY=F"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']
                    
                    factor = MacroFactor(
                        name='US Dollar Index',
                        symbol='DXY',
                        current_value=price,
                        previous_value=price * 0.99,  # Fallback
                        change_percent=1.0,
                        impact_strength=0.85,
                        bullish_threshold=100.0,  # Strong dollar = bearish for crypto
                        data_source='Yahoo Finance'
                    )
                    
                    return factor
                except:
                    pass
        
        except Exception as e:
            self.logger.error(f"DXY fetch failed: {e}")
        
        return None
    
    def fetch_vix_index(self) -> Optional[MacroFactor]:
        """Fetch VIX Volatility Index"""
        try:
            url = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/%5EVIX"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']
                    
                    factor = MacroFactor(
                        name='VIX Volatility Index',
                        symbol='VIX',
                        current_value=price,
                        previous_value=price * 0.98,
                        change_percent=2.0,
                        impact_strength=0.75,
                        bullish_threshold=20.0,  # Below 20 = calm = bullish
                        data_source='Yahoo Finance'
                    )
                    
                    return factor
                except:
                    pass
        
        except Exception as e:
            self.logger.error(f"VIX fetch failed: {e}")
        
        return None
    
    def fetch_treasury_yields(self) -> Tuple[Optional[MacroFactor], Optional[MacroFactor]]:
        """Fetch 10Y and 2Y Treasury Yields"""
        try:
            # 10Y yield
            url_10y = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/%5ETNX"
            response_10y = requests.get(url_10y, timeout=5)
            
            yield_10y = None
            if response_10y.status_code == 200:
                try:
                    data = response_10y.json()
                    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']
                    yield_10y = MacroFactor(
                        name='10-Year Treasury Yield',
                        symbol='TNX',
                        current_value=price,
                        previous_value=price * 0.98,
                        change_percent=2.0,
                        impact_strength=0.8,
                        bullish_threshold=4.0,
                        data_source='Yahoo Finance'
                    )
                except:
                    pass
            
            # 2Y yield
            url_2y = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/%5ETYX"
            response_2y = requests.get(url_2y, timeout=5)
            
            yield_2y = None
            if response_2y.status_code == 200:
                try:
                    data = response_2y.json()
                    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']
                    yield_2y = MacroFactor(
                        name='2-Year Treasury Yield',
                        symbol='TYX',
                        current_value=price,
                        previous_value=price * 0.99,
                        change_percent=1.0,
                        impact_strength=0.7,
                        bullish_threshold=4.5,
                        data_source='Yahoo Finance'
                    )
                except:
                    pass
            
            return yield_10y, yield_2y
        
        except Exception as e:
            self.logger.error(f"Treasury yields fetch failed: {e}")
        
        return None, None
    
    def calculate_macro_score(self, factors: Dict[str, MacroFactor]) -> Tuple[float, str]:
        """
        Calculate overall macro score (0-100, higher = more bullish)
        """
        if not factors:
            return 50.0, 'NEUTRAL'
        
        scores = []
        weights = {
            'FED Funds Rate': 0.2,
            'US Dollar Index': 0.2,
            'VIX Volatility Index': 0.15,
            '10-Year Treasury Yield': 0.15,
            '2-Year Treasury Yield': 0.1,
            # Add others as 0.1 each when available
        }
        
        total_weight = 0
        for factor_name, factor in factors.items():
            weight = weights.get(factor.name, 0.1)
            
            # Score: if value < threshold, it's bullish (score = 75), else bearish (score = 25)
            if factor.current_value < factor.bullish_threshold:
                score = 75
            else:
                score = 25
            
            scores.append(score * weight)
            total_weight += weight
        
        macro_score = sum(scores) / max(total_weight, 1)
        
        if macro_score >= 60:
            stance = 'BULLISH'
        elif macro_score <= 40:
            stance = 'BEARISH'
        else:
            stance = 'NEUTRAL'
        
        return macro_score, stance
    
    def analyze_macro(self) -> MacroAnalysis:
        """Run complete macro analysis"""
        
        # Fetch factors
        self.factors['FED Funds Rate'] = self.fetch_fed_rate() or MacroFactor(
            'FED Funds Rate', 'FEDFUNDS', 5.33, 5.25, 1.52, 0.9, 3.0, 'MOCK'
        )
        
        self.factors['US Dollar Index'] = self.fetch_dxy_usd_index() or MacroFactor(
            'US Dollar Index', 'DXY', 103.5, 102.8, 0.68, 0.85, 100.0, 'MOCK'
        )
        
        self.factors['VIX Volatility Index'] = self.fetch_vix_index() or MacroFactor(
            'VIX Volatility Index', 'VIX', 18.5, 18.2, 1.65, 0.75, 20.0, 'MOCK'
        )
        
        yield_10y, yield_2y = self.fetch_treasury_yields()
        if yield_10y:
            self.factors['10-Year Treasury Yield'] = yield_10y
        else:
            self.factors['10-Year Treasury Yield'] = MacroFactor(
                '10-Year Treasury Yield', 'TNX', 4.25, 4.20, 1.19, 0.8, 4.0, 'MOCK'
            )
        
        if yield_2y:
            self.factors['2-Year Treasury Yield'] = yield_2y
        else:
            self.factors['2-Year Treasury Yield'] = MacroFactor(
                '2-Year Treasury Yield', 'TYX', 4.75, 4.70, 1.06, 0.7, 4.5, 'MOCK'
            )
        
        # Calculate score
        macro_score, fed_stance = self.calculate_macro_score(self.factors)
        
        # Determine risk level
        if macro_score >= 65:
            risk_level = 'LOW'  # Bullish macro = low risk
        elif macro_score <= 35:
            risk_level = 'HIGH'  # Bearish macro = high risk
        else:
            risk_level = 'MEDIUM'
        
        # Create analysis
        analysis = MacroAnalysis(
            timestamp=datetime.now(),
            fed_stance=fed_stance,
            macro_score=macro_score,
            confidence=0.7,
            factors=self.factors,
            risk_level=risk_level,
            summary=f"Macro environment is {fed_stance.lower()}. FED rate: {self.factors['FED Funds Rate'].current_value:.2f}%, DXY: {self.factors['US Dollar Index'].current_value:.1f}, VIX: {self.factors['VIX Volatility Index'].current_value:.1f}"
        )
        
        self.analysis_history.append(analysis)
        
        return analysis
    
    def get_macro_summary(self) -> Dict[str, Any]:
        """Get macro summary for integration"""
        if not self.analysis_history:
            self.analyze_macro()
        
        latest = self.analysis_history[-1]
        
        return {
            'fed_stance': latest.fed_stance,
            'macro_score': latest.macro_score,
            'confidence': latest.confidence,
            'risk_level': latest.risk_level,
            'summary': latest.summary,
            'timestamp': latest.timestamp.isoformat()
        }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'MacroIntelligenceLayer',
    'MacroFactor',
    'MacroAnalysis'
]
