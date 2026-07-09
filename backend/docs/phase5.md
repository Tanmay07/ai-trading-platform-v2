# Phase 5: Advanced Machine Learning, Auto-Learning & Model Intelligence

## Overview
Phase 5 transforms the trading platform from using static predictions into an enterprise-grade MLOps system. The new architecture features a dynamic Feature Store, Ensemble Meta-Learning, Probability Calibration, and an Auto-Retraining engine that tracks Drift.

## Core MLOps Infrastructure
- **`config/ml.yaml`**: Drives all thresholds, from max_depth of XGBoost to the PSI drift alerts.
- **`feature_store.py`**: A localized SQLite storage layer that snapshots candidate data continuously. This enables us to dynamically rebuild unbiased datasets.
- **`dataset_builder.py` & `feature_selector.py`**: Reads from the store, drops look-ahead biases, drops strings, and calculates Mutual Information to retain only the highest signal features.

## Ensemble & Calibration
- **`model_trainer.py`**: Wraps XGBoost, LightGBM, and Random Forest.
- **`ensemble_engine.py`**: Calculates the weighted soft probabilities of the tree models.
- **`meta_learner.py`**: Acts as a stacking classifier (Logistic Regression) taking the Ensemble probability + Phase 4 AI Consensus + Phase 3 Market Regime as input to produce a final refined probability.
- **`probability_calibrator.py`**: Runs Isotonic Regression on the output so that a "74% probability" is mathematically reliable.

## Monitoring & Auto-Retraining
- **`drift_detector.py`**: Implements the PSI (Population Stability Index) mathematical framework to continuously compare live feature distributions against training data distributions.
- **`retraining_engine.py`**: Can be triggered manually or via scheduler. It rebuilds the dataset, executes feature selection, trains the trio of models, trains the meta-learner, calibrates it, and promotes it to the Registry if validation AUC improves.
- **`model_registry.py`**: Saves binary `.pkl` dumps in `data/model_registry/champion_ensemble/<timestamp>/`.

## API Integration
The Phase 5 ML prediction pipeline sits directly before the Phase 4 AI Supervisor in the `orchestrator.py` flow. The ML engine exposes `GET /api/ml/models` and `POST /api/ml/retrain` to interact dynamically.
