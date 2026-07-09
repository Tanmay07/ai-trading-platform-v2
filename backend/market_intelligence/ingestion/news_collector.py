import logging
import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from market_intelligence.providers.rss_provider import RSSProvider
from market_intelligence.processing.deduplicator import Deduplicator
from market_intelligence.storage.models import Article
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class NewsCollector:
    """Orchestrates ingestion from providers and passes to the deduplicator."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("market_intelligence")
        self.rss_config = self.config.get("providers", {}).get("rss", {})
        
        self.rss_provider = RSSProvider()
        self.deduplicator = Deduplicator()
        
    def fetch_all(self, db: Session) -> List[Article]:
        """Fetches from all configured sources and returns ONLY new articles."""
        new_articles = []
        
        if self.rss_config.get("enabled", False):
            sources = self.rss_config.get("sources", [])
            for source in sources:
                raw_articles = self.rss_provider.fetch(source["url"], source["name"])
                
                for raw in raw_articles:
                    hash_id = self.deduplicator.generate_hash(
                        raw["title"], raw["source"], raw["published_time"]
                    )
                    
                    if not self.deduplicator.is_duplicate(db, hash_id):
                        # It's new!
                        article = Article(
                            hash_id=hash_id,
                            source=raw["source"],
                            title=raw["title"],
                            summary=raw["summary"],
                            url=raw["url"],
                            # Basic string conversion for now. Real app needs date parsing.
                            published_time=datetime.datetime.utcnow() 
                        )
                        new_articles.append(article)
                        db.add(article)
                        
        # Commit new articles so they are marked as seen immediately
        if new_articles:
            try:
                db.commit()
                logger.info(f"Ingested {len(new_articles)} new articles.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to save new articles: {e}")
                return []
                
        return new_articles
