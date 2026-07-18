from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import random

from execution.planner.execution_engine import ExecutionEngine

router = APIRouter(tags=["execution"])

class ExecutionRequest(BaseModel):
    portfolio_positions: List[Dict[str, Any]]
    total_capital: float = 100000.0

@router.post("/generate")
def generate_execution_plans(req: ExecutionRequest):
    """
    Generates execution plans from a list of approved portfolio positions.
    """
    try:
        engine = ExecutionEngine()
        result = engine.generate_execution_plans(req.portfolio_positions, req.total_capital)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mock")
def get_mock_execution():
    """
    Returns a mocked execution plan generation for testing the UI directly.
    """
    try:
        # Generate some mock portfolio positions
        positions = []
        for i in range(5):
            positions.append({
                "symbol": f"MOCK_{i}",
                "allocation": 0.08,
                "capital_allocated": 8000.0,
                "trade_quality_prediction": random.uniform(70, 95),
                "confidence": random.uniform(0.7, 0.99),
                "expected_return": random.uniform(5, 15),
                "current_price": random.uniform(100, 500),
                "atr": random.uniform(2, 10),
                "volatility": random.uniform(0.01, 0.05)
            })
            
        engine = ExecutionEngine()
        result = engine.generate_execution_plans(positions, 100000.0)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
