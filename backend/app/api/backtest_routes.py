from datetime import date
from typing import Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from app.backtest.engine import BacktestEngine
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.backtest import BacktestRun

router = APIRouter()

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
def list_backtest_runs(db: Session = Depends(get_db)):
    """List all executed backtest runs (metadata only)."""
    runs = db.query(BacktestRun).order_by(BacktestRun.created_at.desc()).all()
    return [{
        "id": run.id,
        "strategy": run.strategy_name,
        "symbol": run.config.get("symbol", "N/A") if run.config else "N/A",
        "start_date": run.start_date,
        "end_date": run.end_date,
        "total_return": run.total_return,
        "win_rate": run.win_rate,
        "sharpe_ratio": run.sharpe_ratio,
        "max_drawdown": run.max_drawdown,
        "created_at": run.created_at
    } for run in runs]

@router.get("/runs/{run_id}")
def get_backtest_run(run_id: int, db: Session = Depends(get_db)):
    """Retrieve full details and trade history for a specific backtest run."""
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Backtest run not found")
        
    trades = [{
        "id": t.id,
        "symbol": t.symbol,
        "action": t.action,
        "entry_date": t.entry_date,
        "entry_price": t.entry_price,
        "exit_date": t.exit_date,
        "exit_price": t.exit_price,
        "return_pct": t.return_pct,
        "holding_days": t.holding_days
    } for t in run.trades]
    
    return {
        "metadata": {
            "id": run.id,
            "strategy": run.strategy_name,
            "config": run.config,
            "start_date": run.start_date,
            "end_date": run.end_date,
            "initial_capital": run.initial_capital,
            "final_capital": run.final_capital,
            "total_return": run.total_return,
            "sharpe_ratio": run.sharpe_ratio,
            "max_drawdown": run.max_drawdown,
            "win_rate": run.win_rate,
            "total_trades": run.total_trades,
            "created_at": run.created_at
        },
        "trades": trades
    }
