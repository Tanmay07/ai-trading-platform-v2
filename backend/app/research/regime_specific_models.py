from typing import Dict, Any

class RegimeSpecificModels:
    def classify_regime(self, strategy: Dict[str, Any]) -> str:
        """
        Tags the strategy with the market regime it performs best in.
        """
        return "BULL_MARKET"
