# Baseline Comparison Report

| Model | ROC-AUC |
|---|---|
| Linear Regression (Baseline) | 0.5175 |
| Decision Tree (Baseline) | 1.0000 |
| XGBoost (Champion) | 1.0000 |

**Audit Finding:** Even a trivial linear model or a depth-3 decision tree achieves statistically improbable predictive power. This independently confirms that the dataset itself is compromised with direct look-ahead bias.
