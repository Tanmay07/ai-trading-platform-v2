import random
from typing import Dict, Any, List

class CorrelationAnalyzer:
    """
    Computes inter-strategy correlation to ensure the portfolio is diversified.
    """
    def compute_matrix(self, active_strategies: List[str]) -> Dict[str, Dict[str, float]]:
        matrix = {}
        for s1 in active_strategies:
            matrix[s1] = {}
            for s2 in active_strategies:
                if s1 == s2:
                    matrix[s1][s2] = 1.0
                else:
                    # Deterministic mock correlation between -0.4 and 0.8
                    # Hash the names so it's symmetrical (A->B == B->A)
                    hash_str = "".join(sorted([s1, s2]))
                    random.seed(hash_str)
                    matrix[s1][s2] = round(random.uniform(-0.4, 0.8), 2)
        return matrix
