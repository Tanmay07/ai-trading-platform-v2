# Event Platform Architecture

## Overview
The Enterprise Market Intelligence & Event Platform (EMIEP) serves as the "nervous system" of the AI Trading platform. It shifts the architecture from a polling-based model to an Event-Driven Architecture (EDA).

## Components

### 1. Detectors
Detectors are background tasks (or external webhooks) that monitor the market and emit raw domain events.
- **Technical Detector**: Emits `BREAKOUT`, `GOLDEN_CROSS`.
- **Corporate Detector**: Emits `QUARTERLY_RESULTS`, `DIVIDEND`.
- **Macro Detector**: Emits `RBI_POLICY`, `RATE_CUT`.

### 2. Enterprise Market Intelligence Engine
The brain of the platform. It subscribes to all raw events and performs:
- **Deduplication**: Prevents spamming the system with the same event multiple times.
- **Scoring**: Calculates an Impact Score (0-100) based on predefined rules (e.g., Corporate events have a higher base score).
- **Prioritization**: Categorizes events into `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `IGNORE`.
- **Correlation**: Associates multiple related events on the same symbol to generate a unified narrative.

### 3. Event Bus
An asynchronous internal Pub/Sub bus built on `asyncio.Queue`. 
Downstream modules subscribe to the Event Bus using `event_bus.subscribe('*', callback)`.

### 4. Downstream Consumers
- **DecisionEventHandler**: Recalculates the investment recommendation for any holding affected by a `HIGH` or `CRITICAL` event.
- **SmartAlertsHandler**: Generates deduplicated user alerts in the database.
- **WatchlistService**: Allows watchlists to naturally inherit market events.
- **CalendarEngine**: Tracks upcoming scheduled events.

## Data Persistence
Events are persisted to `market_events` and correlations to `event_correlations` in `policy_engine.db` (mocked as `event_engine.db` for separation of concerns initially, eventually unifying). 
This acts as the Event Sourcing truth and provides an audit timeline for AI Copilot usage.
