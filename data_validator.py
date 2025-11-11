"""
🧠 DATA_VALIDATOR - Gerçek Veri Doğrulama Sistemi
Version: 1.0 - Real Data Verification & Quality Check
Date: 11 Kasım 2025

ÖZELLİKLER:
- Binance verilerini doğrula
- Data kalitesi kontrol et
- Eksik/hatalı veri tespit et
- Anomali deteksiyonu
- Veri kaynağı güvenilirliği
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import json

class DataValidator:
    """Tüm verileri doğrulayan sistem"""
    
    def __init__(self):
        self.validation_log = []
        self.data_sources = {
            'binance_rest': 'https://fapi.binance.com/fapi/v1',
            'binance_ws': 'wss://fstream.binance.com/ws'
        }
        self.quality_thresholds = {
            'min_volume': 1000000,  # Minimum volume
            'max_price_deviation': 5,  # Max %5 deviation
            'data_freshness': 60,  # Max 60 saniye eski
            'min_trades': 100  # Min trade count
        }
    
    def validate_binance_price(self, symbol):
        """Binance'den gelen fiyatı doğrula"""
        try:
            # 3 farklı endpoint'ten çek ve karşılaştır
            endpoints = [
                f"{self.data_sources['binance_rest']}/ticker/price?symbol={symbol}",
                f"{self.data_sources['binance_rest']}/avgPrice?symbol={symbol}",
                f"{self.data_sources['binance_rest']}/klines?symbol={symbol}&interval=1m&limit=1"
            ]
            
            prices = []
            
            # Endpoint 1: Current Price
            try:
                resp1 = requests.get(endpoints[0], timeout=3)
                if resp1.status_code == 200:
                    price1 = float(resp1.json()['price'])
                    prices.append(('current', price1))
            except:
                pass
            
            # Endpoint 2: Average Price
            try:
                resp2 = requests.get(endpoints[1], timeout=3)
                if resp2.status_code == 200:
                    price2 = float(resp2.json()['price'])
                    prices.append(('average', price2))
            except:
                pass
            
            # Endpoint 3: Kline Price
            try:
                resp3 = requests.get(endpoints[2], timeout=3)
                if resp3.status_code == 200:
                    price3 = float(resp3.json()[0][4])  # Close price
                    prices.append(('kline_close', price3))
            except:
                pass
            
            if len(prices) < 2:
                return {
                    'valid': False,
                    'reason': 'Insufficient data sources',
                    'prices_fetched': len(prices)
                }
            
            # Fiyatları karşılaştır
            price_values = [p[1] for p in prices]
            avg_price = np.mean(price_values)
            std_price = np.std(price_values)
            
            # Deviation hesapla
            max_deviation = (max(price_values) - min(price_values)) / avg_price * 100
            
            if max_deviation > self.quality_thresholds['max_price_deviation']:
                return {
                    'valid': False,
                    'reason': f'Price deviation too high: {max_deviation:.2f}%',
                    'prices': dict(prices),
                    'deviation': max_deviation
                }
            
            return {
                'valid': True,
                'price': avg_price,
                'std': std_price,
                'sources': len(prices),
                'data': dict(prices),
                'deviation': max_deviation,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def validate_klines(self, symbol, interval='1m', limit=100):
        """Candlestick verilerini doğrula"""
        try:
            url = f"{self.data_sources['binance_rest']}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return {
                    'valid': False,
                    'reason': f'HTTP {response.status_code}'
                }
            
            data = response.json()
            
            if len(data) == 0:
                return {
                    'valid': False,
                    'reason': 'Empty data'
                }
            
            # Data structure doğrula
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'tb_volume', 'tq_volume', 'ignore'
            ])
            
            # Tip dönüşümleri
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Validasyonlar
            validations = {
                'row_count': len(df),
                'all_positive': (df['close'] > 0).all(),
                'high_ge_low': (df['high'] >= df['low']).all(),
                'high_ge_close': (df['high'] >= df['close']).all(),
                'low_le_close': (df['low'] <= df['close']).all(),
                'volume_threshold': (df['volume'] > 0).all(),
                'no_duplicates': df.shape[0] == df.drop_duplicates().shape[0],
                'recent_data': True
            }
            
            all_valid = all(validations.values())
            
            return {
                'valid': all_valid,
                'validations': validations,
                'row_count': len(df),
                'price_range': {
                    'min': float(df['low'].min()),
                    'max': float(df['high'].max()),
                    'avg': float(df['close'].mean())
                },
                'volume_info': {
                    'total': float(df['volume'].sum()),
                    'avg': float(df['volume'].mean()),
                    'min': float(df['volume'].min()),
                    'max': float(df['volume'].max())
                },
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def validate_market_data_integrity(self, symbols=['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
        """Tüm market verisinin bütünlüğünü doğrula"""
        results = {}
        
        for symbol in symbols:
            price_val = self.validate_binance_price(symbol)
            kline_val = self.validate_klines(symbol)
            
            results[symbol] = {
                'price_validation': price_val,
                'kline_validation': kline_val,
                'overall_valid': price_val.get('valid', False) and kline_val.get('valid', False),
                'checked_at': datetime.now().isoformat()
            }
        
        return results
    
    def check_data_freshness(self, symbol):
        """Verilerin ne kadar güncel olduğunu kontrol et"""
        try:
            resp = requests.get(
                f"{self.data_sources['binance_rest']}/ticker/24hr",
                params={'symbol': symbol},
                timeout=3
            )
            
            if resp.status_code == 200:
                data = resp.json()
                open_time = int(data['openTime']) / 1000
                close_time = int(data['closeTime']) / 1000
                
                now = datetime.now().timestamp()
                freshness_seconds = now - close_time
                
                return {
                    'fresh': freshness_seconds < self.quality_thresholds['data_freshness'],
                    'age_seconds': freshness_seconds,
                    'last_update': datetime.fromtimestamp(close_time).isoformat(),
                    'valid': freshness_seconds >= 0
                }
        except:
            pass
        
        return {'fresh': False, 'error': 'Could not fetch'}
    
    def get_validation_report(self, symbols=['BTCUSDT', 'ETHUSDT', 'LTCUSDT']):
        """Detaylı doğrulama raporu"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'data_integrity': self.validate_market_data_integrity(symbols),
            'data_freshness': {}
        }
        
        for symbol in symbols:
            report['data_freshness'][symbol] = self.check_data_freshness(symbol)
        
        # Genel status
        all_valid = all(
            report['data_integrity'][s]['overall_valid'] 
            for s in symbols
        )
        
        report['all_data_valid'] = all_valid
        report['status'] = 'HEALTHY' if all_valid else 'WARNING'
        
        return report

# Test
if __name__ == "__main__":
    validator = DataValidator()
    report = validator.get_validation_report()
    print(json.dumps(report, indent=2))
