from typing import List, Dict, Any

class OpportunityRanker:
    """Ranks opportunities based on the Meta Decision Engine final score."""
    
    @staticmethod
    def rank(decisions: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Sorts the decisions by final_score descending and confidence descending."""
        
        # Only rank BUY decisions
        buys = [d for d in decisions if d.get("action") == "BUY"]
        
        # Sort by final score, then confidence
        ranked = sorted(buys, key=lambda x: (x.get("final_score", 0), x.get("confidence", 0)), reverse=True)
        
        return ranked[:top_n]
