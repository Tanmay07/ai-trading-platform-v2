from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List
import logging

from data_platform.services.data_orchestrator import DataOrchestrator
from data_platform.universe.universe_manager import UniverseManager

router = APIRouter(prefix="/api/data", tags=["Historical Data Platform"])
logger = logging.getLogger(__name__)

# Singleton instance of orchestrator for background tasks
orchestrator = DataOrchestrator()

@router.get("/universe")
async def get_universe() -> Dict[str, Any]:
    """Returns the active NSE equity universe."""
    universe = orchestrator.universe_manager.fetch_active_universe()
    return {
        "count": len(universe),
        "symbols": [u.to_dict() for u in universe]
    }

@router.get("/quality")
async def get_data_quality() -> Dict[str, Any]:
    """Returns data quality and completeness metrics for the Data Lake."""
    return orchestrator.get_data_quality_report()

@router.post("/bootstrap")
async def run_bootstrap(background_tasks: BackgroundTasks, batch_size: int = 50, years: int = 10) -> Dict[str, Any]:
    """
    Triggers a background bootstrap download of all missing historical data.
    """
    # In production, we'd use Celery or similar for distributed tasks. 
    # For MVP, we use FastAPI background tasks.
    background_tasks.add_task(orchestrator.run_bootstrap_sync, batch_size=batch_size, max_workers=5, years=years)
    return {"status": "accepted", "message": "Bootstrap process started in background."}

@router.post("/update")
async def run_incremental_update(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Triggers a background incremental update for all active symbols.
    """
    background_tasks.add_task(orchestrator.run_incremental_update_sync, max_workers=5)
    return {"status": "accepted", "message": "Incremental update started in background."}

@router.get("/history/{symbol}")
async def get_symbol_history(symbol: str) -> Dict[str, Any]:
    """
    Fetches the loaded Parquet data for a symbol (useful for UI charts).
    """
    df = orchestrator.parquet.load_symbol_data(symbol)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol} in Data Lake.")
        
    # Convert latest 100 rows to dict for frontend
    data = df.tail(100).reset_index().to_dict(orient="records")
    return {
        "symbol": symbol,
        "rows": len(df),
        "preview": data
    }
