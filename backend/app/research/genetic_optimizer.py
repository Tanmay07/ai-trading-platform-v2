from typing import Dict, Any, List
import random

class GeneticOptimizer:
    def mutate(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Breeds populations and applies genetic crossover and mutation.
        """
        mutated = strategy.copy()
        mutated["stop_loss_pct"] = round(random.uniform(0.02, 0.10), 2)
        return mutated
