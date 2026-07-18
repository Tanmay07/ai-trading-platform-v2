# Decision Intelligence Attribution (Ablation Study)

This report quantifies the contribution of each Decision Intelligence component by systematically disabling them and measuring the performance degradation.

| Configuration | CAGR | Sharpe | Max Drawdown | Win Rate | Total Trades |
|---|---|---|---|---|---|
| Full System | 10.96% | 0.18 | -10.25% | 66.07% | 56 |
| No Regime Filter | 58.31% | 1.35 | -16.30% | 58.42% | 303 |
| No EV Filter | 10.96% | 0.18 | -10.25% | 66.07% | 56 |
| No Low Vol Filter | -53.57% | -0.34 | -44.79% | 0.21% | 469 |
| No High Vol Filter | 10.85% | 0.17 | -10.25% | 64.91% | 57 |
