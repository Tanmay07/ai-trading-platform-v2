"""
Feature Pipeline — Unified Orchestrator for all Feature Engineering.

``FeaturePipeline`` chains the three feature modules in the correct order
so that dependent features (e.g. ``bb_bandwidth`` needs Bollinger Bands
from ``TechnicalFeatures``) are satisfied automatically.

Usage::

    from app.features import FeaturePipeline

    pipeline = FeaturePipeline()
    df = pipeline.compute_all_features(ohlcv_dataframe)

    # Or fetch + compute in one call:
    df = pipeline.compute_features_for_symbol("RELIANCE.NS", period="1y")

Disclaimer:
    This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.features.technical_features import TechnicalFeatures
from app.features.volume_features import VolumeFeatures
from app.features.volatility_features import VolatilityFeatures
from app.utils.logger import get_logger

# Base OHLCV columns that are NOT features
_OHLCV_COLUMNS = {"Open", "High", "Low", "Close", "Volume"}


class FeaturePipeline:
    """Orchestrates all feature engineering modules into a unified pipeline.

    The pipeline runs modules in a fixed order so that downstream modules
    can leverage columns created by upstream ones:

        1. **TechnicalFeatures** – trend, momentum, volatility bands, OBV …
        2. **VolumeFeatures**    – volume ratios, breakout flags, VPT …
        3. **VolatilityFeatures** – rolling vol, Parkinson, ATR %, BB width …

    Attributes:
        logger: Module-level logger instance.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    # Core pipeline
    # ------------------------------------------------------------------

    def compute_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering: technical, volume, volatility.

        Args:
            df: DataFrame with OHLCV columns
                (``Open``, ``High``, ``Low``, ``Close``, ``Volume``).

        Returns:
            DataFrame with all feature columns added.
            The first *N* rows will contain ``NaN`` for rolling calculations
            — this is expected behaviour.

        Raises:
            ValueError: If required OHLCV columns are missing.
        """
        if df.empty:
            self.logger.warning(
                "compute_all_features() received an empty DataFrame."
            )
            return df

        # Validate input columns
        missing = _OHLCV_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Input DataFrame is missing required OHLCV columns: {missing}"
            )

        self.logger.info(
            "Starting feature pipeline — input shape: %s", df.shape
        )

        # 1. Technical indicators (trend, momentum, volatility bands, OBV)
        try:
            df = TechnicalFeatures.add_all(df)
            self.logger.debug(
                "TechnicalFeatures complete — columns: %d", len(df.columns)
            )
        except Exception:
            self.logger.exception("Error in TechnicalFeatures pipeline.")
            raise

        # 2. Volume features (ratios, breakout flags, VPT)
        try:
            df = VolumeFeatures.add_volume_features(df)
            self.logger.debug(
                "VolumeFeatures complete — columns: %d", len(df.columns)
            )
        except Exception:
            self.logger.exception("Error in VolumeFeatures pipeline.")
            raise

        # 3. Volatility features (rolling vol, Parkinson, bb_bandwidth, …)
        try:
            df = VolatilityFeatures.add_volatility_features(df)
            self.logger.debug(
                "VolatilityFeatures complete — columns: %d", len(df.columns)
            )
        except Exception:
            self.logger.exception("Error in VolatilityFeatures pipeline.")
            raise

        feature_count = len(df.columns) - len(_OHLCV_COLUMNS)
        self.logger.info(
            "Feature pipeline complete — %d features across %d rows.",
            feature_count,
            len(df),
        )
        return df

    # ------------------------------------------------------------------
    # Symbol-level convenience
    # ------------------------------------------------------------------

    def compute_features_for_symbol(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Fetch historical data and compute all features for a symbol.

        This is a convenience wrapper that pulls data via
        ``HistoricalDataService`` and pipes it through the full pipeline.

        Args:
            symbol: NSE symbol with ``.NS`` suffix (e.g. ``"RELIANCE.NS"``).
            period: yfinance-compatible period string (default ``"1y"``).
            interval: yfinance-compatible interval string (default ``"1d"``).

        Returns:
            DataFrame enriched with all feature columns.

        Raises:
            ValueError: If the fetched data is empty or symbol is invalid.
        """
        # Import here to avoid circular imports at module load time
        from app.data.historical_data_service import HistoricalDataService
        from app.data.market_data_service import MarketDataService

        self.logger.info(
            "Computing features for %s (period=%s, interval=%s)",
            symbol, period, interval,
        )

        market_svc = MarketDataService()
        data_service = HistoricalDataService(market_data_service=market_svc)
        df = data_service.get_historical_data(
            symbol=symbol, period=period, interval=interval
        )

        if df is None or df.empty:
            raise ValueError(
                f"No historical data returned for symbol '{symbol}' "
                f"with period='{period}'."
            )

        return self.compute_all_features(df)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_feature_names(self, df: pd.DataFrame | None = None) -> List[str]:
        """Return the list of feature column names (excluding raw OHLCV).

        If *df* is provided, feature names are derived from its actual
        columns.  Otherwise a "dry-run" is performed on a tiny synthetic
        DataFrame to enumerate all columns the pipeline would produce.

        Args:
            df: Optional DataFrame that has already been through the pipeline.

        Returns:
            Sorted list of feature column names.
        """
        if df is not None:
            return sorted(
                [c for c in df.columns if c not in _OHLCV_COLUMNS]
            )

        # Dry-run with minimal synthetic data (300 rows to cover 252-day
        # rolling windows).
        import numpy as np  # local import to keep module-level lean

        n = 300
        synthetic = pd.DataFrame(
            {
                "Open": np.random.uniform(100, 200, n),
                "High": np.random.uniform(100, 200, n),
                "Low": np.random.uniform(100, 200, n),
                "Close": np.random.uniform(100, 200, n),
                "Volume": np.random.randint(1_000, 1_000_000, n),
            }
        )
        # Ensure High >= Low for realistic data
        synthetic["High"] = synthetic[["Open", "High", "Low", "Close"]].max(axis=1)
        synthetic["Low"] = synthetic[["Open", "High", "Low", "Close"]].min(axis=1)

        enriched = self.compute_all_features(synthetic)
        return sorted(
            [c for c in enriched.columns if c not in _OHLCV_COLUMNS]
        )

    def get_latest_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract the most recent row's features as a dictionary.

        Rows with *any* ``NaN`` in the feature columns are dropped first,
        so the returned dict represents the latest row where **all**
        features are computable.

        Args:
            df: DataFrame that has already been through the pipeline.

        Returns:
            Dictionary mapping feature names to their latest values.
            Returns an empty dict if no complete row exists.
        """
        feature_cols = [c for c in df.columns if c not in _OHLCV_COLUMNS]
        if not feature_cols:
            self.logger.warning(
                "get_latest_features() — no feature columns found."
            )
            return {}

        # Drop rows where any feature column is NaN
        clean = df.dropna(subset=feature_cols)
        if clean.empty:
            self.logger.warning(
                "get_latest_features() — all rows have NaN in at least one "
                "feature column.  Returning latest row as-is (may contain NaN)."
            )
            latest = df.iloc[-1]
        else:
            latest = clean.iloc[-1]

        return {col: latest[col] for col in feature_cols}
