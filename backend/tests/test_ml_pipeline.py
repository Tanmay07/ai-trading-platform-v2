import pytest
import pandas as pd
import numpy as np
import os
from app.ml.feature_store import FeatureStore
from app.ml.dataset_builder import DatasetBuilder
from app.ml.drift_detector import DriftDetector
from app.ml.model_monitor import ModelMonitor

def test_feature_store_and_dataset():
    store = FeatureStore()
    store.store_snapshot("AAPL", {"RSI": 45, "MACD": 1.2}, target_5d=0.05, target_hit=1)
    
    df = store.fetch_training_data()
    assert not df.empty
    assert "RSI" in df.columns
    assert "ticker" in df.columns
    
    builder = DatasetBuilder()
    X, y = builder.build_dataset()
    assert not X.empty
    assert not y.empty
    assert "RSI" in X.columns
    assert "ticker" not in X.columns
    
def test_drift_detector():
    detector = DriftDetector()
    expected = pd.Series(np.random.normal(0, 1, 1000))
    actual = pd.Series(np.random.normal(5, 1, 1000)) # Significant drift
    
    psi = detector.calculate_psi(expected, actual)
    assert psi > 0.2
    
def test_model_monitor():
    monitor = ModelMonitor()
    y_true = pd.Series([1, 0, 1, 0])
    y_pred_prob = pd.Series([0.9, 0.1, 0.8, 0.2])
    
    metrics = monitor.calculate_metrics(y_true, y_pred_prob)
    assert metrics["accuracy"] == 1.0
    assert metrics["roc_auc"] == 1.0
    assert "calibration_error" in metrics
