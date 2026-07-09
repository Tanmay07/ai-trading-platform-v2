from typing import Dict
from app.config_ai import ai_config

class AdaptiveWeightEngine:
    def __init__(self):
        self.default_weights = ai_config.agent_weights
        self.regime_adjustments = ai_config.regime_adjustments

    def get_weights(self, market_regime: str) -> Dict[str, float]:
        """
        Returns dynamic agent weights based on the current market regime.
        """
        # If the specific regime has an override, use it
        if market_regime in self.regime_adjustments:
            return self.regime_adjustments[market_regime]
            
        # Fallback to default
        return self.default_weights
