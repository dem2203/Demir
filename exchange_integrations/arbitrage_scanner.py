import os
import asyncio
import aiohttp
import logging
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ArbitrageScanner:
    """
    Multi-Exchange Arbitrage Scanner with Safe Fallback
    
    Features:
    - Scans prices across multiple exchanges (REAL DATA)
    - Calculates arbitrage opportunities
    - Detects profitable spread
    - Graceful fallback if exchange not configured
    
    NO CRASHES: System continues even if some exchanges unavailable
    """
    
    def __init__(self):
        """Initialize Arbitrage Scanner"""
        self.binance_api = "https://api.binance.com/api/v3"
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3',
            'bybit': 'https://api.bybit.com/v5',
            'okx': 'https://www.okx.com/api/v5',
            'coinbase': 'https://api.coinbase.com/v2'
        }
        
        # Load connectors safely (only if keys exist)
        self.bybit_connector = None
        self.okx_connector = None
        self.coinbase_connector = None
        
        self._load_connectors()
    
    def _load_connectors(self):
        """Load exchange connectors only if API keys configured"""
        try:
            from exchange_integrations import (
                get_connector
            )
            
            # Try to load each connector
            self.bybit_connector = get_connector('bybit')
            self.okx_connector = get_connector('okx')
            self.coinbase_connector = get_connector('coinbase')
            
            # Log status
            if self.bybit_connector:
                logger.info("✅ Bybit connector loaded")
            else:
                logger.warning("⚠️ Bybit not configured, skipping...")
            
            if self.okx_connector:
                logger.info("✅ OKX connector loaded")
            else:
                logger.warning("⚠️ OKX not configured, skipping...")
            
            if self.coinbase_connector:
                logger.info("✅ Coinbase connector loaded")
            else:
                logger.warning("⚠️ Coinbase not configured, skipping...")
                
        except ImportError as e:
            logger.warning(f"⚠️ Could not import exchange_integrations: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading connectors: {e}")
    
    # ========== MAIN ARBITRAGE SCANNING ==========
    
    async def scan_arbitrage(self, symbol: str) -> Dict:
        """
        Scan for arbitrage opportunities across exchanges
        
        Returns:
        {
            'opportunity': True/False,
            'spread': float (% difference),
            'buy_exchange': str,
            'sell_exchange': str,
            'profit_potential': float (% after fees),
            'prices': {exchange: price}
        }
        """
        try:
            logger.info(f"🔍 Scanning arbitrage for {symbol}...")
            
            # Get prices from multiple exchanges
            prices = {}
            
            # ===== BINANCE (Always available) =====
            binance_price = await self._get_binance_price(symbol)
            if binance_price:
                prices['binance'] = binance_price
                logger.info(f"  ✅ Binance: ${binance_price:,.2f}")
            
            # ===== BYBIT (Only if configured) =====
            if self.bybit_connector:
                try:
                    bybit_price = await self._get_bybit_price(symbol)
                    if bybit_price:
                        prices['bybit'] = bybit_price
                        logger.info(f"  ✅ Bybit: ${bybit_price:,.2f}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Bybit error: {e}")
            
            # ===== OKX (Only if configured) =====
            if self.okx_connector:
                try:
                    okx_price = await self._get_okx_price(symbol)
                    if okx_price:
                        prices['okx'] = okx_price
                        logger.info(f"  ✅ OKX: ${okx_price:,.2f}")
                except Exception as e:
                    logger.warning(f"  ⚠️ OKX error: {e}")
            
            # ===== COINBASE (Only if configured) =====
            if self.coinbase_connector:
                try:
                    coinbase_price = await self._get_coinbase_price(symbol)
                    if coinbase_price:
                        prices['coinbase'] = coinbase_price
                        logger.info(f"  ✅ Coinbase: ${coinbase_price:,.2f}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Coinbase error: {e}")
            
            # ===== CALCULATE SPREAD =====
            valid_prices = [p for p in prices.values() if p and p > 0]
            
            if len(valid_prices) < 2:
                logger.warning(f"⚠️ Not enough prices for arbitrage (only {len(valid_prices)})")
                return {
                    'opportunity': False,
                    'reason': 'Not enough price data',
                    'prices': prices,
                    'timestamp': datetime.now().isoformat()
                }
            
            max_price = max(valid_prices)
            min_price = min(valid_prices)
            spread_percent = ((max_price - min_price) / min_price * 100)
            
            # Get exchange names
            buy_exchange = [k for k, v in prices.items() if v == min_price][0]
            sell_exchange = [k for k, v in prices.items() if v == max_price][0]
            
            # ===== CALCULATE PROFIT (after fees) =====
            # Approximate fees per exchange:
            # Binance: 0.1% maker, 0.1% taker
            # Bybit: 0.1% maker, 0.1% taker
            # OKX: 0.1% maker, 0.15% taker
            # Coinbase: 0.5% fee
            
            buy_fee = self._get_exchange_fee(buy_exchange, 'maker')
            sell_fee = self._get_exchange_fee(sell_exchange, 'taker')
            
            total_fees = buy_fee + sell_fee
            profit_potential = spread_percent - total_fees
            
            # ===== RETURN RESULT =====
            result = {
                'opportunity': profit_potential > 0.2,  # Only flag if >0.2% profit after fees
                'spread': spread_percent,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': min_price,
                'sell_price': max_price,
                'buy_fee': buy_fee,
                'sell_fee': sell_fee,
                'total_fees': total_fees,
                'profit_potential': profit_potential,
                'prices': prices,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log result
            if result['opportunity']:
                logger.warning(f"💰 ARBITRAGE FOUND: {buy_exchange} (${min_price:,.2f}) → {sell_exchange} (${max_price:,.2f})")
                logger.warning(f"   Spread: {spread_percent:.2f}%, Profit: {profit_potential:.2f}% after fees")
            else:
                logger.info(f"   Spread: {spread_percent:.2f}% (after fees: {profit_potential:.2f}% - not profitable)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error scanning arbitrage: {e}")
            return {
                'opportunity': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # ========== EXCHANGE PRICE FETCHING (REAL DATA) ==========
    
    async def _get_binance_price(self, symbol: str) -> Optional[float]:
        """Get REAL price from Binance API - NO MOCK DATA"""
        try:
            url = f"{self.binance_api}/ticker/price?symbol={symbol}USDT"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching Binance price: {e}")
            return None
    
    async def _get_bybit_price(self, symbol: str) -> Optional[float]:
        """Get REAL price from Bybit API"""
        try:
            if not self.bybit_connector:
                return None
            
            url = f"{self.exchanges['bybit']}/market/tickers"
            params = {
                "category": "linear",
                "symbol": f"{symbol}USDT"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('result', {}).get('list'):
                            return float(data['result']['list'][0]['lastPrice'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching Bybit price: {e}")
            return None
    
    async def _get_okx_price(self, symbol: str) -> Optional[float]:
        """Get REAL price from OKX API"""
        try:
            if not self.okx_connector:
                return None
            
            url = f"{self.exchanges['okx']}/market/tickers"
            params = {
                "instType": "SWAP",
                "instId": f"{symbol}-USDT"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data'):
                            return float(data['data'][0]['last'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching OKX price: {e}")
            return None
    
    async def _get_coinbase_price(self, symbol: str) -> Optional[float]:
        """Get REAL price from Coinbase API"""
        try:
            if not self.coinbase_connector:
                return None
            
            # Coinbase product ID format: BTC-USD, ETH-USD, etc.
            product_id = f"{symbol.replace('USDT', '')}-USD"
            url = f"{self.exchanges['coinbase']}/prices/{product_id}/spot"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('data', {}).get('amount', 0))
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching Coinbase price: {e}")
            return None
    
    # ========== HELPER METHODS ==========
    
    def _get_exchange_fee(self, exchange: str, fee_type: str = 'maker') -> float:
        """Get approximate trading fee for exchange"""
        fees = {
            'binance': {'maker': 0.1, 'taker': 0.1},
            'bybit': {'maker': 0.1, 'taker': 0.1},
            'okx': {'maker': 0.1, 'taker': 0.15},
            'coinbase': {'maker': 0.5, 'taker': 0.6},
            'default': {'maker': 0.1, 'taker': 0.1}
        }
        
        exchange_fees = fees.get(exchange.lower(), fees['default'])
        return exchange_fees.get(fee_type, 0.1)
    
    async def scan_all_symbols(self, symbols: List[str]) -> List[Dict]:
        """
        Scan arbitrage for multiple symbols
        
        Usage:
            scanner = ArbitrageScanner()
            results = await scanner.scan_all_symbols(['BTCUSDT', 'ETHUSDT', 'LTCUSDT'])
        """
        results = []
        
        for symbol in symbols:
            result = await self.scan_arbitrage(symbol)
            results.append(result)
            
            # Rate limiting - don't hammer APIs
            await asyncio.sleep(0.5)
        
        return results
    
    async def monitor_arbitrage(self, symbols: List[str], interval: int = 300):
        """
        Monitor arbitrage opportunities continuously
        
        Args:
            symbols: List of symbols to monitor (e.g., ['BTCUSDT', 'ETHUSDT'])
            interval: Scan interval in seconds (default: 5 minutes)
        
        Usage:
            scanner = ArbitrageScanner()
            await scanner.monitor_arbitrage(['BTCUSDT', 'ETHUSDT'], interval=300)
        """
        logger.info(f"🔍 Starting arbitrage monitor - scanning every {interval}s")
        
        try:
            while True:
                opportunities = []
                
                for symbol in symbols:
                    result = await self.scan_arbitrage(symbol)
                    
                    if result.get('opportunity'):
                        opportunities.append({
                            'symbol': symbol,
                            'profit': result.get('profit_potential', 0),
                            'buy': result.get('buy_exchange'),
                            'sell': result.get('sell_exchange'),
                            'spread': result.get('spread', 0)
                        })
                    
                    await asyncio.sleep(0.2)
                
                # Log opportunities
                if opportunities:
                    logger.warning(f"💰 {len(opportunities)} arbitrage opportunity(ies) found!")
                    for opp in opportunities:
                        logger.warning(f"   {opp['symbol']}: {opp['buy']} → {opp['sell']} (Profit: {opp['profit']:.2f}%)")
                else:
                    logger.info(f"✓ No arbitrage opportunities (checked {len(symbols)} symbols)")
                
                # Wait before next scan
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Arbitrage monitoring stopped")
        except Exception as e:
            logger.error(f"❌ Error in arbitrage monitor: {e}")


# ========== TESTING ==========

if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test arbitrage scanner"""
        scanner = ArbitrageScanner()
        
        # Test single symbol
        print("\n📊 Testing single symbol scan:")
        result = await scanner.scan_arbitrage('BTCUSDT')
        print(f"Result: {result}\n")
        
        # Test multiple symbols
        print("📊 Testing multiple symbols:")
        results = await scanner.scan_all_symbols(['BTCUSDT', 'ETHUSDT'])
        for r in results:
            print(f"  {r.get('prices', {})}\n")
    
    # Run test
    asyncio.run(test())
