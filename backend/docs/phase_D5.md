# Phase D5: AI Meta Decision Engine

## Overview
The Meta Decision Engine represents the apex intelligence layer of the trading platform. Rather than looking at ML models, News Sentiment, and Technicals in isolation, this engine dynamically weighs them against the current **Market Regime**.

## Architecture Pipeline
The flow follows a strict execution path inside `MetaDecisionEngine.evaluate()`:

1. **Regime Classification**: The `RegimeClassifier` evaluates the Nifty Trend and VIX. If VIX > 25, the market is classified as `HighVolatility`. If Nifty is UP, it's a `Bull` market.
2. **Adaptive Weighting**: The `AdaptiveWeightEngine` fetches regime-specific weights from `config/decision_engine.yaml`. For example, in a `Bear` market, *Risk* weighting increases to 30%, while *Technical Momentum* drops to 15%.
3. **Score Normalization**: The `ScoringEngine` forces disparate inputs (RSI, Sentiments, ML Probs) into unified `0-100` scores.
4. **Final Scoring**: Produces an expected ranking score based on a weighted sum.
5. **Confidence Engine**: Starts confidence at `ML Agreement %`, penalizes for stale data, and boosts if technicals+news align perfectly.
6. **Probability Calibration**: Uses `ProbabilityCalibrator` (a Mock Platt Scaling Sigmoid curve) to adjust raw ML overconfidence into a smoother curve.
7. **Decision Explainer**: Translates the matrix mathematics into a human-readable string (e.g. "BUY BEL (Confidence 94%). Why? Under the Bull regime, the system heavily weighs Technical (35%).").

## API Endpoints
- `GET /api/decision/explain/{symbol}`: Returns a full decision payload for a specific stock.
- `GET /api/decision/top`: Mocks a batch scan and ranks the top `N` opportunities using the `OpportunityRanker`.
