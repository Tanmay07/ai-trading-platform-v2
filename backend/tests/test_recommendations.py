import pytest
import pandas as pd
from app.recommendations.risk_engine import RiskEngine
from app.recommendations.position_sizer import PositionSizer
from app.recommendations.stop_loss import StopLossEngine
from app.recommendations.target_engine import TargetEngine
from app.recommendations.confidence_engine import ConfidenceEngine
from app.config_yaml import trading_config

def test_risk_engine():
    engine = RiskEngine()
    # Override config for testing
    engine.config.max_portfolio_risk_percent = 2.0
    engine.config.max_position_allocation_percent = 10.0
    
    res = engine.calculate_risk_limits(100000, current_exposure=10000)
    assert res["max_capital_allocation"] == 10000
    assert res["max_monetary_risk"] == 2000
    assert res["available_buying_power"] == 90000

def test_position_sizer():
    sizer = PositionSizer()
    res = sizer.calculate_position(
        entry_price=100,
        stop_loss=90,
        max_monetary_risk=200,
        max_capital_allocation=1500,
        available_buying_power=2000,
        portfolio_capital=10000
    )
    # Risk per share = 10. Max monetary risk allows 20 shares.
    # Max capital allocation allows 15 shares.
    # Min is 15.
    assert res["recommended_quantity"] == 15
    assert res["capital_required"] == 1500
    assert res["risk_amount"] == 150

def test_position_sizer_insufficient_buying_power():
    sizer = PositionSizer()
    res = sizer.calculate_position(
        entry_price=100,
        stop_loss=90,
        max_monetary_risk=200,
        max_capital_allocation=1500,
        available_buying_power=500,
        portfolio_capital=10000
    )
    # Buying power limits it to 5 shares.
    assert res["recommended_quantity"] == 5

def test_stop_loss_engine():
    engine = StopLossEngine()
    engine.atr_multiplier = 1.5
    
    df = pd.DataFrame({
        "Low": [95, 94, 96, 92, 93],
        "atr_14": [2.0, 2.1, 2.0, 2.0, 2.0],
        "bb_lower": [91, 91, 91, 91, 91]
    })
    
    res = engine.calculate_stop_loss(df, entry_price=100)
    # ATR Stop = 100 - (2.0 * 1.5) = 97
    # Swing Low = 92
    # Support = 91
    # Minimum of (97, 92, 91) = 91
    assert res["selected_stop"] == 91
    assert res["total_risk"] == 9

def test_target_engine():
    engine = TargetEngine()
    engine.ratios.target_1 = 1.0
    engine.ratios.target_2 = 2.0
    engine.ratios.target_3 = 3.0
    
    res = engine.calculate_targets(100, 90) # 10 point risk
    assert res["target_1"] == 110
    assert res["target_2"] == 120
    assert res["target_3"] == 130
    assert res["potential_loss_per_share"] == 10

def test_confidence_engine():
    engine = ConfidenceEngine()
    
    # Perfect bullish setup with 6 rows to pass the len(df) > 5 checks
    data = {
        "Close": [110] * 6,
        "ema_20": [105] * 6,
        "ema_50": [100] * 6,
        "ema_200": [90] * 6,
        "rsi_14": [65] * 6,
        "macd": [1.5] * 6,
        "macd_signal": [1.0] * 6,
        "adx_14": [30] * 6,
        "relative_volume": [2.0] * 6,
        "bb_bandwidth": [5, 6, 7, 8, 9, 10], # Expanding volatility
        "Volume": [1000, 1000, 1000, 1000, 1000, 2500], # Volume spike
        "obv": [100, 200, 300, 400, 500, 600] # Trending up
    }
    df = pd.DataFrame(data)
    
    res = engine.generate_confidence(df)
    assert res["confidence"] > 80
    assert res["grade"] in ["A", "A+"]
