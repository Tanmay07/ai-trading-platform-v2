from typing import Dict, Any
import uuid
from app.research.hypothesis_engine import HypothesisEngine
from app.research.strategy_generator import StrategyGenerator
from app.research.genetic_optimizer import GeneticOptimizer
from app.research.strategy_evaluator import StrategyEvaluator
from app.research.strategy_registry import StrategyRegistry
from app.research.experiment_manager import ExperimentManager

class ResearchOrchestrator:
    def __init__(self):
        self.hypothesis_engine = HypothesisEngine()
        self.generator = StrategyGenerator()
        self.optimizer = GeneticOptimizer()
        self.evaluator = StrategyEvaluator()
        self.registry = StrategyRegistry()
        self.experiment_manager = ExperimentManager()
        
    def run_discovery_cycle(self) -> Dict[str, Any]:
        """
        The main autonomous research loop.
        """
        experiment_id = str(uuid.uuid4())
        
        # 1. Ideation
        hypothesis = self.hypothesis_engine.generate_hypothesis()
        base_strategy = self.generator.generate_strategy(hypothesis)
        
        # 2. Breeding
        mutated_strategy = self.optimizer.mutate(base_strategy)
        
        # 3. Validation
        evaluated_strategy = self.evaluator.evaluate(mutated_strategy)
        
        # 4. Registration
        if evaluated_strategy["metrics"]["sharpe_ratio"] > 1.5:
            self.registry.register_candidate(evaluated_strategy)
            
        self.experiment_manager.log_experiment(experiment_id, evaluated_strategy)
        
        return evaluated_strategy
