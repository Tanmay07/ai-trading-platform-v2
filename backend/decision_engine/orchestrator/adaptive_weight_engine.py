import logging
from typing import Dict, Any
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class AdaptiveWeightEngine:
    """Dynamically sets model weights based on the current market regime."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("decision_engine")
        self.regimes = self.config.get("regimes", {})
        
    def get_weights(self, regime: str) -> Dict[str, float]:
        """Returns the specific weights for a given regime."""
        regime_config = self.regimes.get(regime)
        
        if not regime_config:
            logger.warning(f"Regime {regime} not found in config, falling back to Neutral.")
            regime_config = self.regimes.get("Neutral", {})
            
        return regime_config.get("weights", {})
