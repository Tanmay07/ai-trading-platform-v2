import yfinance as yf
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, date
import pandas as pd

from market_data.providers.base_provider import MarketDataProvider
from market_data.models.dto import MarketQuote, HistoricalCandle, CorporateAction, MarketStatus, IndexData
from market_data.exceptions import ProviderTimeoutError, InvalidSymbolError

logger = logging.getLogger(__name__)

class YahooProvider(MarketDataProvider):
    
    def get_provider_name(self) -> str:
        return "yahoo"
        
    def get_live_quote(self, symbol: str) -> MarketQuote:
        """Fetches latest price. Appends .NS for Indian stocks."""
        ticker = f"{symbol}.NS"
        try:
            stock = yf.Ticker(ticker)
            data = stock.fast_info
            
            last_price = float(data.last_price)
            if not last_price:
                raise InvalidSymbolError(f"Valid price not found for {symbol}")
                
            return MarketQuote(
                symbol=symbol,
                exchange="NSE",
                timestamp=datetime.now(),
                open=float(data.open) if hasattr(data, 'open') and data.open else last_price,
                high=float(data.day_high) if hasattr(data, 'day_high') and data.day_high else last_price,
                low=float(data.day_low) if hasattr(data, 'day_low') and data.day_low else last_price,
                close=last_price,
                previous_close=float(data.previous_close) if hasattr(data, 'previous_close') and data.previous_close else last_price,
                last_price=last_price,
                volume=int(data.last_volume) if hasattr(data, 'last_volume') and data.last_volume else 0,
                validation_score=100
            )
        except Exception as e:
            logger.error(f"Yahoo Provider Error for {symbol}: {e}")
            raise ProviderTimeoutError(str(e))

    def get_live_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Uses yf.download for batch requests."""
        tickers = " ".join([f"{s}.NS" for s in symbols])
        results = {}
        try:
            data = yf.download(tickers, period="1d", interval="1m", progress=False)
            if data.empty:
                return results
                
            for symbol in symbols:
                try:
                    tick = f"{symbol}.NS"
                    if isinstance(data.columns, pd.MultiIndex):
                        close_px = float(data['Close'][tick].iloc[-1])
                        vol = int(data['Volume'][tick].iloc[-1]) if 'Volume' in data else 0
                    else:
                        close_px = float(data['Close'].iloc[-1])
                        vol = int(data['Volume'].iloc[-1]) if 'Volume' in data else 0
                        
                    results[symbol] = MarketQuote(
                        symbol=symbol,
                        exchange="NSE",
                        timestamp=datetime.now(),
                        open=close_px, high=close_px, low=close_px, close=close_px,
                        previous_close=close_px,
                        last_price=close_px,
                        volume=vol,
                        validation_score=100
                    )
                except Exception as ex:
                    logger.error(f"Batch parse failed for {symbol}: {ex}")
            return results
        except Exception as e:
            logger.error(f"Yahoo Provider Batch Error: {e}")
            return results

    def get_historical_data(self, symbol: str, start_date: date, end_date: date) -> List[HistoricalCandle]:
        return []

    def get_intraday_data(self, symbol: str) -> List[HistoricalCandle]:
        return []

    def get_indices(self) -> List[IndexData]:
        return []

    def get_index(self, index_name: str) -> IndexData:
        raise InvalidSymbolError("Not implemented")

    def get_market_status(self) -> MarketStatus:
        return MarketStatus(exchange="NSE", status="Unknown", timestamp=datetime.now())

    def get_trading_calendar(self) -> List[Dict[str, Any]]:
        return []

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        return []

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        return []

    def get_symbol_master(self) -> List[str]:
        return []
