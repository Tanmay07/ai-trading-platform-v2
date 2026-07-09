# Phase E1.5: Production Bootstrap Manager

## Overview
The Bootstrap Manager acts as the orchestrator for the entire AI Trading Platform. Instead of executing scripts manually, it leverages a sophisticated Preflight Estimation Engine to scan the system, estimate workloads, and then executes a resumable state machine to initialize everything from Universe Validation to Model Deployment.

## Architecture
1. **Preflight Engine** (`preflight_engine.py`): Scans the active configuration against the `UniverseManager` and `HistoricalDataService` to estimate how many gigabytes of data will be downloaded, how long it will take, and how many API calls will be dispatched.
2. **Checkpoint Manager** (`checkpoint_manager.py`): Persists the execution state (Pending, Running, Completed) to `bootstrap_recovery.db`. If a node crashes during feature generation, the system resumes precisely from the last symbol batch instead of starting over.
3. **Execution Pipeline**: 
   - `EnvironmentValidation`
   - `UniverseValidation`
   - `HistoricalData`
   - `FeatureGeneration`
   - `DatasetGeneration`
   - `ModelValidation`
   - `PredictionGeneration`

## Configuration (`config/bootstrap.yaml`)
Allows precise control over execution boundaries, enabling/disabling specific stages (e.g. skipping dataset generation if you only want to update historical data), and defining worker concurrency limits to prevent memory exhaustion during the pipeline.

## API & UI
Exposes `/api/bootstrap/preflight`, `/api/bootstrap/start`, and `/api/bootstrap/status/{execution_id}`. The frontend UI provides a real-time progress monitor to track the initialization state of each subsystem.
