"""
Technical Features Module — Pure pandas/numpy Technical Indicator Library.

Implements the following indicators as static methods on ``TechnicalFeatures``:

* **Trend:**       SMA, EMA, MACD, ADX (+DI / −DI), VWAP
* **Momentum:**    RSI, Stochastic %K/%D, Williams %R, CCI
* **Volatility:**  Bollinger Bands, ATR
* **Volume:**      OBV
* **Price Action:** Returns, gaps, breakouts, 52-week distance

Every method follows the same contract:
    Input  → ``pd.DataFrame`` with columns ``[Open, High, Low, Close, Volume]``
    Output → the *same* DataFrame with **new** indicator columns appended.

The first *N* rows will naturally contain ``NaN`` for rolling/exponential
calculations — this is expected and handled downstream by the pipeline.

Disclaimer:
    This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Minimum rows required for the most demanding rolling window (200-period SMA)
# ---------------------------------------------------------------------------
_MIN_ROWS_WARNING = 20


class TechnicalFeatures:
    """Technical indicator calculations using pure pandas/numpy.

    All methods are **static** and **mutate-then-return** the input DataFrame
    by appending new columns.  The caller can chain calls::

        df = TechnicalFeatures.add_sma(df)
        df = TechnicalFeatures.add_rsi(df)

    or simply::

        df = TechnicalFeatures.add_all(df)
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame) -> None:
        """Raise ``ValueError`` if the DataFrame lacks required columns."""
        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"DataFrame is missing required OHLCV columns: {missing}"
            )

    @staticmethod
    def _wilders_smoothing(series: pd.Series, period: int) -> pd.Series:
        """Apply Wilder's smoothing (equivalent to EWM with ``alpha=1/period``).

        Wilder's smoothing is used in RSI, ATR, and ADX calculations.  It is
        an exponential moving average where ``alpha = 1 / period``.

        Args:
            series: Input data series.
            period: Smoothing period.

        Returns:
            Smoothed ``pd.Series``.
        """
        return series.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    # ------------------------------------------------------------------
    # Trend Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def add_sma(
        df: pd.DataFrame,
        periods: List[int] | None = None,
    ) -> pd.DataFrame:
        """Add Simple Moving Averages.

        For each period *p*, a column ``sma_{p}`` is added containing the
        arithmetic mean of the closing price over the last *p* bars.

        Args:
            df: OHLCV DataFrame.
            periods: List of look-back windows.  Defaults to
                ``[5, 10, 20, 50, 100, 200]``.

        Returns:
            DataFrame with ``sma_*`` columns added.
        """
        if periods is None:
            periods = [5, 10, 20, 50, 100, 200]

        TechnicalFeatures._validate_dataframe(df)
        for p in periods:
            df[f"sma_{p}"] = df["Close"].rolling(window=p, min_periods=p).mean()
        return df

    @staticmethod
    def add_ema(
        df: pd.DataFrame,
        periods: List[int] | None = None,
    ) -> pd.DataFrame:
        """Add Exponential Moving Averages.

        EMA reacts faster to recent price changes than SMA.  Uses the standard
        ``span = period`` convention (``alpha = 2 / (period + 1)``).

        Args:
            df: OHLCV DataFrame.
            periods: List of look-back spans.  Defaults to ``[5, 10, 20, 50]``.

        Returns:
            DataFrame with ``ema_*`` columns added.
        """
        if periods is None:
            periods = [5, 10, 20, 50]

        TechnicalFeatures._validate_dataframe(df)
        for p in periods:
            df[f"ema_{p}"] = df["Close"].ewm(span=p, adjust=False).mean()
        return df

    # ------------------------------------------------------------------
    # Momentum Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Relative Strength Index (RSI) using Wilder's smoothing.

        RSI oscillates between 0 and 100:
          * RSI > 70 → traditionally considered **overbought**.
          * RSI < 30 → traditionally considered **oversold**.

        Calculation:
            delta     = Close − Close(−1)
            gain      = max(delta, 0)
            loss      = |min(delta, 0)|
            avg_gain  = Wilder's smoothing of gain
            avg_loss  = Wilder's smoothing of loss
            RS        = avg_gain / avg_loss
            RSI       = 100 − 100 / (1 + RS)

        Args:
            df: OHLCV DataFrame.
            period: RSI look-back period (default 14).

        Returns:
            DataFrame with ``rsi`` column added.
        """
        TechnicalFeatures._validate_dataframe(df)

        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = TechnicalFeatures._wilders_smoothing(gain, period)
        avg_loss = TechnicalFeatures._wilders_smoothing(loss, period)

        rs = avg_gain / avg_loss.replace(0, np.nan)  # avoid division by zero
        df["rsi"] = 100.0 - (100.0 / (1.0 + rs))
        return df

    @staticmethod
    def add_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3,
    ) -> pd.DataFrame:
        """Add Stochastic Oscillator (%K and %D).

        %K measures where the close sits relative to the recent range:
            %K = 100 × (Close − Lowest Low) / (Highest High − Lowest Low)
        %D is the *d_period*-bar SMA of %K (the "signal" line).

        Args:
            df: OHLCV DataFrame.
            k_period: Look-back for %K (default 14).
            d_period: SMA period for %D (default 3).

        Returns:
            DataFrame with ``stoch_k`` and ``stoch_d`` columns.
        """
        TechnicalFeatures._validate_dataframe(df)

        lowest_low = df["Low"].rolling(window=k_period, min_periods=k_period).min()
        highest_high = df["High"].rolling(window=k_period, min_periods=k_period).max()

        range_hl = highest_high - lowest_low
        # Protect against zero range (flat market)
        range_hl = range_hl.replace(0, np.nan)

        df["stoch_k"] = 100.0 * (df["Close"] - lowest_low) / range_hl
        df["stoch_d"] = df["stoch_k"].rolling(window=d_period, min_periods=d_period).mean()
        return df

    @staticmethod
    def add_williams_r(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Williams %R oscillator.

        Williams %R is an inverted Stochastic %K that ranges from −100 to 0:
            %R = −100 × (Highest High − Close) / (Highest High − Lowest Low)

        * %R > −20 → overbought zone.
        * %R < −80 → oversold zone.

        Args:
            df: OHLCV DataFrame.
            period: Look-back window (default 14).

        Returns:
            DataFrame with ``williams_r`` column.
        """
        TechnicalFeatures._validate_dataframe(df)

        highest_high = df["High"].rolling(window=period, min_periods=period).max()
        lowest_low = df["Low"].rolling(window=period, min_periods=period).min()

        range_hl = highest_high - lowest_low
        range_hl = range_hl.replace(0, np.nan)

        df["williams_r"] = -100.0 * (highest_high - df["Close"]) / range_hl
        return df

    @staticmethod
    def add_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Add Commodity Channel Index (CCI).

        CCI measures the deviation of the typical price from its SMA,
        normalised by the mean absolute deviation (MAD):
            TP  = (High + Low + Close) / 3
            CCI = (TP − SMA(TP, period)) / (0.015 × MAD(TP, period))

        The constant 0.015 ensures that roughly 70-80 % of CCI values
        fall between −100 and +100.

        Args:
            df: OHLCV DataFrame.
            period: Look-back window (default 20).

        Returns:
            DataFrame with ``cci`` column.
        """
        TechnicalFeatures._validate_dataframe(df)

        tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
        tp_sma = tp.rolling(window=period, min_periods=period).mean()

        # Mean Absolute Deviation (MAD) — not the same as std
        mad = tp.rolling(window=period, min_periods=period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
        )
        # Protect against zero MAD
        mad = mad.replace(0, np.nan)

        df["cci"] = (tp - tp_sma) / (0.015 * mad)
        return df

    # ------------------------------------------------------------------
    # Trend-Strength / Directional Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def add_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> pd.DataFrame:
        """Add MACD (Moving Average Convergence / Divergence).

        * **MACD Line**  = EMA(Close, fast) − EMA(Close, slow)
        * **Signal Line** = EMA(MACD Line, signal)
        * **Histogram**   = MACD Line − Signal Line

        A positive histogram indicates bullish momentum; negative → bearish.

        Args:
            df: OHLCV DataFrame.
            fast: Fast EMA span (default 12).
            slow: Slow EMA span (default 26).
            signal: Signal EMA span (default 9).

        Returns:
            DataFrame with ``macd``, ``macd_signal``, ``macd_histogram``.
        """
        TechnicalFeatures._validate_dataframe(df)

        ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()

        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        return df

    @staticmethod
    def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average Directional Index (ADX) with +DI and −DI.

        ADX quantifies **trend strength** regardless of direction.
        +DI and −DI indicate the direction of the trend.

        Calculation steps (Wilder's method):
            1. +DM = High − PrevHigh  (if positive *and* > −DM, else 0)
               −DM = PrevLow − Low    (if positive *and* > +DM, else 0)
            2. Smooth +DM, −DM, and True Range with Wilder's EMA.
            3. +DI = 100 × Smoothed(+DM) / Smoothed(TR)
               −DI = 100 × Smoothed(−DM) / Smoothed(TR)
            4. DX  = 100 × |+DI − −DI| / (+DI + −DI)
            5. ADX = Wilder's EMA of DX.

        Interpretation:
            * ADX > 25  → strong trend.
            * ADX < 20  → weak / no trend.

        Args:
            df: OHLCV DataFrame.
            period: Look-back period (default 14).

        Returns:
            DataFrame with ``plus_di``, ``minus_di``, ``adx`` columns.
        """
        TechnicalFeatures._validate_dataframe(df)

        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)

        # --- Directional Movement ---
        plus_dm = high - prev_high
        minus_dm = prev_low - low

        # +DM: positive and larger than −DM
        plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > minus_dm), 0.0)
        # −DM: positive and larger than +DM
        minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0.0)

        # --- True Range ---
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # --- Wilder's Smoothing ---
        smooth_plus_dm = TechnicalFeatures._wilders_smoothing(plus_dm, period)
        smooth_minus_dm = TechnicalFeatures._wilders_smoothing(minus_dm, period)
        smooth_tr = TechnicalFeatures._wilders_smoothing(true_range, period)

        # Avoid division by zero
        smooth_tr = smooth_tr.replace(0, np.nan)

        plus_di = 100.0 * smooth_plus_dm / smooth_tr
        minus_di = 100.0 * smooth_minus_dm / smooth_tr

        di_sum = plus_di + minus_di
        di_sum = di_sum.replace(0, np.nan)

        dx = 100.0 * (plus_di - minus_di).abs() / di_sum
        adx = TechnicalFeatures._wilders_smoothing(dx, period)

        df["plus_di"] = plus_di
        df["minus_di"] = minus_di
        df["adx"] = adx
        return df

    # ------------------------------------------------------------------
    # Volatility Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0,
    ) -> pd.DataFrame:
        """Add Bollinger Bands.

        * **Middle Band** = SMA(Close, period)
        * **Upper Band**  = Middle + std_dev × σ
        * **Lower Band**  = Middle − std_dev × σ
        * **BB Width**    = (Upper − Lower) / Middle
        * **%B**          = (Close − Lower) / (Upper − Lower)
            *  %B > 1 → price above upper band; %B < 0 → below lower band.

        Args:
            df: OHLCV DataFrame.
            period: SMA window (default 20).
            std_dev: Number of standard deviations (default 2).

        Returns:
            DataFrame with ``bb_upper``, ``bb_middle``, ``bb_lower``,
            ``bb_width``, ``bb_pct_b`` columns.
        """
        TechnicalFeatures._validate_dataframe(df)

        rolling_close = df["Close"].rolling(window=period, min_periods=period)
        middle = rolling_close.mean()
        rolling_std = rolling_close.std()

        upper = middle + std_dev * rolling_std
        lower = middle - std_dev * rolling_std

        band_range = upper - lower
        band_range_safe = band_range.replace(0, np.nan)

        df["bb_upper"] = upper
        df["bb_middle"] = middle
        df["bb_lower"] = lower
        df["bb_width"] = band_range / middle.replace(0, np.nan)
        df["bb_pct_b"] = (df["Close"] - lower) / band_range_safe
        return df

    @staticmethod
    def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average True Range (ATR).

        True Range is the greatest of:
            * High − Low
            * |High − Previous Close|
            * |Low  − Previous Close|

        ATR is the Wilder-smoothed average of True Range.
        ``atr_pct`` expresses ATR as a percentage of the closing price.

        Args:
            df: OHLCV DataFrame.
            period: Smoothing period (default 14).

        Returns:
            DataFrame with ``atr`` and ``atr_pct`` columns.
        """
        TechnicalFeatures._validate_dataframe(df)

        high = df["High"]
        low = df["Low"]
        prev_close = df["Close"].shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = TechnicalFeatures._wilders_smoothing(true_range, period)
        df["atr"] = atr

        close_safe = df["Close"].replace(0, np.nan)
        df["atr_pct"] = (atr / close_safe) * 100.0
        return df

    # ------------------------------------------------------------------
    # Volume Indicators
    # ------------------------------------------------------------------

    @staticmethod
    def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Add Volume Weighted Average Price (VWAP).

        For daily data this computes a *cumulative* VWAP from the start of
        the DataFrame (a common approximation when intraday resets are not
        available):
            TP   = (High + Low + Close) / 3
            VWAP = cumsum(TP × Volume) / cumsum(Volume)

        Args:
            df: OHLCV DataFrame.

        Returns:
            DataFrame with ``vwap`` column.
        """
        TechnicalFeatures._validate_dataframe(df)

        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
        cum_vol = df["Volume"].cumsum()
        cum_tp_vol = (typical_price * df["Volume"]).cumsum()

        # Protect against cumulative volume = 0 at the start
        cum_vol_safe = cum_vol.replace(0, np.nan)
        df["vwap"] = cum_tp_vol / cum_vol_safe
        return df

    @staticmethod
    def add_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Add On-Balance Volume (OBV) and its EMA.

        OBV is a running total of volume:
            * Close > Previous Close → OBV += Volume
            * Close < Previous Close → OBV −= Volume
            * Close == Previous Close → OBV unchanged

        ``obv_ema`` is a 20-period EMA of OBV used to identify the OBV trend.

        Args:
            df: OHLCV DataFrame.

        Returns:
            DataFrame with ``obv`` and ``obv_ema`` columns.
        """
        TechnicalFeatures._validate_dataframe(df)

        direction = np.sign(df["Close"].diff())
        # First value has no diff, set to 0
        direction.iloc[0] = 0.0
        df["obv"] = (direction * df["Volume"]).cumsum()
        df["obv_ema"] = df["obv"].ewm(span=20, adjust=False).mean()
        return df

    # ------------------------------------------------------------------
    # Price Action Features
    # ------------------------------------------------------------------

    @staticmethod
    def add_price_action(df: pd.DataFrame) -> pd.DataFrame:
        """Add a suite of price-action / return-based features.

        Columns added:
            * ``daily_return``         – 1-day percentage return.
            * ``return_3d``            – 3-day percentage return.
            * ``return_5d``            – 5-day percentage return.
            * ``return_10d``           – 10-day percentage return.
            * ``gap``                  – Overnight gap: (Open / PrevClose) − 1.
            * ``higher_high``          – Boolean: High > previous High.
            * ``lower_low``            – Boolean: Low < previous Low.
            * ``breakout_20d``         – Boolean: Close > 20-day rolling max.
            * ``distance_from_52w_high`` – Close / 252-day max − 1 (≤ 0).
            * ``distance_from_52w_low``  – Close / 252-day min − 1 (≥ 0).

        Args:
            df: OHLCV DataFrame.

        Returns:
            DataFrame with price-action columns appended.
        """
        TechnicalFeatures._validate_dataframe(df)

        close = df["Close"]
        prev_close = close.shift(1)

        # --- Returns ---
        df["daily_return"] = close.pct_change()
        df["return_3d"] = close.pct_change(periods=3)
        df["return_5d"] = close.pct_change(periods=5)
        df["return_10d"] = close.pct_change(periods=10)

        # --- Gap ---
        df["gap"] = (df["Open"] / prev_close) - 1.0

        # --- Higher high / lower low ---
        df["higher_high"] = (df["High"] > df["High"].shift(1)).astype(int)
        df["lower_low"] = (df["Low"] < df["Low"].shift(1)).astype(int)

        # --- 20-day breakout (close above the *prior* 20-day high) ---
        rolling_max_20 = close.shift(1).rolling(window=20, min_periods=20).max()
        df["breakout_20d"] = (close > rolling_max_20).astype(int)

        # --- Distance from 52-week (252 trading days) extremes ---
        rolling_max_252 = close.rolling(window=252, min_periods=1).max()
        rolling_min_252 = close.rolling(window=252, min_periods=1).min()

        df["distance_from_52w_high"] = (close / rolling_max_252.replace(0, np.nan)) - 1.0
        df["distance_from_52w_low"] = (close / rolling_min_252.replace(0, np.nan)) - 1.0

        return df

    # ------------------------------------------------------------------
    # Convenience: apply everything
    # ------------------------------------------------------------------

    @staticmethod
    def add_all(df: pd.DataFrame) -> pd.DataFrame:
        """Apply **all** technical indicators in a single call.

        Call order:
            1. SMA  →  2. EMA  →  3. RSI  →  4. MACD
            5. Bollinger Bands  →  6. ATR  →  7. ADX  →  8. VWAP
            9. OBV  →  10. Stochastic  →  11. Williams %R  →  12. CCI
            13. Price Action

        Args:
            df: OHLCV DataFrame.

        Returns:
            DataFrame enriched with all indicator columns.

        Raises:
            ValueError: If required columns are missing.
        """
        if df.empty:
            logger.warning("add_all() called with an empty DataFrame — returning as-is.")
            return df

        if len(df) < _MIN_ROWS_WARNING:
            logger.warning(
                "DataFrame has only %d rows; many indicators require more "
                "history and will produce mostly NaN values.",
                len(df),
            )

        TechnicalFeatures._validate_dataframe(df)

        df = TechnicalFeatures.add_sma(df)
        df = TechnicalFeatures.add_ema(df)
        df = TechnicalFeatures.add_rsi(df)
        df = TechnicalFeatures.add_macd(df)
        df = TechnicalFeatures.add_bollinger_bands(df)
        df = TechnicalFeatures.add_atr(df)
        df = TechnicalFeatures.add_adx(df)
        df = TechnicalFeatures.add_vwap(df)
        df = TechnicalFeatures.add_obv(df)
        df = TechnicalFeatures.add_stochastic(df)
        df = TechnicalFeatures.add_williams_r(df)
        df = TechnicalFeatures.add_cci(df)
        df = TechnicalFeatures.add_price_action(df)

        logger.info(
            "add_all() complete — DataFrame now has %d columns (%d rows).",
            len(df.columns),
            len(df),
        )
        return df
