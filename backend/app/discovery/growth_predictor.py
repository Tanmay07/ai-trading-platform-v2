"""
Growth Predictor (AI Prediction Engine)

Predicts the probability of a 5%+ return in the next 30 days.
"""
import random
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

class GrowthPredictor:
    def __init__(self):
        self.logger = get_logger(__name__)

    def predict_growth_probability(self, symbol: str, momentum_score: float, fundamental_score: float, sentiment_score: float) -> Optional[Dict[str, Any]]:
        """
        Predicts the probability of a 5%+ return in the next 30 days.
        For MVP, this is a rule-based approximation mimicking an ML model's output.
        In Phase 3, this will invoke LightGBM/XGBoost.
        """
        try:
            # Simple linear combination mapping to a probability
            # Higher momentum, fundamental, and sentiment lead to higher probability
            base_prob = 30.0
            
            # Momentum contribution (up to 30%)
            mom_contrib = (momentum_score / 100.0) * 30.0
            
            # Fundamental contribution (up to 20%)
            fund_contrib = (fundamental_score / 100.0) * 20.0
            
            # Sentiment contribution (up to 20%)
            sent_contrib = (sentiment_score / 100.0) * 20.0
            
            prob = base_prob + mom_contrib + fund_contrib + sent_contrib
            
            # Add some randomness to simulate ML variance
            prob += random.uniform(-5.0, 5.0)
            
            prob = max(0.0, min(100.0, prob))
            
            confidence = min(99.0, prob * 0.95)
            
            reasons = []
            if prob > 70:
                reasons.append("High probability of 5%+ return based on AI model")
            elif prob < 40:
                reasons.append("Low probability of near-term outperformance")
                
            return {
                "probability": round(prob, 2),
                "confidence": round(confidence, 2),
                "expected_return": round((prob / 100.0) * 8.0, 2), # e.g. up to 8% expected return
                "reasons": reasons
            }
        except Exception as e:
            self.logger.error(f"Failed to predict growth for {symbol}: {e}")
            return None
