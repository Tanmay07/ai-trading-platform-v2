"""
Batch Market Data Service

Specialized for the Discovery Engine to batch download historical data
for multiple stocks concurrently to save time and API calls.
"""
from typing import List, Optional
import pandas as pd
import yfinance as yf
from app.utils.logger import get_logger

class BatchMarketDataService:
    def __init__(self):
        self.logger = get_logger(__name__)

    def download_historical_data(self, symbols: List[str], period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Downloads historical data for multiple symbols simultaneously.
        Returns a MultiIndex DataFrame (Price, Symbol) or None on failure.
        """
        if not symbols:
            return None

        self.logger.info(f"Batch downloading market data for {len(symbols)} symbols. Period: {period}")
        
        try:
            # yfinance returns a MultiIndex DF if multiple tickers are passed
            # e.g. df["Close"]["RELIANCE.NS"]
            data = yf.download(
                tickers=symbols,
                period=period,
                interval=interval,
                group_by="ticker",
                auto_adjust=True,
                threads=True, # Uses multiple threads
                progress=False
            )
            return data
        except Exception as e:
            self.logger.error(f"Failed to batch download market data: {e}")
            return None
