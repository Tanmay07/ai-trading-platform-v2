from typing import Dict, Any, List
from .base_strategy import BaseStrategy
import random

class MeanReversionStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Mean Reversion", "Capitalizes on statistical reversion from overbought/oversold extremes.")

    def generate_signals(self) -> List[Dict[str, Any]]:
        return [{"symbol": "HDFCBANK.NS", "confidence": 0.75, "strategy": self.name}]

    def score_opportunities(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return signals
