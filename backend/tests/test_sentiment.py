"""
Test Suite for Phase 2 — News Sentiment Analysis

Tests cover:
    - VADER sentiment analysis (positive, negative, neutral)
    - Time-decay weighted aggregation
    - News service deduplication and symbol mapping
    - Sentiment features integration
    - Strategy sentiment assessment
    - API route response shapes (mocked)

This is for educational and research purposes only, not financial advice.
"""

import math
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest
import numpy as np
import pandas as pd

# ── VADER Sentiment Analyzer Tests ───────────────────────────


class TestSentimentAnalyzer:
    """Unit tests for the SentimentAnalyzer class."""

    def _make_analyzer(self):
        from app.features.sentiment_analyzer import SentimentAnalyzer
        return SentimentAnalyzer()

    def test_vader_positive_sentiment(self):
        """VADER should classify clearly positive text as positive."""
        analyzer = self._make_analyzer()
        result = analyzer.analyze_text(
            "Excellent earnings results, great profit growth, very happy investors"
        )
        assert result.label == "positive"
        assert result.score > 0
        assert result.confidence > 0
        assert result.analyzer == "vader"

    def test_vader_negative_sentiment(self):
        """VADER should classify clearly negative text as negative."""
        analyzer = self._make_analyzer()
        result = analyzer.analyze_text(
            "Stock crashes 10% amid fraud allegations, investors panic"
        )
        assert result.label == "negative"
        assert result.score < 0
        assert result.confidence > 0
        assert result.analyzer == "vader"

    def test_vader_neutral_sentiment(self):
        """VADER should classify bland/neutral text as neutral."""
        analyzer = self._make_analyzer()
        result = analyzer.analyze_text(
            "Company announces quarterly results for Q2 FY2025"
        )
        # Neutral or weakly positive is fine
        assert result.label in ("neutral", "positive")
        assert -0.3 <= result.score <= 0.3
        assert result.analyzer == "vader"

    def test_empty_text(self):
        """Empty text should return neutral with zero confidence."""
        analyzer = self._make_analyzer()
        result = analyzer.analyze_text("")
        assert result.label == "neutral"
        assert result.score == 0.0
        assert result.confidence == 0.0
        assert result.analyzer == "none"

    def test_whitespace_only(self):
        """Whitespace-only text should return neutral."""
        analyzer = self._make_analyzer()
        result = analyzer.analyze_text("   \n\t  ")
        assert result.label == "neutral"
        assert result.score == 0.0

    def test_sentiment_result_to_dict(self):
        """SentimentResult.to_dict() should return expected keys."""
        from app.features.sentiment_analyzer import SentimentResult
        result = SentimentResult(label="positive", score=0.75, confidence=0.9, analyzer="vader")
        d = result.to_dict()
        assert set(d.keys()) == {"label", "score", "confidence", "analyzer"}
        assert d["label"] == "positive"
        assert d["score"] == 0.75
        assert d["confidence"] == 0.9

    def test_multiple_sentiments_consistency(self):
        """Analysing the same text twice should give identical results."""
        analyzer = self._make_analyzer()
        text = "Great news for the market, investors are excited about growth"
        r1 = analyzer.analyze_text(text)
        r2 = analyzer.analyze_text(text)
        assert r1.label == r2.label
        assert r1.score == r2.score


# ── Aggregation & Time-Decay Tests ────────────────────────────


