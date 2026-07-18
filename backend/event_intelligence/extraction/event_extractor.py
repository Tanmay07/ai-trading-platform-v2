import random
from typing import Dict, Any

class EventExtractor:
    """
    Simulates an LLM parsing unstructured text into a structured Event schema.
    """
    def extract_event(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw news and extracts factual event data.
        """
        headline = article.get("headline", "")
        
        # Simulated LLM logic based on keyword matching for MVP
        event = {
            "source_id": article["id"],
            "timestamp": article["timestamp"],
            "confidence": round(random.uniform(0.85, 0.98), 2)
        }
        
        if "wins" in headline.lower() and "deal" in headline.lower():
            event.update({
                "event_type": "Major Contract Win",
                "company": "TCS.NS",
                "value": "$1.2B",
                "industry": "IT Services"
            })
        elif "hikes repo rate" in headline.lower():
            event.update({
                "event_type": "Macro Interest Rate Hike",
                "company": "MACRO_IN",
                "value": "+25 bps",
                "industry": "Banking"
            })
        elif "profits" in headline.lower():
            event.update({
                "event_type": "Earnings Surprise",
                "company": "RELIANCE.NS",
                "value": "+15%",
                "industry": "Energy/Conglomerate"
            })
        else:
            event.update({
                "event_type": "General News",
                "company": "UNKNOWN",
                "value": "N/A",
                "industry": "N/A"
            })
            
        return event
