import logging

logger = logging.getLogger(__name__)

class ConfidenceEngine:
    """Calculates final confidence of a prediction."""
    
    @staticmethod
    def calculate_confidence(scores: dict, model_agreement: float, data_freshness: float) -> float:
        """
        Combines various meta-signals into a final confidence score 0-100.
        `model_agreement` : How much the ensemble ML models agree (0-1).
        `data_freshness` : How fresh the data is (0-1).
        """
        # Baseline confidence starts with ML agreement
        base = model_agreement * 100.0
        
        # Penalize if data is stale
        penalty = (1.0 - data_freshness) * 20.0
        
        # Boost if technical and sentiment are extremely high
        boost = 0
        if scores.get("technical", 0) > 80 and scores.get("news", 0) > 80:
            boost += 10
            
        final = base - penalty + boost
        return min(100.0, max(0.0, final))
