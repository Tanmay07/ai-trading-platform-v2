# Institutional Training Framework

The `training_framework` module upgrades the AI Platform's modeling methodology from a simple train/validation/test split to an institutional quantitative research standard. This methodology protects against look-ahead bias and autocorrelation leakage in time-series data while rigorously optimizing hyperparameters and recommendation thresholds.

## 1. Purged Walk-Forward Time-Series Validation

Standard cross-validation (like KFold) randomly shuffles data, leading to severe data leakage in financial time-series. The framework uses **Purged Walk-Forward Validation**:

- **Expanding Window**: The training set grows over time (e.g., 2021, then 2021-2022, then 2021-2023) while testing on the immediate next block.
- **Purge**: Any training samples whose prediction horizon overlaps with the start of the validation set are dropped. (Default: 5 Days).
- **Embargo**: A gap is enforced after the validation set before any subsequent training data begins, eliminating serial correlation. (Default: 7 Days).

## 2. Randomized Hyperparameter Search

Instead of static parameters, the framework automatically searches a defined hyperparameter space using `RandomizedSearchCV` paired with the Purged CV generator. The nested validation strategy ensures the hyperparameters are tuned exclusively on historical data and tested blindly.

## 3. Probability Calibration

LightGBM outputs uncalibrated probabilities (which tend to be overconfident or underconfident). The framework fits two calibrators on the out-of-fold validation predictions:
- **Platt Scaling (Logistic Regression)**
- **Isotonic Regression**

The calibrator with the lowest **Brier Score** is automatically persisted and used to calibrate live inference probabilities.

## 4. Threshold Optimization via Trading Metrics

Rather than using an arbitrary `0.5` probability threshold for buy recommendations, the `ThresholdOptimizer` calculates actual trading metrics (Win Rate, Profit Factor, Average Return, Sharpe Ratio) for thresholds ranging from 50% to 85%.

The production recommendation threshold is the probability cutoff that maximizes **Profit Factor** and **Win Rate**.

## 5. Experiment Registry

Every search trial and final trained model is logged to `data/models/experiment_registry.json`. The `/api/training/experiments` endpoint exposes this leaderboard to the React Dashboard, guaranteeing 100% reproducible experiments.
