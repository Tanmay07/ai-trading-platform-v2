# Production Breakout Model (v1.0) - LightGBM

## Overview
This document outlines the architecture, training details, evaluation metrics, and inference pipeline for the first Production AI Model (v1.0) deployed within the AI Trading Platform. This model is responsible for predicting high-probability 5-7 day trading breakout opportunities within the Nifty 750 universe.

## Model Architecture
*   **Algorithm:** LightGBM (LGBMClassifier)
*   **Version:** v1.0
*   **Objective:** Binary Classification (`is_breakout`)
*   **Framework:** `lightgbm` native Python API (without `scikit-learn` wrapper for optimal SHAP compatibility).

### Hyperparameters
```json
{
  "objective": "binary",
  "metric": ["auc", "binary_logloss"],
  "learning_rate": 0.03,
  "num_leaves": 64,
  "max_depth": 8,
  "feature_fraction": 0.8,
  "bagging_fraction": 0.8,
  "bagging_freq": 5,
  "verbose": -1,
  "early_stopping_rounds": 50,
  "num_boost_round": 1000
}
```

## Dataset & Training
*   **Training Dataset:** `dataset_v1.parquet` generated via `FeaturePipeline` batch processing for Nifty 750 (Phase E2).
*   **Target Variable:** `Target_5d_Return` > 3% OR `Target_7d_Return` > 4%.
*   **Split Strategy:** Time-series chronological split.
    *   **Train:** 80%
    *   **Test (OOT):** 20%

## Validation & Calibration
The raw model outputs uncalibrated margin scores.
To convert these to true probabilities suitable for Kelly Criterion sizing and risk management, we implemented an **Isotonic Regression** calibrator.

*   **Calibrator:** `sklearn.isotonic.IsotonicRegression` (out-of-bound clipped).
*   **Evaluation:** Evaluated on the OOT Test set to verify true probability matching.

## Explainability (SHAP)
Due to Python 3.14 incompatibilities with the standard `shap` package, SHAP values are extracted natively using the LightGBM C++ backend.
*   **Extraction:** `model.predict(X, pred_contrib=True)`
*   This approach generates exact TreeSHAP values for every prediction without requiring external library installations.
*   **Usage:** During real-time inference, the `GrowthPredictor` attaches SHAP explanations to every high-probability candidate, passing them to the React frontend.

## Inference Pipeline (`GrowthPredictor`)
1.  **Feature Ingestion:** Reuses the daily `FeaturePipeline` to compute exactly the same features used during training.
2.  **Probability Scoring:** `model.predict()` -> `calibrator.predict()`.
3.  **Thresholding:** Candidates with Calibrated Probability > 80% are flagged as high-probability breakouts.
4.  **SHAP Attribution:** TreeSHAP calculates the top 3 contributing features for each prediction.
5.  **Output:** JSON payload sent to `OpportunityRanker` and React dashboard.

## Registry & Artifacts
The model is persisted securely via the `ModelRegistry`.
*   **Model Weights:** `data/models/lightgbm_v1.0.txt`
*   **Calibrator:** `data/models/calibrator_v1.0.joblib`
*   **Feature Schema:** `data/models/features_v1.0.json`
*   **Metadata:** `data/models/metadata.json`

## Future Work
*   Train XGBoost and CatBoost models.
*   Implement Soft Voting / Stacking ensembles.
*   Introduce Adaptive Learning (online continuous training).
