from typing import List, Dict, Any
from app.ai.base_agent import AgentResponse

class ExplainabilityEngine:
    def generate_explanation(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        positives = []
        negatives = []
        
        for r in responses:
            for reason in r.reasons:
                if reason.startswith("+"):
                    positives.append(reason[1:].strip())
                elif reason.startswith("-"):
                    negatives.append(reason[1:].strip())
                    
        # Sort or prioritize (here we just take top 3 of each)
        top_positives = positives[:4]
        top_negatives = negatives[:3]
        
        summary = ""
        if top_positives:
            summary += "Strong setup supported by " + ", ".join(top_positives[:2]).lower() + ". "
        if top_negatives:
            summary += "However, concerns include " + ", ".join(top_negatives[:2]).lower() + "."
            
        if not summary:
            summary = "Neutral setup with mixed signals."
            
        return {
            "top_positive_factors": top_positives,
            "top_negative_factors": top_negatives,
            "human_readable_summary": summary.strip()
        }
