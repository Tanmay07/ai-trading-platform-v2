def adjust_recommendation_confidence(base_confidence: float, score: float, category: str) -> float:
    """
    Instead of outright rejecting recommendations for lower-tier stocks, we heavily penalize 
    their confidence scores to reflect Execution Risk.
    """
    penalty_multiplier = 1.0
    
    if category == "Institutional Grade":
        penalty_multiplier = 1.0
    elif category == "Highly Tradable":
        penalty_multiplier = 0.95
    elif category == "Tradable":
        penalty_multiplier = 0.85
    elif category == "Monitor":
        penalty_multiplier = 0.60
    elif category == "Restricted":
        penalty_multiplier = 0.10 # Essentially kills the recommendation
        
    return base_confidence * penalty_multiplier

def get_execution_risk_label(category: str) -> str:
    if category in ["Institutional Grade", "Highly Tradable"]:
        return "Low Risk"
    elif category == "Tradable":
        return "Medium Risk"
    else:
        return "High Risk"
