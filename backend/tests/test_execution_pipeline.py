import pytest
from app.execution.execution_validator import ExecutionValidator
from app.execution.execution_manager import ExecutionManager
from app.execution.execution_orchestrator import ExecutionOrchestrator
from app.config_execution import execution_config

def test_execution_validator():
    validator = ExecutionValidator()
    
    # 1. Kill Switch
    execution_config.risk_limits.kill_switch_active = True
    order = {"quantity": 100, "price": 100}
    res = validator.validate_order(order, [], 100000)
    assert res["valid"] == False
    assert "KILL_SWITCH" in res["reason"]
    
    execution_config.risk_limits.kill_switch_active = False
    
    # 2. Insufficient Funds
    order = {"quantity": 100, "price": 100} # 10k required
    res = validator.validate_order(order, [], 5000) # 5k available
    assert res["valid"] == False
    assert "INSUFFICIENT_FUNDS" in res["reason"]
    
    # 3. Valid Order
    res = validator.validate_order(order, [], 50000)
    assert res["valid"] == True

def test_execution_manager():
    manager = ExecutionManager()
    
    funds = manager.get_funds()
    assert funds > 0
    
    order = {"quantity": 100, "price": 100}
    res = manager.execute_order(order)
    assert res["status"] == "FILLED"
    assert "order_id" in res

def test_execution_orchestrator():
    orchestrator = ExecutionOrchestrator()
    reco = {"Ticker": "INFY"}
    
    res = orchestrator.process_recommendation(reco)
    assert res["status"] == "FILLED"
