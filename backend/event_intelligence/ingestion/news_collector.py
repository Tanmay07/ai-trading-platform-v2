import time
import random
from typing import List, Dict, Any

class NewsCollector:
    """
    Simulates fetching raw news articles and exchange filings from external sources.
    """
    def fetch_recent_news(self) -> List[Dict[str, Any]]:
        """
        Returns a list of raw news objects.
        """
        # Mock articles for MVP simulation
        return [
            {
                "id": f"news_{int(time.time())}_1",
                "source": "Reuters",
                "headline": "TCS wins $1.2B digital transformation deal from European Bank.",
                "content": "TCS announced today it has secured a massive $1.2B contract over 5 years...",
                "timestamp": "2026-07-18T10:00:00Z",
                "reliability_score": 0.95
            },
            {
                "id": f"news_{int(time.time())}_2",
                "source": "RBI Press Release",
                "headline": "RBI hikes repo rate by 25 bps to curb inflation.",
                "content": "The central bank decided to increase the repo rate by 25 basis points...",
                "timestamp": "2026-07-18T10:30:00Z",
                "reliability_score": 0.99
            },
            {
                "id": f"news_{int(time.time())}_3",
                "source": "Bloomberg",
                "headline": "Reliance Industries reports a 15% jump in quarterly profits.",
                "content": "Strong refining margins drove Reliance to a 15% increase in Q3 net profit...",
                "timestamp": "2026-07-18T11:15:00Z",
                "reliability_score": 0.92
            }
        ]
