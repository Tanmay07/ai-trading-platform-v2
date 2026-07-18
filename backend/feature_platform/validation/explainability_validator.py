class ExplainabilityValidator:
    """
    Stage 9: Explainability Readiness
    """
    def __init__(self):
        # Basic heuristic dictionary
        self.explainability_map = {
            "trend": {"score": 90, "class": "Highly Explainable"},
            "momentum": {"score": 85, "class": "Highly Explainable"},
            "volatility": {"score": 80, "class": "Highly Explainable"},
            "price_action": {"score": 95, "class": "Highly Explainable"},
            "volume": {"score": 85, "class": "Highly Explainable"},
            "cross_sectional": {"score": 70, "class": "Moderately Explainable"},
            "regime": {"score": 60, "class": "Moderately Explainable"},
            "event": {"score": 95, "class": "Highly Explainable"},
            "risk": {"score": 75, "class": "Moderately Explainable"},
            "portfolio": {"score": 70, "class": "Moderately Explainable"},
            "default": {"score": 50, "class": "Black Box"}
        }
        
    def validate_feature(self, feature_col: str, category: str = "default") -> dict:
        info = self.explainability_map.get(category, self.explainability_map["default"])
        
        # Penalize if feature name is extremely long or complex
        score = info["score"]
        if len(feature_col) > 30:
            score -= 10
            
        return {
            "valid": True,
            "explainability_score": max(0, score),
            "explainability_class": info["class"],
            "issues": []
        }
