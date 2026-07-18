from fastapi import APIRouter
from pydantic import BaseModel
from portfolio_intelligence.engine import PortfolioIntelligenceEngine
from portfolio_intelligence.scenario_analyzer import ScenarioAnalyzer
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio

router = APIRouter()

class ScenarioRequest(BaseModel):
    symbol: str
    amount: float
    action: str = 'BUY'

@router.get("/dashboard")
def get_decision_workspace():
    engine = PortfolioIntelligenceEngine()
    workspace = engine.generate_daily_workspace()
    return {"workspace": workspace}

@router.post("/scenario")
def run_scenario(req: ScenarioRequest):
    portfolio = VirtualPortfolio()
    port_summary = portfolio.get_portfolio_summary()
    
    cash = port_summary.get('cash_balance', 0.0)
    positions = port_summary.get('open_positions', [])
    
    analyzer = ScenarioAnalyzer()
    try:
        impact = analyzer.simulate_trade(positions, cash, req.symbol, req.amount, req.action)
        return {"impact": impact}
    except Exception as e:
        return {"error": str(e)}
