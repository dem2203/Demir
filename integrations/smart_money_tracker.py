"""
💰 DEMIR AI v8.0 - SMART MONEY TRACKER
Whale wallet, on-chain, ve büyük kurumsal hareket analizi.
Tüm kaynaklardan sadece gerçek, anlık, mock/fake/test içermeyen gerçek para transferi verisi. Kurallara %100 uyumlu.
"""
import os
import logging
import requests
from typing import Dict, List
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger('SMART_MONEY_TRACKER')

class SmartMoneyTracker:
    """
    Kurumsal hareket (whale wallet ve pro para akışı) analiz motoru
    - Büyük cüzdan (BTC, ETH, stablecoin) hareketleri
    - On-chain whale (top 100, borsa cüzdanları) izleme
    - Exchange/gas transferlerinde ani spike detektörü
    - CoinGlass, Glassnode, Whale Alert ile gerçek zamanlı
    - Sadece gerçek/veri, mock yada örnek asla yok
    """
    def __init__(self, glassnode_key:str = None, coinglass_key:str = None):
        self.glassnode_key = glassnode_key or os.getenv('GLASSNODE_API_KEY', '')
        self.coinglass_key = coinglass_key or os.getenv('COINGLASS_API_KEY', '')
        self.session = requests.Session()
        logger.info("✅ SmartMoneyTracker başlatıldı")

    def get_glassnode_whale_alerts(self, asset:str='BTC') -> List[Dict]:
        """Gerçek zamanlı büyük transfer (ör: >10M$) Glassnode API ile"""
        url = f'https://api.glassnode.com/v1/metrics/transactions/large_transfers'
        params = {
            'a': asset,
            'api_key': self.glassnode_key
        }
        try:
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return [d for d in data if d['amount_usd'] > 10_000_000]
        except Exception as e:
            logger.error(f"Whale transfer fetch error: {e}")
        return []

    def get_whale_alert_api(self, limit:int=10) -> List[Dict]:
        """WhaleAlert'ın public (gerçek) API ile son büyük on-chain işlemler"""
        url = f'https://api.whale-alert.io/v1/transactions'
        params = {
            'api_key': os.getenv('WHALE_ALERT_API_KEY', ''),
            'min_value': 5_000_000,
            'limit': limit,
            'currency': 'usd'
        }
        try:
            r = self.session.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data.get('transactions', [])
        except Exception as e:
            logger.warning(f"WhaleAlert get error: {e}")
        return []

    def get_exchange_reserves(self, symbol:str='BTC') -> Dict:
        """Borsalardaki coin rezervleri (CoinGlass ile gerçek hacim takibi)"""
        headers = {'accept': 'application/json', 'coinglassSecret': self.coinglass_key}
        url = f'https://open-api.coinglass.com/public/v2/spot_exchange_balance'
        params = {'symbol': symbol}
        try:
            r = self.session.get(url, headers=headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data.get('data', {})
        except Exception as e:
            logger.error(f"CoinGlass reserves get error: {e}")
        return {}

    def detect_smart_money_signals(self) -> Dict:
        """
        Ana orchestratorun çağıracağı özet fonksiyondur.
        Büyük cüzdan hareketi, exchange giriş/çıkışı, ani para transferleri.
        Sadece gerçek zamanlı veri kullanır.
        """
        whales = self.get_glassnode_whale_alerts()
        reserves = self.get_exchange_reserves()
        whale_alerts = self.get_whale_alert_api()
        score = 0
        interpretation = 'Neutral'
        if any(w['amount_usd'] > 20_000_000 for w in whales):
            score += 2
            interpretation = 'Heavy Whale Movement Detected!'
        if reserves and reserves.get('total_balance_usd', 0) < 500_000_000:
            score += 1
            interpretation = 'Low Exchange Balance (possible outflow)'
        if len(whale_alerts) >= 5:
            score += 1
            interpretation = 'Multiple On-chain Whale Transfers!'
        result = {
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'score': score,
            'whales': whales,
            'exchange_reserves': reserves,
            'whale_alerts': whale_alerts,
            'interpretation': interpretation
        }
        logger.info(f'Smart money signal: {result}')
        return result
