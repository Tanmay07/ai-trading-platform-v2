"""
Volume Features Module — Volume-based indicators for market analysis.

This module complements the core technical indicators with volume-specific
features that reveal buying/selling pressure, institutional activity, and
potential breakout signals.

Columns added by ``VolumeFeatures.add_volume_features()``:
    * ``volume_change``       – 1-bar percentage change in volume.
    * ``volume_ma_5``         – 5-period SMA of volume.
    * ``volume_ma_10``        – 10-period SMA of volume.
    * ``volume_ma_20``        – 20-period SMA of volume.
    * ``volume_ratio``        – Current volume ÷ 20-period volume MA.
    * ``volume_breakout``     – Boolean flag: volume > 2 × 20-period MA.
    * ``obv``                 – On-Balance Volume (if not already present).
    * ``volume_price_trend``  – Cumulative volume-price trend indicator.

Disclaimer:
    This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VolumeFeatures:
    """Volume-based feature calculations.

    All methods are **static** and follow the same contract as
    ``TechnicalFeatures``: accept a DataFrame, append columns, return it.
    """

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame) -> None:
        """Ensure the DataFrame has the columns we need."""
        required = {"Close", "Volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"DataFrame is missing required columns for volume "
                f"features: {missing}"
            )

    @staticmethod
    def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
        """Add all volume-derived features to the DataFrame.

        Args:
            df: DataFrame with at least ``Close`` and ``Volume`` columns.
                If ``High`` and ``Low`` are also present they will be used
                for more accurate OBV computation (though not strictly
                required here).

        Returns:
            DataFrame with volume feature columns appended.

        Raises:
            ValueError: If ``Close`` or ``Volume`` columns are missing.
        """
        if df.empty:
            logger.warning(
                "add_volume_features() called with empty DataFrame — "
                "returning as-is."
            )
            return df

        VolumeFeatures._validate_dataframe(df)

        close = df["Close"]
        volume = df["Volume"]

        # ---- Volume change (1-bar %) ------------------------------------
        df["volume_change"] = volume.pct_change()

        # ---- Volume moving averages -------------------------------------
        df["volume_ma_5"] = volume.rolling(window=5, min_periods=5).mean()
        df["volume_ma_10"] = volume.rolling(window=10, min_periods=10).mean()
        df["volume_ma_20"] = volume.rolling(window=20, min_periods=20).mean()

        # ---- Volume ratio (relative volume) -----------------------------
        # How today's volume compares to the 20-day average.
        # > 1 means above-average activity.
        vol_ma_20_safe = df["volume_ma_20"].replace(0, np.nan)
        df["volume_ratio"] = volume / vol_ma_20_safe

        # ---- Volume breakout flag ---------------------------------------
        # Volume more than 2× the 20-day MA often signals institutional
        # participation or a significant news event.
        df["volume_breakout"] = (volume > 2.0 * df["volume_ma_20"]).astype(int)

        # ---- On-Balance Volume (only if not already computed) -----------
        if "obv" not in df.columns:
            direction = np.sign(close.diff())
            direction.iloc[0] = 0.0
            df["obv"] = (direction * volume).cumsum()

        # ---- Volume-Price Trend (VPT) -----------------------------------
        # VPT accumulates volume weighted by the price's percentage change.
        # Rising VPT with rising price confirms an up-trend.
        price_change_pct = close.pct_change().fillna(0.0)
        df["volume_price_trend"] = (price_change_pct * volume).cumsum()

        logger.info(
            "add_volume_features() complete — added volume columns to "
            "DataFrame (%d rows).",
            len(df),
        )
        return df
