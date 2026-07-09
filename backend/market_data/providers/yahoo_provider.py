import yfinance as yf
from typing import Dict, Any, List
import logging
from datetime import datetime

from market_data.providers.base_provider import BaseIntradayProvider

logger = logging.getLogger(__name__)

class YahooIntradayProvider(BaseIntradayProvider):
    
    def get_provider_name(self) -> str:
        return "yahoo"
        
    def fetch_current_price(self, symbol: str) -> Dict[str, Any]:
        """Fetches latest price. Appends .NS for Indian stocks."""
        ticker = f"{symbol}.NS"
        try:
            stock = yf.Ticker(ticker)
            data = stock.fast_info
            
            return {
                "symbol": symbol,
                "provider": self.get_provider_name(),
                "price": float(data.last_price),
                "volume": int(data.last_volume),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Yahoo Provider Error for {symbol}: {e}")
            return {"symbol": symbol, "status": "error", "error": str(e)}

    def fetch_batch_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Uses yf.download for batch requests."""
        tickers = " ".join([f"{s}.NS" for s in symbols])
        results = {}
        try:
            data = yf.download(tickers, period="1d", interval="1m", progress=False)
            if data.empty:
                return results
                
            # Parse the MultiIndex dataframe
            for symbol in symbols:
                try:
                    # Get the last valid row for this ticker
                    tick = f"{symbol}.NS"
                    if isinstance(data.columns, pd.MultiIndex):
                        close_px = float(data['Close'][tick].iloc[-1])
                        vol = int(data['Volume'][tick].iloc[-1])
                    else:
                        close_px = float(data['Close'].iloc[-1])
                        vol = int(data['Volume'].iloc[-1])
                        
                    results[symbol] = {
                        "symbol": symbol,
                        "provider": self.get_provider_name(),
                        "price": close_px,
                        "volume": vol,
                        "timestamp": datetime.now().isoformat(),
                        "status": "success"
                    }
                except Exception as ex:
                    results[symbol] = {"symbol": symbol, "status": "error", "error": str(ex)}
            return results
        except Exception as e:
            logger.error(f"Yahoo Provider Batch Error: {e}")
            return results
