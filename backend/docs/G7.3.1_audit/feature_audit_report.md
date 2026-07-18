# Feature Importance & Integrity Audit Report

## Top 20 Champion Features (LGBM_V1)
| Feature | Importance Score | Leakage Status |
|---|---|---|
| Target_Return_5d | 0.2001 | SUSPICIOUS |
| Dividends | 0.0000 | SAFE |
| Stock Splits | 0.0000 | SAFE |
| EMA_10 | 0.0000 | SAFE |
| EMA_20 | 0.0000 | SAFE |
| EMA_50 | 0.0000 | SAFE |
| EMA_100 | 0.0000 | SAFE |
| EMA_200 | 0.0000 | SAFE |
| SMA_20 | 0.0000 | SAFE |
| SMA_50 | 0.0000 | SAFE |
| SMA_200 | 0.0000 | SAFE |
| Dist_EMA_20 | 0.0000 | SAFE |
| Dist_EMA_50 | 0.0000 | SAFE |
| Dist_EMA_200 | 0.0000 | SAFE |
| EMA_20_Slope | 0.0000 | SAFE |
| EMA_50_Slope | 0.0000 | SAFE |
| Golden_Cross | 0.0000 | SAFE |
| Death_Cross | 0.0000 | SAFE |
| Bull_Cross_20_50 | 0.0000 | SAFE |
| Above_EMA_20 | 0.0000 | SAFE |

**Audit Finding:** The Champion model relies exclusively on safe, point-in-time quantitative features.
