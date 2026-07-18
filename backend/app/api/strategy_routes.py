from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from strategies.registry.strategy_registry import StrategyRegistry
from strategies.evaluation.correlation_analyzer import CorrelationAnalyzer
from strategies.orchestrator.strategy_portfolio import StrategyPortfolio

router = APIRouter(tags=["strategies"])
registry = StrategyRegistry()
portfolio_manager = StrategyPortfolio()
correlation_analyzer = CorrelationAnalyzer()

@router.get("/registry")
def get_strategy_registry():
    """
    Retrieves all strategies currently in the registry.
    """
    try:
        strategies = registry.list_all_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebalance")
def trigger_strategy_rebalance():
    """
    Triggers the strategy evaluation and allocation rebalance cycle.
    """
    try:
        allocations = portfolio_manager.rebuild_portfolio()
        return {"message": "Strategy Portfolio Rebalanced successfully.", "allocations": allocations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation")
def get_strategy_correlation():
    """
    Retrieves the inter-strategy correlation matrix.
    """
    try:
        strategies = list(portfolio_manager.plugins.keys())
        matrix = correlation_analyzer.compute_matrix(strategies)
        return matrix
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
