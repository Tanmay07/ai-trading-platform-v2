import logging
from typing import List, Dict, Any

logger = logging.getLogger("CapitalAllocator")

class CapitalAllocator:
    def __init__(self, strategy: str = "score_weighted"):
        self.strategy = strategy
        
    def allocate(self, selected_positions: List[Dict[str, Any]], available_cash: float, max_weight: float) -> List[Dict[str, Any]]:
        if not selected_positions:
            return []
            
        if self.strategy == "equal_weight":
             return self._allocate_equal(selected_positions, available_cash, max_weight)
        elif self.strategy == "score_weighted":
             return self._allocate_score_weighted(selected_positions, available_cash, max_weight)
        else:
             logger.warning(f"Unknown allocation strategy {self.strategy}, defaulting to equal_weight")
             return self._allocate_equal(selected_positions, available_cash, max_weight)
             
    def _allocate_equal(self, positions: List[Dict[str, Any]], cash: float, max_weight: float) -> List[Dict[str, Any]]:
        n = len(positions)
        raw_weight = 1.0 / n
        final_weight = min(raw_weight, max_weight)
        
        for p in positions:
            p['weight'] = final_weight
            p['capital_allocated'] = cash * final_weight
            
        return positions
        
    def _allocate_score_weighted(self, positions: List[Dict[str, Any]], cash: float, max_weight: float) -> List[Dict[str, Any]]:
        # Calculate a combined score for each position
        # Using a blend of Trade Quality and Classification Probability
        for p in positions:
            p['_alloc_score'] = (p.get('trade_quality_prediction', 50) * 0.7) + (p.get('classification_probability', 0.5) * 100 * 0.3)
            
        total_score = sum(p['_alloc_score'] for p in positions)
        
        # Initial allocation
        for p in positions:
            if total_score > 0:
                p['weight'] = p['_alloc_score'] / total_score
            else:
                p['weight'] = 1.0 / len(positions)
                
        # Cap at max_weight and redistribute excess
        # A simple iterative capping algorithm
        excess_weight = 0.0
        capped_count = 0
        
        for p in positions:
            if p['weight'] > max_weight:
                excess_weight += (p['weight'] - max_weight)
                p['weight'] = max_weight
                capped_count += 1
                p['_capped'] = True
            else:
                p['_capped'] = False
                
        # Redistribute
        if excess_weight > 0 and capped_count < len(positions):
            uncapped_score = sum(p['_alloc_score'] for p in positions if not p['_capped'])
            for p in positions:
                if not p['_capped'] and uncapped_score > 0:
                    added_weight = excess_weight * (p['_alloc_score'] / uncapped_score)
                    p['weight'] = min(p['weight'] + added_weight, max_weight)
                    
        # Assign capital
        for p in positions:
            p['capital_allocated'] = cash * p['weight']
            # cleanup internals
            p.pop('_alloc_score', None)
            p.pop('_capped', None)
            
        return positions
