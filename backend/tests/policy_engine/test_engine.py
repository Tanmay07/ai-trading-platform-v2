import pytest
from unittest.mock import MagicMock
from policy_engine.engine import DecisionPolicyEngine
from policy_engine.models import PolicyVersion, Policy
from decision_engine.models import DecisionCategory

def test_decision_policy_engine_growth_vs_value():
    mock_mds = MagicMock()
    mock_ps = MagicMock()
    mock_db = MagicMock()
    
    engine = DecisionPolicyEngine(mock_ps, mock_mds, mock_db)
    
    # Mocking standard inputs:
    # Strong Tech (100), Weak Valuation (10), Normal Context (100), Normal Risk (100)
    # This is a classic "Growth/Momentum" stock, but a terrible "Value" stock.
    engine.tech_engine.analyze = MagicMock(return_value={"score": 100, "metrics": {"trend": "Strong Bullish", "rsi": 75, "sma_50": 100}})
    engine.val_engine.analyze = MagicMock(return_value={"score": 10, "metrics": {"pe": 50, "eps_growth": 5, "valuation_status": "Overvalued"}})
    engine.ctx_engine.analyze = MagicMock(return_value={"score": 100, "metrics": {"is_concentrated": False, "current_weight_pct": 2}})
    engine.risk_engine.analyze = MagicMock(return_value={"score": 100, "metrics": {"volatility_pct": 20, "max_drawdown_pct": -5, "risk_profile": "Low"}})
    
    # 1. Growth Policy (Cares mostly about tech, ignores valuation)
    growth_policy = PolicyVersion(
        id=1,
        policy=Policy(name="Aggressive Growth"),
        weights={"technical": 80, "valuation": 0, "context": 10, "risk": 10},
        thresholds={"strong_buy": 90, "buy": 80},
        target_logic={}, stop_loss_logic={}, sizing_rules={}
    )
    
    # 2. Value Policy (Cares mostly about valuation)
    value_policy = PolicyVersion(
        id=2,
        policy=Policy(name="Deep Value"),
        weights={"technical": 10, "valuation": 70, "context": 10, "risk": 10},
        thresholds={"strong_buy": 90, "buy": 80},
        target_logic={}, stop_loss_logic={}, sizing_rules={}
    )
    
    # Execute with Growth
    rec_growth = engine.execute_policy("STOCK", 1, "user1", 100, growth_policy)
    
    # Execute with Value
    rec_value = engine.execute_policy("STOCK", 1, "user1", 100, value_policy)
    
    # Assertions
    assert rec_growth.confidence == 100 # (100*0.8) + (10*0) + (100*0.1) + (100*0.1) = 80 + 0 + 10 + 10 = 100
    assert rec_growth.decision == DecisionCategory.STRONG_BUY
    
    assert rec_value.confidence == 37 # (100*0.1) + (10*0.7) + (100*0.1) + (100*0.1) = 10 + 7 + 10 + 10 = 37
    assert rec_value.decision == DecisionCategory.TRIM_POSITION # < 40
    
    # Verify explanations differ by policy
    assert "Aggressive Growth" in rec_growth.explanation_why
    assert "Deep Value" in rec_value.explanation_why
    
    # Verify Audit trail was saved
    assert mock_db.add.call_count == 2
