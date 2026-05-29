"""
ML Data Preparer — Phase 3

Creates feature matrices and target labels from historical stock data
for ML model training.

The target is a ternary classification of the *forward* N-day return:
    UP      → return > +threshold  (default +1%)
    DOWN    → return < −threshold  (default −1%)
    NEUTRAL → return within ±threshold

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any, Tuple

import numpy as np
import pandas as pd

from app.config import settings
from app.data.historical_data_service import HistoricalDataService
from app.data.market_data_service import MarketDataService
from app.features.feature_pipeline import FeaturePipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Columns to drop — they leak future info or are raw OHLCV
_DROP_COLUMNS = frozenset({
    "Open", "High", "Low", "Close", "Volume",
    "future_return", "target",
    # Absolute price columns that vary by stock — use relative features instead
    "vwap",
})

# Label mapping
LABEL_MAP = {"DOWN": 0, "NEUTRAL": 1, "UP": 2}
LABEL_NAMES = {v: k for k, v in LABEL_MAP.items()}


class MLDataPreparer:
    """Prepares training data from raw OHLCV + technical features.

    Usage::

        preparer = MLDataPreparer()
        X, y, feature_names = preparer.prepare_training_data("RELIANCE.NS")
        # X: numpy array (n_samples, n_features)
        # y: numpy array (n_samples,) with values in {0, 1, 2}
        # feature_names: list of column names
    """

    def __init__(
        self,
        feature_pipeline: FeaturePipeline | None = None,
        historical_data: HistoricalDataService | None = None,
    ) -> None:
        self.feature_pipeline = feature_pipeline or FeaturePipeline()
        if historical_data is not None:
            self.historical_data = historical_data
        else:
            self.historical_data = HistoricalDataService(
                market_data_service=MarketDataService()
            )

    def prepare_training_data(
        self,
        symbol: str,
        period: str = "2y",
        forward_days: int | None = None,
        up_threshold: float | None = None,
        down_threshold: float | None = None,
    ) -> Tuple[np.ndarray, np.ndarray, list[str]]:
        """Fetch historical data, compute features, and create labels.

        Args:
            symbol: NSE symbol with ``.NS`` suffix.
            period: yfinance history period (default ``"2y"``).
            forward_days: Prediction horizon in trading days.
                Defaults to ``settings.ML_FORWARD_DAYS``.
            up_threshold: Return threshold for UP label.
                Defaults to ``settings.ML_UP_THRESHOLD``.
            down_threshold: Return threshold for DOWN label.
                Defaults to ``settings.ML_DOWN_THRESHOLD``.

        Returns:
            Tuple of ``(X, y, feature_names)`` where:
                - ``X`` is a 2D numpy array of shape ``(n_samples, n_features)``
                - ``y`` is a 1D numpy array of integer labels ``{0, 1, 2}``
                - ``feature_names`` is a list of column names

        Raises:
            ValueError: If insufficient data after cleaning.
        """
        forward_days = forward_days or settings.ML_FORWARD_DAYS
        up_threshold = up_threshold if up_threshold is not None else settings.ML_UP_THRESHOLD
        down_threshold = down_threshold if down_threshold is not None else settings.ML_DOWN_THRESHOLD

        logger.info(
            "Preparing training data for %s (period=%s, forward=%dd)",
            symbol, period, forward_days,
        )

        # 1. Fetch OHLCV history
        df = self.historical_data.get_historical_data(
            symbol=symbol, period=period, interval="1d",
        )

        if df is None or df.empty:
            raise ValueError(f"No historical data available for {symbol}")

        logger.info("Fetched %d rows of OHLCV data for %s", len(df), symbol)

        # 2. Compute all technical features
        df = self.feature_pipeline.compute_all_features(df)

        # 3. Create forward-looking labels
        df = self._create_labels(df, forward_days, up_threshold, down_threshold)

        # 4. Clean up
        X, y, feature_names = self._clean_and_extract(df)

        logger.info(
            "Training data ready for %s — %d samples, %d features, "
            "class distribution: UP=%d, NEUTRAL=%d, DOWN=%d",
            symbol, X.shape[0], X.shape[1],
            int((y == LABEL_MAP["UP"]).sum()),
            int((y == LABEL_MAP["NEUTRAL"]).sum()),
            int((y == LABEL_MAP["DOWN"]).sum()),
        )

        return X, y, feature_names

    def prepare_prediction_features(
        self,
        symbol: str,
        df_features: pd.DataFrame | None = None,
    ) -> Tuple[np.ndarray, list[str]]:
        """Prepare features for a single prediction (no labels needed).

        Args:
            symbol: NSE symbol with ``.NS`` suffix.
            df_features: Pre-computed feature DataFrame. If ``None``,
                features are fetched and computed from scratch.

        Returns:
            Tuple of ``(X, feature_names)`` where X has shape ``(1, n_features)``.
        """
        if df_features is None:
            df = self.historical_data.get_historical_data(
                symbol=symbol,
                period=settings.YFINANCE_HISTORY_PERIOD,
                interval="1d",
            )
            if df is None or df.empty:
                raise ValueError(f"No data available for {symbol}")
            df_features = self.feature_pipeline.compute_all_features(df)

        # Select feature columns (same logic as training but no label)
        feature_cols = self._get_feature_columns(df_features)

        # Take last row
        last_row = df_features[feature_cols].iloc[[-1]]

        # Fill NaN with 0 for robustness
        last_row = last_row.fillna(0)

        # Replace inf values
        last_row = last_row.replace([np.inf, -np.inf], 0)

        return last_row.values.astype(np.float64), list(feature_cols)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_labels(
        df: pd.DataFrame,
        forward_days: int,
        up_threshold: float,
        down_threshold: float,
    ) -> pd.DataFrame:
        """Add forward return and ternary target label columns.

        The label is based on the *future* N-day return, which means the
        last ``forward_days`` rows will have ``NaN`` targets and are
        dropped during cleaning.
        """
        # Forward return: (Close[t+N] / Close[t]) - 1
        df["future_return"] = df["Close"].pct_change(periods=forward_days).shift(-forward_days)

        # Ternary label
        conditions = [
            df["future_return"] > up_threshold,
            df["future_return"] < down_threshold,
        ]
        choices = [LABEL_MAP["UP"], LABEL_MAP["DOWN"]]
        df["target"] = np.select(conditions, choices, default=LABEL_MAP["NEUTRAL"])

        return df

    def _clean_and_extract(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, list[str]]:
        """Drop NaN rows, extract feature matrix X and label vector y."""
        # Get feature columns
        feature_cols = self._get_feature_columns(df)

        # Subset to features + target
        subset = df[feature_cols + ["target"]].copy()

        # Drop rows with NaN in any feature column or target
        subset = subset.dropna()

        # Replace inf values in features
        subset[feature_cols] = subset[feature_cols].replace([np.inf, -np.inf], 0)

        if len(subset) < settings.ML_MIN_TRAINING_ROWS:
            raise ValueError(
                f"Only {len(subset)} clean rows available, need at least "
                f"{settings.ML_MIN_TRAINING_ROWS}. Try a longer history period."
            )

        X = subset[feature_cols].values.astype(np.float64)
        y = subset["target"].values.astype(np.int32)

        return X, y, list(feature_cols)

    @staticmethod
    def _get_feature_columns(df: pd.DataFrame) -> list[str]:
        """Return sorted list of numeric feature columns, excluding drop cols."""
        feature_cols = []
        for col in df.columns:
            if col in _DROP_COLUMNS:
                continue
            if col == "target":
                continue
            # Only include numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                feature_cols.append(col)
        return sorted(feature_cols)

    @staticmethod
    def get_label_name(label_int: int) -> str:
        """Map integer label back to string name."""
        return LABEL_NAMES.get(label_int, "UNKNOWN")
