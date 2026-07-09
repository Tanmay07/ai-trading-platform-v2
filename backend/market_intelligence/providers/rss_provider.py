import feedparser
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RSSProvider:
    """Fetches and normalizes news from RSS feeds."""
    
    def fetch(self, url: str, source_name: str) -> List[Dict[str, Any]]:
        articles = []
        try:
            logger.info(f"Fetching RSS from {source_name}: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "published_time": entry.get("published", ""),
                    "source": source_name
                })
        except Exception as e:
            logger.error(f"Error fetching RSS from {source_name}: {e}")
            
        return articles
