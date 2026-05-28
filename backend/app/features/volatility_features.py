"""
Volatility Features Module — Risk and volatility metrics.

Provides a set of volatility-based features that capture market uncertainty,
risk regimes, and potential breakout / squeeze conditions.

Columns added by ``VolatilityFeatures.add_volatility_features()``:
    * ``rolling_volatility_10``  – Annualised 10-day rolling volatility.
    * ``rolling_volatility_20``  – Annualised 20-day rolling volatility.
    * ``rolling_volatility_60``  – Annualised 60-day rolling volatility.
    * ``atr_pct``                – ATR as % of closing price (if ATR present).
    * ``bb_bandwidth``           – Bollinger Band width ratio (if BB present).
    * ``high_low_range``         – Daily (High − Low) / Close.
    * ``avg_high_low_range``     – 20-day SMA of ``high_low_range``.
    * ``parkinson_volatility``   – Parkinson (1980) high-low volatility estimator.

Disclaimer:
    This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Number of trading days in a year (Indian market: ~252)
_TRADING_DAYS_PER_YEAR = 252


class VolatilityFeatures:
    """Volatility-based feature calculations.

    All methods are **static** and append columns to the input DataFrame.
    """

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame) -> None:
        """Ensure the DataFrame has at least Close, High, and Low."""
        required = {"Close", "High", "Low"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"DataFrame is missing required columns for volatility "
                f"features: {missing}"
            )

    @staticmethod
    def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add all volatility-derived features to the DataFrame.

        If ATR or Bollinger Band columns have already been computed (e.g. by
        ``TechnicalFeatures``), this method will leverage them.  Otherwise,
        ATR-dependent and BB-dependent columns are skipped with a debug log.

        Args:
            df: DataFrame with at least ``Open, High, Low, Close`` columns.

        Returns:
            DataFrame with volatility feature columns appended.

        Raises:
            ValueError: If ``Close``, ``High``, or ``Low`` columns are missing.
        """
        if df.empty:
            logger.warning(
                "add_volatility_features() called with empty DataFrame — "
                "returning as-is."
            )
            return df

        VolatilityFeatures._validate_dataframe(df)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        # ================================================================
        # 1. Annualised rolling volatility (close-to-close)
        # ================================================================
        # Standard deviation of log-returns, annualised by √252.
        daily_return = close.pct_change()
        sqrt_252 = np.sqrt(_TRADING_DAYS_PER_YEAR)

        for window in (10, 20, 60):
            col = f"rolling_volatility_{window}"
            df[col] = daily_return.rolling(
                window=window, min_periods=window
            ).std() * sqrt_252

        # ================================================================
        # 2. ATR as percentage of close (leverage existing ATR if available)
        # ================================================================
        if "atr" in df.columns:
            close_safe = close.replace(0, np.nan)
            df["atr_pct"] = (df["atr"] / close_safe) * 100.0
        else:
            logger.debug(
                "Column 'atr' not found — skipping atr_pct.  Run "
                "TechnicalFeatures.add_atr() first."
            )

        # ================================================================
        # 3. Bollinger Bandwidth (leverage existing BB columns)
        # ================================================================
        if {"bb_upper", "bb_lower", "bb_middle"}.issubset(df.columns):
            bb_middle_safe = df["bb_middle"].replace(0, np.nan)
            df["bb_bandwidth"] = (
                (df["bb_upper"] - df["bb_lower"]) / bb_middle_safe
            )
        else:
            logger.debug(
                "Bollinger Band columns not found — skipping bb_bandwidth.  "
                "Run TechnicalFeatures.add_bollinger_bands() first."
            )

        # ================================================================
        # 4. Daily high-low range normalised by close
        # ================================================================
        close_safe = close.replace(0, np.nan)
        df["high_low_range"] = (high - low) / close_safe

        # 20-day average of the high-low range
        df["avg_high_low_range"] = (
            df["high_low_range"]
            .rolling(window=20, min_periods=20)
            .mean()
        )

        # ================================================================
        # 5. Parkinson volatility estimator (1980)
        # ================================================================
        # Uses the high-low range which captures intraday volatility better
        # than close-to-close methods.
        #
        #   σ² = (1 / 4n·ln2) Σ [ln(H_i / L_i)]²
        #
        # We compute a *rolling* version over 20 bars and annualise it.
        log_hl_sq = np.log(high / low.replace(0, np.nan)) ** 2
        parkinson_window = 20
        rolling_sum = log_hl_sq.rolling(
            window=parkinson_window, min_periods=parkinson_window
        ).sum()
        parkinson_var = rolling_sum / (
            4.0 * parkinson_window * np.log(2)
        )
        # Annualise: multiply variance by 252, then sqrt
        df["parkinson_volatility"] = np.sqrt(
            parkinson_var * _TRADING_DAYS_PER_YEAR
        )

        logger.info(
            "add_volatility_features() complete — added volatility columns "
            "to DataFrame (%d rows).",
            len(df),
        )
        return df
