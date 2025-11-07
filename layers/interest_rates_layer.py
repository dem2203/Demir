import os
import requests
from datetime import datetime, timedelta
import yfinance as yf

class InterestRatesLayer:
    """
    Interest Rates Layer - Analyzes US interest rates impact on crypto
    Uses 10-year Treasury yield (^TNX) as primary indicator
    """
    
    def __init__(self):
        self.symbols = {
            'US10Y': '^TNX',      # US 10-year Treasury yield
            'US2Y': '^TYX',       # US 2-year Treasury yield
            'DXY': 'DX-Y.NYB'     # Dollar Index (inverse correlation)
        }
        
        print("✅ Interest Rates Layer initialized")

    def fetch_rate_data(self, symbol, days=30):
        """Fetch interest rate or related data using yfinance"""
        debug = {}
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                debug['error'] = f"Empty history for {symbol}"
                return None, debug
            
            df = {
                'timestamp': hist.index.astype(int) // 10**9,
                'close': hist['Close'].values,
                'volume': hist['Volume'].values if 'Volume' in hist.columns else None
            }
            
            debug['info'] = f"Fetched {len(df['close'])} bars for {symbol}"
            return df, debug
            
        except Exception as e:
            debug['exception'] = str(e)
            return None, debug

    def analyze_rates_impact(self, symbol='BTCUSDT', days=30):
        """
        Analyze how interest rates affect crypto
        
        Key relationships:
        - Rising rates → Bearish for crypto (flight to safety)
        - Falling rates → Bullish for crypto (risk-on)
        - High real rates → Negative for crypto
        - Low/negative rates → Positive for crypto
        """
        print(f"\n{'='*60}\n📊 Interest Rates Impact Analysis\n{'='*60}\n")
        
        rates_data = {}
        changes = {}
        
        # Fetch 10-year Treasury yield (most important)
        us10y_data, us10y_debug = self.fetch_rate_data(self.symbols['US10Y'], days)
        
        if us10y_data is not None:
            us10y_close = us10y_data['close']
            us10y_change = ((us10y_close[-1] / us10y_close[0]) - 1) * 100
            rates_data['US10Y'] = us10y_close[-1]
            changes['US10Y'] = us10y_change
            print(f"✅ 10Y Yield: {us10y_close[-1]:.2f}% (Change: {us10y_change:+.2f}%)")
        else:
            rates_data['US10Y'] = 3.5  # Default assumption
            changes['US10Y'] = 0.0
            print(f"⚠️ 10Y Yield: Using default 3.5%")
        
        # Fetch 2-year Treasury yield
        us2y_data, us2y_debug = self.fetch_rate_data(self.symbols['US2Y'], days)
        
        if us2y_data is not None:
            us2y_close = us2y_data['close']
            us2y_change = ((us2y_close[-1] / us2y_close[0]) - 1) * 100
            rates_data['US2Y'] = us2y_close[-1]
            changes['US2Y'] = us2y_change
            print(f"✅ 2Y Yield: {us2y_close[-1]:.2f}% (Change: {us2y_change:+.2f}%)")
        else:
            rates_data['US2Y'] = 4.2  # Default assumption
            changes['US2Y'] = 0.0
            print(f"⚠️ 2Y Yield: Using default 4.2%")
        
        # Calculate yield curve slope
        yield_curve_slope = rates_data['US10Y'] - rates_data['US2Y']
        print(f"✅ Yield Curve Slope: {yield_curve_slope:+.2f}%")
        
        # ================================================
        # SCORING LOGIC
        # ================================================
        
        base_score = 50
        
        # Factor 1: Absolute 10Y level
        if rates_data['US10Y'] > 5.0:
            score_factor1 = 30  # Very high rates, bearish
        elif rates_data['US10Y'] > 4.0:
            score_factor1 = 40  # High rates, moderately bearish
        elif rates_data['US10Y'] > 3.0:
            score_factor1 = 50  # Moderate rates, neutral
        elif rates_data['US10Y'] > 2.0:
            score_factor1 = 60  # Low rates, moderately bullish
        else:
            score_factor1 = 70  # Very low rates, bullish
        
        # Factor 2: Rate change direction
        if changes['US10Y'] > 0.5:
            score_factor2 = 30  # Rates rising, bearish
        elif changes['US10Y'] > 0.1:
            score_factor2 = 40  # Rates slightly rising
        elif changes['US10Y'] < -0.5:
            score_factor2 = 70  # Rates falling, bullish
        elif changes['US10Y'] < -0.1:
            score_factor2 = 60  # Rates slightly falling
        else:
            score_factor2 = 50  # Rates stable
        
        # Factor 3: Yield curve inversion
        if yield_curve_slope < -0.5:
            curve_signal = "INVERTED_SEVERE"
            score_factor3 = 65  # Inversion signals recession, risk-off, but crypto can rally
        elif yield_curve_slope < 0:
            curve_signal = "SLIGHTLY_INVERTED"
            score_factor3 = 55
        elif yield_curve_slope > 1.0:
            curve_signal = "STEEP"
            score_factor3 = 45  # Steep curve, risk-off later
        else:
            curve_signal = "NORMAL"
            score_factor3 = 50
        
        # Weighted scoring
        total_score = (score_factor1 * 0.40 + score_factor2 * 0.35 + score_factor3 * 0.25)
        total_score = max(0, min(100, total_score))
        
        # ================================================
        # SIGNAL INTERPRETATION
        # ================================================
        
        if total_score >= 65:
            signal = "BULLISH"
            explanation = "Low/falling rates favor crypto (risk-on environment)"
        elif total_score >= 55:
            signal = "SLIGHTLY_BULLISH"
            explanation = "Moderately favorable rates for crypto"
        elif total_score >= 45:
            signal = "NEUTRAL"
            explanation = "Neutral rates impact on crypto"
        elif total_score >= 35:
            signal = "SLIGHTLY_BEARISH"
            explanation = "Rising rates create headwinds for crypto"
        else:
            signal = "BEARISH"
            explanation = "High/rising rates unfavorable for crypto (risk-off)"
        
        # Real rates approximation (using 2.5% inflation assumption)
        inflation_assumption = 2.5
        real_rate_10y = rates_data['US10Y'] - inflation_assumption
        
        return {
            'available': True,
            'total_score': round(total_score, 2),
            'signal': signal,
            'explanation': explanation,
            'rates': {
                'US10Y': round(rates_data['US10Y'], 2),
                'US2Y': round(rates_data['US2Y'], 2),
                'yield_curve_slope': round(yield_curve_slope, 2),
                'real_rate_10y': round(real_rate_10y, 2)
            },
            'changes': {
                'US10Y_change': round(changes['US10Y'], 2),
                'US2Y_change': round(changes['US2Y'], 2)
            },
            'curve_signal': curve_signal,
            'factor_scores': {
                'absolute_level': round(score_factor1, 2),
                'rate_change': round(score_factor2, 2),
                'yield_curve': round(score_factor3, 2)
            },
            'timestamp': datetime.now().isoformat(),
            'crypto_symbol': symbol,
            'analysis_period_days': days
        }

def get_interest_rates_signal(symbol='BTCUSDT'):
    """Wrapper function for ai_brain integration"""
    layer = InterestRatesLayer()
    return layer.analyze_rates_impact(symbol)

def analyze_interest_impact(symbol='BTCUSDT', days=30):
    """Analyze interest rates impact"""
    layer = InterestRatesLayer()
    return layer.analyze_rates_impact(symbol, days)

if __name__ == "__main__":
    print("📊 INTEREST RATES LAYER - TEST")
    print("=" * 70)
    
    layer = InterestRatesLayer()
    result = layer.analyze_rates_impact("BTCUSDT", 30)
    
    print("\n" + "=" * 70)
    print("📊 INTEREST RATES ANALYSIS:")
    print(f"   Score: {result['total_score']}/100")
    print(f"   Signal: {result['signal']}")
    print(f"   US 10Y: {result['rates']['US10Y']}%")
    print(f"   Yield Curve Slope: {result['rates']['yield_curve_slope']}%")
    print(f"   Real Rate (est): {result['rates']['real_rate_10y']}%")
    print(f"   Explanation: {result['explanation']}")
    print("=" * 70)
