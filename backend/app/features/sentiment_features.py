"""
Sentiment Features — Phase 2

Bridge between the NLP sentiment pipeline and the trading strategy.
Fetches news → analyses sentiment → returns feature-ready data that
the recommendation engine can consume.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any

from app.data.news_service import NewsService
from app.features.sentiment_analyzer import (
    AggregatedSentimentResult,
    SentimentAnalyzer,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentFeatures:
    """Computes sentiment features for a stock symbol.

    Orchestrates:
        1. ``NewsService`` to fetch articles.
        2. ``SentimentAnalyzer`` to score and aggregate.
        3. Maps results to a feature dict consumable by the strategy layer.

    Usage::

        sf = SentimentFeatures()
        features = sf.compute_sentiment_features("RELIANCE.NS")
        # features = {
        #     "sentiment_score": 0.32,
        #     "sentiment_confidence": 0.71,
        #     "sentiment_label": "bullish",
        #     "bullish_ratio": 0.6,
        #     "bearish_ratio": 0.2,
        #     "article_count": 10,
        #     "top_headlines": [...],
        # }
    """

    def __init__(
        self,
        news_service: NewsService | None = None,
        analyzer: SentimentAnalyzer | None = None,
    ) -> None:
        self.news_service = news_service or NewsService()
        self.analyzer = analyzer or SentimentAnalyzer()

    def compute_sentiment_features(self, symbol: str) -> dict[str, Any]:
        """Fetch news and compute sentiment features for a symbol.

        Args:
            symbol: NSE symbol with ``.NS`` suffix (e.g. ``"RELIANCE.NS"``).

        Returns:
            Dictionary of sentiment features:
                - ``sentiment_score`` (float, -1 to 1): overall score
                - ``sentiment_confidence`` (float, 0 to 1): confidence
                - ``sentiment_label`` (str): "bullish", "bearish", "neutral"
                - ``bullish_ratio`` (float, 0 to 1): fraction of bullish articles
                - ``bearish_ratio`` (float, 0 to 1): fraction of bearish articles
                - ``article_count`` (int): total articles analysed
                - ``top_headlines`` (list): top impactful headlines
        """
        logger.info("Computing sentiment features for %s", symbol)

        try:
            # Step 1: Fetch news articles
            articles = self.news_service.fetch_news(symbol)

            if not articles:
                logger.info("No articles found for %s — returning neutral", symbol)
                return self._empty_features()

            # Step 2: Analyse and aggregate
            aggregated: AggregatedSentimentResult = self.analyzer.analyze_articles(articles)

            # Step 3: Compute ratios
            total = aggregated.article_count
            bullish_ratio = aggregated.bullish_count / total if total > 0 else 0.0
            bearish_ratio = aggregated.bearish_count / total if total > 0 else 0.0

            features = {
                "sentiment_score": aggregated.overall_score,
                "sentiment_confidence": aggregated.confidence,
                "sentiment_label": aggregated.overall_label,
                "bullish_ratio": round(bullish_ratio, 4),
                "bearish_ratio": round(bearish_ratio, 4),
                "article_count": total,
                "top_headlines": aggregated.top_headlines,
            }

            logger.info(
                "Sentiment for %s: label=%s, score=%.3f, articles=%d",
                symbol,
                aggregated.overall_label,
                aggregated.overall_score,
                total,
            )

            return features

        except Exception as exc:
            logger.error(
                "Failed to compute sentiment for %s: %s", symbol, exc, exc_info=True
            )
            return self._empty_features()

    def get_sentiment_summary(self, symbol: str) -> str:
        """Return a one-line human-readable sentiment summary.

        Useful for the ``sentiment_summary`` field in recommendations.

        Args:
            symbol: NSE symbol with ``.NS`` suffix.

        Returns:
            A summary string like ``"Bullish (score: 0.32, 10 articles)"``
            or ``"N/A (no news data)"`` if no articles are found.
        """
        features = self.compute_sentiment_features(symbol)
        count = features["article_count"]

        if count == 0:
            return "N/A (no news data)"

        label = features["sentiment_label"].capitalize()
        score = features["sentiment_score"]
        return f"{label} (score: {score:+.2f}, {count} articles)"

    @staticmethod
    def _empty_features() -> dict[str, Any]:
        """Return a neutral sentiment feature dict when no data is available."""
        return {
            "sentiment_score": 0.0,
            "sentiment_confidence": 0.0,
            "sentiment_label": "neutral",
            "bullish_ratio": 0.0,
            "bearish_ratio": 0.0,
            "article_count": 0,
            "top_headlines": [],
        }
