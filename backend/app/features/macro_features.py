"""
Macro Features Module
Provides global macroeconomic and implied volatility features.
"""

import pandas as pd
import yfinance as yf
from functools import lru_cache

from app.utils.logger import get_logger

logger = get_logger(__name__)

class MacroFeatures:
    @staticmethod
    @lru_cache(maxsize=1)
    def _fetch_macro_data(period: str = "2y") -> pd.DataFrame:
        """Fetches macro data and caches it per run to avoid redundant calls."""
        logger.info(f"Fetching macro data for period {period}...")
        
        symbols = {
            "india_vix": "^INDIAVIX",
            "us_10y_yield": "^TNX",
            "usd_inr": "INR=X"
        }
        
        dfs = []
        for feature_name, ticker in symbols.items():
            try:
                # Need to use auto_adjust=False and multi_level_index=False for yf>=0.2 if needed, 
                # but standard download returns a MultiIndex if multiple tickers.
                # Since we download one by one, it returns a single level column index.
                data = yf.download(ticker, period=period, interval="1d", progress=False)
                if not data.empty:
                    df = data[["Close"]].copy()
                    
                    # Handle MultiIndex column issue in newer yfinance versions
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                        
                    df.columns = [feature_name]
                    dfs.append(df)
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {e}")
                
        if not dfs:
            return pd.DataFrame()
            
        # Merge all macro features on Date
        macro_df = dfs[0]
        for df in dfs[1:]:
            macro_df = macro_df.join(df, how="outer")
            
        # Forward fill to handle mismatched trading holidays (e.g. US vs India)
        macro_df = macro_df.ffill()
        
        # Make index tz-naive to match standard stock dataframes
        if macro_df.index.tz is not None:
            macro_df.index = macro_df.index.tz_localize(None)
            
        return macro_df

    @staticmethod
    def add_macro_features(df: pd.DataFrame, period: str = "2y") -> pd.DataFrame:
        """Adds macro features to the stock dataframe by joining on Date."""
        if df.empty:
            return df
            
        macro_df = MacroFeatures._fetch_macro_data(period=period)
        if macro_df.empty:
            logger.warning("No macro data available. Skipping macro features.")
            return df
            
        original_tz = df.index.tz
        if original_tz is not None:
            df.index = df.index.tz_localize(None)
            
        # Left join macro features
        df = df.join(macro_df, how="left")
        
        features = ["india_vix", "us_10y_yield", "usd_inr"]
        existing_features = [f for f in features if f in df.columns]
        df[existing_features] = df[existing_features].ffill()
        
        if original_tz is not None:
            df.index = df.index.tz_localize(original_tz)
            
        return df
