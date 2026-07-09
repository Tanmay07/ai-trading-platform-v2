# Phase E1: Historical Data Bootstrap & Initial Model Pipeline

## Overview
Phase E1 is the grand orchestrator. It brings together the Historical Data Lake (D1) and the Feature Store / ML Platform (D2) into a cohesive, fault-tolerant execution pipeline. It fetches historical data for the entire NSE universe, generates all necessary technical features, builds supervised labels, trains the baseline models (LightGBM, XGBoost, CatBoost), and combines them into an operational Meta Ensemble.

## Execution Flow (`BootstrapManager`)
The pipeline runs asynchronously in the background via `backend/bootstrap_engine/manager.py` and progresses sequentially through 12 steps. State is persisted in `bootstrap.db` via SQLAlchemy.

1. **Universe**: Loads the active NSE universe.
2. **Download**: Asynchronously fetches 10-years of Yahoo Finance data in batches.
3. **Validation**: Checks for missing candles and duplicate rows.
4. **Features**: Triggers the `Feature Store` to compute Trend, Momentum, and Volatility indicators.
5. **Labels**: Generates 5-day and 7-day future return supervised labels.
6. **Dataset**: Compiles Train/Val/Test splits with strict walk-forward (no-leakage) boundaries.
7. **Train**: Trains `LightGBM`, `XGBoost`, and `CatBoost`.
8. **Ensemble**: Combines models using soft voting / weighted averaging.
9. **Validate**: Generates classification and trading metrics (e.g. Sharpe Ratio, Win Rate).
10. **Register**: Registers the best model into the ML registry for production use.
11. **Predict**: Generates predictions for the current active universe using the new model.
12. **Recommendation**: Injects the predictions directly into the `Recommendation Engine`.

## API Endpoints
Exposed via `app.api.bootstrap_routes`:
- `POST /api/bootstrap/start`: Triggers or resumes the pipeline.
- `GET /api/bootstrap/status`: Returns current step (1-12) and status.
- `GET /api/bootstrap/progress`: Returns deeply nested JSON mapping to UI dashboard metrics.

## Resilience
If the server crashes during Step 4, calling `POST /api/bootstrap/start` will query `bootstrap.db`, detect that steps 1-3 are completed, and immediately resume at Step 4, guaranteeing idempotency.
