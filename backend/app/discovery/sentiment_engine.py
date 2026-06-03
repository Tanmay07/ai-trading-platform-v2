"""
Discovery Sentiment Engine

Leverages the existing SentimentAnalyzer and NewsService to compute
sentiment scores for the Discovery pipeline.
"""
from typing import Dict, Any, Optional
from app.utils.logger import get_logger
from app.features.sentiment_analyzer import SentimentAnalyzer
from app.data.news_service import NewsService

class DiscoverySentimentEngine:
    def __init__(self, analyzer: SentimentAnalyzer, news_service: NewsService):
        self.logger = get_logger(__name__)
        self.analyzer = analyzer
        self.news_service = news_service

    async def compute_sentiment_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches news for a symbol, analyzes it using FinBERT, and returns
        a sentiment score (0-100) for the Discovery Engine.
        """
        try:
            articles = self.news_service.fetch_news(symbol)
            if not articles:
                return {
                    "sentiment_score": 50.0,
                    "reasons": ["No recent news available (neutral sentiment)"]
                }
            
            # Analyze each article
            scored_articles = self.analyzer.analyze_articles(articles)
            
            if not scored_articles:
                return {
                    "sentiment_score": 50.0,
                    "reasons": ["No parsable news available (neutral sentiment)"]
                }
                
            # The analyzer output score is between -1 (Bearish) and 1 (Bullish)
            # Average the compound score
            avg_score = sum(a.compound_score for a in scored_articles) / len(scored_articles)
            
            # Map -1 to 1 into 0 to 100
            # -1 -> 0, 0 -> 50, 1 -> 100
            mapped_score = (avg_score + 1.0) * 50.0
            
            # Bound the score
            final_score = max(0, min(100, mapped_score))
            
            reasons = []
            if final_score > 70:
                reasons.append("Highly positive recent news sentiment")
            elif final_score > 55:
                reasons.append("Slightly positive news sentiment")
            elif final_score < 30:
                reasons.append("Highly negative recent news sentiment")
            elif final_score < 45:
                reasons.append("Slightly negative news sentiment")
            else:
                reasons.append("Neutral news sentiment")
                
            return {
                "sentiment_score": round(final_score, 2),
                "raw_compound": round(avg_score, 4),
                "article_count": len(scored_articles),
                "reasons": reasons
            }

        except Exception as e:
            self.logger.error(f"Failed to compute discovery sentiment for {symbol}: {e}")
            return None
