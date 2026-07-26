import pytest
from unittest.mock import MagicMock
from decision_engine.engine import InvestmentDecisionEngine
from decision_engine.models import DecisionCategory

def test_decision_engine_strong_buy():
    # Setup Mocks
    mock_mds = MagicMock()
    mock_ps = MagicMock()
    
    engine = InvestmentDecisionEngine(mock_ps, mock_mds)
    
    # Mocking intelligence components to force a STRONG BUY
    engine.tech_engine.analyze = MagicMock(return_value={"score": 95, "metrics": {"trend": "Bullish", "rsi": 50, "sma_50": 100}})
    engine.val_engine.analyze = MagicMock(return_value={"score": 95, "metrics": {"pe": 12, "eps_growth": 20, "valuation_status": "Undervalued"}})
    engine.ctx_engine.analyze = MagicMock(return_value={"score": 100, "metrics": {"is_concentrated": False, "current_weight_pct": 2}})
    engine.risk_engine.analyze = MagicMock(return_value={"score": 90, "metrics": {"volatility_pct": 15, "max_drawdown_pct": -10, "risk_profile": "Low"}})
    
    rec = engine.analyze_holding("TCS", portfolio_id=1, user_id="tenant_1", current_price=1000.0)
    
    assert rec.decision == DecisionCategory.STRONG_BUY
    assert rec.confidence > 90.0
    assert "Attractive valuation with PE at 12x" in rec.explanation_why

def test_decision_engine_concentration_penalty():
    # Setup Mocks
    mock_mds = MagicMock()
    mock_ps = MagicMock()
    
    engine = InvestmentDecisionEngine(mock_ps, mock_mds)
    
    # Same high scores for fundamental and tech
    engine.tech_engine.analyze = MagicMock(return_value={"score": 95, "metrics": {"trend": "Bullish", "rsi": 50, "sma_50": 100}})
    engine.val_engine.analyze = MagicMock(return_value={"score": 95, "metrics": {"pe": 12, "eps_growth": 20, "valuation_status": "Undervalued"}})
    engine.risk_engine.analyze = MagicMock(return_value={"score": 90, "metrics": {"volatility_pct": 15, "max_drawdown_pct": -10, "risk_profile": "Low"}})
    
    # BUT heavily concentrated!
    engine.ctx_engine.analyze = MagicMock(return_value={"score": 20, "metrics": {"is_concentrated": True, "current_weight_pct": 30}})
    
    rec = engine.analyze_holding("RELIANCE", portfolio_id=1, user_id="tenant_1", current_price=1000.0)
    
    # Should downgrade from STRONG BUY due to 20% weight of context pulling it down
    assert rec.decision != DecisionCategory.STRONG_BUY
