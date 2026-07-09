# Phase 12: Hedge Fund Operating System (HFOS)

## Overview
Phase 12 is the final layer of the AI Trading Platform, elevating it into a comprehensive Autonomous Hedge Fund Operating System (HFOS). This tier sits above all underlying systems (Research, Execution, Portfolio, MLOps) and acts as the C-Suite governance layer.

## The AI Investment Committee
The `InvestmentCommittee` orchestrates a group of simulated AI Directors (e.g. Technical Director, Macro Director, Risk Director). 
Every trade must pass this committee. For a trade to be approved, a majority of directors (configurable in `hfos.yaml`) must cast a `BUY` vote based on their localized context.

## Capital & Strategy Allocation
Rather than treating the platform as a single pool of money, the `CapitalAllocator` dynamically bounds the maximum capital any individual strategy (e.g., Mean Reversion vs Breakout) can access, based on overarching market regimes. The `PortfolioAllocator` then breaks down that block order into individual client accounts.

## Governance & Compliance
This is a Human-in-the-Loop system.
- **`ComplianceEngine`**: Enforces strict pre-trade checks (e.g. blocking restricted stocks).
- **`StrategyGovernance`**: Ensures no AI-discovered strategy (from Phase 11) is ever promoted to live trading without an explicit API call by a human administrator (`/api/hfos/approve`).
- **`RiskGovernance`**: Monitors global limits and contains the master Kill Switch.

## Operations
The `CommandCenter` and `ReportingCenter` synthesize data across all 11 underlying phases into a unified health dashboard and daily CIO reports, exposing endpoints like `/api/hfos/dashboard`.
