# Root Cause Analysis

## Incident Description
During Phase G7.3, all candidate models achieved a perfect ROC-AUC of 1.000 and extraordinary simulated financial returns. This triggered an independent audit.

## Root Cause
**Direct Target Leakage (Look-Ahead Bias)**
The dataset pipeline generated simulation columns and target variables (such as 5-day future returns) and stored them in the parquet files alongside legitimate features.
During the training orchestration, the feature selection logic was implemented as a blocklist:
```python
exclude = ['Date', 'Symbol', 'Target_Forward_Return', 'Target_Class', 'Open', 'High', 'Low', 'Close', 'Volume']
features = [c for c in df.columns if c not in exclude]
```
Because the actual target columns were named differently (e.g., `Target_Return_5d`, `Target_Class_5d`) and included simulated outcomes (e.g., `Simulated_Return_Pct`), the blocklist failed to exclude them. The models ingested the literal answers to the predictions during training.

**Confirmed Leakage Columns Fed to Model:** 
**Highly Suspicious Columns Fed to Model:** `Target_Return_5d`, `Target_Return_7d`, `Target_Class_5d`, `Target_Breakout_Success`, `Simulated_Return_Pct`, `MFE_Pct`, `MAE_Pct`, `Days_To_Target`, `Days_To_Stop`, `Simulated_Exit_Price`, `Trade_Quality_Score`, `Label_Baseline`, `Label_TradeSuccess`, `Label_Ranking`, `Breakout_Quality_Factor`

## Corrective Action Required
1. Refactor the Orchestrator to use an explicit **allowlist** of features, or programmatically enforce regex exclusion of `Target_*`, `Simulated_*`, and `Label_*` columns.
2. Clear the Model Registry and re-run the Multi-Model Arena.
