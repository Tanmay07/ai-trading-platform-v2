import pytest
from app.reinforcement.reward_engine import RewardEngine
from app.reinforcement.state_builder import StateBuilder
from app.reinforcement.confidence_optimizer import ConfidenceOptimizer
from app.reinforcement.action_engine import ActionEngine

def test_reward_engine():
    engine = RewardEngine()
    
    trade_success = {
        "profit_pct": 0.15,
        "max_drawdown": 0.02,
        "holding_period_days": 5,
        "hit_target": True
    }
    
    trade_fail = {
        "profit_pct": -0.05,
        "max_drawdown": 0.06,
        "holding_period_days": 10,
        "hit_target": False
    }
    
    r1 = engine.calculate_reward(trade_success)
    r2 = engine.calculate_reward(trade_fail)
    
    assert r1 > r2
    assert r1 > 0

def test_state_builder():
    builder = StateBuilder()
    mock_candidate = {
        "breakout_score": 75,
        "Relative_Strength": 1.2,
        "regime": "Strong Bull",
        "market_score": 80,
        "consensus_score": 90,
        "buy_probability": 0.85
    }
    
    state = builder.build_state(mock_candidate)
    
    assert len(state) == 6
    assert state[0] == 0.75 # normalized breakout
    assert state[1] == 1.2  # relative strength
    assert state[2] == 1.0  # regime
    assert state[3] == 0.8  # market score
    
def test_confidence_optimizer():
    opt = ConfidenceOptimizer()
    
    assert opt.calibrate(80, 0.1) == 88.0
    assert opt.calibrate(80, -0.1) == 72.0
    assert opt.calibrate(95, 0.5) == 100.0 # bounds
    
def test_action_engine():
    engine = ActionEngine()
    # bounds are config limits, e.g. max_confidence_adjust = 0.15, min_exposure = -0.20
    action = engine.decode_action([0.5, -0.5])
    assert action["confidence_adjustment"] == 0.15
    assert action["exposure_multiplier"] == 0.80
