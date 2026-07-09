from typing import Dict, Any, List

class StrategyRegistry:
    def __init__(self):
        self.registry = []
        
    def register_candidate(self, strategy: Dict[str, Any]):
        """
        Saves a validated strategy for human review.
        """
        strategy["status"] = "PENDING_APPROVAL"
        self.registry.append(strategy)
        
    def get_candidates(self) -> List[Dict[str, Any]]:
        return self.registry
