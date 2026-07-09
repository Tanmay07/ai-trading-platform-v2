import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MarketMemoryEngine:
    """
    Tracks how similar news affected a stock historically.
    Institutional enhancement turning sentiment into historically validated predictions.
    """
    
    def __init__(self):
        # In a real system, this queries the historical data lake joining news + price.
        # Here we mock the historical intelligence database.
        self._mock_memory = {
            "BEL": {
                "Business": { # Order Wins
                    "matches": 18,
                    "avg_t7_return": 8.6,
                    "success_rate": 78,
                    "avg_drawdown": -2.3
                }
            },
            "TCS": {
                "Earnings": {
                    "matches": 40,
                    "avg_t7_return": 3.2,
                    "success_rate": 65,
                    "avg_drawdown": -1.5
                }
            }
        }

    def get_historical_context(self, symbol: str, event_type: str, sentiment: str) -> Optional[Dict[str, Any]]:
        """
        Looks up what usually happens to this stock when this event occurs.
        """
        # A positive event context
        if sentiment == "Neutral" or event_type == "General":
            return None
            
        company_mem = self._mock_memory.get(symbol)
        if not company_mem:
            return None
            
        event_mem = company_mem.get(event_type)
        if not event_mem:
            return None
            
        # If sentiment is negative, we'd invert or have a different lookup.
        # For simplicity, returning the mocked data.
        return {
            "symbol": symbol,
            "event_type": event_type,
            "historical_matches": event_mem["matches"],
            "avg_t7_return_pct": event_mem["avg_t7_return"] if sentiment == "Positive" else -event_mem["avg_t7_return"],
            "success_rate_pct": event_mem["success_rate"],
            "avg_drawdown_pct": event_mem["avg_drawdown"],
            "confidence_score": min(95, event_mem["success_rate"] + (event_mem["matches"] / 2))
        }
        
    def generate_insight_text(self, symbol: str, event_type: str, context: Dict[str, Any]) -> str:
        if not context:
            return f"No significant historical edge found for {symbol} {event_type} events."
            
        return (f"This type of event ({event_type}) has historically led to "
                f"{context['avg_t7_return_pct']}% 7-day price action in {symbol} "
                f"with a {context['success_rate_pct']}% success rate across {context['historical_matches']} similar events.")
