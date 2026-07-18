import logging
from typing import Dict, Any, List

logger = logging.getLogger("EntryOptimizer")

class EntryOptimizer:
    """
    Implements the Execution Strategy Framework.
    Generates multiple candidate entry strategies for a position and scores them.
    """
    
    def generate_entry_strategies(self, position: Dict[str, Any], current_price: float) -> List[Dict[str, Any]]:
        volatility = position.get("volatility", 0.02)
        
        strategies = []
        
        # 1. Market Entry (Immediate)
        strategies.append({
            "name": "Immediate Market Entry",
            "type": "market",
            "entry_price": current_price,
            "max_slippage": current_price * 0.005, # 0.5% max chase
            "validity_window": "1_day",
            "score": self._score_strategy("market", volatility)
        })
        
        # 2. Limit Entry (Pullback)
        pullback_price = current_price * (1 - (volatility * 0.5))
        strategies.append({
            "name": "Conservative Pullback Limit",
            "type": "limit",
            "entry_price": pullback_price,
            "max_slippage": pullback_price * 0.001,
            "validity_window": "3_days",
            "score": self._score_strategy("limit", volatility)
        })
        
        # 3. Breakout Confirmation (Stop-Limit)
        breakout_price = current_price * (1 + (volatility * 0.2))
        strategies.append({
            "name": "Breakout Confirmation",
            "type": "stop_limit",
            "entry_price": breakout_price,
            "max_slippage": breakout_price * 0.002,
            "validity_window": "2_days",
            "score": self._score_strategy("breakout", volatility)
        })
        
        # Sort by score descending
        return sorted(strategies, key=lambda x: x["score"], reverse=True)
        
    def _score_strategy(self, strat_type: str, volatility: float) -> int:
        # High volatility -> Prefer Pullbacks
        # Low volatility -> Prefer Breakouts or Market
        if strat_type == "market":
            return int(max(10, 80 - (volatility * 1000)))
        elif strat_type == "limit":
            return int(min(90, 40 + (volatility * 1000)))
        elif strat_type == "breakout":
            return 75 # Consistent baseline score
        return 50
