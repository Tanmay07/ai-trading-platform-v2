import yaml
import random
from typing import Dict, Any

class SignificanceEngine:
    """
    Assigns a 0-100 Significance Score to extracted events.
    """
    def __init__(self):
        with open("config/event_intelligence.yaml", "r") as f:
            self.config = yaml.safe_load(f)["event_intelligence"]["significance"]
            
    def score_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the magnitude and rarity of the event.
        """
        event_type = event.get("event_type", "Unknown")
        
        # Base scores based on type
        base_scores = {
            "Macro Interest Rate Hike": 95,
            "Major Contract Win": 85,
            "Earnings Surprise": 80,
            "General News": 20
        }
        
        base_score = base_scores.get(event_type, 50)
        
        # Add small randomization to simulate model variance
        final_score = base_score + random.uniform(-5.0, 5.0)
        final_score = max(0, min(100, round(final_score, 1)))
        
        event["significance_score"] = final_score
        
        if final_score >= self.config["minimum_score"]:
            event["is_significant"] = True
        else:
            event["is_significant"] = False
            
        return event
