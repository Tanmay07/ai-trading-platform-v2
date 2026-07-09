from typing import Dict, Any, List

class FactorLibrary:
    def __init__(self):
        self.factors = []
        
    def save_factor(self, factor: Dict[str, Any]):
        self.factors.append(factor)
        
    def get_top_factors(self) -> List[Dict[str, Any]]:
        return self.factors
