# Phase 8: Institutional Backtesting, Walk-Forward Analysis & Strategy Validation

## Overview
Phase 8 implements a strict Sandbox environment for strategies, ML models, and RL policies. Rather than blindly trusting historical returns, the platform enforces Walk-Forward analysis and Monte Carlo simulations, adjusted for realistic transaction costs and slippage, before approving a strategy for production.

## Key Engines
1. **`event_driven_simulator.py`**: A true event-driven backtester (replaces vectorised loops) that ensures chronological execution and prevents look-ahead bias.
2. **`transaction_cost_engine.py`**: Calculates Indian-specific execution costs, including Brokerage (e.g., Zerodha), STT (0.1% delivery), Exchange Transaction Charges, GST, and SEBI fees.
3. **`slippage_engine.py` & `liquidity_engine.py`**: Simulates the penalty of trading illiquid stocks or during highly volatile regimes. Caps participation at 5% of Average Daily Volume (ADV).
4. **`monte_carlo_engine.py`**: Runs thousands of simulated trade sequence permutations to discover the true "Worst Case Drawdown" and "Probability of Ruin".
5. **`validation_engine.py`**: The final judge. Checks if the strategy meets the config requirements (e.g. `min_cagr: 0.15`, `max_drawdown: 0.20`, `min_monte_carlo_survival: 0.95`). Outputs a PASS/FAIL and a Validation Score.

## APIs
The `/api/backtest_v2` sub-router exposes:
- `POST /api/backtest_v2/run`: Executes the full backtest pipeline for a given strategy name and returns the JSON report.
- `GET /api/backtest_v2/validation`: Retrieves the latest validation scores.
- `GET /api/backtest_v2/montecarlo`: Retrieves the Monte Carlo simulation data.
