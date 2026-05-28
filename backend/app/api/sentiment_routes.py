"""
Sentiment API Routes — Phase 2

Provides endpoints for stock-level and market-level sentiment analysis.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.data.news_service import NewsService
from app.features.sentiment_analyzer import SentimentAnalyzer
from app.features.sentiment_features import SentimentFeatures
from app.utils.helpers import DISCLAIMER, validate_symbol
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Sentiment"])

# Shared service instances
_news_service = NewsService()
_analyzer = SentimentAnalyzer()
_sentiment_features = SentimentFeatures(
    news_service=_news_service, analyzer=_analyzer
)


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.get("/{symbol}")
async def get_sentiment(symbol: str) -> dict[str, Any]:
    """Get aggregated sentiment analysis for a stock symbol.

    Fetches recent news from all active sources, analyses sentiment,
    and returns an aggregated score with breakdown.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE`` or ``RELIANCE.NS``).

    Returns:
        JSON with aggregated sentiment data including overall label,
        score, confidence, and article statistics.
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /sentiment/%s", symbol)

    try:
        loop = asyncio.get_running_loop()
        features: dict = await loop.run_in_executor(
            None,
            partial(_sentiment_features.compute_sentiment_features, symbol),
        )

        return {
            "symbol": symbol,
            "sentiment": {
                "overall_label": features["sentiment_label"],
                "overall_score": round(features["sentiment_score"], 4),
                "confidence": round(features["sentiment_confidence"], 4),
                "article_count": features["article_count"],
                "bullish_ratio": features["bullish_ratio"],
                "bearish_ratio": features["bearish_ratio"],
                "top_headlines": features["top_headlines"],
            },
            "available_sources": _news_service.get_available_sources(),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error getting sentiment for %s: %s", symbol, exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute sentiment: {exc}",
        )


@router.get("/{symbol}/articles")
async def get_sentiment_articles(
    symbol: str,
    max_articles: int = Query(
        default=20, ge=1, le=50, description="Maximum articles to return"
    ),
) -> dict[str, Any]:
    """Get recent news articles with individual sentiment scores.

    Returns each article with its headline, source, published date,
    and computed sentiment score.

    Args:
        symbol: NSE stock symbol (e.g. ``RELIANCE`` or ``RELIANCE.NS``).
        max_articles: Number of articles to return (1–50).

    Returns:
        JSON with a list of articles, each annotated with sentiment data.
    """
    symbol = validate_symbol(symbol)
    logger.info("GET /sentiment/%s/articles  max=%d", symbol, max_articles)

    try:
        loop = asyncio.get_running_loop()

        # Fetch articles
        articles: list[dict] = await loop.run_in_executor(
            None,
            partial(_news_service.fetch_news, symbol, max_articles),
        )

        # Score each article individually
        scored_articles: list[dict] = []
        for article in articles:
            headline = article.get("headline", "")
            summary = article.get("summary", "")
            text = f"{headline}. {summary}".strip() if summary else headline

            result = _analyzer.analyze_text(text)

            published = article.get("published_at")
            scored_articles.append({
                "headline": headline,
                "summary": (summary[:200] + "...") if len(summary) > 200 else summary,
                "source": article.get("source", ""),
                "provider": article.get("provider", ""),
                "url": article.get("url", ""),
                "published_at": published.isoformat() if published else None,
                "sentiment": result.to_dict(),
            })

        return {
            "symbol": symbol,
            "articles": scored_articles,
            "count": len(scored_articles),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error(
            "Error fetching sentiment articles for %s: %s", symbol, exc, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch sentiment articles: {exc}",
        )


@router.get("/market/overview")
async def get_market_sentiment(
    top_n: int = Query(
        default=10, ge=1, le=20, description="Number of stocks to include"
    ),
) -> dict[str, Any]:
    """Get overall market sentiment across top watchlist stocks.

    Analyses sentiment for each stock in the default watchlist and
    returns an aggregate market-level view.

    Args:
        top_n: Number of stocks from the watchlist to include.

    Returns:
        JSON with per-stock sentiment and overall market sentiment.
    """
    logger.info("GET /sentiment/market/overview  top_n=%d", top_n)

    try:
        symbols = list(settings.DEFAULT_WATCHLIST)[:top_n]
        loop = asyncio.get_running_loop()

        stock_sentiments: list[dict] = []
        total_score = 0.0
        total_articles = 0

        for sym in symbols:
            try:
                features: dict = await loop.run_in_executor(
                    None,
                    partial(_sentiment_features.compute_sentiment_features, sym),
                )
                stock_sentiments.append({
                    "symbol": sym,
                    "label": features["sentiment_label"],
                    "score": round(features["sentiment_score"], 4),
                    "article_count": features["article_count"],
                })
                total_score += features["sentiment_score"]
                total_articles += features["article_count"]
            except Exception as exc:
                logger.warning("Skipping %s in market sentiment: %s", sym, exc)
                stock_sentiments.append({
                    "symbol": sym,
                    "label": "neutral",
                    "score": 0.0,
                    "article_count": 0,
                })

        # Overall market sentiment
        avg_score = total_score / len(symbols) if symbols else 0.0
        if avg_score > 0.05:
            market_label = "bullish"
        elif avg_score < -0.05:
            market_label = "bearish"
        else:
            market_label = "neutral"

        return {
            "market_sentiment": {
                "overall_label": market_label,
                "overall_score": round(avg_score, 4),
                "total_articles": total_articles,
                "stocks_analysed": len(symbols),
            },
            "stocks": stock_sentiments,
            "available_sources": _news_service.get_available_sources(),
            "disclaimer": DISCLAIMER,
        }
    except Exception as exc:
        logger.error("Error computing market sentiment: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute market sentiment: {exc}",
        )
