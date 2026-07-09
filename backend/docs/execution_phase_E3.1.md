# Phase E3.1: Scenario Dataset Generator & Specialized Training Platform

## Overview
Phase E3.1 acts as the gateway to the **Hierarchical Model Registry**. Instead of forcing a single ML model to generalize across all market conditions, this module automatically slices the E3 Master Dataset into highly specialized scenarios (e.g., Bull Markets, Banking Sector, High Volatility). 

## Architecture & Workflow
1. **Scenario Registry**: A SQLite DB (`scenario_registry.db`) that tracks every spawned scenario, recording its parent dataset (from E3) to maintain strict data lineage.
2. **Segmentation Engines**:
    - `MarketRegimeSplitter`: Uses Index moving averages to isolate Bull, Bear, and Sideways periods.
    - `SectorSplitter`: Isolates stocks by NSE sectoral indices (e.g., IT, Banking, Pharma).
    - `VolatilitySplitter`: Uses ATR or VIX percentiles to isolate high vs. low volatility regimes.
    - `EventSplitter`: Slices a configurable `+/- N` day window around major macro events (like the Union Budget).
3. **Scenario Validator**: Enforces statistical rigor by rejecting datasets that are too small (e.g., < 1000 rows or < 10 symbols) to prevent overfitting during specialized model training.
4. **Scenario Builder**: The orchestrator that ingests a master dataset and automatically spins off all configured permutations.

## Configuration (`config/scenario_dataset.yaml`)
- Configures regime boundaries (`sma_fast > sma_slow`).
- Configures volatility percentiles (`high: 75`, `low: 25`).
- Configures event dates and window sizes.
- Configures minimum dataset validation limits.

## API & UI
- **APIs**: `/api/scenarios/` serves the generation metrics and scenario registry.
- **UI**: `ScenarioIntelligence.jsx` exposes the distribution of regimes, sectors, and top scenario dataset sizes to the frontend.
