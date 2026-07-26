import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import time
from jugaad_data.nse import NSELive, stock_df
import pandas as pd

from market_data.providers.base_provider import MarketDataProvider
from market_data.models.dto import MarketQuote, HistoricalCandle, CorporateAction, MarketStatus, IndexData
from market_data.exceptions import ProviderTimeoutError, InvalidSymbolError

logger = logging.getLogger(__name__)

class JugaadProvider(MarketDataProvider):
    """
    Implementation of MarketDataProvider using jugaad-data (NSE unofficial).
    """
    
    def __init__(self):
        self.nse_live = NSELive()
        self.provider_name = "jugaad"

    def get_provider_name(self) -> str:
        return self.provider_name
        
    def _parse_quote(self, symbol: str, quote: dict) -> MarketQuote:
        price_info = quote.get('priceInfo', {})
        
        last_price = price_info.get('lastPrice', 0)
        
        if not last_price:
            raise InvalidSymbolError(f"Valid price not found for {symbol} in Jugaad response")
            
        vol = quote.get('preOpenMarket', {}).get('totalTradedVolume', 0)
        if not vol:
            vol = quote.get('securityWiseDP', {}).get('quantityTraded', 0)
            
        return MarketQuote(
            symbol=symbol,
            exchange="NSE",
            timestamp=datetime.now(),
            open=float(price_info.get('open', 0)),
            high=float(price_info.get('intraDayHighLow', {}).get('max', 0) or price_info.get('high', 0)),
            low=float(price_info.get('intraDayHighLow', {}).get('min', 0) or price_info.get('low', 0)),
            close=float(price_info.get('close', 0) or last_price),
            previous_close=float(price_info.get('previousClose', 0)),
            last_price=float(last_price),
            volume=int(vol),
            vwap=float(price_info.get('vwap', 0)) if price_info.get('vwap') else None,
            upper_circuit=float(price_info.get('upperCP', 0)) if price_info.get('upperCP') else None,
            lower_circuit=float(price_info.get('lowerCP', 0)) if price_info.get('lowerCP') else None,
            week_52_high=float(price_info.get('weekHighLow', {}).get('max', 0)) if price_info.get('weekHighLow') else None,
            week_52_low=float(price_info.get('weekHighLow', {}).get('min', 0)) if price_info.get('weekHighLow') else None,
            validation_score=100
        )

    def get_live_quote(self, symbol: str) -> MarketQuote:
        try:
            quote = self.nse_live.stock_quote(symbol)
            return self._parse_quote(symbol, quote)
        except InvalidSymbolError:
            raise
        except Exception as e:
            logger.error(f"Jugaad Provider Error for {symbol}: {e}")
            raise ProviderTimeoutError(str(e))

    def get_live_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get_live_quote(symbol)
                time.sleep(0.1) # Rate limit avoidance
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol} in batch: {e}")
        return results

    def get_historical_data(self, symbol: str, start_date: date, end_date: date) -> List[HistoricalCandle]:
        try:
            df = stock_df(symbol=symbol, from_date=start_date, to_date=end_date, series="EQ")
            candles = []
            for _, row in df.iterrows():
                candles.append(HistoricalCandle(
                    date=row['DATE'].date() if isinstance(row['DATE'], pd.Timestamp) else pd.to_datetime(row['DATE']).date(),
                    open=float(row['OPEN']),
                    high=float(row['HIGH']),
                    low=float(row['LOW']),
                    close=float(row['CLOSE']),
                    volume=int(row['VOLUME'])
                ))
            return sorted(candles, key=lambda x: x.date)
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            raise ProviderTimeoutError(str(e))

    def get_intraday_data(self, symbol: str) -> List[HistoricalCandle]:
        # Jugaad doesn't support easy intraday minute candles without heavy scraping.
        # Fallback to returning empty list or raising error.
        return []

    def get_indices(self) -> List[IndexData]:
        try:
            all_indices = self.nse_live.all_indices()
            data = all_indices.get("data", [])
            res = []
            for item in data:
                res.append(IndexData(
                    index_name=item.get("indexSymbol"),
                    current_value=float(item.get("last", 0)),
                    open=float(item.get("open", 0)),
                    high=float(item.get("high", 0)),
                    low=float(item.get("low", 0)),
                    previous_close=float(item.get("previousClose", 0)),
                    percent_change=float(item.get("percentChange", 0))
                ))
            return res
        except Exception as e:
            logger.error(f"Failed to fetch indices: {e}")
            return []

    def get_index(self, index_name: str) -> IndexData:
        indices = self.get_indices()
        for idx in indices:
            if idx.index_name == index_name:
                return idx
        raise InvalidSymbolError(f"Index {index_name} not found")

    def get_market_status(self) -> MarketStatus:
        try:
            status = self.nse_live.market_status()
            market_state = status.get('marketState', [])
            capital_market = next((x for x in market_state if x.get('market') == 'Capital Market'), {})
            
            return MarketStatus(
                exchange="NSE",
                status=capital_market.get('marketStatus', 'Unknown'),
                timestamp=datetime.now(),
                message=capital_market.get('tradeDate')
            )
        except Exception as e:
            logger.error(f"Failed to fetch market status: {e}")
            return MarketStatus(exchange="NSE", status="Unknown", timestamp=datetime.now())

    def get_trading_calendar(self) -> List[Dict[str, Any]]:
        # Usually from holiday API, returning mock for this provider if not supported directly.
        return []

    def get_corporate_actions(self, symbol: str) -> List[CorporateAction]:
        return []

    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        return []

    def get_symbol_master(self) -> List[str]:
        return []
