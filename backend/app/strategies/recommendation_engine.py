"""
Recommendation Engine — combines rule-based signals, feature engineering,
and risk metrics to produce actionable BUY / SELL / HOLD recommendations.

Phase 1 uses only rule-based scoring.  Phase 3 will add ML model predictions
and sentiment analysis.

DISCLAIMER: This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.config import settings
from app.data.historical_data_service import HistoricalDataService
from app.data.market_data_service import MarketDataService
from app.features.feature_pipeline import FeaturePipeline
from app.features.sentiment_features import SentimentFeatures
from app.strategies.rule_based_strategy import RuleBasedStrategy
from app.utils.helpers import DISCLAIMER, get_ist_now, validate_symbol
from app.utils.logger import get_logger


class RecommendationEngine:
    """Generates BUY / SELL / HOLD recommendations by combining multiple signals.

    Workflow:
        1. Fetch historical OHLCV data for the symbol.
        2. Compute all technical features via :class:`FeaturePipeline`.
        3. Run :class:`RuleBasedStrategy` to get signal scores.
        4. Map the composite score to an actionable recommendation.
        5. Compute stop-loss / target prices using ATR.

    DISCLAIMER: This is for educational and research purposes only,
    not financial advice.
    """

    # Thresholds for mapping combined score → action
    BUY_THRESHOLD: float = settings.BUY_THRESHOLD   # default 0.3
    SELL_THRESHOLD: float = settings.SELL_THRESHOLD  # default -0.3

    def __init__(self) -> None:
        self.strategy = RuleBasedStrategy()
        self.feature_pipeline = FeaturePipeline()
        self.market_data = MarketDataService()
        self.historical_data = HistoricalDataService(market_data_service=self.market_data)
        self.sentiment_features = SentimentFeatures()
        self.logger = get_logger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_recommendation(
        self,
        symbol: str,
        current_price: float | None = None,
        holding: dict | None = None,
    ) -> dict:
        """Generate a complete recommendation for *symbol*.

        Args:
            symbol: NSE stock symbol (with or without ``.NS`` suffix).
            current_price: Optional override; if ``None`` the engine fetches
                the latest price via :class:`MarketDataService`.
            holding: Optional portfolio context — ``{quantity, avg_buy_price}``.

        Returns:
            A dictionary with the following keys:
                symbol, action, confidence_score, risk_score, reasons,
                supporting_indicators, sentiment_summary, model_probability,
                suggested_stop_loss, suggested_target, time_horizon,
                current_price, disclaimer, timestamp.
        """
        symbol = validate_symbol(symbol)
        self.logger.info("Generating recommendation for %s", symbol)

        try:
            # 1. Fetch historical data
            df: pd.DataFrame = self.historical_data.get_historical_data(
                symbol=symbol,
                period=settings.YFINANCE_HISTORY_PERIOD,
                interval="1d",
            )

            if df is None or df.empty:
                self.logger.warning("No historical data for %s", symbol)
                return self._empty_recommendation(symbol, current_price)

            # 2. Compute features
            df_features: pd.DataFrame = self.feature_pipeline.compute_all_features(df)

            # 3. Run rule-based strategy with sentiment
            # Fetch sentiment features
            try:
                sentiment_data = self.sentiment_features.compute_sentiment_features(symbol)
            except Exception as exc:
                self.logger.warning("Sentiment fetch failed for %s: %s", symbol, exc)
                sentiment_data = None

            signals: dict = self.strategy.analyze(df_features, sentiment_data=sentiment_data)

            # 4. Determine current price
            if current_price is None:
                try:
                    price_data = self.market_data.get_current_price(symbol)
                    current_price = price_data.get("price", df_features["Close"].iloc[-1])
                except Exception:
                    current_price = float(df_features["Close"].iloc[-1])

            # 5. Extract latest ATR & volatility for stop-loss / target / risk
            last_row = df_features.iloc[-1]
            atr = self._safe_float(last_row, "atr", default=current_price * 0.02)
            volatility = self._safe_float(last_row, "volatility_20d", default=0.02)

            # 6. Map score → action
            combined = signals["combined_score"]
            action = self._score_to_action(combined, holding)
            confidence = self._score_to_confidence(combined)
            risk_label = self._map_risk_score(volatility, combined)

            # 7. Collect reasons (including sentiment)
            all_reasons: list[str] = []
            for dim in ("trend", "momentum", "volume", "volatility", "sentiment"):
                all_reasons.extend(signals["signal_details"][dim]["reasons"])

            # 8. Supporting indicator snapshot
            supporting: dict[str, Any] = {
                "rsi": self._safe_float(last_row, "rsi"),
                "macd_histogram": self._safe_float(last_row, "macd_histogram"),
                "sma_20": self._safe_float(last_row, "sma_20"),
                "sma_50": self._safe_float(last_row, "sma_50"),
                "sma_200": self._safe_float(last_row, "sma_200"),
                "atr": round(atr, 2),
                "volume_ratio": self._safe_float(last_row, "volume_ratio"),
            }

            # 9. Stop-loss & target
            stop_loss = self._calculate_stop_loss(current_price, atr, action)
            target = self._calculate_target(current_price, atr, action)

            # 10. Sentiment summary
            sentiment_summary = self._build_sentiment_summary(sentiment_data)

            return {
                "symbol": symbol,
                "action": action,
                "confidence_score": round(confidence, 2),
                "risk_score": risk_label,
                "reasons": all_reasons,
                "supporting_indicators": supporting,
                "sentiment_summary": sentiment_summary,
                "model_probability": None,    # Phase 1 — no ML yet
                "suggested_stop_loss": round(stop_loss, 2),
                "suggested_target": round(target, 2),
                "time_horizon": "1–2 weeks (swing trade)",
                "current_price": round(current_price, 2),
                "disclaimer": DISCLAIMER,
                "timestamp": get_ist_now().isoformat(),
            }

        except Exception as exc:
            self.logger.error("Recommendation failed for %s: %s", symbol, exc, exc_info=True)
            return self._empty_recommendation(symbol, current_price)

    def get_portfolio_recommendations(self, holdings: list[dict]) -> list[dict]:
        """Generate recommendations for every portfolio holding.

        Args:
            holdings: List of dicts, each with at least ``symbol``, ``quantity``,
                and ``avg_buy_price``.

        Returns:
            List of recommendation dicts (same shape as :meth:`get_recommendation`).
        """
        recommendations: list[dict] = []
        for h in holdings:
            symbol = h.get("symbol", "")
            holding_ctx = {
                "quantity": h.get("quantity", 0),
                "avg_buy_price": h.get("avg_buy_price", 0.0),
            }
            rec = self.get_recommendation(
                symbol=symbol,
                current_price=h.get("current_price"),
                holding=holding_ctx,
            )
            recommendations.append(rec)
        return recommendations

    def get_top_upside_stocks(
        self,
        symbols: list[str] | None = None,
        top_n: int = 5,
    ) -> list[dict]:
        """Screen stocks and return the top *top_n* with the highest upside score.

        In Phase 1 this is driven purely by rule-based scoring.
        Phase 3 will integrate ML predictions.

        Args:
            symbols: Symbols to screen.  Defaults to ``settings.DEFAULT_WATCHLIST``.
            top_n: Number of top results to return.

        Returns:
            Sorted list of recommendation dicts (best upside first).
        """
        if symbols is None:
            symbols = list(settings.DEFAULT_WATCHLIST)

        scored: list[dict] = []
        for sym in symbols:
            try:
                rec = self.get_recommendation(sym)
                scored.append(rec)
            except Exception as exc:
                self.logger.warning("Skipping %s in screening: %s", sym, exc)

        # Sort by combined confidence + bullish bias
        scored.sort(
            key=lambda r: r.get("confidence_score", 0)
            * (1 if r.get("action") == "BUY" else -0.5 if r.get("action") == "SELL" else 0.1),
            reverse=True,
        )

        return scored[:top_n]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _calculate_stop_loss(self, price: float, atr: float, action: str) -> float:
        """Calculate suggested stop-loss based on ATR.

        For BUY  → ``price - 2 × ATR``  (protect against downside)
        For SELL → ``price + 2 × ATR``  (protect against upside squeeze)
        """
        if action == "BUY":
            return max(price - 2.0 * atr, 0.0)
        elif action == "SELL":
            return price + 2.0 * atr
        # HOLD — use a wider stop (2.5×ATR below)
        return max(price - 2.5 * atr, 0.0)

    def _calculate_target(self, price: float, atr: float, action: str) -> float:
        """Calculate suggested target based on ATR.

        Aims for roughly 1.5 : 1 risk-reward.
        For BUY  → ``price + 3 × ATR``
        For SELL → ``price - 3 × ATR``
        """
        if action == "BUY":
            return price + 3.0 * atr
        elif action == "SELL":
            return max(price - 3.0 * atr, 0.0)
        # HOLD — modest upside target
        return price + 2.0 * atr

    def _map_risk_score(self, volatility: float, combined_score: float) -> str:
        """Map numerical volatility and signal strength to a risk label.

        Higher volatility and weaker signal conviction → higher risk.
        """
        # Annualise if daily
        if 0 < volatility < 1:
            annual_vol = volatility * np.sqrt(252)
        else:
            annual_vol = volatility

        abs_score = abs(combined_score)

        # Strong conviction + low vol → Low risk
        if annual_vol < 0.25 and abs_score > 0.4:
            return "Low"
        # High vol or very weak signal → High risk
        if annual_vol > 0.45 or abs_score < 0.1:
            return "High"
        return "Medium"

    def _score_to_action(self, score: float, holding: dict | None = None) -> str:
        """Convert combined score to BUY / SELL / HOLD.

        If the user already holds the stock, a marginally positive score
        defaults to HOLD rather than BUY to avoid over-concentration.
        """
        if score >= self.BUY_THRESHOLD:
            return "BUY"
        if score <= self.SELL_THRESHOLD:
            return "SELL"
        return "HOLD"

    @staticmethod
    def _score_to_confidence(score: float) -> float:
        """Map a [-1, 1] combined score to a [0, 100] confidence percentage."""
        return round(abs(score) * 100, 2)

    @staticmethod
    def _safe_float(row: pd.Series, key: str, default: float = 0.0) -> float:
        """Safely extract a float from a Series row."""
        try:
            val = row.get(key)
            if val is None:
                return default
            val = float(val)
            return default if (np.isnan(val) or np.isinf(val)) else round(val, 4)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _build_sentiment_summary(sentiment_data: dict | None) -> str:
        """Build a one-line sentiment summary for the recommendation response.

        Args:
            sentiment_data: Feature dict from :class:`SentimentFeatures`.

        Returns:
            Human-readable string like ``"Bullish (score: +0.32, 10 articles)"``
            or ``"N/A (no news data)"`` if unavailable.
        """
        if not sentiment_data:
            return "N/A (sentiment unavailable)"

        count = sentiment_data.get("article_count", 0)
        if count == 0:
            return "N/A (no news data)"

        label = sentiment_data.get("sentiment_label", "neutral").capitalize()
        score = sentiment_data.get("sentiment_score", 0.0)
        return f"{label} (score: {score:+.2f}, {count} articles)"


    def _empty_recommendation(self, symbol: str, price: float | None = None) -> dict:
        """Return a safe default recommendation when data is unavailable."""
        return {
            "symbol": symbol,
            "action": "HOLD",
            "confidence_score": 0.0,
            "risk_score": "High",
            "reasons": ["Insufficient data to generate recommendation"],
            "supporting_indicators": {},
            "sentiment_summary": "N/A",
            "model_probability": None,
            "suggested_stop_loss": 0.0,
            "suggested_target": 0.0,
            "time_horizon": "N/A",
            "current_price": round(price, 2) if price else 0.0,
            "disclaimer": DISCLAIMER,
            "timestamp": get_ist_now().isoformat(),
        }
