# ============================================================================
# DEMIR AI TRADING BOT - Enhanced Macro Correlation Layer
# ============================================================================
# Phase 6.1: Traditional Markets Correlation (SPX, NASDAQ, DXY)
# Date: 4 Kasim 2025, 22:45 CET
# Version: 2.0 - ENHANCED WITH REAL-TIME DATA
#
# FEATURES:
# - SPX (S&P 500) correlation
# - NASDAQ correlation
# - DXY (Dollar Index) inverse correlation
# - Real-time market sentiment
# - Cross-market analysis
# - Risk-on/Risk-off detection
# ============================================================================

import requests
import numpy as np
from typing import Dict, Optional
from datetime import datetime

class EnhancedMacroLayer:
    """
    Enhanced macro market correlation analysis
    """

    def __init__(self):
        """Initialize macro layer"""
        self.alpha_vantage_key = None
        print("Enhanced Macro Layer initialized")

    def get_spx_data(self) -> Optional[Dict]:
        """Get S&P 500 (SPX) data"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
            params = {'interval': '1d', 'range': '5d'}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'chart' not in data or 'result' not in data['chart']:
                return None

            result = data['chart']['result'][0]
            quote = result['indicators']['quote'][0]
            closes = [c for c in quote['close'] if c is not None]
            
            if len(closes) < 2:
                return None

            current_price = closes[-1]
            prev_price = closes[-2]
            change = (current_price - prev_price) / prev_price
            trend = (closes[-1] - closes[0]) / closes[0]

            return {
                'price': current_price,
                'change_1d': change,
                'trend_5d': trend,
                'sentiment': 'BULLISH' if change > 0.002 else 'BEARISH' if change < -0.002 else 'NEUTRAL'
            }
        except Exception as e:
            print(f"SPX data error: {e}")
            return None

    def get_nasdaq_data(self) -> Optional[Dict]:
        """Get NASDAQ data"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC"
            params = {'interval': '1d', 'range': '5d'}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'chart' not in data or 'result' not in data['chart']:
                return None

            result = data['chart']['result'][0]
            quote = result['indicators']['quote'][0]
            closes = [c for c in quote['close'] if c is not None]
            
            if len(closes) < 2:
                return None

            current_price = closes[-1]
            prev_price = closes[-2]
            change = (current_price - prev_price) / prev_price
            trend = (closes[-1] - closes[0]) / closes[0]

            return {
                'price': current_price,
                'change_1d': change,
                'trend_5d': trend,
                'sentiment': 'BULLISH' if change > 0.002 else 'BEARISH' if change < -0.002 else 'NEUTRAL'
            }
        except Exception as e:
            print(f"NASDAQ data error: {e}")
            return None

    def get_dxy_data(self) -> Optional[Dict]:
        """Get DXY (Dollar Index) data - INVERSE correlation"""
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
            params = {'interval': '1d', 'range': '5d'}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'chart' not in data or 'result' not in data['chart']:
                return None

            result = data['chart']['result'][0]
            quote = result['indicators']['quote'][0]
            closes = [c for c in quote['close'] if c is not None]
            
            if len(closes) < 2:
                return None

            current_price = closes[-1]
            prev_price = closes[-2]
            change = (current_price - prev_price) / prev_price
            trend = (closes[-1] - closes[0]) / closes[0]

            return {
                'price': current_price,
                'change_1d': change,
                'trend_5d': trend,
                'sentiment': 'BEARISH' if change > 0.002 else 'BULLISH' if change < -0.002 else 'NEUTRAL'
            }
        except Exception as e:
            print(f"DXY data error: {e}")
            return None

    def analyze_risk_sentiment(self, spx_ Dict, nasdaq_ Dict, dxy_ Dict) -> str:
        """Analyze overall market risk sentiment"""
        if not all([spx_data, nasdaq_data, dxy_data]):
            return 'UNKNOWN'

        bullish_count = sum([
            spx_data['sentiment'] == 'BULLISH',
            nasdaq_data['sentiment'] == 'BULLISH',
            dxy_data['sentiment'] == 'BULLISH'
        ])

        if bullish_count >= 2:
            return 'RISK_ON'
        elif bullish_count == 0:
            return 'RISK_OFF'
        else:
            return 'MIXED'

    def calculate_macro_score(self) -> Dict:
        """Calculate comprehensive macro score"""
        print("\n" + "="*80)
        print("ENHANCED MACRO ANALYSIS")
        print("="*80 + "\n")

        spx = self.get_spx_data()
        nasdaq = self.get_nasdaq_data()
        dxy = self.get_dxy_data()

        available_data = sum([spx is not None, nasdaq is not None, dxy is not None])
        if available_data == 0:
            print("No macro data available")
            return {'score': 50, 'signal': 'NEUTRAL', 'confidence': 0}

        spx_score = self._sentiment_to_score(spx['sentiment']) if spx else 50
        nasdaq_score = self._sentiment_to_score(nasdaq['sentiment']) if nasdaq else 50
        dxy_score = self._sentiment_to_score(dxy['sentiment']) if dxy else 50

        final_score = (spx_score * 0.4 + nasdaq_score * 0.4 + dxy_score * 0.2)
        risk_sentiment = self.analyze_risk_sentiment(spx, nasdaq, dxy)
        confidence = available_data / 3.0

        if spx:
            print(f"S&P 500: ${spx['price']:.2f} ({spx['change_1d']:+.2%}) - {spx['sentiment']}")
        if nasdaq:
            print(f"NASDAQ: ${nasdaq['price']:.2f} ({nasdaq['change_1d']:+.2%}) - {nasdaq['sentiment']}")
        if dxy:
            print(f"DXY: ${dxy['price']:.2f} ({dxy['change_1d']:+.2%}) - {dxy['sentiment']} for crypto")

        print(f"\nRisk Sentiment: {risk_sentiment}")
        print(f"Macro Score: {final_score:.1f}/100")
        print(f"Confidence: {confidence:.1%}")
        print("="*80 + "\n")

        return {
            'score': final_score,
            'signal': self._score_to_signal(final_score),
            'confidence': confidence,
            'risk_sentiment': risk_sentiment,
            'spx': spx,
            'nasdaq': nasdaq,
            'dxy': dxy,
            'timestamp': datetime.now().isoformat()
        }

    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment to 0-100 score"""
        mapping = {'BULLISH': 70, 'NEUTRAL': 50, 'BEARISH': 30}
        return mapping.get(sentiment, 50)

    def _score_to_signal(self, score: float) -> str:
        """Convert score to signal"""
        if score >= 60:
            return 'LONG'
        elif score <= 40:
            return 'SHORT'
        else:
            return 'NEUTRAL'

def get_macro_signal() -> Dict:
    """Get macro correlation signal"""
    layer = EnhancedMacroLayer()
    return layer.calculate_macro_score()

def analyze_traditional_markets() -> Dict:
    """Alias for get_macro_signal"""
    return get_macro_signal()

if __name__ == "__main__":
    print("="*80)
    print("ENHANCED MACRO LAYER TEST")
    print("="*80)
    result = get_macro_signal()
    if result['confidence'] > 0:
        print(f"\nAnalysis complete!")
        print(f"Signal: {result['signal']}")
        print(f"Score: {result['score']:.1f}/100")
        print(f"Risk: {result['risk_sentiment']}")
    else:
        print("\nNo data available")
