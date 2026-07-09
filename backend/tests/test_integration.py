import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.recommendations.orchestrator import RecommendationEngine
from app.discovery.universe_builder import UniverseBuilder

client = TestClient(app)

@patch("app.discovery.universe_builder.BhavcopyService.get_bhavcopy_df")
@patch("app.discovery.universe_builder.yf.Ticker")
def test_universe_builder(mock_ticker, mock_bhavcopy):
    # Mock Bhavcopy DataFrame
    df = pd.DataFrame({
        "SctySrs": ["EQ", "EQ", "BE"],
        "TckrSymb": ["RELIANCE", "TCS", "PENNY"],
        "ClosePric": [2500, 3500, 10],
        "TotTrdQty": [1000000, 500000, 100],
        "TtlTrfVal": [2500000000, 1750000000, 1000],
        "DlvryQty": [600000, 200000, 10]
    })
    mock_bhavcopy.return_value = df
    
    # Mock yfinance
    mock_info = MagicMock()
    mock_info.info = {
        "shortName": "Reliance Industries",
        "sector": "Energy",
        "industry": "Oil & Gas",
        "marketCap": 15000000000000,
        "averageVolume": 5000000
    }
    mock_ticker.return_value = mock_info
    
    builder = UniverseBuilder()
    builder.config.minimum_price = 50
    builder.config.minimum_market_cap = 30000000000
    builder.config.minimum_average_volume = 100000
    builder.config.minimum_delivery_percent = 30
    
    candidates = builder.get_candidate_universe(max_candidates=2)
    assert len(candidates) == 2
    assert candidates[0]["Ticker"] in ["RELIANCE.NS", "TCS.NS"]
    
@patch("app.recommendations.orchestrator.UniverseBuilder.get_candidate_universe")
@patch("app.recommendations.orchestrator.FeaturePipeline.compute_features_for_symbol")
def test_orchestrator(mock_compute, mock_universe):
    mock_universe.return_value = [{
        "Ticker": "RELIANCE.NS",
        "Company": "Reliance",
        "Sector": "Energy",
        "Market_Cap": 10000000000,
        "Liquidity_Score": 5000000
    }]
    
    data = {
        "Close": [2500] * 10,
        "Low": [2450] * 10,
        "ema_20": [2400] * 10,
        "ema_50": [2300] * 10,
        "ema_200": [2200] * 10,
        "rsi_14": [65] * 10,
        "macd": [1.5] * 10,
        "macd_signal": [1.0] * 10,
        "adx_14": [30] * 10,
        "relative_volume": [2.0] * 10,
        "bb_bandwidth": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        "Volume": [100000] * 9 + [250000],
        "obv": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        "atr_14": [50] * 10,
        "bb_lower": [2400] * 10
    }
    mock_compute.return_value = pd.DataFrame(data)
    
    engine = RecommendationEngine()
    res = engine.generate_recommendations(portfolio_capital=500000, sector="Energy")
    
    assert "recommendations" in res
    assert len(res["recommendations"]) == 1
    rec = res["recommendations"][0]
    assert rec["Ticker"] == "RELIANCE.NS"
    assert rec["Confidence"] > 80
    assert rec["Recommended_Quantity"] > 0

@patch("app.api.recommendation_routes.RecommendationEngine.generate_recommendations")
def test_api_recommendations(mock_generate):
    mock_generate.return_value = {
        "generated_at": "2023-01-01",
        "portfolio_capital": 500000,
        "recommendations": []
    }
    
    response = client.get("/api/recommendations/?capital=500000&sector=IT")
    assert response.status_code == 200
    assert response.json()["portfolio_capital"] == 500000
