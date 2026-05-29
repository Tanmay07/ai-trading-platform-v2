import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.backtest.engine import BacktestEngine
from app.database import Base, engine, get_db

# Create a test client
client = TestClient(app)

# --- Synthetic Data Helper ---
def make_synthetic_ohlcv(days=300):
    start = datetime.today() - timedelta(days=days)
    dates = [start + timedelta(days=i) for i in range(days)]
    
    np.random.seed(42)
    # create an upward trending series with some noise
    close = np.cumsum(np.random.normal(0.5, 2, days)) + 100
    
    df = pd.DataFrame({
        "Open": close - np.random.uniform(0, 2, days),
        "High": close + np.random.uniform(0, 5, days),
        "Low": close - np.random.uniform(0, 5, days),
        "Close": close,
        "Volume": np.random.randint(1000, 10000, days)
    }, index=pd.DatetimeIndex(dates))
    
    df["High"] = df[["Open", "High", "Close"]].max(axis=1)
    df["Low"] = df[["Open", "Low", "Close"]].min(axis=1)
    return df

class TestBacktestEngine:
    
    @patch("app.backtest.engine.HistoricalDataService.get_historical_data")
    @patch("app.backtest.engine.get_db")
    def test_backtest_run_success(self, mock_get_db, mock_get_historical):
        """Test the full backtest loop with synthetic data."""
        # Mock database session
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])
        
        # Mock historical data
        df = make_synthetic_ohlcv(500)
        mock_get_historical.return_value = df
        
        # Initialize engine
        bt_engine = BacktestEngine()
        
        # Override the transaction cost to avoid making tests brittle
        bt_engine.transaction_cost_pct = 0.0
        
        # Force the strategy to always BUY on first day and HOLD
        # To do this predictably, we mock analyze_row
        with patch.object(bt_engine.strategy, 'analyze_row') as mock_analyze:
            # First 5 calls return BUY (score 0.8), the rest return neutral (0.0)
            def side_effect(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return {"combined_score": 0.8}
                elif calls == 100:
                    return {"combined_score": -0.8} # Sell on day 100
                return {"combined_score": 0.0}
            
            calls = 0
            mock_analyze.side_effect = side_effect
            
            start_dt = (datetime.today() - timedelta(days=150)).strftime("%Y-%m-%d")
            end_dt = datetime.today().strftime("%Y-%m-%d")
            
            result = bt_engine.run_backtest("MOCK.NS", start_dt, end_dt, initial_capital=100_000.0)
            
            # Verify structure
            assert "metrics" in result
            assert "trades" in result
            assert "portfolio_history" in result
            
            metrics = result["metrics"]
            assert metrics["initial_capital"] == 100_000.0
            assert "final_capital" in metrics
            assert "total_return" in metrics
            assert "sharpe_ratio" in metrics
            assert "max_drawdown" in metrics
            
            # DB should have been called to persist
            assert mock_session.add.called
            assert mock_session.commit.called

    @patch("app.backtest.engine.HistoricalDataService.get_historical_data")
    def test_backtest_no_data(self, mock_get_historical):
        """Test backtest raises error when no data is found."""
        mock_get_historical.return_value = pd.DataFrame()
        
        bt_engine = BacktestEngine()
        with pytest.raises(ValueError, match="No historical data found"):
            bt_engine.run_backtest("EMPTY.NS", "2020-01-01", "2020-12-31")

class TestBacktestAPI:
    
    @patch("app.api.backtest_routes.BacktestEngine.run_backtest")
    def test_run_backtest_endpoint(self, mock_run):
        mock_run.return_value = {
            "metrics": {"total_return": 0.15},
            "trades": []
        }
        
        response = client.post("/backtest/run", json={
            "symbol": "TCS.NS",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 50000.0
        })
        
        assert response.status_code == 200
        assert response.json() == {
            "metrics": {"total_return": 0.15},
            "trades": []
        }
        
        mock_run.assert_called_once_with(
            symbol="TCS.NS",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=50000.0
        )
