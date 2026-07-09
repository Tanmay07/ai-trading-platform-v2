import logging
from typing import Dict, Any, List
from datetime import datetime
from jugaad_data.nse import NSELive

from market_data.providers.base_provider import BaseIntradayProvider

logger = logging.getLogger(__name__)

class JugaadProvider(BaseIntradayProvider):
    """Fetches real-time data using the jugaad-data library (NSE unofficial)."""
    
    def __init__(self):
        self.nse_live = NSELive()

    def get_provider_name(self) -> str:
        return "jugaad"
        
    def fetch_current_price(self, symbol: str) -> Dict[str, Any]:
        try:
            quote = self.nse_live.stock_quote(symbol)
            # The structure of the quote changes often, we extract the basics
            price_info = quote.get('priceInfo', {})
            last_price = price_info.get('lastPrice', 0)
            
            # Getting volume (might be under preOpenMarket or tradeInfo)
            vol = quote.get('preOpenMarket', {}).get('totalTradedVolume', 0)
            if not vol:
                vol = quote.get('securityWiseDP', {}).get('quantityTraded', 0)
                
            if not last_price:
                return {"symbol": symbol, "status": "error", "error": "Price not found in Jugaad response"}

            return {
                "symbol": symbol,
                "provider": self.get_provider_name(),
                "price": float(last_price),
                "volume": int(vol),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Jugaad Provider Error for {symbol}: {e}")
            return {"symbol": symbol, "status": "error", "error": str(e)}

    def fetch_batch_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        # Jugaad doesn't have a bulk stock quote API that works perfectly, 
        # so we iterate. In a real system, you'd use asyncio or ThreadPoolExecutor here.
        results = {}
        for symbol in symbols:
            results[symbol] = self.fetch_current_price(symbol)
        return results
