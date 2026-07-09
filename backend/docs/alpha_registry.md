# Phase E2.1: Institutional Alpha Factor Registry & Research Platform

## Overview
Phase E2.1 upgrades the Feature Store into a quantitative **Alpha Research Platform**. Rather than passing all engineered features blindly into the Machine Learning models, every feature is now formally registered as an "Alpha Factor".

These factors are continuously evaluated for:
- **Predictive Power**: Measured via Information Coefficient (IC).
- **Stability**: Measured via rolling IC window comparisons to detect factor degradation.
- **Regime Performance**: Evaluated independently in Bull, Bear, and Sideways markets.
- **Correlation**: Duplicate or highly correlated factors are flagged for removal.

## Architecture & Integration
The Alpha Registry sits directly between the `Feature Store` and the `ML Dataset Builder`.

1. **Storage**: We use a SQLite database (`alpha_registry.db`) defined in `alpha_metadata.py` to persist the historical IC scores, metadata, and lifecycle status (Production, Experimental, Deprecated) of every factor.
2. **Dataset Builder Integration**: The `DatasetBuilder` now queries the `AlphaSelector` for an approved list of features, preventing known "weak" or "decaying" factors from polluting the ML datasets. This ensures the prediction engine relies solely on evidence-based alpha.

## Module Structure (`backend/alpha_registry/`)
- `registry/`: SQLite models and CRUD operations for the Factor Catalog.
- `evaluation/`: Scripts to calculate Information Coefficient, Rank IC, and Stability metrics.
- `analytics/`: Correlation matrices and Factor Ranking engines to identify the Top 10 predictors.
- `optimization/`: `AlphaSelector` logic which enforces the thresholds defined in `config/alpha_registry.yaml`.

## Configuration (`config/alpha_registry.yaml`)
You can tweak the thresholds that promote a factor from "Experimental" to "Production":
- `min_ic_production`: Minimum IC required to be used in live ML datasets (default 0.02).
- `max_correlation`: Maximum allowed correlation before flagging redundancy (default 0.85).

## API & UI
- **APIs**: Exposes `/api/alpha/` and `/api/alpha/ranking` to serve evaluation metrics.
- **UI**: Added `AlphaIntelligence.jsx` (Alpha Research Lab) to the frontend. It visualizes Top Predictive Factors, Alpha Decay Alerts, and Regime-specific Alpha performance.
