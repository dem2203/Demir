class AltcoinSeasonLayer:
    def analyze(self):
        try:
            # Bitcoin dominance < 50% = Altseason
            btc_dom = btc_dominance.analyze()['btc_dominance']
            season = 'altseason' if btc_dom < 50 else 'bitcoin_season'
            return {'season': season, 'dominance': btc_dom}
        except:
            return {'season': 'unknown'}

altcoin_season = AltcoinSeasonLayer()
