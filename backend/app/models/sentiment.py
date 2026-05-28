"""
Sentiment ORM Models — Phase 2

Stores news articles, per-article sentiment scores, and
per-symbol aggregated sentiment for persistence and analysis.

This is for educational and research purposes only, not financial advice.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class NewsArticle(Base):
    """A news article fetched from an external source."""

    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    headline = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)       # e.g. "newsapi", "gnews", "rss"
    provider = Column(String(100), nullable=True)     # e.g. "Economic Times"
    url = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, server_default=func.now())

    # Relationship to individual sentiment scores
    scores = relationship("SentimentScore", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_news_symbol_published", "symbol", "published_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<NewsArticle(symbol={self.symbol!r}, "
            f"headline={self.headline[:50]!r}...)>"
        )


class SentimentScore(Base):
    """Sentiment score for a single news article, computed by a specific analyzer."""

    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    analyzer = Column(String(20), nullable=False)      # "vader" or "finbert"
    label = Column(String(10), nullable=False)          # "positive", "negative", "neutral"
    score = Column(Float, nullable=False)               # -1.0 to 1.0
    confidence = Column(Float, nullable=True)           # 0.0 to 1.0
    created_at = Column(DateTime, server_default=func.now())

    article = relationship("NewsArticle", back_populates="scores")

    def __repr__(self) -> str:
        return (
            f"<SentimentScore(article_id={self.article_id}, "
            f"analyzer={self.analyzer!r}, label={self.label!r}, "
            f"score={self.score})>"
        )


class AggregatedSentiment(Base):
    """Per-symbol aggregated sentiment snapshot."""

    __tablename__ = "aggregated_sentiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    overall_label = Column(String(10), nullable=False)   # "bullish", "bearish", "neutral"
    overall_score = Column(Float, nullable=False)         # -1.0 to 1.0
    confidence = Column(Float, nullable=True)
    article_count = Column(Integer, default=0)
    bullish_count = Column(Integer, default=0)
    bearish_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    computed_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_agg_symbol_computed", "symbol", "computed_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AggregatedSentiment(symbol={self.symbol!r}, "
            f"label={self.overall_label!r}, score={self.overall_score})>"
        )
