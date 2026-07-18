from typing import Dict, Any, List
import random
import logging

logger = logging.getLogger("EnsembleDetector")

class EnsembleDetector:
    """
    Combines outputs from multiple Regime Detection models to 
    determine the highest-confidence market regime.
    """
    def __init__(self):
        self.models = ["HMM", "GMM", "GradientBoost", "RuleBased"]
        self.regimes = [
            "strong_bull", "weak_bull", "high_volatility_expansion", 
            "panic", "recovery", "sideways_consolidation"
        ]
        
    def detect_current_regime(self) -> Dict[str, Any]:
        """
        Simulates an ensemble vote.
        """
        # In a real environment, this calls each model and weights their outputs.
        # Here we mock a detection outcome.
        
        # Let's say we detect a high volatility expansion regime currently.
        detected = "high_volatility_expansion"
        
        return {
            "regime": detected,
            "confidence": round(random.uniform(75.0, 95.0), 1),
            "evidence": [
                "India VIX above 85th percentile",
                "Breadth deterioration observed in mid-caps",
                "Rising bond yields (+15bps)",
                "Increasing realized volatility on Nifty50"
            ],
            "model_votes": {
                "HMM": "high_volatility_expansion",
                "GMM": "high_volatility_expansion",
                "GradientBoost": "panic",
                "RuleBased": "high_volatility_expansion"
            }
        }
        
    def detect_historical_regimes(self, days=365) -> List[Dict[str, Any]]:
        """
        Returns a mock timeseries of historical regimes.
        """
        history = []
        current_regime = "strong_bull"
        
        for i in range(days):
            if random.random() < 0.05: # 5% chance to change regime daily
                current_regime = random.choice(self.regimes)
                
            history.append({
                "day_offset": -i,
                "regime": current_regime
            })
            
        return history
