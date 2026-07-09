import pytest
import pandas as pd
from unittest.mock import patch

from app.services.multi_timeframe_engine import MultiTimeframeEngine
from app.services.relative_strength_engine import RelativeStrengthEngine
from app.services.sector_rotation_engine import SectorRotationEngine
from app.services.breakout_pattern_engine import BreakoutPatternEngine
from app.services.price_action_engine import PriceActionEngine
from app.services.vwap_engine import VWAPEngine
from app.services.support_resistance_engine import SupportResistanceEngine
from app.services.breakout_score_engine import BreakoutScoreEngine
from app.services.technical_orchestrator import TechnicalOrchestrator

@pytest.fixture
def mock_df():
    data = {
        "Open": [100] * 50 + [102] * 10,
        "High": [105] * 50 + [106] * 10,
        "Low": [95] * 50 + [101] * 10,
        "Close": [102] * 50 + [105] * 10,
        "Volume": [1000] * 50 + [2000] * 10
    }
    df = pd.DataFrame(data)
    # Add date index for VWAP
    df.index = pd.date_range(start="2023-01-01", periods=60)
    return df

def test_multi_timeframe(mock_df):
    engine = MultiTimeframeEngine()
    # Simple test for empty
    assert engine.analyze({})["mtf_score"] == 0
    # Provide daily
    dfs = {"1d": mock_df, "1wk": mock_df, "4h": mock_df, "1h": mock_df}
    res = engine.analyze(dfs)
    assert res["mtf_score"] > 0
    assert res["daily_score"] > 0

def test_relative_strength(mock_df):
    engine = RelativeStrengthEngine()
    df_market = mock_df.copy()
    df_market["Close"] = [100] * 60
    res = engine.analyze(mock_df, df_market, mock_df)
    assert res["rs_score"] > 0
    assert "rs_market_20d" in res

def test_sector_rotation(mock_df):
    engine = SectorRotationEngine()
    sectors = {"IT": mock_df}
    engine.pre_calculate_ranks(sectors, mock_df)
    res = engine.analyze("IT")
    assert res["sector_rank"] == 1
    assert res["sector_trend"] == "Bullish"

def test_patterns(mock_df):
    engine = BreakoutPatternEngine()
    # Mock VCP
    df_vcp = mock_df.copy()
    df_vcp['Volume'] = [2000] * 50 + [1000] * 10
    res = engine.analyze(df_vcp)
    assert isinstance(res, list)

def test_price_action(mock_df):
    engine = PriceActionEngine()
    res = engine.analyze(mock_df)
    assert "trend_quality" in res
    assert "candle_strength" in res

def test_vwap(mock_df):
    engine = VWAPEngine()
    res = engine.analyze(mock_df)
    assert res["vwap_score"] > 0
    assert "distance_to_anchored_vwap" in res

def test_support_resistance(mock_df):
    engine = SupportResistanceEngine()
    res = engine.analyze(mock_df)
    assert res["support_level"] > 0

def test_score_engine():
    engine = BreakoutScoreEngine()
    res = engine.score(100, 100, 100, 50, 100, 100, 2)
    assert res["breakout_score"] > 80
    assert res["breakout_grade"] in ["A", "A+"]

@patch("app.services.technical_orchestrator.TechnicalOrchestrator._bulk_download")
def test_technical_orchestrator(mock_download, mock_df):
    # Setup mock to return a multi-index column DataFrame
    # Actually just a single index since it's hard to mock multi-index
    mock_download.return_value = pd.DataFrame()
    
    orch = TechnicalOrchestrator()
    candidates = [{"Ticker": "RELIANCE.NS", "Sector": "Energy"}]
    res = orch.analyze_candidates(candidates)
    assert len(res) == 1
    assert "mtf_score" in res[0]
