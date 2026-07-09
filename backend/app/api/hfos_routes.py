from fastapi import APIRouter
from typing import Dict, Any, List
from app.hfos.command_center import CommandCenter
from app.hfos.reporting_center import ReportingCenter
from app.hfos.strategy_marketplace import StrategyMarketplace

router = APIRouter(prefix="/api/hfos", tags=["HFOS Phase 12"])

@router.get("/dashboard")
def get_hfos_dashboard() -> Dict[str, Any]:
    cmd = CommandCenter()
    return cmd.get_system_health()

@router.get("/strategies")
def get_hfos_strategies() -> List[Dict[str, Any]]:
    marketplace = StrategyMarketplace()
    return marketplace.list_strategies()
    
@router.get("/reports")
def get_hfos_reports() -> Dict[str, Any]:
    reports = ReportingCenter()
    return reports.generate_daily_cio_report()
