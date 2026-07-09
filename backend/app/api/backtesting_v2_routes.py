from fastapi import APIRouter
from typing import Dict, Any
from app.backtesting.backtesting_orchestrator import BacktestingOrchestrator

router = APIRouter(prefix="/api/backtest_v2", tags=["Backtesting Phase 8"])

@router.post("/run")
def run_backtest(strategy_name: str = "Breakout_AI_v5") -> Dict[str, Any]:
    orchestrator = BacktestingOrchestrator()
    # Mocking some trades
    mock_trades = [{"ticker": "TCS", "action": "BUY"}]
    report = orchestrator.validate_strategy(strategy_name, mock_trades)
    return report

@router.get("/report")
def get_report() -> Dict[str, Any]:
    return {"status": "ok", "message": "Returns latest generated backtest report."}

@router.get("/validation")
def get_validation() -> Dict[str, Any]:
    return {"status": "ok", "message": "Returns the validation scores."}

@router.get("/montecarlo")
def get_montecarlo() -> Dict[str, Any]:
    return {"status": "ok", "message": "Returns the monte carlo analysis."}

@router.get("/walkforward")
def get_walkforward() -> Dict[str, Any]:
    return {"status": "ok", "message": "Returns the walk forward analysis."}
