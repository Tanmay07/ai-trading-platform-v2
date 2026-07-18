from typing import Dict, Any, List
from .base_strategy import BaseStrategy
import random

class VolatilityStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Volatility", "Capitalizes on short-term price dislocation during high VIX regimes.")

    def generate_signals(self) -> List[Dict[str, Any]]:
        return [{"symbol": "SBIN.NS", "confidence": 0.65, "strategy": self.name}]

    def score_opportunities(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return signals
