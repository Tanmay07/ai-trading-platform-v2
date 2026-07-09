import pytest
import pandas as pd
from unittest.mock import patch

from app.services.market_regime_engine import MarketRegimeEngine
from app.services.market_breadth_engine import MarketBreadthEngine
from app.services.macro_engine import MacroEngine
from app.services.fii_dii_engine import FiiDiiEngine
from app.services.volatility_engine import VolatilityEngine
from app.services.liquidity_engine import LiquidityEngine
from app.services.market_score_engine import MarketScoreEngine
from app.services.market_intelligence_orchestrator import MarketIntelligenceOrchestrator

@pytest.fixture
def mock_market_df():
    data = {
        "Close": [100] * 50 + [110] * 50 + [120] * 50 + [130] * 50 + [140] * 50
    }
    return pd.DataFrame(data)

def test_market_regime(mock_market_df):
    engine = MarketRegimeEngine()
    res = engine.analyze(mock_market_df)
    assert res["regime"] == "Strong Bull"
    assert res["exposure_multiplier"] == 1.0

def test_market_breadth():
    engine = MarketBreadthEngine()
    # Mocking multi index
    arrays = [['RELIANCE.NS'], ['Close']]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples)
    df = pd.DataFrame([100]*250, columns=index)
    
    # Adding High and Low for new highs/lows
    df[('RELIANCE.NS', 'High')] = [105]*250
    df[('RELIANCE.NS', 'Low')] = [95]*250
    
    res = engine.analyze(df)
    assert res["breadth_score"] >= 0

def test_macro_engine():
    engine = MacroEngine()
    arrays = [['^INDIAVIX'], ['Close']]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples)
    df = pd.DataFrame([15]*50, columns=index)
    res = engine.analyze(df)
    assert res["macro_score"] >= 0
    assert "global_sentiment" in res

def test_fii_dii():
    engine = FiiDiiEngine()
    res = engine.analyze()
    assert "fii_score" in res

def test_volatility_engine():
    engine = VolatilityEngine()
    df = pd.DataFrame({"Close": [15]*50})
    res = engine.analyze(df)
    assert res["volatility_state"] == "Normal Volatility"

def test_liquidity_engine():
    engine = LiquidityEngine()
    arrays = [['RELIANCE.NS'], ['Volume']]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples)
    df = pd.DataFrame([1000]*50, columns=index)
    res = engine.analyze(df)
    assert res["liquidity_score"] == 60

def test_market_score():
    engine = MarketScoreEngine()
    res = engine.score(100, 100, 100, 100, 100, 100, 100)
    assert res["market_grade"] in ["A", "A+"]

@patch("app.services.market_intelligence_orchestrator.MarketIntelligenceOrchestrator._fetch_macro_data")
def test_mi_orchestrator(mock_fetch, mock_market_df):
    mock_fetch.return_value = pd.DataFrame()
    orch = MarketIntelligenceOrchestrator()
    res = orch.analyze_market(mock_market_df, pd.DataFrame())
    assert "market_score" in res
    assert "regime" in res
