import requests

class BitcoinDominanceLayer:
    def analyze(self):
        try:
            url = "https://api.coingecko.com/api/v3/global"
            data = requests.get(url).json()
            btc_dom = data['data']['btc_market_cap_percentage']
            return {'btc_dominance': btc_dom, 'trend': 'up' if btc_dom > 45 else 'down'}
        except:
            return {'error': 'API error'}

btc_dominance = BitcoinDominanceLayer()
