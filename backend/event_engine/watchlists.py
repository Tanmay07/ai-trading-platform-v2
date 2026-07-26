from typing import List, Dict, Any
from sqlalchemy.orm import Session
from event_engine.models import MarketEventRecord

class WatchlistService:
    """
    Module 9 - Watchlists.
    Every watchlist inherits event intelligence automatically.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def get_watchlist_events(self, watchlist_name: str, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Fetches the recent high-impact events for a specific watchlist.
        """
        # In SQLite/PostgreSQL JSON filtering is different.
        # For this simplified mock, we fetch all recent events and filter in memory.
        # In prod, use Postgres JSONB queries.
        recent_events = self.db.query(MarketEventRecord).order_by(MarketEventRecord.created_at.desc()).limit(200).all()
        
        filtered = []
        for e in recent_events:
            event_symbols = e.symbols_json or []
            if any(s in event_symbols for s in symbols):
                filtered.append({
                    "event_id": e.event_id,
                    "type": e.type,
                    "subtype": e.subtype,
                    "impact": e.impact_score,
                    "symbols": e.symbols_json,
                    "timestamp": e.created_at
                })
                
        return filtered
