"""
Regime Features Module
Implements a Hidden Markov Model (HMM) to classify market regimes.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from functools import lru_cache
from hmmlearn import hmm

from app.utils.logger import get_logger

logger = get_logger(__name__)

class RegimeFeatures:
    @staticmethod
    @lru_cache(maxsize=1)
    def _fetch_and_train_hmm(period: str = "2y") -> pd.DataFrame:
        """Fetches Nifty and VIX, trains HMM, and returns a dataframe with regime states."""
        logger.info(f"Training HMM market regime classifier for period {period}...")
        
        try:
            # Fetch Nifty 50 for returns
            nifty_data = yf.download("^NSEI", period=period, interval="1d", progress=False)
            if nifty_data.empty:
                return pd.DataFrame()
                
            # Fetch VIX for volatility
            vix_data = yf.download("^INDIAVIX", period=period, interval="1d", progress=False)
            
            # Use Close prices
            nifty_close = nifty_data[["Close"]].copy()
            if isinstance(nifty_close.columns, pd.MultiIndex):
                nifty_close.columns = nifty_close.columns.get_level_values(0)
            nifty_close.columns = ["nifty"]
            
            # Compute daily returns
            nifty_close["nifty_return"] = nifty_close["nifty"].pct_change()
            
            if not vix_data.empty:
                vix_close = vix_data[["Close"]].copy()
                if isinstance(vix_close.columns, pd.MultiIndex):
                    vix_close.columns = vix_close.columns.get_level_values(0)
                vix_close.columns = ["vix"]
                df = nifty_close.join(vix_close, how="left").ffill().dropna()
            else:
                # Fallback to Nifty rolling std if VIX is unavailable
                df = nifty_close.dropna()
                df["vix"] = df["nifty_return"].rolling(window=10).std()
                df = df.dropna()
                
            if len(df) < 50:
                logger.warning("Not enough data to train HMM.")
                return pd.DataFrame()
                
            # Features for HMM: Returns and VIX
            X = df[["nifty_return", "vix"]].values
            
            # Train 2-state Gaussian HMM
            model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=42)
            model.fit(X)
            
            states = model.predict(X)
            
            # Ensure state 1 is always the "High Volatility" state
            state_0_vix_mean = df.iloc[states == 0]["vix"].mean()
            state_1_vix_mean = df.iloc[states == 1]["vix"].mean()
            
            if state_0_vix_mean > state_1_vix_mean:
                states = 1 - states
                
            df["market_regime"] = states
            
            # Make index tz-naive
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
                
            return df[["market_regime"]]
            
        except Exception as e:
            logger.error(f"Error training HMM regime model: {e}")
            return pd.DataFrame()

    @staticmethod
    def add_regime_features(df: pd.DataFrame, period: str = "2y") -> pd.DataFrame:
        """Adds market regime features to the stock dataframe by joining on Date."""
        if df.empty:
            return df
            
        regime_df = RegimeFeatures._fetch_and_train_hmm(period=period)
        if regime_df.empty:
            logger.warning("No regime data available. Skipping regime features.")
            return df
            
        original_tz = df.index.tz
        if original_tz is not None:
            df.index = df.index.tz_localize(None)
            
        # Left join regime feature
        df = df.join(regime_df, how="left")
        
        # Forward fill missing values
        if "market_regime" in df.columns:
            df["market_regime"] = df["market_regime"].ffill().fillna(0)
            
        if original_tz is not None:
            df.index = df.index.tz_localize(original_tz)
            
        return df
