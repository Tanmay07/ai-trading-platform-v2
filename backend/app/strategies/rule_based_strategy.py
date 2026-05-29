"""
Rule-based trading strategy using technical indicators.

Analyzes a DataFrame containing technical features and produces signal scores
across four dimensions: trend, momentum, volume, and volatility.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from app.utils.logger import get_logger


class RuleBasedStrategy:
    """Rule-based trading strategy using technical indicators.

    Produces signals in the range [-1, 1] where:
        -1 = strongly bearish
         0 = neutral
        +1 = strongly bullish

    The strategy evaluates six independent dimensions and combines them
    into a weighted composite score.

    Weights (Phase 3):
        - Trend:      27%  (most reliable in trending markets)
        - Momentum:   23%  (confirms trend direction)
        - Volume:     15%  (validates price moves)
        - Volatility: 11%  (risk-adjusted overlay)
        - Sentiment:   9%  (news sentiment from NLP analysis)
        - ML:         15%  (gradient-boosted model predictions)
    """

    # Weights for combining signal dimensions
    TREND_WEIGHT: float = 0.27
    MOMENTUM_WEIGHT: float = 0.23
    VOLUME_WEIGHT: float = 0.15
    VOLATILITY_WEIGHT: float = 0.11
    SENTIMENT_WEIGHT: float = 0.09
    ML_WEIGHT: float = 0.15

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        df: pd.DataFrame,
        sentiment_data: dict | None = None,
        ml_prediction: dict | None = None,
    ) -> dict:
        """Analyze a DataFrame with pre-computed features and return signal components.

        The method always operates on the **last row** of the DataFrame so that
        the caller only needs to pass in a feature-enriched time-series.

        Args:
            df: DataFrame with OHLCV columns *and* technical indicator columns
                produced by :class:`FeaturePipeline`.
            sentiment_data: Optional sentiment feature dict from
                :class:`SentimentFeatures`.  If provided, sentiment is
                included as a signal dimension.
            ml_prediction: Optional ML prediction dict with keys
                ``direction``, ``probability``, ``confidence``.

        Returns:
            Dictionary with keys:
                - ``trend_signal``      (float, -1 to 1)
                - ``momentum_signal``   (float, -1 to 1)
                - ``volume_signal``     (float, -1 to 1)
                - ``volatility_signal`` (float, -1 to 1)
                - ``sentiment_signal``  (float, -1 to 1)
                - ``ml_signal``         (float, -1 to 1)
                - ``combined_score``    (float, weighted average)
                - ``signal_details``    (dict, detailed breakdown)
        """
        if df is None or df.empty:
            self.logger.warning("Empty DataFrame received — returning neutral signals.")
            return self._neutral_signals()

        try:
            row: pd.Series = df.iloc[-1]
        except IndexError:
            self.logger.warning("Cannot access last row — returning neutral signals.")
            return self._neutral_signals()

        # Evaluate each dimension independently
        trend_score, trend_reasons = self._assess_trend(row)
        momentum_score, momentum_reasons = self._assess_momentum(row)
        volume_score, volume_reasons = self._assess_volume(row)
        volatility_score, volatility_reasons = self._assess_volatility(row)
        sentiment_score, sentiment_reasons = self._assess_sentiment(sentiment_data)
        ml_score, ml_reasons = self._assess_ml_prediction(ml_prediction)

        # Weighted combination
        combined_score: float = (
            trend_score * self.TREND_WEIGHT
            + momentum_score * self.MOMENTUM_WEIGHT
            + volume_score * self.VOLUME_WEIGHT
            + volatility_score * self.VOLATILITY_WEIGHT
            + sentiment_score * self.SENTIMENT_WEIGHT
            + ml_score * self.ML_WEIGHT
        )

        # Clamp to [-1, 1]
        combined_score = float(np.clip(combined_score, -1.0, 1.0))

        signal_details: dict = {
            "trend": {"score": round(trend_score, 4), "reasons": trend_reasons},
            "momentum": {"score": round(momentum_score, 4), "reasons": momentum_reasons},
            "volume": {"score": round(volume_score, 4), "reasons": volume_reasons},
            "volatility": {"score": round(volatility_score, 4), "reasons": volatility_reasons},
            "sentiment": {"score": round(sentiment_score, 4), "reasons": sentiment_reasons},
            "ml": {"score": round(ml_score, 4), "reasons": ml_reasons},
        }

        self.logger.debug(
            "Signals — trend=%.3f  momentum=%.3f  volume=%.3f  "
            "volatility=%.3f  sentiment=%.3f  ml=%.3f  combined=%.3f",
            trend_score,
            momentum_score,
            volume_score,
            volatility_score,
            sentiment_score,
            ml_score,
            combined_score,
        )

        return {
            "trend_signal": round(trend_score, 4),
            "momentum_signal": round(momentum_score, 4),
            "volume_signal": round(volume_score, 4),
            "volatility_signal": round(volatility_score, 4),
            "sentiment_signal": round(sentiment_score, 4),
            "ml_signal": round(ml_score, 4),
            "combined_score": round(combined_score, 4),
            "signal_details": signal_details,
        }

    # ------------------------------------------------------------------
    # Signal assessment helpers
    # ------------------------------------------------------------------

    def _assess_trend(self, row: pd.Series) -> tuple[float, list[str]]:
        """Assess trend based on SMA/EMA positioning.

        Checks:
            - Price vs SMA-20 / SMA-50 / SMA-200
            - SMA-20 vs SMA-50 (golden cross / death cross)
            - EMA-12 vs EMA-26 alignment
        """
        score: float = 0.0
        reasons: list[str] = []

        close = self._safe_get(row, "Close")
        if close is None or close <= 0:
            return 0.0, ["Close price unavailable"]

        # --- Price vs SMAs ---
        sma_20 = self._safe_get(row, "sma_20")
        sma_50 = self._safe_get(row, "sma_50")
        sma_200 = self._safe_get(row, "sma_200")

        if sma_20 is not None and sma_20 > 0:
            if close > sma_20:
                score += 0.15
                reasons.append("Price above SMA-20 (short-term bullish)")
            else:
                score -= 0.15
                reasons.append("Price below SMA-20 (short-term bearish)")

        if sma_50 is not None and sma_50 > 0:
            if close > sma_50:
                score += 0.20
                reasons.append("Price above SMA-50 (medium-term bullish)")
            else:
                score -= 0.20
                reasons.append("Price below SMA-50 (medium-term bearish)")

        if sma_200 is not None and sma_200 > 0:
            if close > sma_200:
                score += 0.25
                reasons.append("Price above SMA-200 (long-term bullish)")
            else:
                score -= 0.25
                reasons.append("Price below SMA-200 (long-term bearish)")

        # --- Golden / Death cross (SMA-20 vs SMA-50) ---
        if sma_20 is not None and sma_50 is not None and sma_50 > 0:
            if sma_20 > sma_50:
                score += 0.20
                reasons.append("SMA-20 above SMA-50 (golden cross zone)")
            else:
                score -= 0.20
                reasons.append("SMA-20 below SMA-50 (death cross zone)")

        # --- EMA alignment ---
        ema_12 = self._safe_get(row, "ema_12")
        ema_26 = self._safe_get(row, "ema_26")
        if ema_12 is not None and ema_26 is not None and ema_26 > 0:
            if ema_12 > ema_26:
                score += 0.20
                reasons.append("EMA-12 above EMA-26 (bullish alignment)")
            else:
                score -= 0.20
                reasons.append("EMA-12 below EMA-26 (bearish alignment)")

        # Clamp to [-1, 1]
        score = float(np.clip(score, -1.0, 1.0))
        return score, reasons

    def _assess_momentum(self, row: pd.Series) -> tuple[float, list[str]]:
        """Assess momentum using RSI, MACD and Stochastic oscillators.

        Checks:
            - RSI zones: oversold (<30) → bullish, overbought (>70) → bearish
            - MACD histogram sign and magnitude
            - Stochastic %K vs %D crossover
        """
        score: float = 0.0
        reasons: list[str] = []

        # --- RSI ---
        rsi = self._safe_get(row, "rsi")
        if rsi is not None:
            if rsi < 30:
                score += 0.40
                reasons.append(f"RSI={rsi:.1f} — oversold, potential reversal up")
            elif rsi < 40:
                score += 0.20
                reasons.append(f"RSI={rsi:.1f} — approaching oversold")
            elif rsi > 70:
                score -= 0.40
                reasons.append(f"RSI={rsi:.1f} — overbought, potential reversal down")
            elif rsi > 60:
                score -= 0.10
                reasons.append(f"RSI={rsi:.1f} — approaching overbought")
            else:
                reasons.append(f"RSI={rsi:.1f} — neutral zone")

        # --- MACD ---
        macd_hist = self._safe_get(row, "macd_histogram")
        macd = self._safe_get(row, "macd")
        macd_signal = self._safe_get(row, "macd_signal")

        if macd_hist is not None:
            if macd_hist > 0:
                score += 0.20
                reasons.append("MACD histogram positive (bullish momentum)")
            else:
                score -= 0.20
                reasons.append("MACD histogram negative (bearish momentum)")

        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                score += 0.15
                reasons.append("MACD above signal line (bullish crossover)")
            else:
                score -= 0.15
                reasons.append("MACD below signal line (bearish crossover)")

        # --- Stochastic Oscillator ---
        stoch_k = self._safe_get(row, "stoch_k")
        stoch_d = self._safe_get(row, "stoch_d")
        if stoch_k is not None:
            if stoch_k < 20:
                score += 0.15
                reasons.append(f"Stochastic %K={stoch_k:.1f} — oversold")
            elif stoch_k > 80:
                score -= 0.15
                reasons.append(f"Stochastic %K={stoch_k:.1f} — overbought")

        if stoch_k is not None and stoch_d is not None:
            if stoch_k > stoch_d and stoch_k < 50:
                score += 0.10
                reasons.append("Stochastic %K crossed above %D (bullish)")
            elif stoch_k < stoch_d and stoch_k > 50:
                score -= 0.10
                reasons.append("Stochastic %K crossed below %D (bearish)")

        # Clamp to [-1, 1]
        score = float(np.clip(score, -1.0, 1.0))
        return score, reasons

    def _assess_volume(self, row: pd.Series) -> tuple[float, list[str]]:
        """Assess volume confirmation for the current price move.

        Checks:
            - Volume vs 20-period average (volume ratio)
            - On-Balance Volume (OBV) trend
            - Volume breakout detection
        """
        score: float = 0.0
        reasons: list[str] = []

        # --- Volume ratio (current / moving average) ---
        volume_ratio = self._safe_get(row, "volume_ratio")
        if volume_ratio is not None:
            if volume_ratio > 2.0:
                score += 0.40
                reasons.append(f"Volume {volume_ratio:.1f}x average — significant breakout")
            elif volume_ratio > 1.5:
                score += 0.25
                reasons.append(f"Volume {volume_ratio:.1f}x average — above-average activity")
            elif volume_ratio > 1.0:
                score += 0.10
                reasons.append(f"Volume {volume_ratio:.1f}x average — moderate")
            elif volume_ratio < 0.5:
                score -= 0.20
                reasons.append(f"Volume {volume_ratio:.1f}x average — very low, weak conviction")
            else:
                score -= 0.05
                reasons.append(f"Volume {volume_ratio:.1f}x average — below average")
        else:
            # Fallback: compare raw volume to volume_sma_20
            volume = self._safe_get(row, "Volume")
            vol_sma = self._safe_get(row, "volume_sma_20")
            if volume is not None and vol_sma is not None and vol_sma > 0:
                ratio = volume / vol_sma
                if ratio > 1.5:
                    score += 0.25
                    reasons.append(f"Volume above 20-day average ({ratio:.1f}x)")
                elif ratio < 0.5:
                    score -= 0.15
                    reasons.append(f"Volume below 20-day average ({ratio:.1f}x)")

        # --- OBV trend ---
        obv = self._safe_get(row, "obv")
        obv_sma = self._safe_get(row, "obv_sma")
        if obv is not None and obv_sma is not None:
            if obv > obv_sma:
                score += 0.25
                reasons.append("OBV above its moving average (accumulation)")
            else:
                score -= 0.25
                reasons.append("OBV below its moving average (distribution)")

        # --- Volume-price trend (positive close + high volume is bullish) ---
        close = self._safe_get(row, "Close")
        prev_close = self._safe_get(row, "prev_close")
        if close is not None and prev_close is not None and prev_close > 0:
            price_change_pct = (close - prev_close) / prev_close
            if volume_ratio is not None:
                if price_change_pct > 0 and volume_ratio > 1.2:
                    score += 0.15
                    reasons.append("Rising price with high volume (strong bullish)")
                elif price_change_pct < 0 and volume_ratio > 1.2:
                    score -= 0.15
                    reasons.append("Falling price with high volume (strong bearish)")

        # Clamp to [-1, 1]
        score = float(np.clip(score, -1.0, 1.0))
        return score, reasons

    def _assess_volatility(self, row: pd.Series) -> tuple[float, list[str]]:
        """Assess the volatility regime as a risk-adjustment overlay.

        High volatility → higher risk → signal skews negative.
        Bollinger squeeze → pending breakout signal.

        Checks:
            - ATR as percentage of price
            - Bollinger Band width / squeeze
            - Rolling annualized volatility
        """
        score: float = 0.0
        reasons: list[str] = []

        close = self._safe_get(row, "Close")

        # --- ATR as % of price ---
        atr = self._safe_get(row, "atr")
        atr_pct = self._safe_get(row, "atr_pct")
        if atr_pct is None and atr is not None and close is not None and close > 0:
            atr_pct = (atr / close) * 100

        if atr_pct is not None:
            if atr_pct > 4.0:
                score -= 0.40
                reasons.append(f"ATR={atr_pct:.2f}% of price — very high volatility (risky)")
            elif atr_pct > 2.5:
                score -= 0.20
                reasons.append(f"ATR={atr_pct:.2f}% of price — elevated volatility")
            elif atr_pct < 1.0:
                score += 0.20
                reasons.append(f"ATR={atr_pct:.2f}% of price — low volatility (stable)")
            else:
                score += 0.05
                reasons.append(f"ATR={atr_pct:.2f}% of price — moderate volatility")

        # --- Bollinger Band width (squeeze detection) ---
        bb_upper = self._safe_get(row, "bb_upper")
        bb_lower = self._safe_get(row, "bb_lower")
        bb_mid = self._safe_get(row, "bb_middle")

        if bb_upper is not None and bb_lower is not None and bb_mid is not None and bb_mid > 0:
            bb_width = (bb_upper - bb_lower) / bb_mid
            if bb_width < 0.05:
                # Tight squeeze — expect a breakout
                score += 0.20
                reasons.append(f"Bollinger squeeze (width={bb_width:.3f}) — breakout imminent")
            elif bb_width > 0.15:
                score -= 0.15
                reasons.append(f"Bollinger wide (width={bb_width:.3f}) — high volatility regime")
            else:
                reasons.append(f"Bollinger width={bb_width:.3f} — normal range")

            # Price position within bands
            if close is not None:
                if close > bb_upper:
                    score -= 0.15
                    reasons.append("Price above upper Bollinger Band (overextended)")
                elif close < bb_lower:
                    score += 0.15
                    reasons.append("Price below lower Bollinger Band (potential bounce)")

        # --- Rolling annualized volatility ---
        rolling_vol = self._safe_get(row, "volatility_20d")
        if rolling_vol is not None:
            annual_vol = rolling_vol * np.sqrt(252) if rolling_vol < 1 else rolling_vol
            if annual_vol > 0.50:
                score -= 0.20
                reasons.append(f"Annualized vol={annual_vol:.1%} — very high risk")
            elif annual_vol > 0.35:
                score -= 0.10
                reasons.append(f"Annualized vol={annual_vol:.1%} — elevated risk")
            elif annual_vol < 0.15:
                score += 0.15
                reasons.append(f"Annualized vol={annual_vol:.1%} — low risk")

        # Clamp to [-1, 1]
        score = float(np.clip(score, -1.0, 1.0))
        return score, reasons

    # ------------------------------------------------------------------
    # Sentiment assessment (Phase 2)
    # ------------------------------------------------------------------

    def _assess_sentiment(
        self, sentiment_data: dict | None
    ) -> tuple[float, list[str]]:
        """Assess the sentiment signal from NLP analysis.

        Maps the aggregated sentiment score and confidence into a
        normalised signal in ``[-1, 1]``.

        Args:
            sentiment_data: Feature dict from :class:`SentimentFeatures`.
                Expected keys: ``sentiment_score``, ``sentiment_confidence``,
                ``sentiment_label``, ``article_count``.

        Returns:
            Tuple of ``(score, reasons)``.
        """
        if not sentiment_data:
            return 0.0, ["No sentiment data available"]

        article_count = sentiment_data.get("article_count", 0)
        if article_count == 0:
            return 0.0, ["No news articles found"]

        raw_score = sentiment_data.get("sentiment_score", 0.0)
        confidence = sentiment_data.get("sentiment_confidence", 0.0)
        label = sentiment_data.get("sentiment_label", "neutral")

        # Scale by confidence — low-confidence sentiment has less impact
        score = raw_score * min(confidence, 1.0)

        reasons: list[str] = []
        score_val = 0.0

        if score > 0.3:
            score_val = min(score, 1.0)
            reasons.append(
                f"Strong bullish sentiment ({label}, score={raw_score:+.2f}, "
                f"{article_count} articles)"
            )
        elif score > 0.1:
            score_val = score
            reasons.append(
                f"Mildly bullish sentiment ({label}, score={raw_score:+.2f}, "
                f"{article_count} articles)"
            )
        elif score < -0.3:
            score_val = max(score, -1.0)
            reasons.append(
                f"Strong bearish sentiment ({label}, score={raw_score:+.2f}, "
                f"{article_count} articles)"
            )
        elif score < -0.1:
            score_val = score
            reasons.append(
                f"Mildly bearish sentiment ({label}, score={raw_score:+.2f}, "
                f"{article_count} articles)"
            )
        else:
            score_val = score
            reasons.append(
                f"Neutral sentiment ({label}, score={raw_score:+.2f}, "
                f"{article_count} articles)"
            )

        # Clamp to [-1, 1]
        score_val = float(np.clip(score_val, -1.0, 1.0))
        return score_val, reasons

    # ------------------------------------------------------------------
    # ML prediction assessment (Phase 3)
    # ------------------------------------------------------------------

    def _assess_ml_prediction(
        self, ml_prediction: dict | None
    ) -> tuple[float, list[str]]:
        """Assess the ML model prediction signal.

        Maps an ML prediction (direction + probability + confidence)
        into a normalised signal in ``[-1, 1]``.

        Args:
            ml_prediction: Prediction dict with keys:
                ``direction`` (str), ``probability`` (float),
                ``confidence`` (float).

        Returns:
            Tuple of ``(score, reasons)``.
        """
        if not ml_prediction:
            return 0.0, ["No ML model available"]

        direction = ml_prediction.get("direction", "NEUTRAL")
        probability = ml_prediction.get("probability", 0.0)
        confidence = ml_prediction.get("confidence", 0.0)

        # Map direction to base signal
        if direction == "UP":
            base = 1.0
        elif direction == "DOWN":
            base = -1.0
        else:
            base = 0.0

        # Scale by confidence (0–1) to avoid overweighting weak predictions
        score = base * confidence
        score = float(np.clip(score, -1.0, 1.0))

        reasons: list[str] = []
        if abs(score) > 0.5:
            reasons.append(
                f"ML predicts {direction} with high confidence "
                f"(prob={probability:.1%}, confidence={confidence:.1%})"
            )
        elif abs(score) > 0.2:
            reasons.append(
                f"ML predicts {direction} with moderate confidence "
                f"(prob={probability:.1%}, confidence={confidence:.1%})"
            )
        elif direction == "NEUTRAL":
            reasons.append(
                f"ML predicts NEUTRAL (prob={probability:.1%})"
            )
        else:
            reasons.append(
                f"ML predicts {direction} with low confidence "
                f"(prob={probability:.1%}, confidence={confidence:.1%})"
            )

        return score, reasons

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_get(row: pd.Series, key: str) -> float | None:
        """Safely retrieve a numeric value from a Series row.

        Returns ``None`` if the key is missing, the value is NaN, or the
        value cannot be converted to a float.
        """
        try:
            value = row.get(key)
            if value is None:
                return None
            value = float(value)
            if np.isnan(value) or np.isinf(value):
                return None
            return value
        except (TypeError, ValueError):
            return None

    def _neutral_signals(self) -> dict:
        """Return a fully neutral signal dictionary."""
        return {
            "trend_signal": 0.0,
            "momentum_signal": 0.0,
            "volume_signal": 0.0,
            "volatility_signal": 0.0,
            "sentiment_signal": 0.0,
            "ml_signal": 0.0,
            "combined_score": 0.0,
            "signal_details": {
                "trend": {"score": 0.0, "reasons": ["Insufficient data"]},
                "momentum": {"score": 0.0, "reasons": ["Insufficient data"]},
                "volume": {"score": 0.0, "reasons": ["Insufficient data"]},
                "volatility": {"score": 0.0, "reasons": ["Insufficient data"]},
                "sentiment": {"score": 0.0, "reasons": ["No sentiment data"]},
                "ml": {"score": 0.0, "reasons": ["No ML model"]},
            },
        }
