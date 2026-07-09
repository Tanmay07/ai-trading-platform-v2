import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DecisionExplainer:
    """Translates a numerical decision into a human-readable explanation."""
    
    def explain(self, symbol: str, action: str, confidence: float, final_score: float, regime: str, scores: Dict[str, float], weights: Dict[str, float]) -> str:
        """Generates English-language reasoning for the decision."""
        
        explanation = f"{action} {symbol} (Confidence: {confidence}% | Score: {final_score})\n"
        explanation += f"Why? Under the current {regime} market regime, the system heavily weighs "
        
        # Find the highest weighted factors
        top_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:2]
        explanation += f"{top_weights[0][0].capitalize()} ({top_weights[0][1]*100}%) and {top_weights[1][0].capitalize()} ({top_weights[1][1]*100}%).\n"
        
        # Highlight strong scores
        strong_scores = [k for k, v in scores.items() if v >= 80]
        if strong_scores:
            explanation += "Strong signals detected in: " + ", ".join(s.capitalize() for s in strong_scores) + ".\n"
            
        # Highlight weak scores if buying
        weak_scores = [k for k, v in scores.items() if v <= 40]
        if action == "BUY" and weak_scores:
            explanation += "Warning: Weakness remains in: " + ", ".join(s.capitalize() for s in weak_scores) + "."
            
        return explanation.strip()
