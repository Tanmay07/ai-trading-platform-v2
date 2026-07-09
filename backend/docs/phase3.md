# Phase 3: Market Intelligence & Institutional Analytics

## Overview
Phase 3 introduces a robust Market Intelligence layer that evaluates the overall market environment before any trade recommendation is generated. This layer prevents the system from recommending high-risk long breakouts in a Bear market or Risk-Off environment.

## 10-Engine Architecture
1. **Market Regime Engine**: Evaluates the Nifty 50 against 20, 50, and 200 EMAs to classify the market into 9 regimes (Strong Bull -> Capitulation) and assigns a portfolio exposure multiplier.
2. **Market Breadth Engine**: Scans the entire Phase 2 Nifty 500 DataFrame to calculate A/D Ratios and percentage of stocks above key moving averages.
3. **Macro Engine**: Fetches India VIX, USD/INR, DXY, US 10Y Yield, and Brent Crude to assess global macroeconomic risk.
4. **FII / DII Engine**: Assesses institutional flow (Currently using simulated baselines pending Phase 4 data source).
5. **Institutional Activity Engine**: Evaluates block deals and promoter buying (Simulated baseline).
6. **Volatility Engine**: Contextualizes the India VIX absolute value and trend.
7. **Liquidity Engine**: Measures the ratio of today's total market volume vs the 20-day average.
8. **Global Market Engine**: Evaluates overnight sentiment using S&P 500, Dow Jones, and Nikkei 225 returns.
9. **Market Health Engine**: A composite score of Breadth, Volatility, Liquidity, Macro, and Institutional Activity.
10. **Market Score Engine**: A weighted 0-100 score indicating the overall health of the trading environment.

## Integration
The `MarketIntelligenceOrchestrator` is injected into the Phase 1 `RecommendationEngine`.
1. It runs *after* Phase 2 (Technical Analysis).
2. It fetches global macro data concurrently via `yfinance`.
3. It derives Breadth and Liquidity metrics *directly* from the `df_daily_all` universe dataframe fetched by Phase 2, resulting in **zero additional API overhead**.
4. The resulting `Market Score` is applied as a multiplier to the Breakout Probability of each candidate.
5. The resulting `Market Regime` determines an `exposure_multiplier`, which dynamically shrinks the `max_monetary_risk` and `max_capital_allocation` parameters passed into the Phase 1 `RiskEngine`. This ensures smaller position sizes during high-risk regimes.

## API Endpoint
`GET /api/market-intelligence`
Returns the standalone market health and regime without generating individual stock recommendations.
