import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NewsImportanceScorer:
    """Calculates an importance score (0-100) for a news article."""
    
    def __init__(self):
        # Base multipliers for sources
        self.source_weights = {
            "NSE Announcements": 1.0,
            "Reuters": 0.9,
            "Bloomberg": 0.9,
            "Economic Times": 0.7,
            "Moneycontrol Market": 0.6,
            "Google News Business": 0.5
        }
        
        # Multipliers based on event type
        self.event_weights = {
            "Earnings": 1.0,
            "Corporate": 0.9,
            "Business": 0.8,
            "Risk": 0.9,
            "Macro": 0.7,
            "General": 0.2
        }
        
    def score(self, source: str, event_type: str, sentiment_confidence: float) -> int:
        source_w = self.source_weights.get(source, 0.4)
        event_w = self.event_weights.get(event_type, 0.2)
        
        # A highly confident sentiment means it's heavily impactful
        sentiment_w = min(1.0, sentiment_confidence)
        
        # Formula: Weighted average scaled to 100
        # This can be configured in market_intelligence.yaml
        raw_score = (source_w * 30) + (event_w * 40) + (sentiment_w * 30)
        
        return min(100, max(0, int(raw_score)))