class TestSentimentAggregation:
    """Tests for batch analysis with time-decay weighting."""

    def _make_analyzer(self):
        from app.features.sentiment_analyzer import SentimentAnalyzer
        return SentimentAnalyzer()

    def test_aggregation_with_articles(self):
        """Aggregation should produce valid metrics for a list of articles."""
        analyzer = self._make_analyzer()
        articles = [
            {
                "headline": "Stock surges on strong earnings beat",
                "summary": "Company reported record profits.",
                "published_at": datetime.now(tz=timezone.utc),
            },
            {
                "headline": "Analysts upgrade stock to buy rating",
                "summary": "Multiple brokerages raised targets.",
                "published_at": datetime.now(tz=timezone.utc) - timedelta(hours=12),
            },
            {
                "headline": "Market steady ahead of budget announcement",
                "summary": "",
                "published_at": datetime.now(tz=timezone.utc) - timedelta(hours=24),
            },
        ]

        agg = analyzer.analyze_articles(articles)
        assert agg.article_count == 3
        assert agg.bullish_count + agg.bearish_count + agg.neutral_count == 3
        assert -1.0 <= agg.overall_score <= 1.0
        assert agg.overall_label in ("bullish", "bearish", "neutral")
        assert agg.confidence > 0

    def test_aggregation_empty_list(self):
        """Aggregation with empty list should return neutral defaults."""
        analyzer = self._make_analyzer()
        agg = analyzer.analyze_articles([])
        assert agg.article_count == 0
        assert agg.overall_score == 0.0
        assert agg.overall_label == "neutral"

    def test_time_decay_newer_articles_higher_weight(self):
        """Newer articles should have higher weight than older ones."""
        from app.features.sentiment_analyzer import SentimentAnalyzer

        now = datetime.now(tz=timezone.utc)

        # Test the decay function directly
        w_new = SentimentAnalyzer._compute_decay_weight(now, now, 72)
        w_old = SentimentAnalyzer._compute_decay_weight(
            now - timedelta(hours=72), now, 72
        )

        assert w_new == pytest.approx(1.0, abs=0.01)
        assert w_old == pytest.approx(0.5, abs=0.01)  # exactly one half-life
        assert w_new > w_old

    def test_time_decay_very_old_article(self):
        """A 10-day-old article should have very low weight."""
        from app.features.sentiment_analyzer import SentimentAnalyzer

        now = datetime.now(tz=timezone.utc)
        w = SentimentAnalyzer._compute_decay_weight(
            now - timedelta(days=10), now, 72
        )
        assert w < 0.15  # Should be quite low

    def test_time_decay_none_published_at(self):
        """If published_at is None, weight should be 0.5."""
        from app.features.sentiment_analyzer import SentimentAnalyzer

        now = datetime.now(tz=timezone.utc)
        w = SentimentAnalyzer._compute_decay_weight(None, now, 72)
        assert w == 0.5

    def test_aggregated_result_to_dict(self):
        """AggregatedSentimentResult.to_dict() should contain all expected keys."""
        analyzer = self._make_analyzer()
        articles = [
            {"headline": "Positive news for markets", "summary": "", "published_at": None}
        ]
        agg = analyzer.analyze_articles(articles)
        d = agg.to_dict()
        assert "overall_label" in d
        assert "overall_score" in d
        assert "confidence" in d
        assert "article_count" in d
        assert "bullish_count" in d
        assert "bearish_count" in d
        assert "neutral_count" in d
        assert "top_headlines" in d


# ── News Service Tests ────────────────────────────────────────


class TestNewsService:
    """Tests for NewsService utility methods."""

    def test_symbol_to_query_known(self):
        """Known NSE symbols should map to company names."""
        from app.data.news_service import NewsService

        assert NewsService._symbol_to_query("RELIANCE.NS") == "Reliance Industries"
        assert NewsService._symbol_to_query("TCS.NS") == "Tata Consultancy Services TCS"
        assert NewsService._symbol_to_query("INFY.NS") == "Infosys"

    def test_symbol_to_query_unknown(self):
        """Unknown symbols should fall back to symbol + 'stock'."""
        from app.data.news_service import NewsService

        result = NewsService._symbol_to_query("XYZFAKE.NS")
        assert result == "XYZFAKE stock"

    def test_deduplication(self):
        """Duplicate headlines should be removed."""
        from app.data.news_service import NewsService

        articles = [
            {"headline": "Stock surges 5% today", "source": "newsapi"},
            {"headline": "Stock surges 5% today", "source": "gnews"},
            {"headline": "Different headline entirely", "source": "rss"},
            {"headline": "", "source": "rss"},  # empty — should be removed
        ]
        unique = NewsService._deduplicate(articles)
        assert len(unique) == 2  # one duplicate + one empty removed

    def test_deduplication_case_insensitive(self):
        """Deduplication should be case-insensitive."""
        from app.data.news_service import NewsService

        articles = [
            {"headline": "RELIANCE stock rises", "source": "a"},
            {"headline": "reliance stock rises", "source": "b"},
        ]
        unique = NewsService._deduplicate(articles)
        assert len(unique) == 1

    def test_parse_datetime_iso(self):
        """ISO datetime strings should be parsed correctly."""
        from app.data.news_service import NewsService

        dt = NewsService._parse_datetime("2025-01-15T10:30:00Z")
        assert dt is not None
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    def test_parse_datetime_none(self):
        """None input should return None."""
        from app.data.news_service import NewsService

        assert NewsService._parse_datetime(None) is None

    def test_available_sources_always_includes_rss(self):
        """RSS should always be available regardless of API keys."""
        from app.data.news_service import NewsService

        service = NewsService()
        sources = service.get_available_sources()
        assert "rss" in sources


