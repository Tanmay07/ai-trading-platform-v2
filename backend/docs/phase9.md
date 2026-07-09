# Phase 9: Live Trading Platform & Execution Management System

## Overview
Phase 9 transitions the platform from a theoretical paper-trading research engine into a true Live Trading Platform. It achieves this by introducing an Execution Management System (EMS) and a strict Broker Abstraction Layer.

## Broker Abstraction Layer
The AI no longer cares who executes the trade.
- **`BaseBroker`**: A common interface demanding `login()`, `get_funds()`, `place_order()`, `get_positions()`, and `cancel_order()`.
- **`PaperAdapter`**: The default MVP broker. It simulates successful fills and maintains local state without risking actual capital.
- **Stubbed Adapters**: Prepared classes for `Zerodha`, `Upstox`, `AngelOne`, and `ICICI` that can be implemented as the user chooses.

## Execution Core
1. **`ExecutionValidator`**: The final safety net. Before any order is sent to a broker, this engine verifies that the `kill_switch_active` is False, there is sufficient capital, and `max_open_trades` has not been exceeded.
2. **`ExecutionManager`**: Responsible for routing the validated order to the configured `BrokerFactory` instance.
3. **`ExecutionAudit`**: Logs every API request/response and order state change immutably for compliance.
4. **`AccountManager`**: Abstracts the underlying broker funds payload into a standardized JSON response format.

## APIs
The `/api/execution` sub-router exposes:
- `GET /api/execution/account`: Returns a unified account summary regardless of the active broker.
- `GET /api/execution/positions`: Retrieves current open positions from the active broker.
- `POST /api/execution/order/test`: A developer testing endpoint to mock sending a generated AI recommendation straight through the execution pipeline.
