from typing import Dict, Any, List
import logging

logger = logging.getLogger("EventAlpha")

class EventAlphaGenerator:
    """
    Converts significant structured events into candidate alpha factors 
    for the Alpha Registry (Phase G1).
    """
    def generate_candidates(self, analyzed_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generates new alpha factor candidates from the event stream.
        """
        alpha_candidates = []
        for e in analyzed_events:
            if e.get("is_significant") and e.get("causal_expectations", {}).get("historical_win_rate", 0) > 0.6:
                alpha = {
                    "factor_name": f"{e['event_type'].replace(' ', '')}Factor_{e['company']}",
                    "source": "EventIntelligenceEngine",
                    "description": f"Generated from {e['event_type']} with {e['causal_expectations']['expected_return_60d']}% expected 60-day return.",
                    "status": "Experimental"
                }
                alpha_candidates.append(alpha)
                
        return alpha_candidates
