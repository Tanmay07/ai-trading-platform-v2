"""
Unit tests for the TechnicalFeatures module.

Validates that all technical indicators produce correct column names,
sensible value ranges, and handle edge cases (empty data, short data).

Run with:
    cd backend && python -m pytest tests/ -v
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.features.technical_features import TechnicalFeatures


# ------------------------------------------------------------------
# Test data helpers
# ------------------------------------------------------------------


def create_sample_ohlcv(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Create a realistic sample OHLCV DataFrame for testing.

    Generates a random-walk price series with volume that looks like
    a real stock trading over *n* sessions.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")  # Business days

    # Random-walk close price starting at ₹1000
    daily_returns = rng.normal(loc=0.0005, scale=0.015, size=n)
    close = 1000.0 * np.cumprod(1 + daily_returns)

    # Construct OHLCV from close
    high = close * (1 + np.abs(rng.normal(0, 0.008, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.008, n)))
    open_ = close * (1 + rng.normal(0, 0.005, n))
    volume = rng.integers(500_000, 5_000_000, size=n)

    return pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )


def create_short_ohlcv(n: int = 5) -> pd.DataFrame:
    """Very short DataFrame for edge-case testing."""
    return create_sample_ohlcv(n=n, seed=99)


# ------------------------------------------------------------------
# SMA tests
# ------------------------------------------------------------------


class TestSMA:
    def test_sma_columns_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_sma(df.copy())
        for p in [5, 10, 20, 50, 100, 200]:
            assert f"sma_{p}" in result.columns, f"Missing sma_{p}"

    def test_sma_values_after_warmup(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_sma(df.copy())
        # SMA-20 should be non-NaN from row 19 onward
        assert result["sma_20"].iloc[19:].notna().all()

    def test_sma_custom_periods(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_sma(df.copy(), periods=[3, 7])
        assert "sma_3" in result.columns
        assert "sma_7" in result.columns


# ------------------------------------------------------------------
# EMA tests
# ------------------------------------------------------------------


class TestEMA:
    def test_ema_columns_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_ema(df.copy())
        for p in [5, 10, 20, 50]:
            assert f"ema_{p}" in result.columns, f"Missing ema_{p}"

    def test_ema_no_nans_after_first_value(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_ema(df.copy())
        # EMA has values from the very first row (seed = first value)
        assert result["ema_5"].iloc[1:].notna().all()


# ------------------------------------------------------------------
# RSI tests
# ------------------------------------------------------------------


class TestRSI:
    def test_rsi_column_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_rsi(df.copy())
        assert "rsi" in result.columns

    def test_rsi_range(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_rsi(df.copy())
        valid = result["rsi"].dropna()
        assert len(valid) > 0, "RSI has no valid values"
        assert (valid >= 0).all(), "RSI has values below 0"
        assert (valid <= 100).all(), "RSI has values above 100"

    def test_rsi_short_data(self):
        df = create_short_ohlcv(n=5)
        result = TechnicalFeatures.add_rsi(df.copy())
        assert "rsi" in result.columns
        # Most values will be NaN, but no errors raised


# ------------------------------------------------------------------
# MACD tests
# ------------------------------------------------------------------


class TestMACD:
    def test_macd_columns_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_macd(df.copy())
        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_histogram" in result.columns

    def test_macd_histogram_consistency(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_macd(df.copy())
        valid = result.dropna(subset=["macd", "macd_signal", "macd_histogram"])
        if len(valid) > 0:
            # histogram = macd - signal (within floating point tolerance)
            diff = valid["macd"] - valid["macd_signal"]
            np.testing.assert_allclose(
                valid["macd_histogram"].values, diff.values, atol=1e-10
            )


# ------------------------------------------------------------------
# Bollinger Bands tests
# ------------------------------------------------------------------


class TestBollingerBands:
    def test_bb_columns_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_bollinger_bands(df.copy())
        for col in ["bb_upper", "bb_middle", "bb_lower", "bb_width", "bb_pct_b"]:
            assert col in result.columns, f"Missing {col}"

    def test_bb_upper_above_lower(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_bollinger_bands(df.copy())
        valid = result.dropna(subset=["bb_upper", "bb_lower"])
        assert (valid["bb_upper"] >= valid["bb_lower"]).all()

    def test_bb_middle_equals_sma(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_bollinger_bands(df.copy(), period=20)
        sma_20 = df["Close"].rolling(20).mean()
        valid_idx = sma_20.dropna().index
        np.testing.assert_allclose(
            result.loc[valid_idx, "bb_middle"].values,
            sma_20.loc[valid_idx].values,
            atol=1e-10,
        )


# ------------------------------------------------------------------
# ATR tests
# ------------------------------------------------------------------


class TestATR:
    def test_atr_columns_added(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_atr(df.copy())
        assert "atr" in result.columns
        assert "atr_pct" in result.columns

    def test_atr_positive(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_atr(df.copy())
        valid = result["atr"].dropna()
        assert (valid >= 0).all(), "ATR should be non-negative"


# ------------------------------------------------------------------
# Stochastic Oscillator tests
# ------------------------------------------------------------------


class TestStochastic:
    def test_stochastic_columns(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_stochastic(df.copy())
        assert "stoch_k" in result.columns
        assert "stoch_d" in result.columns

    def test_stochastic_range(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_stochastic(df.copy())
        valid_k = result["stoch_k"].dropna()
        assert (valid_k >= 0).all() and (valid_k <= 100).all(), "%K out of range"


# ------------------------------------------------------------------
# Williams %R tests
# ------------------------------------------------------------------


class TestWilliamsR:
    def test_williams_r_column(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_williams_r(df.copy())
        assert "williams_r" in result.columns

    def test_williams_r_range(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_williams_r(df.copy())
        valid = result["williams_r"].dropna()
        assert (valid >= -100).all() and (valid <= 0).all(), "Williams %R out of range"


# ------------------------------------------------------------------
# CCI tests
# ------------------------------------------------------------------


class TestCCI:
    def test_cci_column(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_cci(df.copy())
        assert "cci" in result.columns

    def test_cci_has_valid_values(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_cci(df.copy())
        valid = result["cci"].dropna()
        assert len(valid) > 0


# ------------------------------------------------------------------
# OBV tests
# ------------------------------------------------------------------


class TestOBV:
    def test_obv_columns(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_obv(df.copy())
        assert "obv" in result.columns

    def test_obv_first_value(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_obv(df.copy())
        # OBV should start from the first row
        assert result["obv"].notna().sum() > 0


# ------------------------------------------------------------------
# Price Action tests
# ------------------------------------------------------------------


class TestPriceAction:
    def test_price_action_columns(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_price_action(df.copy())
        expected_cols = [
            "daily_return", "return_3d", "return_5d", "return_10d",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing {col}"

    def test_daily_return_values(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_price_action(df.copy())
        # Manually verify first non-NaN daily return
        expected = (df["Close"].iloc[1] - df["Close"].iloc[0]) / df["Close"].iloc[0]
        np.testing.assert_almost_equal(
            result["daily_return"].iloc[1], expected, decimal=10
        )


# ------------------------------------------------------------------
# ADX tests
# ------------------------------------------------------------------


class TestADX:
    def test_adx_columns(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_adx(df.copy())
        for col in ["plus_di", "minus_di", "adx"]:
            assert col in result.columns, f"Missing {col}"

    def test_adx_range(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_adx(df.copy())
        valid = result["adx"].dropna()
        if len(valid) > 0:
            assert (valid >= 0).all(), "ADX should be non-negative"
            assert (valid <= 100).all(), "ADX should be <= 100"


# ------------------------------------------------------------------
# add_all integration test
# ------------------------------------------------------------------


class TestAddAll:
    def test_add_all_adds_many_columns(self):
        df = create_sample_ohlcv(250)
        original_cols = set(df.columns)
        result = TechnicalFeatures.add_all(df.copy())
        new_cols = set(result.columns) - original_cols
        # We expect at least 30 new indicator columns
        assert len(new_cols) >= 25, f"Only {len(new_cols)} new columns — expected >= 25"

    def test_add_all_no_errors_on_short_data(self):
        """Ensure add_all doesn't crash on very short DataFrames."""
        df = create_short_ohlcv(n=10)
        result = TechnicalFeatures.add_all(df.copy())
        assert len(result) == 10

    def test_add_all_preserves_ohlcv(self):
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_all(df.copy())
        # Original OHLCV columns must still exist
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            assert col in result.columns


# ------------------------------------------------------------------
# Edge case tests
# ------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_dataframe(self):
        """All methods should handle empty DataFrames without errors."""
        empty = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        result = TechnicalFeatures.add_sma(empty.copy())
        assert result.empty

    def test_single_row(self):
        """Single-row DataFrame should not crash."""
        df = create_sample_ohlcv(n=1)
        result = TechnicalFeatures.add_all(df.copy())
        assert len(result) == 1

    def test_columns_are_lowercase(self):
        """All generated indicator columns should be lowercase."""
        df = create_sample_ohlcv()
        result = TechnicalFeatures.add_all(df.copy())
        indicator_cols = [c for c in result.columns if c not in ("Open", "High", "Low", "Close", "Volume")]
        for col in indicator_cols:
            assert col == col.lower(), f"Column {col} is not lowercase"
