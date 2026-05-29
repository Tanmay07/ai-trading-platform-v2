from datetime import date
from typing import Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.backtest.engine import BacktestEngine
from app.data.s3_service import S3StorageService

router = APIRouter()
s3_svc = S3StorageService()

class BacktestRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 100_000.0

@router.post("/run")
def run_backtest(request: BacktestRequest) -> dict[str, Any]:
    """Execute a backtest simulation for a given symbol and date range."""
    engine = BacktestEngine()
    try:
        result = engine.run_backtest(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/runs")
def list_backtest_runs():
    """List all executed backtest runs (metadata only)."""
    index_data = s3_svc.download_json("backtests/index.json") or []
    
    # Sort by timestamp descending
    index_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return [{
        "id": run.get("id"),
        "strategy": run.get("strategy_name"),
        "symbol": run.get("config", {}).get("symbol", "N/A"),
        "start_date": run.get("start_date"),
        "end_date": run.get("end_date"),
        "total_return": run.get("total_return"),
        "win_rate": run.get("win_rate"),
        "sharpe_ratio": run.get("sharpe_ratio"),
        "max_drawdown": run.get("max_drawdown"),
        "created_at": run.get("timestamp")
    } for run in index_data]

@router.get("/runs/{run_id}")
def get_backtest_run(run_id: str):
    """Retrieve full details and trade history for a specific backtest run."""
    run_data = s3_svc.download_json(f"backtests/{run_id}.json")
    if not run_data:
        raise HTTPException(status_code=404, detail="Backtest run not found")
        
    run = run_data["run_record"]
    trades = run_data.get("trades", [])
    
    return {
        "metadata": {
            "id": run.get("id"),
            "strategy": run.get("strategy_name"),
            "config": run.get("config"),
            "start_date": run.get("start_date"),
            "end_date": run.get("end_date"),
            "initial_capital": run.get("initial_capital"),
            "final_capital": run.get("final_capital"),
            "total_return": run.get("total_return"),
            "sharpe_ratio": run.get("sharpe_ratio"),
            "max_drawdown": run.get("max_drawdown"),
            "win_rate": run.get("win_rate"),
            "total_trades": run.get("total_trades"),
            "created_at": run.get("timestamp")
        },
        "trades": trades
    }
