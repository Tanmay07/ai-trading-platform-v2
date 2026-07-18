from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from portfolio_optimizer.engine.optimizer import PortfolioOptimizerEngine
from portfolio_optimizer.engine.digital_twin import PortfolioDigitalTwin
from portfolio_optimizer.validation.scenario_analysis import ScenarioAnalysis

router = APIRouter(tags=["optimizer"])
optimizer_engine = PortfolioOptimizerEngine()
digital_twin = PortfolioDigitalTwin()
scenario_analysis = ScenarioAnalysis()

@router.post("/optimize")
def run_optimization(request: Dict[str, Any]):
    """
    Runs the optimizer on a provided opportunity set.
    """
    try:
        universe = request.get("opportunity_universe", [])
        method = request.get("method", "hrp")
        
        # 1. Run Core Optimizer
        optimal_portfolio = optimizer_engine.optimize(universe, method)
        
        # 2. Digital Twin Decision
        recommendation = digital_twin.evaluate_rebalance(optimal_portfolio["weights"])
        optimal_portfolio["rebalance_decision"] = recommendation
        
        # 3. Scenario Analysis
        scenarios = scenario_analysis.run_stress_tests(optimal_portfolio["weights"])
        optimal_portfolio["stress_tests"] = scenarios
        
        return optimal_portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
