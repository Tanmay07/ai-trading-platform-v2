"""
Test Suite for Phase 3 — ML Prediction Models

Tests cover:
    - Data preparer label creation and cleaning
    - XGBoost model train/predict cycle
    - LightGBM model train/predict cycle
    - Ensemble model soft-voting
    - Model persistence (save/load via joblib)
    - PredictionResult and TrainingMetrics structure
    - Strategy ML integration
    - Weight balance validation

All tests use synthetic data — no network calls or real yfinance data.

This is for educational and research purposes only, not financial advice.
"""

import os
import shutil
import tempfile
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

# ── Synthetic Data Helpers ────────────────────────────────────


def make_synthetic_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame with realistic structure."""
    rng = np.random.RandomState(seed)

    # Generate a price series with a slight upward drift
    returns = rng.normal(0.0005, 0.015, n)
    close = 100.0 * np.cumprod(1 + returns)

    high = close * (1 + rng.uniform(0.001, 0.025, n))
    low = close * (1 - rng.uniform(0.001, 0.025, n))
    open_ = close * (1 + rng.normal(0, 0.005, n))

    volume = rng.randint(100_000, 5_000_000, n)

    df = pd.DataFrame({
        "Open": open_,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume,
    })

    # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
    df["High"] = df[["Open", "High", "Close"]].max(axis=1)
    df["Low"] = df[["Open", "Low", "Close"]].min(axis=1)

    return df


def make_synthetic_features(n: int = 300, n_features: int = 30, seed: int = 42):
    """Create synthetic feature matrix X and ternary labels y."""
    rng = np.random.RandomState(seed)
    X = rng.randn(n, n_features).astype(np.float64)
    y = rng.choice([0, 1, 2], size=n).astype(np.int32)
    feature_names = [f"feature_{i}" for i in range(n_features)]
    return X, y, feature_names


# ── Data Preparer Tests ───────────────────────────────────────


class TestMLDataPreparer:
    """Unit tests for the MLDataPreparer class."""

    def test_label_creation(self):
        """Forward labels should be correctly assigned as UP/DOWN/NEUTRAL."""
        from app.ml.ml_data_preparer import MLDataPreparer, LABEL_MAP

        df = make_synthetic_ohlcv(100)
        df_labeled = MLDataPreparer._create_labels(
            df.copy(), forward_days=5, up_threshold=0.01, down_threshold=-0.01
        )

        assert "future_return" in df_labeled.columns
        assert "target" in df_labeled.columns

        # Last 5 rows should have NaN future_return
        assert df_labeled["future_return"].iloc[-1] != df_labeled["future_return"].iloc[-1]  # NaN

        # Valid labels should be in {0, 1, 2}
        valid = df_labeled["target"].dropna()
        assert set(valid.unique()).issubset({0, 1, 2})

    def test_label_names_mapping(self):
        """LABEL_MAP and LABEL_NAMES should be inverse mappings."""
        from app.ml.ml_data_preparer import LABEL_MAP, LABEL_NAMES

        assert LABEL_MAP["DOWN"] == 0
        assert LABEL_MAP["NEUTRAL"] == 1
        assert LABEL_MAP["UP"] == 2
        assert LABEL_NAMES[0] == "DOWN"
        assert LABEL_NAMES[1] == "NEUTRAL"
        assert LABEL_NAMES[2] == "UP"

    def test_get_feature_columns_excludes_ohlcv(self):
        """Feature columns should not include raw OHLCV or target columns."""
        from app.ml.ml_data_preparer import MLDataPreparer

        df = make_synthetic_ohlcv(50)
        df["rsi"] = 50.0
        df["sma_20"] = 100.0
        df["target"] = 1

        cols = MLDataPreparer._get_feature_columns(df)
        assert "rsi" in cols
        assert "sma_20" in cols
        assert "Close" not in cols
        assert "Volume" not in cols
        assert "target" not in cols

    def test_get_label_name(self):
        """get_label_name should map ints back to strings."""
        from app.ml.ml_data_preparer import MLDataPreparer

        assert MLDataPreparer.get_label_name(0) == "DOWN"
        assert MLDataPreparer.get_label_name(1) == "NEUTRAL"
        assert MLDataPreparer.get_label_name(2) == "UP"
        assert MLDataPreparer.get_label_name(99) == "UNKNOWN"


# ── XGBoost Model Tests ──────────────────────────────────────


class TestXGBoostModel:
    """Tests for the XGBoost model wrapper."""

    def test_train_and_predict(self):
        """XGBoost should train and predict without errors."""
        from app.ml.models import XGBoostModel

        X, y, names = make_synthetic_features(200, 20)
        model = XGBoostModel()
        model.train(X, y, names)

        assert model.is_fitted
        preds = model.predict(X[:5])
        assert preds.shape == (5,)
        assert all(p in {0, 1, 2} for p in preds)

    def test_predict_proba_shape(self):
        """predict_proba should return (n_samples, 3) array."""
        from app.ml.models import XGBoostModel

        X, y, names = make_synthetic_features(200, 20)
        model = XGBoostModel()
        model.train(X, y, names)

        probas = model.predict_proba(X[:10])
        assert probas.shape == (10, 3)
        # Each row should sum to ~1
        for row in probas:
            assert abs(row.sum() - 1.0) < 0.01

    def test_predict_single(self):
        """predict_single should return a PredictionResult."""
        from app.ml.models import XGBoostModel

        X, y, names = make_synthetic_features(200, 20)
        model = XGBoostModel()
        model.train(X, y, names)

        result = model.predict_single(X[:1])
        assert result.direction in {"UP", "DOWN", "NEUTRAL"}
        assert 0.0 <= result.probability <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.model_name == "xgboost"
        assert "UP" in result.probabilities
        assert "DOWN" in result.probabilities
        assert "NEUTRAL" in result.probabilities

    def test_feature_importance(self):
        """Feature importance should be available after training."""
        from app.ml.models import XGBoostModel

        X, y, names = make_synthetic_features(200, 20)
        model = XGBoostModel()
        model.train(X, y, names)

        imp = model.get_feature_importance()
        assert len(imp) == 20
        assert all(isinstance(v, (float, np.floating)) for v in imp.values())

    def test_get_params(self):
        """get_params should return expected keys."""
        from app.ml.models import XGBoostModel

        model = XGBoostModel()
        params = model.get_params()
        assert "max_depth" in params
        assert "n_estimators" in params
        assert "learning_rate" in params

    def test_unfitted_raises(self):
        """Predicting with unfitted model should raise RuntimeError."""
        from app.ml.models import XGBoostModel

        model = XGBoostModel()
        with pytest.raises(RuntimeError, match="not been trained"):
            model.predict(np.zeros((1, 10)))


# ── LightGBM Model Tests ─────────────────────────────────────


class TestLightGBMModel:
    """Tests for the LightGBM model wrapper."""

    def test_train_and_predict(self):
        """LightGBM should train and predict without errors."""
        from app.ml.models import LightGBMModel

        X, y, names = make_synthetic_features(200, 20)
        model = LightGBMModel()
        model.train(X, y, names)

        assert model.is_fitted
        preds = model.predict(X[:5])
        assert preds.shape == (5,)
        assert all(p in {0, 1, 2} for p in preds)

    def test_predict_proba_shape(self):
        """predict_proba should return (n_samples, 3) array."""
        from app.ml.models import LightGBMModel

        X, y, names = make_synthetic_features(200, 20)
        model = LightGBMModel()
        model.train(X, y, names)

        probas = model.predict_proba(X[:10])
        assert probas.shape == (10, 3)
        for row in probas:
            assert abs(row.sum() - 1.0) < 0.01

    def test_get_params(self):
        """get_params should return expected keys."""
        from app.ml.models import LightGBMModel

        model = LightGBMModel()
        params = model.get_params()
        assert "num_leaves" in params
        assert "n_estimators" in params


# ── Ensemble Model Tests ──────────────────────────────────────


class TestEnsembleModel:
    """Tests for the soft-voting ensemble model."""

    def test_ensemble_trains_both(self):
        """Ensemble should train both XGBoost and LightGBM."""
        from app.ml.models import EnsembleModel

        X, y, names = make_synthetic_features(200, 20)
        model = EnsembleModel()
        model.train(X, y, names)

        assert model.is_fitted
        assert model.xgb.is_fitted
        assert model.lgb.is_fitted

    def test_ensemble_averages_probabilities(self):
        """Ensemble probabilities should be the average of constituents."""
        from app.ml.models import EnsembleModel

        X, y, names = make_synthetic_features(200, 20)
        model = EnsembleModel()
        model.train(X, y, names)

        X_test = X[:5]
        proba_ens = model.predict_proba(X_test)
        proba_xgb = model.xgb.predict_proba(X_test)
        proba_lgb = model.lgb.predict_proba(X_test)

        expected = (proba_xgb + proba_lgb) / 2.0
        np.testing.assert_array_almost_equal(proba_ens, expected, decimal=6)

    def test_ensemble_predict_single(self):
        """Ensemble predict_single should return valid PredictionResult."""
        from app.ml.models import EnsembleModel

        X, y, names = make_synthetic_features(200, 20)
        model = EnsembleModel()
        model.train(X, y, names)

        result = model.predict_single(X[:1])
        assert result.direction in {"UP", "DOWN", "NEUTRAL"}
        assert result.model_name == "ensemble"

    def test_ensemble_feature_importance_averages(self):
        """Ensemble feature importance should average both models."""
        from app.ml.models import EnsembleModel

        X, y, names = make_synthetic_features(200, 20)
        model = EnsembleModel()
        model.train(X, y, names)

        imp = model.get_feature_importance()
        assert len(imp) == 20

    def test_ensemble_get_params(self):
        """Ensemble params should list constituent models."""
        from app.ml.models import EnsembleModel

        model = EnsembleModel()
        params = model.get_params()
        assert params["voting"] == "soft"
        assert "xgboost" in params["models"]
        assert "lightgbm" in params["models"]


# ── Model Persistence Tests ──────────────────────────────────


class TestModelPersistence:
    """Tests for joblib save/load via ModelManager."""

    def test_save_and_load_roundtrip(self):
        """Saved model should produce identical predictions after loading."""
        import joblib
        from app.ml.models import XGBoostModel

        X, y, names = make_synthetic_features(200, 20)
        model = XGBoostModel()
        model.train(X, y, names)

        # Save
        tmp_dir = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp_dir, "test_model.joblib")
            joblib.dump(model, path)

            # Load
            loaded = joblib.load(path)
            assert loaded.is_fitted
            assert loaded.name == "xgboost"

            # Compare predictions
            orig_preds = model.predict(X[:5])
            loaded_preds = loaded.predict(X[:5])
            np.testing.assert_array_equal(orig_preds, loaded_preds)

            # Compare probabilities
            orig_probas = model.predict_proba(X[:5])
            loaded_probas = loaded.predict_proba(X[:5])
            np.testing.assert_array_almost_equal(orig_probas, loaded_probas)

        finally:
            shutil.rmtree(tmp_dir)


# ── PredictionResult & TrainingMetrics Tests ──────────────────


class TestDataClasses:
    """Tests for result dataclasses."""

    def test_prediction_result_to_dict(self):
        """PredictionResult.to_dict() should have expected keys."""
        from app.ml.models import PredictionResult

        result = PredictionResult(
            direction="UP",
            direction_int=2,
            probability=0.65,
            confidence=0.48,
            probabilities={"DOWN": 0.15, "NEUTRAL": 0.20, "UP": 0.65},
            model_name="xgboost",
        )
        d = result.to_dict()
        assert d["direction"] == "UP"
        assert d["probability"] == 0.65
        assert d["confidence"] == 0.48
        assert "DOWN" in d["probabilities"]
        assert d["model_name"] == "xgboost"

    def test_training_metrics_to_dict(self):
        """TrainingMetrics.to_dict() should have expected keys."""
        from app.ml.models import TrainingMetrics

        m = TrainingMetrics(
            accuracy=0.65,
            precision_macro=0.60,
            recall_macro=0.58,
            f1_macro=0.59,
            train_samples=300,
            test_samples=100,
            feature_count=30,
        )
        d = m.to_dict()
        assert d["accuracy"] == 0.65
        assert d["train_samples"] == 300
        assert d["test_samples"] == 100


# ── Strategy ML Integration Tests ─────────────────────────────


class TestStrategyMLIntegration:
    """Tests for ML signal integration in RuleBasedStrategy."""

    def _make_strategy(self):
        from app.strategies.rule_based_strategy import RuleBasedStrategy
        return RuleBasedStrategy()

    def _make_sample_df(self):
        """Create a minimal DataFrame with required feature columns."""
        n = 50
        np.random.seed(42)
        df = pd.DataFrame({
            "Open": np.random.uniform(100, 200, n),
            "High": np.random.uniform(100, 200, n),
            "Low": np.random.uniform(100, 200, n),
            "Close": np.random.uniform(100, 200, n),
            "Volume": np.random.randint(10000, 100000, n),
            "sma_20": np.random.uniform(100, 200, n),
            "sma_50": np.random.uniform(100, 200, n),
            "sma_200": np.random.uniform(100, 200, n),
            "ema_12": np.random.uniform(100, 200, n),
            "ema_26": np.random.uniform(100, 200, n),
            "rsi": np.random.uniform(30, 70, n),
            "macd": np.random.uniform(-5, 5, n),
            "macd_signal": np.random.uniform(-5, 5, n),
            "macd_histogram": np.random.uniform(-3, 3, n),
            "stoch_k": np.random.uniform(20, 80, n),
            "stoch_d": np.random.uniform(20, 80, n),
            "volume_ratio": np.random.uniform(0.5, 2.0, n),
            "obv": np.random.uniform(100000, 200000, n),
            "obv_sma": np.random.uniform(100000, 200000, n),
            "atr": np.random.uniform(1, 5, n),
            "atr_pct": np.random.uniform(0.5, 3.0, n),
            "bb_upper": np.random.uniform(180, 220, n),
            "bb_middle": np.random.uniform(150, 180, n),
            "bb_lower": np.random.uniform(100, 150, n),
            "volatility_20d": np.random.uniform(0.01, 0.05, n),
            "prev_close": np.random.uniform(100, 200, n),
        })
        df["High"] = df[["Open", "High", "Low", "Close"]].max(axis=1)
        df["Low"] = df[["Open", "High", "Low", "Close"]].min(axis=1)
        return df

    def test_analyze_with_ml_prediction(self):
        """Strategy should incorporate ML signal when provided."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        ml_prediction = {
            "direction": "UP",
            "probability": 0.72,
            "confidence": 0.58,
        }

        result = strategy.analyze(df, ml_prediction=ml_prediction)
        assert "ml_signal" in result
        assert "ml" in result["signal_details"]
        assert result["ml_signal"] != 0.0

    def test_analyze_without_ml_prediction(self):
        """Strategy should work without ML prediction."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        result = strategy.analyze(df, ml_prediction=None)
        assert "ml_signal" in result
        assert result["ml_signal"] == 0.0
        assert "No ML model available" in result["signal_details"]["ml"]["reasons"]

    def test_analyze_backwards_compatible(self):
        """Strategy should work when called without any optional kwargs."""
        strategy = self._make_strategy()
        df = self._make_sample_df()

        result = strategy.analyze(df)
        assert "combined_score" in result
        assert "ml_signal" in result
        assert "sentiment_signal" in result

    def test_neutral_signals_include_ml(self):
        """Neutral signals dict should include ml_signal."""
        strategy = self._make_strategy()
        neutral = strategy._neutral_signals()
        assert "ml_signal" in neutral
        assert neutral["ml_signal"] == 0.0
        assert "ml" in neutral["signal_details"]

    def test_weights_sum_to_one(self):
        """All six dimension weights should sum to 1.0."""
        strategy = self._make_strategy()
        total = (
            strategy.TREND_WEIGHT
            + strategy.MOMENTUM_WEIGHT
            + strategy.VOLUME_WEIGHT
            + strategy.VOLATILITY_WEIGHT
            + strategy.SENTIMENT_WEIGHT
            + strategy.ML_WEIGHT
        )
        assert total == pytest.approx(1.0, abs=0.001)

    def test_ml_bullish_signal_is_positive(self):
        """ML predicting UP with high confidence should produce positive signal."""
        strategy = self._make_strategy()

        ml_pred = {
            "direction": "UP",
            "probability": 0.85,
            "confidence": 0.78,
        }
        score, reasons = strategy._assess_ml_prediction(ml_pred)
        assert score > 0

    def test_ml_bearish_signal_is_negative(self):
        """ML predicting DOWN with high confidence should produce negative signal."""
        strategy = self._make_strategy()

        ml_pred = {
            "direction": "DOWN",
            "probability": 0.80,
            "confidence": 0.70,
        }
        score, reasons = strategy._assess_ml_prediction(ml_pred)
        assert score < 0

    def test_ml_neutral_signal_is_zero(self):
        """ML predicting NEUTRAL should produce zero signal."""
        strategy = self._make_strategy()

        ml_pred = {
            "direction": "NEUTRAL",
            "probability": 0.45,
            "confidence": 0.18,
        }
        score, reasons = strategy._assess_ml_prediction(ml_pred)
        assert score == 0.0


# ── Training Result Tests ─────────────────────────────────────


class TestTrainingResult:
    """Tests for the TrainingResult dataclass."""

    def test_to_dict_structure(self):
        """TrainingResult.to_dict() should have expected keys."""
        from app.ml.model_manager import TrainingResult
        from app.ml.models import TrainingMetrics

        result = TrainingResult(
            symbol="RELIANCE.NS",
            model_name="ensemble",
            metrics=TrainingMetrics(accuracy=0.65, f1_macro=0.60),
            feature_importance={"rsi": 0.15, "macd": 0.12},
            trained_at="2025-01-01T00:00:00Z",
            training_period="2y",
        )

        d = result.to_dict()
        assert d["symbol"] == "RELIANCE.NS"
        assert d["model_name"] == "ensemble"
        assert d["success"] is True
        assert "metrics" in d
        assert "feature_importance_top10" in d


# ── Model Manager (Unit-Level) Tests ──────────────────────────


class TestModelManagerUnit:
    """Unit tests for ModelManager that don't require network access."""

    def test_needs_retrain_no_model(self):
        """needs_retrain should return True when no model exists."""
        from app.ml.model_manager import ModelManager

        tmp_dir = tempfile.mkdtemp()
        try:
            manager = ModelManager(model_dir=tmp_dir)
            assert manager.needs_retrain("FAKE.NS") is True
        finally:
            shutil.rmtree(tmp_dir)

    def test_get_model_info_no_model(self):
        """get_model_info should return None when no model exists."""
        from app.ml.model_manager import ModelManager

        tmp_dir = tempfile.mkdtemp()
        try:
            manager = ModelManager(model_dir=tmp_dir)
            assert manager.get_model_info("FAKE.NS") is None
        finally:
            shutil.rmtree(tmp_dir)

    def test_predict_without_training(self):
        """predict should return None when no model is trained."""
        from app.ml.model_manager import ModelManager

        tmp_dir = tempfile.mkdtemp()
        try:
            manager = ModelManager(model_dir=tmp_dir)
            result = manager.predict("FAKE.NS")
            assert result is None
        finally:
            shutil.rmtree(tmp_dir)

    def test_get_all_model_info_empty(self):
        """get_all_model_info should return empty list for empty dir."""
        from app.ml.model_manager import ModelManager

        tmp_dir = tempfile.mkdtemp()
        try:
            manager = ModelManager(model_dir=tmp_dir)
            assert manager.get_all_model_info() == []
        finally:
            shutil.rmtree(tmp_dir)
