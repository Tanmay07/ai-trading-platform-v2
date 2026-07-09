# Phase 2: Professional Technical Analysis & Institutional Breakout Intelligence

## Overview
Phase 2 extends the AI Trading Platform with institutional-grade technical analysis capabilities. 
It analyzes candidate stocks passed by Phase 1 to produce a 0-100 `Breakout Score`, which is derived from multiple technical indicators and multi-timeframe confirmation.

## Key Components

1. **Multi-Timeframe Engine**: Analyzes Weekly, Daily, 4H, and 1H trends to ensure structural alignment before a breakout.
2. **Relative Strength Engine**: Computes RS over 20 and 50 days against both the Nifty 50 and the stock's Sector Index.
3. **Sector Rotation Engine**: Pre-calculates momentum and RS for all sectors to produce a Sector Rank. Candidates from top-ranked sectors receive a score boost.
4. **Breakout Pattern Engine**: Detects institutional setups like VCP, Darvas Box, and Inside Bars.
5. **Price Action Engine**: Analyzes bare candlestick patterns and HH/HL structures.
6. **VWAP Engine**: Evaluates price relative to Daily VWAP and Anchored VWAP (from recent swing lows).
7. **Support & Resistance Engine**: Maps horizontal levels and distances to support.
8. **Breakout Score Engine**: Aggregates all engine outputs into a final percentage score using weights defined in `config/technical.yaml`.
9. **Technical Orchestrator**: Uses `yfinance.download(..., threads=True)` to concurrently bulk download Weekly, Daily, and Intraday data for all candidates at once. This avoids redundant network requests and ensures the Nifty 500 can be processed under 20 seconds.

## API Usage
`GET /api/technical-analysis?symbol=RELIANCE.NS&sector=Energy`

Returns the complete technical suite for a single symbol.

## Architecture & Integration
The `TechnicalOrchestrator` runs *after* the Phase 1 filtering inside `app/recommendations/orchestrator.py`. 
Only candidates that pass Phase 1 risk and confidence checks are passed to Phase 2 for technical scoring. The final result set is sorted by the new `Breakout Score`.
