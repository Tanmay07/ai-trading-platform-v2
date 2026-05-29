"""
Model Manager — Phase 3

Orchestrates ML model training, evaluation, persistence, and prediction.
Handles the full lifecycle: data prep → train → evaluate → save → load → predict.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import TimeSeriesSplit

from app.config import settings
from app.data.s3_service import S3StorageService
from app.ml.ml_data_preparer import LABEL_NAMES, MLDataPreparer
from app.ml.models import (
    BaseMLModel,
    EnsembleModel,
    LightGBMModel,
    PredictionResult,
    TrainingMetrics,
    XGBoostModel,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------
# Training result
# ------------------------------------------------------------------


@dataclass
class TrainingResult:
    """Full result of a model training run."""

    symbol: str
    model_name: str
    metrics: TrainingMetrics
    feature_importance: dict[str, float] = field(default_factory=dict)
    trained_at: str = ""
    model_path: str = ""
    training_period: str = ""
    success: bool = True
    error: str = ""
    best_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "model_name": self.model_name,
            "metrics": self.metrics.to_dict(),
            "feature_importance_top10": dict(
                list(self.feature_importance.items())[:10]
            ),
            "trained_at": self.trained_at,
            "training_period": self.training_period,
            "success": self.success,
            "error": self.error,
            "best_params": self.best_params,
        }


# ------------------------------------------------------------------
# Model Manager
# ------------------------------------------------------------------


class ModelManager:
    """Orchestrates ML model training, persistence, and prediction.

    Usage::

        manager = ModelManager()

        # Train
        result = manager.train_model("RELIANCE.NS")
        print(result.metrics.accuracy)

        # Predict
        prediction = manager.predict("RELIANCE.NS")
        print(prediction.direction, prediction.probability)

        # Batch train
        results = manager.train_all(["RELIANCE.NS", "TCS.NS"])
    """

    def __init__(
        self,
        model_dir: str | None = None,
        data_preparer: MLDataPreparer | None = None,
    ) -> None:
        self.model_dir = Path(model_dir or settings.ML_MODEL_DIR)
        self.data_preparer = data_preparer or MLDataPreparer()
        self._model_cache: dict[str, BaseMLModel] = {}
        self.s3_svc = S3StorageService()

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train_model(
        self,
        symbol: str,
        period: str = "2y",
        n_iter: int = 10,
    ) -> TrainingResult:
        """Train all model types and save the best one.

        Trains XGBoost, LightGBM, and Ensemble, evaluates each on a
        held-out test set using time-series-aware splitting, and
        persists the model with the highest F1 score.

        Args:
            symbol: NSE symbol with ``.NS`` suffix.
            period: History period for training data (default ``"2y"``).
            n_iter: Number of tuning iterations.

        Returns:
            TrainingResult with metrics from the best model.
        """
        logger.info("Starting ML training for %s (period=%s)", symbol, period)

        try:
            # 1. Prepare data
            X, y, feature_names = self.data_preparer.prepare_training_data(
                symbol, period=period
            )

            # 2. Time-series split (respects temporal ordering)
            n_splits = 3
            tscv = TimeSeriesSplit(n_splits=n_splits)

            # Use the last split for final evaluation
            splits = list(tscv.split(X))
            train_idx, test_idx = splits[-1]
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            logger.info(
                "Split data — train: %d samples, test: %d samples",
                len(X_train), len(X_test),
            )

            # 3. Train all models
            models: dict[str, BaseMLModel] = {
                "xgboost": XGBoostModel(),
                "lightgbm": LightGBMModel(),
                "ensemble": EnsembleModel(),
            }

            best_model: BaseMLModel | None = None
            best_f1: float = -1.0
            best_name: str = ""
            best_metrics: TrainingMetrics | None = None

            for name, model in models.items():
                try:
                    model.train(X_train, y_train, feature_names, n_iter=n_iter)
                    metrics = self._evaluate_model(model, X_test, y_test, X_train)

                    logger.info(
                        "%s — accuracy=%.3f, F1=%.3f",
                        name, metrics.accuracy, metrics.f1_macro,
                    )

                    if metrics.f1_macro > best_f1:
                        best_f1 = metrics.f1_macro
                        best_model = model
                        best_name = name
                        best_metrics = metrics

                except Exception as exc:
                    logger.warning("Model %s training failed: %s", name, exc)

            if best_model is None or best_metrics is None:
                return TrainingResult(
                    symbol=symbol,
                    model_name="none",
                    metrics=TrainingMetrics(),
                    success=False,
                    error="All models failed to train",
                )

            # 4. Persist the best model
            model_path = self._save_model(symbol, best_model, feature_names)

            # 5. Cache the model
            self._model_cache[symbol] = best_model

            # 6. Build result
            feature_importance = best_model.get_feature_importance()

            result = TrainingResult(
                symbol=symbol,
                model_name=best_name,
                metrics=best_metrics,
                feature_importance=feature_importance,
                trained_at=datetime.now(tz=timezone.utc).isoformat(),
                model_path=str(model_path),
                training_period=period,
                success=True,
                best_params=best_model.get_params(),
            )

            logger.info(
                "Best model for %s: %s (F1=%.3f, accuracy=%.3f)",
                symbol, best_name, best_metrics.f1_macro, best_metrics.accuracy,
            )

            return result

        except Exception as exc:
            logger.error("Training failed for %s: %s", symbol, exc, exc_info=True)
            return TrainingResult(
                symbol=symbol,
                model_name="none",
                metrics=TrainingMetrics(),
                success=False,
                error=str(exc),
            )

    def train_all(
        self,
        symbols: list[str] | None = None,
        period: str = "2y",
        n_iter: int = 10,
    ) -> list[TrainingResult]:
        """Batch train models for multiple symbols.

        Args:
            symbols: List of NSE symbols. Defaults to watchlist.
            period: History period.

        Returns:
            List of TrainingResult objects.
        """
        if symbols is None:
            symbols = list(settings.DEFAULT_WATCHLIST)

        results: list[TrainingResult] = []
        for sym in symbols:
            result = self.train_model(sym, period=period, n_iter=n_iter)
            results.append(result)

        success_count = sum(1 for r in results if r.success)
        logger.info(
            "Batch training complete — %d/%d models trained successfully",
            success_count, len(results),
        )

        return results

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(
        self,
        symbol: str,
        df_features: Any | None = None,
    ) -> PredictionResult | None:
        """Generate an ML prediction for a symbol.

        If no trained model exists, returns ``None``.

        Args:
            symbol: NSE symbol with ``.NS`` suffix.
            df_features: Pre-computed feature DataFrame (optional).

        Returns:
            PredictionResult or None if no model is available.
        """
        model = self._load_model(symbol)
        if model is None:
            logger.info("No trained model for %s — skipping ML prediction", symbol)
            return None

        try:
            X, feature_names = self.data_preparer.prepare_prediction_features(
                symbol, df_features=df_features,
            )

            prediction = model.predict_single(X)
            logger.info(
                "ML prediction for %s: %s (prob=%.3f, confidence=%.3f)",
                symbol, prediction.direction,
                prediction.probability, prediction.confidence,
            )
            return prediction

        except Exception as exc:
            logger.error("ML prediction failed for %s: %s", symbol, exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Model info & status
    # ------------------------------------------------------------------

    def get_model_info(self, symbol: str) -> dict[str, Any] | None:
        """Return metadata about a trained model.

        Returns:
            Dictionary with model info, or ``None`` if no model exists.
        """
        safe_name = symbol.replace(".", "_").replace("/", "_")
        s3_key = f"ml_models/{safe_name}/metadata.json"
        return self.s3_svc.download_json(s3_key)

    def get_all_model_info(self) -> list[dict[str, Any]]:
        """Return metadata for all trained models from S3."""
        results = []
        keys = self.s3_svc.list_objects("ml_models/")
        
        for key in keys:
            if key.endswith("metadata.json"):
                info = self.s3_svc.download_json(key)
                if info:
                    results.append(info)
                    
        return results

    def needs_retrain(self, symbol: str) -> bool:
        """Check if a model needs retraining (older than ML_RETRAIN_DAYS)."""
        info = self.get_model_info(symbol)
        if info is None:
            return True

        trained_at_str = info.get("trained_at", "")
        if not trained_at_str:
            return True

        try:
            trained_at = datetime.fromisoformat(trained_at_str)
            age_days = (datetime.now(tz=timezone.utc) - trained_at).days
            return age_days >= settings.ML_RETRAIN_DAYS
        except (ValueError, TypeError):
            return True

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_model(
        self,
        symbol: str,
        model: BaseMLModel,
        feature_names: list[str],
    ) -> Path:
        """Save a trained model and its metadata to disk and S3."""
        model_dir = self._get_model_dir(symbol)
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / "model.joblib"
        
        # Save model locally temporarily
        joblib.dump(model, model_path)

        # Upload model to S3
        safe_name = symbol.replace(".", "_").replace("/", "_")
        s3_model_key = f"ml_models/{safe_name}/model.joblib"
        self.s3_svc.upload_file(s3_model_key, str(model_path))

        # Save metadata to S3
        metadata = {
            "symbol": symbol,
            "model_name": model.name,
            "feature_names": feature_names,
            "feature_count": len(feature_names),
            "trained_at": datetime.now(tz=timezone.utc).isoformat(),
            "params": model.get_params(),
        }
        s3_metadata_key = f"ml_models/{safe_name}/metadata.json"
        self.s3_svc.upload_json(s3_metadata_key, metadata)

        logger.info("Saved %s model for %s to S3: %s", model.name, symbol, s3_model_key)
        return model_path

    def _load_model(self, symbol: str) -> BaseMLModel | None:
        """Load a trained model from cache or S3."""
        # Check cache first
        if symbol in self._model_cache:
            return self._model_cache[symbol]

        model_dir = self._get_model_dir(symbol)
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "model.joblib"
        
        safe_name = symbol.replace(".", "_").replace("/", "_")
        s3_model_key = f"ml_models/{safe_name}/model.joblib"

        if not model_path.exists():
            # Try to download from S3
            success = self.s3_svc.download_file(s3_model_key, str(model_path))
            if not success:
                return None

        try:
            model: BaseMLModel = joblib.load(model_path)
            self._model_cache[symbol] = model
            logger.info("Loaded %s model for %s", model.name, symbol)
            return model
        except Exception as exc:
            logger.error("Failed to load model for %s: %s", symbol, exc)
            return None

    def _get_model_dir(self, symbol: str) -> Path:
        """Return the directory for a symbol's model files."""
        # Sanitise symbol for filesystem (e.g. "RELIANCE.NS" → "RELIANCE_NS")
        safe_name = symbol.replace(".", "_").replace("/", "_")
        return self.model_dir / safe_name

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_model(
        model: BaseMLModel,
        X_test: np.ndarray,
        y_test: np.ndarray,
        X_train: np.ndarray,
    ) -> TrainingMetrics:
        """Evaluate a trained model on the test set."""
        y_pred = model.predict(X_test)

        # Compute metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
        recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

        # Classification report (as dict)
        label_names = [LABEL_NAMES.get(i, str(i)) for i in sorted(set(y_test) | set(y_pred))]
        report = classification_report(
            y_test, y_pred,
            target_names=label_names,
            output_dict=True,
            zero_division=0,
        )

        return TrainingMetrics(
            accuracy=accuracy,
            precision_macro=precision,
            recall_macro=recall,
            f1_macro=f1,
            class_report=report,
            train_samples=len(X_train),
            test_samples=len(X_test),
            feature_count=X_test.shape[1],
        )
