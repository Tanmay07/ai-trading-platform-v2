from typing import Dict, Any, List

class StrategyComparator:
    def compare(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ranks strategies based on Sharpe Ratio.
        """
        sorted_strats = sorted(strategies, key=lambda x: x.get("sharpe", 0.0), reverse=True)
        return {
            "winner": sorted_strats[0] if sorted_strats else None,
            "rankings": sorted_strats
        }
