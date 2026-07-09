# Phase 6: Reinforcement Learning & Self-Optimizing Decision Engine

## Overview
Phase 6 introduces a Reinforcement Learning (RL) Meta-Optimizer to the trading platform. Rather than attempting to predict stock prices directly, the RL subsystem acts as a continuous learning supervisor that adjusts internal thresholds based on historical paper-trading performance. 

## Key Philosophy
The system operates as an **Offline Contextual Bandit**:
1. It **observes** the state (Breakout Score, Market Regime, ML Probabilities, AI Consensus).
2. It takes a meta-**action** (e.g., lower confidence, reduce position sizing).
3. The Paper Trading Engine closes a trade and provides a **reward** (Profit, minus drawdown penalty, minus time penalty).
4. The offline `LearningScheduler` updates the underlying Regression model to map States -> Optimal Actions.

## Sub-Modules
- **`state_builder.py`**: Normalizes all incoming recommendation metrics into a [0, 1] bounded feature array.
- **`action_engine.py`**: Decodes raw policy outputs into clipped safety limits (e.g. max 15% confidence tweak).
- **`reward_engine.py`**: A composite reward function that balances pure profit with Sharpe ratio analogs.
- **`experience_buffer.py`**: A SQLite engine keeping a ledger of every state, action, and outcome.
- **`confidence_optimizer.py`**: Converts raw AI Supervisor Confidences into mathematically calibrated RL Confidences.
- **`rl_orchestrator.py`**: Hooked into the end of `orchestrator.py`, it injects these adjustments before position sizing.

## API Integration
The RL engine provides several endpoints in `backend/app/api/reinforcement_routes.py`:
- `GET /api/reinforcement/policy`
- `GET /api/reinforcement/performance`
- `GET /api/reinforcement/rewards`
- `POST /api/reinforcement/retrain`
