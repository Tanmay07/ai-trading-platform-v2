# Phase 11: Autonomous Quant Research Platform

## Overview
Phase 11 converts the platform into an autonomous research laboratory. The system is no longer just a passive executor of predefined rules; it actively discovers, breeds, and evaluates new trading strategies in the background.

## Airgapped Research Lifecycle
The `app/research/` module is strictly isolated from production (`app/execution/` and `app/portfolio/`).
The lifecycle follows:

1. **Alpha & Feature Generation**:
   - `AlphaFactory`: Discovers new alpha factors via mathematical permutations.
   - `FeatureDiscovery`: Prunes non-predictive features from historical datasets.

2. **Ideation & Strategy Breeding**:
   - `HypothesisEngine`: Formulates text-based theories.
   - `StrategyGenerator`: Translates theories into hard thresholds (e.g., RSI > 60).
   - `GeneticOptimizer`: Breeds variations of the thresholds to seek higher Sharpe ratios.

3. **Evaluation**:
   - `StrategyEvaluator`: Pipes the mutated strategy into the Phase 8 Backtesting engines (Walk-Forward & Monte Carlo).
   - If the metrics exceed `validation_thresholds` defined in `research.yaml`, the strategy is promoted to the `StrategyRegistry`.

4. **Human Approval Pipeline**:
   - Discovered strategies sit in `StrategyRegistry` as `PENDING_APPROVAL`. A human quant must review the metrics before it can be activated in the live AI Supervisor array.

## Alpha Decay Monitoring
The `AlphaDecayEngine` bridges the gap between research and production. It continuously monitors the live rolling Sharpe of approved models. If a strategy's edge decays below acceptable limits, the engine flags it for retirement and prompts the `ResearchOrchestrator` to find a replacement.

## Endpoints
Accessible via `/api/research`:
- `POST /api/research/start`: Triggers a full, synchronous discovery loop for demonstration.
- `GET /api/research/strategies`: Lists generated strategies awaiting human approval.
- `GET /api/research/factors`: Retrieves mathematical alphas discovered by the engine.
