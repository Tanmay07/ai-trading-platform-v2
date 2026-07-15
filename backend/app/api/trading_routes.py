from fastapi import APIRouter
from typing import Dict, Any, List
from pydantic import BaseModel
from trading_platform.oms.order_manager import OrderManager
from trading_platform.oms.position_manager import PositionManager
from trading_platform.execution.execution_engine import ExecutionEngine
from trading_platform.brokers.broker_factory import BrokerFactory

router = APIRouter(prefix="/api/trading", tags=["Execution Phase 5"])

# Pydantic Models for requests
class OrderRequest(BaseModel):
    symbol: str
    action: str
    confidence: float
    current_price: float

class OrderActionRequest(BaseModel):
    order_id: str

@router.get("/portfolio")
def get_portfolio() -> Dict[str, Any]:
    manager = PositionManager()
    return manager.get_portfolio_summary()

@router.get("/orders")
def get_orders() -> List[Dict[str, Any]]:
    manager = OrderManager()
    return manager.get_all_orders()

@router.get("/broker/status")
def get_broker_status() -> Dict[str, Any]:
    broker = BrokerFactory.get_broker()
    return broker.get_profile()

@router.post("/execute/signal")
def execute_signal(request: OrderRequest) -> Dict[str, Any]:
    """Receives AI signal and routes through Execution Engine"""
    engine = ExecutionEngine()
    return engine.process_signal(request.dict())

@router.post("/execute/approve")
def approve_pending_order(request: OrderActionRequest) -> Dict[str, Any]:
    """Manually approve a pending order"""
    order_mgr = OrderManager()
    order = order_mgr.get_order(request.order_id)
    if not order:
        return {"status": "ERROR", "message": "Order not found"}
        
    if order["status"] != "PENDING_APPROVAL":
        return {"status": "ERROR", "message": f"Order status is {order['status']}, cannot approve."}
        
    engine = ExecutionEngine()
    # Execute the raw order
    return engine.execute_order(order)
