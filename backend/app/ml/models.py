"""
ML Model Wrappers — Phase 3

Provides a unified interface for XGBoost, LightGBM, and a soft-voting
ensemble classifier.

Each wrapper implements:
    - ``train(X, y)``          — fit the model
    - ``predict(X)``           — return integer labels
    - ``predict_proba(X)``     — return class probabilities
    - ``get_params()``         — return hyperparameters dict
    - ``name``                 — human-readable model name

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from app.utils.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------
# Result dataclasses
# ------------------------------------------------------------------


@dataclass
class PredictionResult:
    """Result of a single ML prediction."""

    direction: str          # "UP", "DOWN", "NEUTRAL"
    direction_int: int      # 0=DOWN, 1=NEUTRAL, 2=UP
    probability: float      # probability of predicted class
    confidence: float       # calibrated confidence (0–1)
    probabilities: dict[str, float] = field(default_factory=dict)
    model_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "direction": self.direction,
            "probability": round(self.probability, 4),
            "confidence": round(self.confidence, 4),
            "probabilities": {
                k: round(v, 4) for k, v in self.probabilities.items()
            },
            "model_name": self.model_name,
        }


@dataclass
class TrainingMetrics:
    """Metrics from model evaluation on the test set."""

    accuracy: float = 0.0
    precision_macro: float = 0.0
    recall_macro: float = 0.0
    f1_macro: float = 0.0
    class_report: dict = field(default_factory=dict)
    train_samples: int = 0
    test_samples: int = 0
    feature_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision_macro": round(self.precision_macro, 4),
            "recall_macro": round(self.recall_macro, 4),
            "f1_macro": round(self.f1_macro, 4),
            "train_samples": self.train_samples,
            "test_samples": self.test_samples,
            "feature_count": self.feature_count,
        }


# ------------------------------------------------------------------
# Abstract base
# ------------------------------------------------------------------


class BaseMLModel(ABC):
    """Abstract interface for all ML models."""

    name: str = "base"

    def __init__(self) -> None:
        self.model: Any = None
        self.scaler: StandardScaler = StandardScaler()
        self.is_fitted: bool = False
        self._feature_names: list[str] = []

    @abstractmethod
    def _create_model(self) -> Any:
        """Create and return the underlying model instance."""

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> None:
        """Fit the model on training data.

        Args:
            X_train: Feature matrix (n_samples, n_features).
            y_train: Label vector (n_samples,).
            feature_names: Optional list of feature column names.
        """
        self.model = self._create_model()
        self._feature_names = list(feature_names) if feature_names else []

        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        logger.info(
            "Training %s on %d samples with %d features",
            self.name, X_scaled.shape[0], X_scaled.shape[1],
        )

        self.model.fit(X_scaled, y_train)
        self.is_fitted = True

        logger.info("%s training complete", self.name)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted integer labels.

        Args:
            X: Feature matrix (n_samples, n_features).

        Returns:
            Array of integer labels.
        """
        self._check_fitted()
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probabilities.

        Args:
            X: Feature matrix (n_samples, n_features).

        Returns:
            Array of shape (n_samples, n_classes) with probabilities.
        """
        self._check_fitted()
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def predict_single(self, X: np.ndarray) -> PredictionResult:
        """Predict for a single sample and return a structured result.

        Args:
            X: Feature matrix of shape (1, n_features).

        Returns:
            PredictionResult with direction, probability, and confidence.
        """
        from app.ml.ml_data_preparer import LABEL_NAMES

        self._check_fitted()
        probas = self.predict_proba(X)[0]  # shape: (n_classes,)
        pred_int = int(np.argmax(probas))
        pred_prob = float(probas[pred_int])

        # Confidence: how much the top class exceeds a uniform distribution
        # For 3 classes, uniform = 0.333; max confidence at prob = 1.0
        confidence = min((pred_prob - 1.0 / 3.0) / (1.0 - 1.0 / 3.0), 1.0)
        confidence = max(confidence, 0.0)

        return PredictionResult(
            direction=LABEL_NAMES.get(pred_int, "UNKNOWN"),
            direction_int=pred_int,
            probability=pred_prob,
            confidence=confidence,
            probabilities={
                LABEL_NAMES.get(i, f"class_{i}"): float(probas[i])
                for i in range(len(probas))
            },
            model_name=self.name,
        )

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        """Return model hyperparameters."""

    def get_feature_importance(self) -> dict[str, float]:
        """Return feature importance scores (if available).

        Returns:
            Dictionary mapping feature name to importance score.
        """
        if not self.is_fitted or not hasattr(self.model, "feature_importances_"):
            return {}

        importances = self.model.feature_importances_
        names = self._feature_names or [f"f{i}" for i in range(len(importances))]

        result = dict(zip(names, importances))
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    def _check_fitted(self) -> None:
        if not self.is_fitted:
            raise RuntimeError(f"{self.name} has not been trained yet")


# ------------------------------------------------------------------
# XGBoost
# ------------------------------------------------------------------


class XGBoostModel(BaseMLModel):
    """XGBoost gradient-boosted tree classifier."""

    name = "xgboost"

    def _create_model(self) -> Any:
        from xgboost import XGBClassifier

        return XGBClassifier(
            max_depth=6,
            n_estimators=200,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            reg_alpha=0.1,
            reg_lambda=1.0,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )

    def get_params(self) -> dict[str, Any]:
        return {
            "max_depth": 6,
            "n_estimators": 200,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 3,
        }


# ------------------------------------------------------------------
# LightGBM
# ------------------------------------------------------------------


class LightGBMModel(BaseMLModel):
    """LightGBM gradient-boosted tree classifier."""

    name = "lightgbm"

    def _create_model(self) -> Any:
        from lightgbm import LGBMClassifier

        return LGBMClassifier(
            num_leaves=31,
            n_estimators=200,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_samples=20,
            reg_alpha=0.1,
            reg_lambda=1.0,
            objective="multiclass",
            num_class=3,
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        )

    def get_params(self) -> dict[str, Any]:
        return {
            "num_leaves": 31,
            "n_estimators": 200,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_samples": 20,
        }


# ------------------------------------------------------------------
# Soft-Voting Ensemble
# ------------------------------------------------------------------


class EnsembleModel(BaseMLModel):
    """Soft-voting ensemble of XGBoost + LightGBM.

    Averages predicted probabilities from both constituent models
    and selects the class with the highest average probability.
    """

    name = "ensemble"

    def __init__(self) -> None:
        super().__init__()
        self.xgb = XGBoostModel()
        self.lgb = LightGBMModel()

    def _create_model(self) -> Any:
        # The ensemble doesn't have a single underlying model
        return None

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> None:
        """Train both constituent models."""
        self._feature_names = list(feature_names) if feature_names else []

        # Scale features using the ensemble's own scaler
        self.scaler.fit(X_train)
        X_scaled = self.scaler.transform(X_train)

        # Train both models with pre-scaled data (they will re-scale, but
        # we need consistent scaling for predict)
        self.xgb.train(X_train, y_train, feature_names)
        self.lgb.train(X_train, y_train, feature_names)

        self.is_fitted = True
        logger.info("Ensemble training complete (XGBoost + LightGBM)")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted labels via averaged probabilities."""
        self._check_fitted()
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average class probabilities from both models."""
        self._check_fitted()
        proba_xgb = self.xgb.predict_proba(X)
        proba_lgb = self.lgb.predict_proba(X)
        return (proba_xgb + proba_lgb) / 2.0

    def get_params(self) -> dict[str, Any]:
        return {
            "models": ["xgboost", "lightgbm"],
            "voting": "soft",
            "xgboost_params": self.xgb.get_params(),
            "lightgbm_params": self.lgb.get_params(),
        }

    def get_feature_importance(self) -> dict[str, float]:
        """Average feature importance from both constituent models."""
        imp_xgb = self.xgb.get_feature_importance()
        imp_lgb = self.lgb.get_feature_importance()

        if not imp_xgb and not imp_lgb:
            return {}

        all_keys = set(imp_xgb.keys()) | set(imp_lgb.keys())
        averaged = {}
        for key in all_keys:
            averaged[key] = (imp_xgb.get(key, 0.0) + imp_lgb.get(key, 0.0)) / 2.0

        return dict(sorted(averaged.items(), key=lambda x: x[1], reverse=True))
