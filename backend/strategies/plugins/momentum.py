from typing import Dict, Any, List
from .base_strategy import BaseStrategy
import random

class MomentumStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Momentum", "Capitalizes on prevailing trends and relative strength.")

    def generate_signals(self) -> List[Dict[str, Any]]:
        # Dummy mock signals
        return [{"symbol": "RELIANCE.NS", "confidence": 0.85, "strategy": self.name}]

    def score_opportunities(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return signals
