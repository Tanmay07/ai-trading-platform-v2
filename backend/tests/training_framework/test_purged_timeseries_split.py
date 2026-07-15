import pytest
import pandas as pd
import numpy as np
from datetime import timedelta
from training_framework.validation.purged_timeseries_split import PurgedTimeSeriesSplit

def test_purged_timeseries_split_no_leakage():
    # Create 100 days of data
    dates = pd.date_range(start="2020-01-01", periods=100, freq='D')
    df = pd.DataFrame({'feature': np.random.randn(100)}, index=dates)
    
    cv = PurgedTimeSeriesSplit(n_splits=3, prediction_horizon_days=5, embargo_days=7)
    
    for train_idx, test_idx in cv.split(df):
        train_dates = df.index[train_idx]
        test_dates = df.index[test_idx]
        
        test_start = test_dates.min()
        test_end = test_dates.max()
        
        # Check purge condition
        # Max train date before test_start should be strictly before test_start - 5 days
        train_before_test = train_dates[train_dates < test_start]
        if len(train_before_test) > 0:
            assert train_before_test.max() < (test_start - timedelta(days=5))
            
        # Check embargo condition
        # Min train date after test_end should be strictly after test_end + 7 days
        train_after_test = train_dates[train_dates > test_end]
        if len(train_after_test) > 0:
            assert train_after_test.min() > (test_end + timedelta(days=7))

def test_multi_index_support():
    # MultiIndex (Date, Symbol)
    dates = pd.date_range(start="2020-01-01", periods=10, freq='D')
    symbols = ['AAPL', 'MSFT']
    
    idx = pd.MultiIndex.from_product([dates, symbols], names=['Date', 'Symbol'])
    df = pd.DataFrame({'feature': np.random.randn(20)}, index=idx)
    
    cv = PurgedTimeSeriesSplit(n_splits=2, prediction_horizon_days=2, embargo_days=2)
    
    splits = list(cv.split(df))
    assert len(splits) == 2
    
    train_idx, test_idx = splits[0]
    assert len(train_idx) > 0
    assert len(test_idx) > 0
