import pytest
import pandas as pd
from datetime import datetime, timedelta
import os
import shutil

from data_platform.universe.symbol_validator import SymbolValidator
from data_platform.universe.universe_manager import UniverseManager
from data_platform.providers.provider_factory import ProviderFactory
from data_platform.validation.data_validator import DataValidator
from data_platform.storage.parquet_manager import ParquetManager

# Mock configuration
TEST_DATA_DIR = "test_historical_lake"

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    yield
    # Teardown
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)

def test_symbol_validator():
    assert SymbolValidator.validate_nse_symbol("RELIANCE") == True
    assert SymbolValidator.validate_nse_symbol("TCS.NS") == True
    assert SymbolValidator.validate_nse_symbol("INVALID!@#") == False
    
    assert SymbolValidator.validate_isin("INE002A01018") == True
    assert SymbolValidator.validate_isin("INVALID") == False

def test_universe_manager():
    manager = UniverseManager()
    universe = manager.fetch_active_universe()
    assert len(universe) > 0
    assert any(u.symbol == "RELIANCE" for u in universe)

def test_yahoo_provider():
    provider = ProviderFactory.get_provider("yahoo")
    assert provider.provider_name() == "yahoo"
    
    # We test get_latest_history just to verify structure, avoiding long downloads
    df = provider.get_latest_history("TCS", days=5)
    assert not df.empty
    assert "Close" in df.columns
    assert "Volume" in df.columns

def test_data_validator():
    validator = DataValidator()
    
    # Create valid dummy df
    dates = pd.date_range("2023-01-01", periods=3)
    valid_df = pd.DataFrame({
        "Open": [100, 101, 102],
        "High": [105, 106, 107],
        "Low": [95, 96, 97],
        "Close": [102, 103, 104],
        "Volume": [1000, 1100, 1200]
    }, index=dates)
    
    assert validator.validate_ohlcv(valid_df, "TEST") == True
    
    # Create invalid df (High < Low)
    invalid_df = valid_df.copy()
    invalid_df.loc[invalid_df.index[0], "High"] = 90
    assert validator.validate_ohlcv(invalid_df, "TEST") == False

def test_parquet_manager():
    manager = ParquetManager(base_path=TEST_DATA_DIR)
    
    dates = pd.date_range("2023-01-01", periods=3)
    df = pd.DataFrame({
        "Close": [102.5, 103.5, 104.5],
    }, index=dates)
    
    # Test Save
    assert manager.save_symbol_data(df, "TEST_SYM") == True
    
    # Test Load
    loaded_df = manager.load_symbol_data("TEST_SYM")
    assert not loaded_df.empty
    assert len(loaded_df) == 3
    
    # Test Append
    new_dates = pd.date_range("2023-01-04", periods=1)
    df_new = pd.DataFrame({"Close": [105.0]}, index=new_dates)
    assert manager.append_symbol_data(df_new, "TEST_SYM") == True
    
    final_df = manager.load_symbol_data("TEST_SYM")
    assert len(final_df) == 4
