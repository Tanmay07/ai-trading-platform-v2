from typing import Dict, Any, List

class StrategyMarketplace:
    def __init__(self):
        self.strategies = [
            {"id": "strat_1", "name": "Swing Breakout", "status": "Production", "capacity": 1000000},
            {"id": "strat_2", "name": "Mean Reversion", "status": "Candidate", "capacity": 500000}
        ]
        
    def list_strategies(self) -> List[Dict[str, Any]]:
        return self.strategies
