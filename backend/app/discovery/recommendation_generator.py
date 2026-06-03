"""
Recommendation Generator

Converts raw Opportunity Scores into categorical recommendations and builds
the explanation payloads.
"""
from typing import Dict, Any

class RecommendationGenerator:
    @staticmethod
    def generate_recommendation(opp: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a raw opportunity dictionary and adds categorical recommendations
        and formatted explanations.
        """
        score = opp.get("opportunity_score", 50)
        
        if score >= 80:
            rec = "Strong Buy"
            risk = "Low"
        elif score >= 65:
            rec = "Buy"
            risk = "Medium"
        elif score >= 50:
            rec = "Watchlist"
            risk = "Medium"
        elif score >= 35:
            rec = "Hold"
            risk = "High"
        else:
            rec = "Avoid"
            risk = "High"
            
        opp["recommendation"] = rec
        opp["risk_level"] = risk
        
        # Build the final output explanation
        opp["explanation"] = {
            "key_drivers": opp.get("all_reasons", [])[:4], # Top 4 reasons
            "summary": f"{opp['symbol']} has an opportunity score of {score}. AI predicts a {opp['predicted_return']}% return with {opp['confidence']}% confidence."
        }
        
        return opp
