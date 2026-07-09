import pytest
from app.research.alpha_factory import AlphaFactory
from app.research.genetic_optimizer import GeneticOptimizer
from app.research.alpha_decay_engine import AlphaDecayEngine
from app.research.research_orchestrator import ResearchOrchestrator

def test_alpha_factory():
    factory = AlphaFactory()
    alphas = factory.generate_candidate_factors()
    assert len(alphas) > 0
    assert "formula" in alphas[0]

def test_genetic_optimizer():
    optimizer = GeneticOptimizer()
    base_strategy = {"entry_rsi_min": 60, "stop_loss_pct": 0.05}
    mutated = optimizer.mutate(base_strategy)
    
    assert mutated["entry_rsi_min"] == 60 # untouched
    assert mutated["stop_loss_pct"] != 0.05 # mutated
    
def test_alpha_decay():
    engine = AlphaDecayEngine()
    
    healthy = {"rolling_sharpe": 1.5}
    res = engine.monitor_decay("strat_1", healthy)
    assert res["status"] == "HEALTHY"
    
    decayed = {"rolling_sharpe": 0.15}
    res = engine.monitor_decay("strat_2", decayed)
    assert res["status"] == "DECAYED"
    
def test_orchestrator():
    orchestrator = ResearchOrchestrator()
    res = orchestrator.run_discovery_cycle()
    
    assert "hypothesis" in res
    assert "metrics" in res
    assert res["metrics"]["sharpe_ratio"] > 0
