# Phase 7: Portfolio Intelligence & Dynamic Capital Allocation

## Overview
Phase 7 shifts the platform from a "Stock Recommendation Engine" into a "Portfolio Management System". Recommendations are no longer evaluated in a vacuum—every AI/ML/RL-generated candidate is subjected to a final gauntlet to see if it *improves* the overall portfolio.

## Sub-Modules
- **`portfolio_analyzer.py`**: Computes portfolio-level sector allocation, cash drag, and concentration metrics (HHI).
- **`correlation_engine.py`**: Ensures new candidates do not simply mirror existing risk (blocks stocks that behave identically to the portfolio).
- **`exposure_engine.py`**: Hard stops! Enforces constraints like `max_sector_exposure` (30%) and `max_stock_allocation` (15%).
- **`kelly_optimizer.py`**: Calculates the theoretically optimal fraction of capital to risk on a trade given the AI's win probability and the assumed risk/reward ratio. Uses a Half-Kelly bounds for safety.
- **`allocation_engine.py`**: Takes the Kelly fraction and the exposure limits to output the final `Recommended_Allocation_Cash`.
- **`portfolio_orchestrator.py`**: Tied directly into the `RecommendationEngine` as the ultimate filter before results hit the API.

## APIs
The `/api/portfolio_intel` sub-router exposes:
- `GET /api/portfolio_intel/analysis`: Sector weights, Diversification Score, Concentration Score.
- `GET /api/portfolio_intel/risk`: VaR (Value at Risk) and Portfolio Volatility metrics.
- `POST /api/portfolio_intel/rebalance`: Triggers the rebalancing engine to check for portfolio drift against target weights.
