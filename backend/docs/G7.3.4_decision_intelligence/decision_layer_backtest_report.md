# Decision Layer Backtest Report

By integrating the Decision Intelligence Layer (Dynamic Thresholding + Cost-Aware Filtering), we filtered out hundreds of low-EV trades that were bleeding capital to friction.

## 1. Filter Engine Metrics
- **Executed Trades:** 56
- **Rejected Low-EV Trades:** 1052

## 2. Institutional Performance (Filtered vs Unfiltered)
| Metric | G7.3.3 Unfiltered Result | G7.3.4 Decision Filtered Result |
|---|---|---|
| Institutional CAGR | -37.68% | 10.96% |
| Institutional Sharpe | -0.33 | 0.18 |
| Max Drawdown | -35.66% | -10.25% |
| Win Rate | 19.67% | 66.07% |
