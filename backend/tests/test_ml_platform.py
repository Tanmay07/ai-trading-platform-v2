import pytest
import pandas as pd
import numpy as np

from ml_platform.feature_engineering.technical_features import TechnicalFeatures
from ml_platform.feature_engineering.volatility_features import VolatilityFeatures
from ml_platform.datasets.label_generator import LabelGenerator
from ml_platform.datasets.leakage_detector import LeakageDetector
from ml_platform.feature_selection.correlation_filter import CorrelationFilter
from ml_platform.training.ensemble_trainer import EnsembleTrainer

def get_dummy_data():
    dates = pd.date_range("2023-01-01", periods=100)
    # create somewhat realistic random walk
    np.random.seed(42)
    returns = np.random.normal(0, 0.01, 100)
    prices = 100 * np.exp(returns.cumsum())
    
    df = pd.DataFrame({
        "Open": prices * 0.99,
        "High": prices * 1.02,
        "Low": prices * 0.98,
        "Close": prices,
        "Volume": np.random.randint(1000, 10000, 100)
    }, index=dates)
    return df

def test_technical_features():
    df = get_dummy_data()
    features = TechnicalFeatures.add_trend_features(df)
    
    assert "EMA_20" in features.columns
    assert "RSI_14" in features.columns
    assert "MACD_Line" in features.columns
    assert not features["EMA_20"].isna().all()

def test_volatility_features():
    df = get_dummy_data()
    features = VolatilityFeatures.add_volatility_features(df)
    
    assert "ATR_14" in features.columns
    assert "BB_Upper" in features.columns
    assert not features["ATR_14"].isna().all()

def test_label_generator():
    df = get_dummy_data()
    labeled = LabelGenerator.generate_labels(df, horizons=[5])
    
    assert "Target_5d_Return" in labeled.columns
    assert "Target_5d_Class" in labeled.columns
    
    # Last 5 days should be NaN because we can't see the future
    assert labeled["Target_5d_Return"].tail(5).isna().all()

def test_leakage_detector():
    df = pd.DataFrame(columns=["feature1", "feature2", "Target_5d_Class"])
    features = ["feature1", "feature2", "Target_5d_Class"]
    labels = ["Target_5d_Class"]
    
    # Should detect leakage
    assert LeakageDetector.assert_no_leakage(df, features, labels) == False
    
    # Clean features
    clean_features = ["feature1", "feature2"]
    assert LeakageDetector.assert_no_leakage(df, clean_features, labels) == True

def test_correlation_filter():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [1, 2, 3, 4, 5], # perfectly correlated
        "C": [5, 4, 1, 2, 3]  # random
    })
    
    filtered = CorrelationFilter.remove_highly_correlated(df, threshold=0.99)
    assert "B" not in filtered.columns
    assert "A" in filtered.columns
    assert "C" in filtered.columns

def test_ensemble_trainer():
    df = get_dummy_data()
    
    # Create random features and target for testing
    X = pd.DataFrame(np.random.rand(100, 5), columns=["f1", "f2", "f3", "f4", "f5"])
    y = pd.Series(np.random.randint(0, 2, 100))
    
    trainer = EnsembleTrainer()
    trainer.train(X, y)
    
    preds = trainer.predict(X)
    probs = trainer.predict_proba(X)
    
    assert len(preds) == 100
    assert probs.shape == (100, 2)
