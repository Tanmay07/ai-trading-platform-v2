from fastapi import APIRouter
from typing import Dict, Any, List
from app.execution.execution_orchestrator import ExecutionOrchestrator
from app.execution.account_manager import AccountManager
from app.execution.execution_manager import ExecutionManager

router = APIRouter(prefix="/api/execution", tags=["Execution Phase 9"])

@router.get("/account")
def get_account() -> Dict[str, Any]:
    manager = AccountManager()
    return manager.get_account_summary()

@router.get("/positions")
def get_positions() -> List[Dict[str, Any]]:
    manager = ExecutionManager()
    return manager.get_positions()

@router.post("/order/test")
def test_order() -> Dict[str, Any]:
    orchestrator = ExecutionOrchestrator()
    mock_reco = {"Ticker": "RELIANCE", "Action": "BUY", "Portfolio_Fit_Score": 0.95}
    return orchestrator.process_recommendation(mock_reco)
