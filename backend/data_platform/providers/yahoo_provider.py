import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
from typing import Optional

from data_platform.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)

class YahooProvider(BaseProvider):
    """
    Yahoo Finance implementation of the BaseProvider.
    Uses yfinance to fetch historical market data.
    """

    def _format_symbol(self, symbol: str) -> str:
        """Yahoo Finance requires .NS suffix for Indian NSE stocks."""
        if not symbol.endswith('.NS'):
            return f"{symbol}.NS"
        return symbol

    def _standardize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure standard OHLCV columns and timezone-naive datetimes."""
        if df is None or df.empty:
            return pd.DataFrame()
            
        # Ensure column names are standard
        expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in expected_cols:
            if col not in df.columns:
                logger.warning(f"Missing column {col} in Yahoo response.")
        
        # Make index timezone naive if it has timezone
        if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
            df.index = df.index.tz_localize(None)
            
        # Standardize index name
        df.index.name = 'Date'
        return df

    def get_symbol_history(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        formatted_symbol = self._format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol)
            # yf accepts YYYY-MM-DD
            df = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            return self._standardize_df(df)
        except Exception as e:
            logger.error(f"Error fetching Yahoo history for {symbol}: {e}")
            return pd.DataFrame()

    def get_latest_history(self, symbol: str, days: int = 5) -> pd.DataFrame:
        formatted_symbol = self._format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol)
            df = ticker.history(period=f"{days}d")
            return self._standardize_df(df)
        except Exception as e:
            logger.error(f"Error fetching latest Yahoo history for {symbol}: {e}")
            return pd.DataFrame()

    def get_corporate_actions(self, symbol: str) -> pd.DataFrame:
        formatted_symbol = self._format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol)
            df = ticker.actions
            if df is not None and not df.empty:
                if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching corporate actions for {symbol}: {e}")
            return pd.DataFrame()

    def validate_symbol(self, symbol: str) -> bool:
        formatted_symbol = self._format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol)
            info = ticker.fast_info
            return 'lastPrice' in info
        except Exception:
            return False

    def provider_name(self) -> str:
        return "yahoo"
