"""
Recommendation Engine — combines rule-based signals, ML predictions,
sentiment analysis, and risk metrics to produce actionable
BUY / SELL / HOLD recommendations.

Phase 3 adds ML model predictions alongside rule-based scoring.

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
from app.ml.model_manager import ModelManager
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

    # Thresholds for mapping combined score → action (STRICTER)
    BUY_THRESHOLD: float = 0.35   # Was 0.45 (relaxed slightly so technicals alone can trigger it)
    SELL_THRESHOLD: float = -0.15  # Cut losses early

    def __init__(self) -> None:
        self.strategy = RuleBasedStrategy()
        self.feature_pipeline = FeaturePipeline()
        self.market_data = MarketDataService()
        self.historical_data = HistoricalDataService(market_data_service=self.market_data)
        self.sentiment_features = SentimentFeatures()
        self.model_manager = ModelManager()
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
        """Generate a complete recommendation for *symbol*."""
        symbol = validate_symbol(symbol)
        self.logger.info("Generating strict recommendation for %s", symbol)

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

            # 3. Fetch sentiment features
            try:
                sentiment_data = self.sentiment_features.compute_sentiment_features(symbol)
            except Exception as exc:
                self.logger.warning("Sentiment fetch failed for %s: %s", symbol, exc)
                sentiment_data = None

            # 3b. Fetch ML prediction (if model exists)
            ml_data: dict | None = None
            ml_probability: dict | None = None
            try:
                ml_result = self.model_manager.predict(symbol, df_features=df_features)
                if ml_result is not None:
                    ml_data = ml_result.to_dict()
                    ml_probability = {
                        "direction": ml_result.direction,
                        "probability": round(ml_result.probability, 4),
                        "confidence": round(ml_result.confidence, 4),
                        "probabilities": ml_result.probabilities,
                        "model_name": ml_result.model_name,
                    }
            except Exception as exc:
                self.logger.warning("ML prediction failed for %s: %s", symbol, exc)

            # 4. Run hybrid strategy (rule-based + sentiment + ML)
            signals: dict = self.strategy.analyze(
                df_features,
                sentiment_data=sentiment_data,
                ml_prediction=ml_data,
            )

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

            # 6. Map score → strict action
            combined = signals["combined_score"]
            action, action_reason = self._score_to_strict_action(combined, current_price, holding)
            confidence = self._score_to_confidence(combined)
            risk_label = self._map_risk_score(volatility, combined)

            # 7. Collect reasons (including sentiment & ML)
            all_reasons: list[str] = [action_reason] if action_reason else []
            for dim in ("trend", "momentum", "volume", "volatility", "sentiment", "ml"):
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
            
            hold_target = None
            if "HOLD" in action:
                # If holding, suggest a target based on resistance
                hold_target = round(price_data.get("dayHigh", current_price + 1.5 * atr) if hasattr(self, 'price_data') else current_price + 1.5 * atr, 2)

            # 10. Sentiment summary
            sentiment_summary = self._build_sentiment_summary(sentiment_data)
            
            # 11. Generate backend conclusion
            conclusion = self._generate_backend_conclusion(action, confidence, hold_target, action_reason)

            return {
                "symbol": symbol,
                "action": action,
                "conclusion": conclusion,
                "confidence_score": round(confidence, 2),
                "risk_score": risk_label,
                "reasons": all_reasons,
                "supporting_indicators": supporting,
                "sentiment_summary": sentiment_summary,
                "model_probability": ml_probability,
                "suggested_stop_loss": round(stop_loss, 2),
                "suggested_target": round(target, 2),
                "hold_target": hold_target,
                "time_horizon": "1–2 weeks (swing trade)",
                "current_price": round(current_price, 2),
                "disclaimer": DISCLAIMER,
                "timestamp": get_ist_now().isoformat(),
            }

        except Exception as exc:
            self.logger.error("Recommendation failed for %s: %s", symbol, exc, exc_info=True)
            return self._empty_recommendation(symbol, current_price)

    def get_portfolio_recommendations(self, holdings: list[dict]) -> list[dict]:
        """Generate recommendations for every portfolio holding."""
        recommendations: list[dict] = []
        for h in holdings:
            symbol = h.get("symbol", "")
            holding_ctx = {
                "quantity": h.get("quantity", 0),
                "avg_buy_price": h.get("avg_buy_price", 0.0),
            }
            try:
                rec = self.get_recommendation(
                    symbol=symbol,
                    current_price=h.get("current_price"),
                    holding=holding_ctx,
                )
                recommendations.append(rec)
            except Exception as e:
                self.logger.error(f"Error processing recommendation for {symbol}: {e}")
                recommendations.append(self._empty_recommendation(symbol))
        return recommendations

    def get_watchlist_recommendations(self, symbols: list[str]) -> list[dict]:
        """Generate recommendations for an arbitrary list of symbols."""
        recommendations: list[dict] = []
        for symbol in symbols:
            try:
                rec = self.get_recommendation(symbol=symbol)
                recommendations.append(rec)
            except Exception as exc:
                self.logger.warning("Failed recommendation for %s: %s", symbol, exc)
                recommendations.append(self._empty_recommendation(symbol))
        return recommendations

    def get_top_upside_stocks(
        self,
        symbols: list[str] | None = None,
        top_n: int = 5,
    ) -> list[dict]:
        """Screen stocks and return the top *top_n* with the highest upside score."""
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
            * (1 if "BUY" in r.get("action", "") else -0.5 if "SELL" in r.get("action", "") else 0.1),
            reverse=True,
        )

        return scored[:top_n]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_backend_conclusion(self, action: str, confidence: float, hold_target: float | None, reason: str | None) -> str:
        """Generate a dynamic conclusion string."""
        if action == "CUT LOSSES":
            return f"The engine strongly advises CUTTING LOSSES. The technical trend is completely broken and sentiment is weak. The probability of regaining your invested capital or reaching a previous peak is exceptionally low right now. Reallocate your capital to higher-probability setups."
        elif action == "BUY MORE":
            return f"The AI identifies extreme bullish momentum and strong sentiment. Since you already hold this position, it is recommended to BUY MORE (Accumulate) to maximize profits on this confirmed uptrend."
        elif action == "BUY":
            return f"The engine recommends a STRICT BUY with {confidence}% conviction. Current market scenarios and sentiment indicate a high-probability upside move."
        elif action == "SELL":
            return f"The engine recommends a SELL. Momentum and sentiment are decaying, posing a risk of further capital erosion."
        else: # HOLD
            target_str = f" Hold until the price reaches ₹{hold_target} before re-evaluating." if hold_target else ""
            if confidence < 30:
                return f"The AI recommends HOLDING due to highly conflicting signals or neutral momentum. Avoid deploying fresh capital here.{target_str}"
            else:
                return f"The AI recommends a HOLD. The stock is range-bound or currently forming a base.{target_str}"

    def _calculate_stop_loss(self, price: float, atr: float, action: str) -> float:
        """Calculate suggested stop-loss based on ATR."""
        if "BUY" in action:
            return max(price - 2.0 * atr, 0.0)
        elif "SELL" in action or action == "CUT LOSSES":
            return price + 2.0 * atr
        return max(price - 2.5 * atr, 0.0)

    def _calculate_target(self, price: float, atr: float, action: str) -> float:
        """Calculate suggested target based on ATR."""
        if "BUY" in action:
            return price + 3.0 * atr
        elif "SELL" in action or action == "CUT LOSSES":
            return max(price - 3.0 * atr, 0.0)
        return price + 2.0 * atr

    def _map_risk_score(self, volatility: float, combined_score: float) -> str:
        """Map numerical volatility and signal strength to a risk label."""
        if 0 < volatility < 1:
            annual_vol = volatility * np.sqrt(252)
        else:
            annual_vol = volatility

        abs_score = abs(combined_score)

        if annual_vol < 0.25 and abs_score > 0.4:
            return "Low"
        if annual_vol > 0.45 or abs_score < 0.1:
            return "High"
        return "Medium"

    def _score_to_strict_action(self, score: float, current_price: float, holding: dict | None = None) -> tuple[str, str | None]:
        """Convert combined score to strict portfolio-aware action."""
        
        # If user holds the stock, evaluate peak distance and loss
        if holding and holding.get("quantity", 0) > 0:
            avg_buy = holding.get("avg_buy_price", 0.0)
            if avg_buy > 0:
                unrealized_pct = ((current_price - avg_buy) / avg_buy) * 100
                
                # If deeply underwater and score is negative (bearish) => CUT LOSSES
                if unrealized_pct < -5.0 and score < 0.0:
                    reason = f"Position is underwater by {unrealized_pct:.1f}% and technicals are deeply bearish. Very low chance of regaining peak."
                    return "CUT LOSSES", reason
                
                # If heavily in profit and score is extremely high => BUY MORE
                if unrealized_pct > 2.0 and score >= self.BUY_THRESHOLD:
                    reason = f"Position is in profit by {unrealized_pct:.1f}% with strong continuation signals."
                    return "BUY MORE", reason

        if score >= self.BUY_THRESHOLD:
            return "BUY", None
        if score <= self.SELL_THRESHOLD:
            return "SELL", None
        return "HOLD", None

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