# ── Sentiment Features Tests ──────────────────────────────────


class TestSentimentFeatures:
    """Tests for the SentimentFeatures bridge module."""

    def test_empty_features_structure(self):
        """Empty features should have all expected keys."""
        from app.features.sentiment_features import SentimentFeatures

        features = SentimentFeatures._empty_features()
        assert features["sentiment_score"] == 0.0
        assert features["sentiment_confidence"] == 0.0
        assert features["sentiment_label"] == "neutral"
        assert features["bullish_ratio"] == 0.0
        assert features["bearish_ratio"] == 0.0
        assert features["article_count"] == 0
        assert features["top_headlines"] == []

    def test_compute_with_mocked_news(self):
        """SentimentFeatures should produce valid output with mocked news."""
        from app.features.sentiment_features import SentimentFeatures
        from app.features.sentiment_analyzer import SentimentAnalyzer
        from app.data.news_service import NewsService

        # Mock the news service
        mock_news = MagicMock(spec=NewsService)
        mock_news.fetch_news.return_value = [
            {
                "headline": "Reliance shares jump 4% on strong results",
                "summary": "Excellent quarterly performance.",
                "published_at": datetime.now(tz=timezone.utc),
                "source": "test",
                "provider": "TestProvider",
            },
        ]

        sf = SentimentFeatures(news_service=mock_news, analyzer=SentimentAnalyzer())
        features = sf.compute_sentiment_features("RELIANCE.NS")

        assert features["article_count"] == 1
        assert features["sentiment_label"] in ("bullish", "bearish", "neutral")
        assert -1.0 <= features["sentiment_score"] <= 1.0

    def test_compute_with_no_articles(self):
        """SentimentFeatures should return neutral when no articles found."""
        from app.features.sentiment_features import SentimentFeatures
        from app.data.news_service import NewsService

        mock_news = MagicMock(spec=NewsService)
        mock_news.fetch_news.return_value = []

        sf = SentimentFeatures(news_service=mock_news)
        features = sf.compute_sentiment_features("UNKNOWN.NS")

        assert features["article_count"] == 0
        assert features["sentiment_score"] == 0.0
        assert features["sentiment_label"] == "neutral"

    def test_get_sentiment_summary(self):
        """get_sentiment_summary should return a readable string."""
        from app.features.sentiment_features import SentimentFeatures
        from app.data.news_service import NewsService

        mock_news = MagicMock(spec=NewsService)
        mock_news.fetch_news.return_value = [
            {
                "headline": "Great earnings growth reported",
                "summary": "",
                "published_at": datetime.now(tz=timezone.utc),
                "source": "test",
            },
        ]

        sf = SentimentFeatures(news_service=mock_news)
        summary = sf.get_sentiment_summary("TCS.NS")

        assert isinstance(summary, str)
        assert "1 articles" in summary or "N/A" in summary


# ── Strategy Sentiment Integration Tests ──────────────────────


