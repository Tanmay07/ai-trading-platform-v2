# Configurable Investment Decision Policy Engine (Phase P3.1)

## Overview
The Investment Decision Policy Engine transforms the static logic of the Decision Intelligence Engine (Phase P3) into a fully dynamic, version-controlled execution environment. This allows the platform to support multiple distinct investment styles simultaneously without altering core Python logic.

## Architecture

1. **Policy Repository**: The heart of the system is the `policy_engine.db` SQLite database. It stores the `Policy` (e.g., "Aggressive Growth") and its immutable `PolicyVersion`.
2. **Dynamic Weights & Thresholds**: Instead of hard-coded values, the engine reads a JSON configuration at runtime containing the exact weights for Technical, Valuation, Portfolio Context, and Risk intelligence, as well as the threshold mapping for decisions (e.g., Score > 90 = STRONG_BUY).
3. **Execution Routing (`DecisionPolicyEngine`)**: The engine calls the 4 underlying Intelligence modules, gathers the metrics, applies the policy weights to compute a dynamic score, and routes the execution logic through `MethodologyEngine` for targets and stops.
4. **Audit Trail**: Every decision made by the system generates a `DecisionAuditLog`, storing the exact market data snapshot, portfolio context snapshot, version ID used, and the generated JSON breakdown. This ensures 100% reproducibility and explainability.

## API Integration
To invoke the engine:
```
GET /api/v2/decision/recommendations/1?policy_id=2
```
If `policy_id` is passed, the engine maps the decision logic to the specified policy. If omitted, the engine uses the active default policy.

## Extensibility (Future Enhancements)
- **A/B Testing**: The system can compare the Hit Rate of "Growth v1.0" against "Growth v2.0" by cross-referencing the `DecisionAuditLog` with subsequent price action.
- **Market Regimes**: The `market_regime_rules` JSON field allows the application of regime-specific overrides (e.g., dynamically altering beta-weighting during a bearish regime).
