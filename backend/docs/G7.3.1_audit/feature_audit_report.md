# Feature Importance & Integrity Audit Report

## Top 20 Champion Features
| Feature | Importance Score | Leakage Status |
|---|---|---|

**Audit Finding:** The Champion model relied entirely on variables constructed from future outcomes (like `Target_Return_5d` or `Simulated_Return_Pct`).