class TestStrategySentimentIntegration:
    """Tests for sentiment integration in RuleBasedStrategy."""

    def _make_strategy(self):
        from app.strategies.rule_based_strategy import RuleBasedStrategy
        return RuleBasedStrategy()

    def _make_sample_df(self):
        """Create a minimal DataFrame with required feature columns."""
        n = 50
        np.random.seed(42)
        df = pd.DataFrame({
            "Open": np.random.uniform(100, 200, n),
            "High": np.random.uniform(100, 200, n),
            "Low": np.random.uniform(100, 200, n),
            "Close": np.random.uniform(100, 200, n),
            "Volume": np.random.randint(10000, 100000, n),
            "sma_20": np.random.uniform(100, 200, n),
            "sma_50": np.random.uniform(100, 200, n),
            "sma_200": np.random.uniform(100, 200, n),
            "ema_12": np.random.uniform(100, 200, n),
            "ema_26": np.random.uniform(100, 200, n),
            "rsi": np.random.uniform(30, 70, n),
            "macd": np.random.uniform(-5, 5, n),
            "macd_signal": np.random.uniform(-5, 5, n),
            "macd_histogram": np.random.uniform(-3, 3, n),
            "stoch_k": np.random.uniform(20, 80, n),
            "stoch_d": np.random.uniform(20, 80, n),
            "volume_ratio": np.random.uniform(0.5, 2.0, n),
            "obv": np.random.uniform(100000, 200000, n),
            "obv_sma": np.random.uniform(100000, 200000, n),
            "atr": np.random.uniform(1, 5, n),
            "atr_pct": np.random.uniform(0.5, 3.0, n),
            "bb_upper": np.random.uniform(180, 220, n),
            "bb_middle": np.random.uniform(150, 180, n),
            "bb_lower": np.random.uniform(100, 150, n),
            "volatility_20d": np.random.uniform(0.01, 0.05, n),
            "prev_close": np.random.uniform(100, 200, n),
        })
        df["High"] = df[["Open", "High", "Low", "Close"]].max(axis=1)
        df["Low"] = df[["Open", "High", "Low", "Close"]].min(axis=1)
        return df

    def test_analyze_with_sentiment_data(self):
        """Strategy should incorporate sentiment when provided."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        sentiment_data = {
            "sentiment_score": 0.5,
            "sentiment_confidence": 0.8,
            "sentiment_label": "bullish",
            "article_count": 10,
        }

        result = strategy.analyze(df, sentiment_data=sentiment_data)
        assert "sentiment_signal" in result
        assert "sentiment" in result["signal_details"]
        assert result["sentiment_signal"] != 0.0

    def test_analyze_without_sentiment_data(self):
        """Strategy should still work without sentiment data."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        result = strategy.analyze(df, sentiment_data=None)
        assert "sentiment_signal" in result
        assert result["sentiment_signal"] == 0.0
        assert "No sentiment data available" in result["signal_details"]["sentiment"]["reasons"]

    def test_analyze_backwards_compatible(self):
        """Strategy should work when called without sentiment kwarg."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        result = strategy.analyze(df)
        assert "combined_score" in result
        assert "sentiment_signal" in result

    def test_neutral_signals_include_sentiment(self):
        """Neutral signals dict should include sentiment_signal."""
        strategy = self._make_strategy()
        neutral = strategy._neutral_signals()
        assert "sentiment_signal" in neutral
        assert neutral["sentiment_signal"] == 0.0
        assert "sentiment" in neutral["signal_details"]

    def test_weights_sum_to_one(self):
        """All dimension weights should sum to 1.0."""
        strategy = self._make_strategy()
        total = (
            strategy.TREND_WEIGHT
            + strategy.MOMENTUM_WEIGHT
            + strategy.VOLUME_WEIGHT
            + strategy.VOLATILITY_WEIGHT
            + strategy.SENTIMENT_WEIGHT
            + strategy.ML_WEIGHT
        )
        assert total == pytest.approx(1.0, abs=0.001)


# ── ORM Model Tests ───────────────────────────────────────────


class TestSentimentModels:
    """Tests for sentiment ORM model definitions."""

    def test_news_article_model(self):
        """NewsArticle model should be importable and have expected columns."""
        from app.models.sentiment import NewsArticle
        assert NewsArticle.__tablename__ == "news_articles"
        assert hasattr(NewsArticle, "symbol")
        assert hasattr(NewsArticle, "headline")
        assert hasattr(NewsArticle, "source")
        assert hasattr(NewsArticle, "published_at")

    def test_sentiment_score_model(self):
        """SentimentScore model should be importable and have expected columns."""
        from app.models.sentiment import SentimentScore
        assert SentimentScore.__tablename__ == "sentiment_scores"
        assert hasattr(SentimentScore, "article_id")
        assert hasattr(SentimentScore, "analyzer")
        assert hasattr(SentimentScore, "label")
        assert hasattr(SentimentScore, "score")

    def test_aggregated_sentiment_model(self):
        """AggregatedSentiment model should be importable and have expected columns."""
        from app.models.sentiment import AggregatedSentiment
        assert AggregatedSentiment.__tablename__ == "aggregated_sentiments"
        assert hasattr(AggregatedSentiment, "symbol")
        assert hasattr(AggregatedSentiment, "overall_label")
        assert hasattr(AggregatedSentiment, "overall_score")
        assert hasattr(AggregatedSentiment, "article_count")
