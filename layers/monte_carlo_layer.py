# ===========================================
# monte_carlo_layer.py v2.0 - STRING FORMATTING FIX
# ===========================================
# ✅ DÜZELTMELER:
# 1. String formatting hatası düzeltildi
# 2. num_simulations parametresi doğrulandı
# 3. Error handling iyileştirildi
# ===========================================

"""
🔱 DEMIR AI TRADING BOT - Monte Carlo Layer v2.0
====================================================================
Tarih: 3 Kasım 2025, 14:50 CET
Versiyon: 2.0 - STRING FORMATTING FIX

DÜZELTMELER v2.0:
-----------------
✅ String formatting hatası (f-string) düzeltildi
✅ num_simulations parametresi doğru kullanılıyor
✅ trades_per_simulation parametresi eklendi
✅ Error handling geliştirildi
"""

import numpy as np
import requests
from datetime import datetime
from typing import Dict, Any

# ============================================================================
# MONTE CARLO SİMÜLASYONU
# ============================================================================

def run_monte_carlo_simulation(
    symbol: str,
    interval: str = '1h',
    num_simulations: int = 1000,
    trades_per_simulation: int = 100,
    limit: int = 500
) -> Dict[str, Any]:
    """
    Monte Carlo simülasyonu ile gelecek trade sonuçlarını simüle eder
    
    ✅ v2.0 DÜZELTME: String formatting ve parametreler düzeltildi
    
    Args:
        symbol: Trading pair (örn: 'BTCUSDT')
        interval: Mum aralığı ('1m', '5m', '15m', '1h', '4h', '1d')
        num_simulations: Simülasyon sayısı (default: 1000)
        trades_per_simulation: Her simülasyondaki trade sayısı (default: 100)
        limit: Geçmiş veri sayısı (default: 500)
    
    Returns:
        dict: {
            'success': bool,
            'expected_return': float (% olarak),
            'downside_risk': float (5th percentile),
            'upside_potential': float (95th percentile),
            'num_simulations': int,
            'trades_per_simulation': int,
            'timestamp': str
        }
    """
    print(f"🎲 Monte Carlo Simulation starting...")
    print(f"   Simulations: {num_simulations}")
    print(f"   Trades per sim: {trades_per_simulation}")
    
    try:
        # ====================================================================
        # 1. BİNANCE'DEN GEÇMİŞ VERİ ÇEK
        # ====================================================================
        
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ Binance API hatası: {response.status_code}")
            return {
                'success': False,
                'error': f'Binance API error: {response.status_code}'
            }
        
        klines = response.json()
        
        if not klines or len(klines) < 50:
            print(f"⚠️ Yetersiz veri: {len(klines)} mum")
            return {
                'success': False,
                'error': 'Insufficient historical data'
            }
        
        # ====================================================================
        # 2. FİYAT DEĞİŞİMLERİNİ HESAPLA
        # ====================================================================
        
        closes = [float(k[4]) for k in klines]
        returns = np.diff(closes) / closes[:-1]
        
        # İstatistikler
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        print(f"📊 Geçmiş veri: {len(closes)} mum")
        print(f"📊 Ortalama return: {mean_return:.6f}")
        print(f"📊 Standart sapma: {std_return:.6f}")
        
        # ====================================================================
        # 3. MONTE CARLO SİMÜLASYONU
        # ====================================================================
        
        simulation_results = []
        
        for sim in range(num_simulations):
            cumulative_return = 0
            
            for trade in range(trades_per_simulation):
                # Rastgele return üret (normal dağılım)
                trade_return = np.random.normal(mean_return, std_return)
                cumulative_return += trade_return
            
            simulation_results.append(cumulative_return)
        
        # ====================================================================
        # 4. SONUÇLARI ANALİZ ET
        # ====================================================================
        
        expected_return = np.mean(simulation_results) * 100  # Yüzdeye çevir
        downside_risk = np.percentile(simulation_results, 5) * 100  # 5th percentile
        upside_potential = np.percentile(simulation_results, 95) * 100  # 95th percentile
        
        median_return = np.median(simulation_results) * 100
        std_sim = np.std(simulation_results) * 100
        
        # ✅ DÜZELTME: String formatting (sadece f-string kullan)
        print(f"\n{'='*80}")
        print(f"✅ Monte Carlo tamamlandı!")
        print(f"   Expected Return: {expected_return:.2f}%")
        print(f"   Median Return: {median_return:.2f}%")
        print(f"   Std Dev: {std_sim:.2f}%")
        print(f"   Downside Risk (5%): {downside_risk:.2f}%")
        print(f"   Upside Potential (95%): {upside_potential:.2f}%")
        print(f"{'='*80}\n")
        
        # ====================================================================
        # 5. RETURN SONUCU
        # ====================================================================
        
        return {
            'success': True,
            'expected_return': round(expected_return, 2),
            'median_return': round(median_return, 2),
            'downside_risk': round(downside_risk, 2),
            'upside_potential': round(upside_potential, 2),
            'std_deviation': round(std_sim, 2),
            'num_simulations': num_simulations,
            'trades_per_simulation': trades_per_simulation,
            'sample_size': len(closes),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        # ✅ DÜZELTME: Exception handling
        print(f"⚠️ Monte Carlo hatası: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# LEGACY FONKSİYON (GERİYE UYUMLULUK)
# ============================================================================

def calculate_monte_carlo_score(
    symbol: str,
    interval: str = '1h',
    num_simulations: int = 1000
) -> Dict[str, Any]:
    """
    Legacy wrapper - run_monte_carlo_simulation() ile aynı
    """
    return run_monte_carlo_simulation(
        symbol=symbol,
        interval=interval,
        num_simulations=num_simulations
    )

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🔱 MONTE CARLO LAYER v2.0 - STRING FORMATTING FIX TEST!")
    print("=" * 80)
    print()
    
    # Test 1: BTCUSDT
    print("📊 Test 1: BTCUSDT 1h")
    result = run_monte_carlo_simulation('BTCUSDT', '1h', 1000, 100)
    
    if result['success']:
        print(f"\n✅ BAŞARILI!")
        print(f"  Expected Return: {result['expected_return']:.2f}%")
        print(f"  Downside Risk: {result['downside_risk']:.2f}%")
        print(f"  Upside Potential: {result['upside_potential']:.2f}%")
    else:
        print(f"\n❌ HATA: {result.get('error', 'Unknown')}")
    
    print("\n" + "=" * 80)
    
    # Test 2: ETHUSDT
    print("\n📊 Test 2: ETHUSDT 15m")
    result2 = run_monte_carlo_simulation('ETHUSDT', '15m', 500, 50)
    
    if result2['success']:
        print(f"\n✅ BAŞARILI!")
        print(f"  Expected Return: {result2['expected_return']:.2f}%")
        print(f"  Downside Risk: {result2['downside_risk']:.2f}%")
        print(f"  Upside Potential: {result2['upside_potential']:.2f}%")
    else:
        print(f"\n❌ HATA: {result2.get('error', 'Unknown')}")
    
    print("\n" + "=" * 80)
