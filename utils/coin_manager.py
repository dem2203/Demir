"""
=============================================================================
DEMIR AI v25.0 - COIN MANAGER & MULTI-EXCHANGE SELECTOR
=============================================================================
Purpose: Dinamik coin ekleme, yönetim ve trade çifti seçimi
Location: /utils/ klasörü
Integrations: streamlit_app.py, auto_trade_manual.py, daemon_core.py
=============================================================================
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TradingPair:
    """Trading pair configuration"""
    symbol: str  # e.g., "BTCUSDT"
    base_asset: str  # e.g., "BTC"
    quote_asset: str  # e.g., "USDT"
    exchange: str  # e.g., "BINANCE"
    is_active: bool = True
    min_notional: float = 10.0  # Minimum order value
    precision: int = 2  # Price decimal places
    added_date: str = None
    
    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.now().isoformat()


class CoinManager:
    """
    Yönetim: Tüm trade çiftlerinin dinamik ekleme/kaldırma/yönetimi
    Features:
    - Multi-exchange coin desteği
    - Coin validasyon
    - Binance API ile canlı bakiye kontrol
    - Persistent storage (JSON)
    """
    
    def __init__(self, config_file: str = "config/trading_pairs.json"):
        self.config_file = config_file
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.default_pairs = [
            TradingPair("BTCUSDT", "BTC", "USDT", "BINANCE"),
            TradingPair("ETHUSDT", "ETH", "USDT", "BINANCE"),
            TradingPair("LTCUSDT", "LTC", "USDT", "BINANCE"),
        ]
        self._ensure_config_dir()
        self._load_pairs()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    
    def _load_pairs(self):
        """Load trading pairs from persistent storage"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for pair_data in data:
                        pair = TradingPair(**pair_data)
                        self.trading_pairs[pair.symbol] = pair
                logger.info(f"✅ Loaded {len(self.trading_pairs)} trading pairs from {self.config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Error loading pairs: {e}. Using defaults.")
                self._init_defaults()
        else:
            self._init_defaults()
    
    def _init_defaults(self):
        """Initialize with default pairs"""
        for pair in self.default_pairs:
            self.trading_pairs[pair.symbol] = pair
        self._save_pairs()
        logger.info("📌 Initialized with default trading pairs")
    
    def _save_pairs(self):
        """Save trading pairs to persistent storage"""
        try:
            data = [asdict(pair) for pair in self.trading_pairs.values()]
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved {len(data)} trading pairs to {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Error saving pairs: {e}")
    
    def add_coin(self, symbol: str, base_asset: str, quote_asset: str, 
                 exchange: str = "BINANCE", min_notional: float = 10.0) -> Tuple[bool, str]:
        """
        Yeni coin ekleme fonksiyonu
        
        Args:
            symbol: Trading pair (e.g., "ADAUSDT")
            base_asset: Base coin (e.g., "ADA")
            quote_asset: Quote coin (e.g., "USDT")
            exchange: Exchange name (default: BINANCE)
            min_notional: Minimum order value
        
        Returns:
            (success: bool, message: str)
        """
        # Validation
        if symbol in self.trading_pairs:
            return False, f"❌ {symbol} already exists"
        
        if not symbol.endswith(quote_asset):
            return False, f"❌ Symbol must end with {quote_asset}"
        
        # Validate on exchange (TODO: Add Binance API validation)
        # For now, simple format check
        if len(symbol) < 5:
            return False, f"❌ Invalid symbol format"
        
        # Create new pair
        new_pair = TradingPair(
            symbol=symbol.upper(),
            base_asset=base_asset.upper(),
            quote_asset=quote_asset.upper(),
            exchange=exchange.upper(),
            min_notional=min_notional
        )
        
        self.trading_pairs[symbol.upper()] = new_pair
        self._save_pairs()
        logger.info(f"✅ Added new trading pair: {symbol}")
        return True, f"✅ {symbol} added successfully"
    
    def remove_coin(self, symbol: str) -> Tuple[bool, str]:
        """Remove coin from trading list"""
        if symbol not in self.trading_pairs:
            return False, f"❌ {symbol} not found"
        
        # Prevent removal of default pairs
        if symbol in ["BTCUSDT", "ETHUSDT", "LTCUSDT"]:
            return False, f"⚠️ Cannot remove default pair {symbol}"
        
        del self.trading_pairs[symbol]
        self._save_pairs()
        logger.info(f"❌ Removed trading pair: {symbol}")
        return True, f"✅ {symbol} removed successfully"
    
    def get_active_coins(self) -> List[TradingPair]:
        """Get all active trading pairs"""
        return [pair for pair in self.trading_pairs.values() if pair.is_active]
    
    def get_all_coins(self) -> List[TradingPair]:
        """Get all trading pairs"""
        return list(self.trading_pairs.values())
    
    def toggle_coin(self, symbol: str) -> Tuple[bool, str]:
        """Enable/disable a trading pair"""
        if symbol not in self.trading_pairs:
            return False, f"❌ {symbol} not found"
        
        pair = self.trading_pairs[symbol]
        pair.is_active = not pair.is_active
        self._save_pairs()
        status = "✅ ACTIVE" if pair.is_active else "⏸️ INACTIVE"
        logger.info(f"{status}: {symbol}")
        return True, f"{status}: {symbol}"
    
    def get_coin_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed info for a coin"""
        if symbol not in self.trading_pairs:
            return None
        
        pair = self.trading_pairs[symbol]
        return asdict(pair)
    
    def list_coins_table(self) -> List[Dict]:
        """Get formatted coin list for GUI display"""
        return [
            {
                "Symbol": pair.symbol,
                "Base": pair.base_asset,
                "Quote": pair.quote_asset,
                "Exchange": pair.exchange,
                "Status": "🟢 ACTIVE" if pair.is_active else "⏸️ INACTIVE",
                "Added": pair.added_date[:10],  # Date only
            }
            for pair in self.get_all_coins()
        ]


# ============================================================================
# TEST & USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize
    manager = CoinManager()
    
    # Display current coins
    print("\n📊 Current Trading Pairs:")
    for pair in manager.get_all_coins():
        print(f"  • {pair.symbol} ({pair.base_asset}/{pair.quote_asset}) - {pair.exchange}")
    
    # Add new coin
    success, msg = manager.add_coin("ADAUSDT", "ADA", "USDT")
    print(f"\n{msg}")
    
    # Get table format
    print("\n📋 Coins Table:")
    for row in manager.list_coins_table():
        print(f"  {row}")
