"""
Sentiment Analyzer — Phase 2

Provides VADER-based (and optionally FinBERT-based) sentiment analysis
for financial news headlines and article text.

VADER is the default — fast, rule-based, zero model downloads.
FinBERT can be enabled via ``settings.USE_FINBERT`` for higher accuracy
on financial text.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentResult:
    """Result of analysing a single piece of text.

    Attributes:
        label: ``"positive"``, ``"negative"``, or ``"neutral"``.
        score: Continuous score in ``[-1.0, 1.0]``.
        confidence: Model confidence in ``[0.0, 1.0]``.
        analyzer: Name of the analyzer that produced this result.
    """

    __slots__ = ("label", "score", "confidence", "analyzer")

    def __init__(
        self,
        label: str,
        score: float,
        confidence: float,
        analyzer: str = "vader",
    ) -> None:
        self.label = label
        self.score = score
        self.confidence = confidence
        self.analyzer = analyzer

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "score": round(self.score, 4),
            "confidence": round(self.confidence, 4),
            "analyzer": self.analyzer,
        }

    def __repr__(self) -> str:
        return (
            f"SentimentResult(label={self.label!r}, "
            f"score={self.score:.3f}, confidence={self.confidence:.3f})"
        )


class AggregatedSentimentResult:
    """Aggregated sentiment across multiple articles with time-decay weighting.

    Attributes:
        overall_label: ``"bullish"``, ``"bearish"``, or ``"neutral"``.
        overall_score: Weighted average score in ``[-1.0, 1.0]``.
        confidence: Average confidence of individual results.
        article_count: Total number of articles analysed.
        bullish_count: Number of positive articles.
        bearish_count: Number of negative articles.
        neutral_count: Number of neutral articles.
        top_headlines: The most impactful headlines (by |score|).
    """

    __slots__ = (
        "overall_label",
        "overall_score",
        "confidence",
        "article_count",
        "bullish_count",
        "bearish_count",
        "neutral_count",
        "top_headlines",
    )

    def __init__(
        self,
        overall_label: str,
        overall_score: float,
        confidence: float,
        article_count: int,
        bullish_count: int,
        bearish_count: int,
        neutral_count: int,
        top_headlines: list[dict] | None = None,
    ) -> None:
        self.overall_label = overall_label
        self.overall_score = overall_score
        self.confidence = confidence
        self.article_count = article_count
        self.bullish_count = bullish_count
        self.bearish_count = bearish_count
        self.neutral_count = neutral_count
        self.top_headlines = top_headlines or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_label": self.overall_label,
            "overall_score": round(self.overall_score, 4),
            "confidence": round(self.confidence, 4),
            "article_count": self.article_count,
            "bullish_count": self.bullish_count,
            "bearish_count": self.bearish_count,
            "neutral_count": self.neutral_count,
            "top_headlines": self.top_headlines[:5],
        }

    def __repr__(self) -> str:
        return (
            f"AggregatedSentimentResult(label={self.overall_label!r}, "
            f"score={self.overall_score:.3f}, articles={self.article_count})"
        )


class SentimentAnalyzer:
    """Analyses text sentiment using VADER (default) or FinBERT (opt-in).

    Usage::

        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Reliance stock surges 5% on record earnings")
        print(result.label, result.score)

    For batch analysis with time-decay::

        agg = analyzer.analyze_articles(articles)
        print(agg.overall_label, agg.overall_score)
    """

    # VADER compound thresholds
    _POSITIVE_THRESHOLD = 0.05
    _NEGATIVE_THRESHOLD = -0.05

    def __init__(self) -> None:
        self._vader = SentimentIntensityAnalyzer()
        self._finbert_pipeline = None  # Lazy-loaded

    # ------------------------------------------------------------------
    # Single-text analysis
    # ------------------------------------------------------------------

    def analyze_text(self, text: str) -> SentimentResult:
        """Analyse a single piece of text and return a SentimentResult.

        Uses VADER by default. If ``settings.USE_FINBERT`` is True and
        the model is available, uses FinBERT instead.

        Args:
            text: The text to analyse (headline, summary, etc.).

        Returns:
            A :class:`SentimentResult` with label, score, and confidence.
        """
        if not text or not text.strip():
            return SentimentResult(
                label="neutral", score=0.0, confidence=0.0, analyzer="none"
            )

        if settings.USE_FINBERT:
            try:
                return self._analyze_with_finbert(text)
            except Exception as exc:
                logger.warning("FinBERT failed, falling back to VADER: %s", exc)

        return self._analyze_with_vader(text)

    # ------------------------------------------------------------------
    # Batch analysis with time-decay
    # ------------------------------------------------------------------

    def analyze_articles(
        self,
        articles: list[dict],
        half_life_hours: int | None = None,
    ) -> AggregatedSentimentResult:
        """Analyse a list of articles and return aggregated sentiment.

        Applies exponential time-decay weighting so that newer articles
        have more influence than older ones.

        Args:
            articles: List of article dicts with ``headline``, ``summary``,
                and optionally ``published_at`` (datetime).
            half_life_hours: Decay half-life in hours. Defaults to
                ``settings.SENTIMENT_DECAY_HALF_LIFE_HOURS``.

        Returns:
            An :class:`AggregatedSentimentResult` with aggregated metrics.
        """
        if half_life_hours is None:
            half_life_hours = settings.SENTIMENT_DECAY_HALF_LIFE_HOURS

        if not articles:
            return AggregatedSentimentResult(
                overall_label="neutral",
                overall_score=0.0,
                confidence=0.0,
                article_count=0,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
            )

        now = datetime.now(tz=timezone.utc)
        weighted_scores: list[float] = []
        weights: list[float] = []
        confidences: list[float] = []
        bullish = 0
        bearish = 0
        neutral = 0
        scored_headlines: list[dict] = []

        for article in articles:
            # Combine headline + summary for analysis
            headline = article.get("headline", "")
            summary = article.get("summary", "")
            text = f"{headline}. {summary}".strip() if summary else headline

            result = self.analyze_text(text)

            # Compute time-decay weight
            published_at = article.get("published_at")
            weight = self._compute_decay_weight(published_at, now, half_life_hours)

            weighted_scores.append(result.score * weight)
            weights.append(weight)
            confidences.append(result.confidence)

            # Count labels
            if result.label == "positive":
                bullish += 1
            elif result.label == "negative":
                bearish += 1
            else:
                neutral += 1

            scored_headlines.append({
                "headline": headline[:200],
                "score": round(result.score, 3),
                "label": result.label,
                "source": article.get("source", ""),
                "provider": article.get("provider", ""),
            })

        # Weighted average score
        total_weight = sum(weights)
        if total_weight > 0:
            overall_score = sum(weighted_scores) / total_weight
        else:
            overall_score = 0.0

        # Map to label
        if overall_score > self._POSITIVE_THRESHOLD:
            overall_label = "bullish"
        elif overall_score < self._NEGATIVE_THRESHOLD:
            overall_label = "bearish"
        else:
            overall_label = "neutral"

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Sort headlines by absolute score for top-impact
        scored_headlines.sort(key=lambda h: abs(h["score"]), reverse=True)

        return AggregatedSentimentResult(
            overall_label=overall_label,
            overall_score=overall_score,
            confidence=avg_confidence,
            article_count=len(articles),
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            top_headlines=scored_headlines[:5],
        )

    # ------------------------------------------------------------------
    # VADER
    # ------------------------------------------------------------------

    def _analyze_with_vader(self, text: str) -> SentimentResult:
        """Analyse text using VADER — fast, rule-based, no downloads."""
        scores = self._vader.polarity_scores(text)
        compound = scores["compound"]  # [-1.0, 1.0]

        if compound >= self._POSITIVE_THRESHOLD:
            label = "positive"
        elif compound <= self._NEGATIVE_THRESHOLD:
            label = "negative"
        else:
            label = "neutral"

        # Confidence derived from how far the compound is from 0
        confidence = min(abs(compound), 1.0)

        return SentimentResult(
            label=label,
            score=compound,
            confidence=confidence,
            analyzer="vader",
        )

    # ------------------------------------------------------------------
    # FinBERT (opt-in)
    # ------------------------------------------------------------------

    def _analyze_with_finbert(self, text: str) -> SentimentResult:
        """Analyse text using the FinBERT transformer model.

        Requires ``transformers`` and ``torch`` to be installed.
        The model is lazy-loaded on first call.
        """
        if self._finbert_pipeline is None:
            self._finbert_pipeline = self._load_finbert()

        result = self._finbert_pipeline(text[:512])[0]  # Truncate for BERT
        label_raw = result["label"].lower()
        confidence = result["score"]

        # Map FinBERT labels to our standard labels
        label_map = {"positive": "positive", "negative": "negative", "neutral": "neutral"}
        label = label_map.get(label_raw, "neutral")

        # Convert to continuous score
        if label == "positive":
            score = confidence
        elif label == "negative":
            score = -confidence
        else:
            score = 0.0

        return SentimentResult(
            label=label,
            score=score,
            confidence=confidence,
            analyzer="finbert",
        )

    @staticmethod
    def _load_finbert():
        """Lazy-load the FinBERT pipeline from HuggingFace."""
        try:
            from transformers import pipeline as hf_pipeline

            logger.info("Loading FinBERT model (first use may download ~440MB)...")
            pipe = hf_pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert",
            )
            logger.info("FinBERT model loaded successfully.")
            return pipe
        except ImportError:
            raise RuntimeError(
                "FinBERT requires 'transformers' and 'torch'. "
                "Install them with: pip install transformers torch"
            )

    # ------------------------------------------------------------------
    # Time-decay helper
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_decay_weight(
        published_at: datetime | None,
        now: datetime,
        half_life_hours: int,
    ) -> float:
        """Compute exponential decay weight based on article age.

        Weight = 2^(-age_hours / half_life_hours)

        A 3-day-old article with a 72-hour half-life gets weight 0.5.
        A 6-day-old article gets weight 0.25, etc.

        Args:
            published_at: When the article was published.
            now: Current UTC time.
            half_life_hours: Decay half-life in hours.

        Returns:
            Weight in ``(0.0, 1.0]``. Returns 0.5 if published_at is None.
        """
        if published_at is None:
            return 0.5  # Unknown age → moderate weight

        # Ensure timezone-aware comparison
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        age_hours = (now - published_at).total_seconds() / 3600
        if age_hours < 0:
            age_hours = 0  # Future dates treated as just published

        if half_life_hours <= 0:
            return 1.0

        return math.pow(2, -age_hours / half_life_hours)
