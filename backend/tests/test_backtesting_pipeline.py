import pytest
import math
from app.backtesting.transaction_cost_engine import TransactionCostEngine
from app.backtesting.slippage_engine import SlippageEngine
from app.backtesting.liquidity_engine import LiquidityEngine
from app.backtesting.capacity_engine import CapacityEngine
from app.backtesting.validation_engine import ValidationEngine

def test_transaction_cost_engine():
    engine = TransactionCostEngine()
    # 100,000 INR trade
    trade_value = 100000.0
    
    # Buy: Stamp duty applies
    buy_cost = engine.calculate_costs(trade_value, is_buy=True)
    assert buy_cost > 0.0
    
    # Sell: No stamp duty
    sell_cost = engine.calculate_costs(trade_value, is_buy=False)
    assert sell_cost > 0.0
    
    assert buy_cost > sell_cost

def test_slippage_engine():
    engine = SlippageEngine()
    
    normal_slippage = engine.calculate_slippage_pct(volatility=0.01)
    high_vol_slippage = engine.calculate_slippage_pct(volatility=0.05)
    
    assert high_vol_slippage > normal_slippage

def test_liquidity_engine():
    engine = LiquidityEngine()
    
    # 5% max participation
    adv = 100000
    max_part = 0.05
    
    # 4000 shares is 4%
    assert engine.validate_execution(4000, adv, max_part) == True
    # 6000 shares is 6%
    assert engine.validate_execution(6000, adv, max_part) == False

def test_capacity_engine():
    engine = CapacityEngine()
    
    adv = 100000
    price = 500.0
    max_part = 0.05
    
    # capacity = (100000 * 0.05) * 500 = 5000 * 500 = 2500000
    capacity = engine.calculate_capacity(adv, price, max_part)
    
    assert math.isclose(capacity, 2500000.0)

def test_validation_engine():
    engine = ValidationEngine()
    
    # Pass scenario
    bt_res = {"simulated_cagr": 0.25, "simulated_drawdown": 0.10, "win_rate": 0.55}
    mc_res = {"survival_probability": 0.99}
    
    val1 = engine.validate(bt_res, mc_res)
    assert val1["status"] == "APPROVED"
    assert val1["score"] == 95
    
    # Fail scenario
    bt_res_fail = {"simulated_cagr": 0.05, "simulated_drawdown": 0.10, "win_rate": 0.55}
    val2 = engine.validate(bt_res_fail, mc_res)
    assert val2["status"] == "REJECTED"
    assert len(val2["reasons"]) > 0
