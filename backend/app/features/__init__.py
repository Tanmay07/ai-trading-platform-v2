"""
Feature Engineering Module for AI Trading Platform.

This module provides a comprehensive suite of technical analysis feature
engineering tools built entirely with pandas and numpy — no external TA
libraries required.

Exports:
    TechnicalFeatures  – SMA, EMA, RSI, MACD, Bollinger Bands, ADX, ATR,
                          Stochastic, Williams %R, CCI, VWAP, OBV, price action.
    VolumeFeatures     – Volume ratios, breakouts, and volume-price trend.
    VolatilityFeatures – Rolling volatility, Parkinson estimator, range metrics.
    FeaturePipeline    – Orchestrator that chains all feature modules together.

Disclaimer:
    This is for educational and research purposes only, not financial advice.
"""

from app.features.technical_features import TechnicalFeatures
from app.features.volume_features import VolumeFeatures
from app.features.volatility_features import VolatilityFeatures
from app.features.feature_pipeline import FeaturePipeline

__all__ = [
    "TechnicalFeatures",
    "VolumeFeatures",
    "VolatilityFeatures",
    "FeaturePipeline",
]
