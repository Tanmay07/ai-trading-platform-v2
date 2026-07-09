from typing import Dict, Any

class StrategyAllocator:
    def get_strategy_allocation(self, strategy_id: str) -> float:
        """
        Retrieves the specific maximum allocation for a given strategy.
        """
        return 0.20 # 20% limit
