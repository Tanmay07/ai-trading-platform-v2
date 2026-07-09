import hashlib
import logging
from typing import Dict, Any

from sqlalchemy.orm import Session
from market_intelligence.storage.models import Article

logger = logging.getLogger(__name__)

class Deduplicator:
    """Ensures we never process the same article twice."""
    
    @staticmethod
    def generate_hash(title: str, source: str, published_time: str) -> str:
        raw = f"{title}|{source}|{published_time}".encode('utf-8')
        return hashlib.sha256(raw).hexdigest()
        
    def is_duplicate(self, db: Session, hash_id: str) -> bool:
        """Checks if the article already exists in the database."""
        exists = db.query(Article).filter(Article.hash_id == hash_id).first()
        return exists is not None
