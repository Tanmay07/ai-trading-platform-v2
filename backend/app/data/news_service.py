"""
Multi-Source News Aggregation Service — Phase 2

Fetches financial news from NewsAPI, GNews, and RSS feeds,
deduplicates headlines, and returns normalised article dicts.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── NSE Symbol → Company Name Mapping ─────────────────────────
# Used to build human-readable search queries for news APIs.
SYMBOL_COMPANY_MAP: dict[str, str] = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services TCS",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India SBI",
    "LT.NS": "Larsen Toubro",
    "AXISBANK.NS": "Axis Bank",
    "BHARTIARTL.NS": "Bharti Airtel",
    "ITC.NS": "ITC Limited",
    "WIPRO.NS": "Wipro",
    "HCLTECH.NS": "HCL Technologies",
    "TATAMOTORS.NS": "Tata Motors",
    "TATASTEEL.NS": "Tata Steel",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "MARUTI.NS": "Maruti Suzuki",
    "BAJFINANCE.NS": "Bajaj Finance",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ADANIENT.NS": "Adani Enterprises",
    "SUNPHARMA.NS": "Sun Pharmaceutical",
    "POWERGRID.NS": "Power Grid Corporation",
    "NTPC.NS": "NTPC Limited",
    "ONGC.NS": "ONGC",
    "M&M.NS": "Mahindra Mahindra",
    "ASIANPAINT.NS": "Asian Paints",
}


# ── Indian Financial RSS Feeds ────────────────────────────────
RSS_FEEDS: list[dict[str, str]] = [
    {
        "name": "MoneyControl",
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
    },
    {
        "name": "Economic Times Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    },
    {
        "name": "LiveMint Markets",
        "url": "https://www.livemint.com/rss/markets",
    },
]


class NewsService:
    """Aggregates news from multiple sources with caching and deduplication.

    Sources (configurable via ``settings.NEWS_SOURCES``):
        - ``newsapi`` — NewsAPI.org REST API (requires ``NEWS_API_KEY``)
        - ``gnews``  — GNews.io REST API (requires ``GNEWS_API_KEY``)
        - ``rss``    — Free Indian financial RSS feeds (no key needed)

    The service maintains an in-memory TTL cache to avoid hammering APIs.

    Attributes:
        _cache: Dict mapping ``symbol`` → ``(timestamp, articles)`` tuples.
    """

    NEWSAPI_BASE = "https://newsapi.org/v2/everything"
    GNEWS_BASE = "https://gnews.io/api/v4/search"

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._http = httpx.Client(timeout=15.0, follow_redirects=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_news(
        self,
        symbol: str,
        max_articles: int | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch news articles for a stock symbol from all active sources.

        Args:
            symbol: NSE symbol with ``.NS`` suffix (e.g. ``"RELIANCE.NS"``).
            max_articles: Maximum number of articles to return.
                Defaults to ``settings.SENTIMENT_MAX_ARTICLES``.

        Returns:
            List of article dicts, each containing:
                ``headline``, ``summary``, ``source``, ``provider``,
                ``url``, ``published_at``.
        """
        if max_articles is None:
            max_articles = settings.SENTIMENT_MAX_ARTICLES

        # Check cache
        cached = self._get_cached(symbol)
        if cached is not None:
            logger.debug("Cache hit for %s (%d articles)", symbol, len(cached))
            return cached[:max_articles]

        query = self._symbol_to_query(symbol)
        logger.info("Fetching news for %s (query=%r)", symbol, query)

        all_articles: list[dict] = []
        active_sources = settings.NEWS_SOURCES

        # Fetch from each active source
        if "newsapi" in active_sources and settings.NEWS_API_KEY:
            try:
                articles = self._fetch_from_newsapi(query)
                all_articles.extend(articles)
                logger.info("NewsAPI: %d articles for %s", len(articles), symbol)
            except Exception as exc:
                logger.warning("NewsAPI fetch failed for %s: %s", symbol, exc)

        if "gnews" in active_sources and settings.GNEWS_API_KEY:
            try:
                articles = self._fetch_from_gnews(query)
                all_articles.extend(articles)
                logger.info("GNews: %d articles for %s", len(articles), symbol)
            except Exception as exc:
                logger.warning("GNews fetch failed for %s: %s", symbol, exc)

        if "rss" in active_sources:
            try:
                articles = self._fetch_from_rss(query)
                all_articles.extend(articles)
                logger.info("RSS: %d articles for %s", len(articles), symbol)
            except Exception as exc:
                logger.warning("RSS fetch failed for %s: %s", symbol, exc)

        if not all_articles:
            logger.warning("No articles fetched for %s from any source", symbol)

        # Deduplicate by headline similarity
        unique = self._deduplicate(all_articles)

        # Sort by published_at descending (newest first)
        unique.sort(
            key=lambda a: a.get("published_at") or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        # Cache the result
        self._set_cache(symbol, unique)

        return unique[:max_articles]

    def get_available_sources(self) -> list[str]:
        """Return which news sources are actually available (have keys)."""
        available: list[str] = []
        if settings.NEWS_API_KEY:
            available.append("newsapi")
        if settings.GNEWS_API_KEY:
            available.append("gnews")
        available.append("rss")  # always available
        return available

    # ------------------------------------------------------------------
    # Provider Adapters
    # ------------------------------------------------------------------

    def _fetch_from_newsapi(self, query: str) -> list[dict]:
        """Fetch articles from NewsAPI.org.

        Requires ``NEWS_API_KEY`` to be set in the environment.
        Free tier: 100 requests/day.
        """
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(settings.SENTIMENT_MAX_ARTICLES, 20),
            "apiKey": settings.NEWS_API_KEY,
        }

        resp = self._http.get(self.NEWSAPI_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

        articles: list[dict] = []
        for item in data.get("articles", []):
            articles.append({
                "headline": item.get("title", ""),
                "summary": item.get("description", ""),
                "source": "newsapi",
                "provider": (item.get("source") or {}).get("name", "Unknown"),
                "url": item.get("url", ""),
                "published_at": self._parse_datetime(item.get("publishedAt")),
            })

        return articles

    def _fetch_from_gnews(self, query: str) -> list[dict]:
        """Fetch articles from GNews.io.

        Requires ``GNEWS_API_KEY`` to be set in the environment.
        Free tier: 100 requests/day.
        """
        params = {
            "q": query,
            "lang": "en",
            "country": "in",
            "max": min(settings.SENTIMENT_MAX_ARTICLES, 10),
            "token": settings.GNEWS_API_KEY,
        }

        resp = self._http.get(self.GNEWS_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

        articles: list[dict] = []
        for item in data.get("articles", []):
            articles.append({
                "headline": item.get("title", ""),
                "summary": item.get("description", ""),
                "source": "gnews",
                "provider": (item.get("source") or {}).get("name", "Unknown"),
                "url": item.get("url", ""),
                "published_at": self._parse_datetime(item.get("publishedAt")),
            })

        return articles

    def _fetch_from_rss(self, query: str) -> list[dict]:
        """Fetch articles from Indian financial RSS feeds.

        This is always available (no API key needed) and serves as the
        fallback source. Articles are filtered by keyword relevance
        to the search query.
        """
        articles: list[dict] = []
        query_words = set(query.lower().split())

        for feed_info in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_info["url"])
                for entry in feed.entries[:20]:  # Limit per feed
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))

                    # Relevance filter: check if any query word appears
                    text_lower = f"{title} {summary}".lower()
                    if not any(w in text_lower for w in query_words):
                        continue

                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        except (TypeError, ValueError):
                            pass

                    articles.append({
                        "headline": title,
                        "summary": summary[:500],  # Trim long summaries
                        "source": "rss",
                        "provider": feed_info["name"],
                        "url": entry.get("link", ""),
                        "published_at": published,
                    })
            except Exception as exc:
                logger.warning("Failed to parse RSS feed %s: %s", feed_info["name"], exc)

        return articles

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _symbol_to_query(symbol: str) -> str:
        """Convert NSE symbol to a human-readable search query.

        Falls back to the raw symbol name (without ``.NS``) if no
        mapping exists.

        Examples:
            >>> NewsService._symbol_to_query("RELIANCE.NS")
            'Reliance Industries'
            >>> NewsService._symbol_to_query("UNKNOWN.NS")
            'UNKNOWN stock'
        """
        if symbol in SYMBOL_COMPANY_MAP:
            return SYMBOL_COMPANY_MAP[symbol]
        # Strip .NS and use as query
        base = symbol.replace(".NS", "").replace(".BO", "")
        return f"{base} stock"

    @staticmethod
    def _parse_datetime(dt_string: str | None) -> datetime | None:
        """Parse ISO 8601 datetime strings from news APIs."""
        if not dt_string:
            return None
        try:
            # Handle various ISO formats
            dt_string = dt_string.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_string)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _deduplicate(articles: list[dict]) -> list[dict]:
        """Remove duplicate articles based on headline similarity.

        Uses MD5 hash of normalised headline text as the dedup key.
        """
        seen: set[str] = set()
        unique: list[dict] = []

        for article in articles:
            headline = article.get("headline", "").strip().lower()
            if not headline:
                continue
            # Normalise: remove extra whitespace, keep alphanumeric
            normalised = "".join(c for c in headline if c.isalnum() or c.isspace())
            normalised = " ".join(normalised.split())
            key = hashlib.md5(normalised.encode()).hexdigest()

            if key not in seen:
                seen.add(key)
                unique.append(article)

        return unique

    def _get_cached(self, symbol: str) -> list[dict] | None:
        """Return cached articles if within TTL, else None."""
        if symbol not in self._cache:
            return None
        cached_at, articles = self._cache[symbol]
        if time.time() - cached_at > settings.SENTIMENT_CACHE_TTL_SECONDS:
            del self._cache[symbol]
            return None
        return articles

    def _set_cache(self, symbol: str, articles: list[dict]) -> None:
        """Store articles in the in-memory cache."""
        self._cache[symbol] = (time.time(), articles)

    def clear_cache(self, symbol: str | None = None) -> None:
        """Clear the cache for a specific symbol or all symbols."""
        if symbol:
            self._cache.pop(symbol, None)
        else:
            self._cache.clear()
