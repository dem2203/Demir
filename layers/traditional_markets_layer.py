import os
import requests
import yfinance as yf

class TraditionalMarketsLayer:
    def __init__(self):
        self.twelve_data_apikey = os.getenv('TWELVEDATAAPIKEY')
        self.alpha_vantage_apikey = os.getenv('ALPHAVANTAGEAPIKEY')

    def get_traditional_markets_signal(self, symbol=None):
        symbol = symbol or 'SPY'
        # Önce Twelve Data API
        try:
            url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={self.twelve_data_apikey}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'values' not in data or not data['values']:
                raise ValueError('No price data from Twelve Data')
            close_prices = [float(item['close']) for item in data['values']]
            last_close = close_prices[0]
            prev_close = close_prices[1] if len(close_prices) > 1 else last_close
            change = (last_close - prev_close) / prev_close
            score = max(0, min(100, 50 + change * 200))
            signal = 'BULLISH' if score > 55 else 'BEARISH' if score < 45 else 'NEUTRAL'
            return {
                'available': True,
                'score': float(score),
                'signal': signal,
                'error': None
            }
        except Exception as e:
            # Fallback Yahoo Finance
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period='2d')
                if df.empty:
                    raise ValueError('No data from Yahoo Finance')
                last_close = df['Close'][-1]
                prev_close = df['Close'][-2]
                change = (last_close - prev_close) / prev_close
                score = max(0, min(100, 50 + change * 200))
                signal = 'BULLISH' if score > 55 else 'BEARISH' if score < 45 else 'NEUTRAL'
                return {
                    'available': True,
                    'score': float(score),
                    'signal': signal,
                    'error': None
                }
            except Exception as yfe:
                return {
                    'available': False,
                    'score': 50.0,
                    'signal': 'NEUTRAL',
                    'error': f'All APIs failed: {str(e)} | Yahoo error: {str(yfe)}'
                }
