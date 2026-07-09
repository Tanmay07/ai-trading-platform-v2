# Tradability Intelligence Engine

## Overview
The Tradability Intelligence Engine acts as the dynamic gatekeeper for the AI Trading Platform. Rather than statically blacklisting stocks, it dynamically evaluates the entire NSE universe every day to generate a continuous **Tradability Score (0-100)**. 

This score determines a stock's classification and dictates whether it can be used for ML model training, backtesting, or live trading.

## Scoring Methodology
The final score is a weighted average of 5 discrete sub-scores, configured in `config/tradability.yaml`:
1. **Liquidity Score (35%)**: Measures 30-day ADTV (Average Daily Traded Value), Delivery percentages, and raw volume to ensure we can enter/exit positions.
2. **Execution Score (20%)**: Estimates slippage and order fill probabilities.
3. **Volatility Score (15%)**: Rewards healthy ATRs while penalizing erratic jumps or dead momentum.
4. **Data Quality Score (15%)**: Penalizes stocks with missing historical candles or duplicate rows.
5. **Circuit Behavior Score (15%)**: Heavily penalizes stocks that frequently hit upper/lower circuits, as this prevents trade execution.

## Tradability Categories
Based on the final score, a stock falls into one of 5 categories:
- **Institutional Grade** (90-100)
- **Highly Tradable** (75-89)
- **Tradable** (60-74)
- **Monitor** (40-59)
- **Restricted** (0-39)

## Integration Points
1. **Model Training (Phase D2)**: `DatasetBuilder` strictly imports the `training_filter.py` and strips out any rows belonging to `Monitor` or `Restricted` stocks before feeding them to XGBoost/LightGBM. This ensures the model learns from high-quality price action only.
2. **Recommendation Engine**: The engine uses `recommendation_filter.py` to artificially lower the `confidence` score of predictions made on `Monitor` stocks, labeling them as "High Execution Risk". 

## Monitoring (Promotions & Demotions)
The `TradabilityMonitor` runs nightly. It compares yesterday's score category to today's. If a stock shifts across a tier boundary (e.g. from `Tradable` down to `Monitor` due to crashing volume), it triggers the `demotion_engine.py` which logs the event to `tradability.db` for historical auditability.
