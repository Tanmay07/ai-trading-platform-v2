"""
Portfolio Service — manages holdings, calculates P&L, and records transactions.

Provides CRUD operations for portfolio holdings and integrates with
:class:`MarketDataService` to compute live market values and unrealized P&L.

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.data.market_data_service import MarketDataService
from app.models.portfolio import PortfolioHolding, Transaction
from app.utils.helpers import DISCLAIMER, get_ist_now, validate_symbol
from app.utils.logger import get_logger


class PortfolioService:
    """Manages portfolio holdings and calculates P&L.

    All database mutations go through this service so that transaction
    history is recorded automatically.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.market_data = MarketDataService()

    # ------------------------------------------------------------------
    # Holdings CRUD
    # ------------------------------------------------------------------

    def add_holding(
        self,
        db: Session,
        symbol: str,
        quantity: int,
        buy_price: float,
        sector: str | None = None,
        notes: str | None = None,
    ) -> PortfolioHolding:
        """Add a new holding or average into an existing one.

        If the symbol already exists the buy price is recalculated as a
        weighted-average and the quantity is incremented.

        Args:
            db: SQLAlchemy session.
            symbol: NSE stock symbol (auto-suffixed with ``.NS``).
            quantity: Number of shares to add (must be > 0).
            buy_price: Purchase price per share.
            sector: Optional sector classification.
            notes: Free-text notes.

        Returns:
            The created or updated :class:`PortfolioHolding` instance.

        Raises:
            ValueError: If *quantity* ≤ 0 or *buy_price* ≤ 0.
        """
        symbol = validate_symbol(symbol)

        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if buy_price <= 0:
            raise ValueError("Buy price must be positive.")

        existing: PortfolioHolding | None = (
            db.query(PortfolioHolding)
            .filter(PortfolioHolding.symbol == symbol)
            .first()
        )

        if existing:
            # Weighted-average price
            total_cost = (existing.avg_buy_price * existing.quantity) + (buy_price * quantity)
            new_qty = existing.quantity + quantity
            existing.avg_buy_price = round(total_cost / new_qty, 2)
            existing.quantity = new_qty
            existing.updated_at = get_ist_now()
            if sector:
                existing.sector = sector
            if notes:
                existing.notes = notes
            holding = existing
            self.logger.info(
                "Updated holding %s: qty=%d avg_price=%.2f",
                symbol,
                new_qty,
                existing.avg_buy_price,
            )
        else:
            holding = PortfolioHolding(
                symbol=symbol,
                quantity=quantity,
                avg_buy_price=round(buy_price, 2),
                sector=sector,
                notes=notes,
                added_at=get_ist_now(),
                updated_at=get_ist_now(),
            )
            db.add(holding)
            self.logger.info(
                "Created holding %s: qty=%d price=%.2f", symbol, quantity, buy_price
            )

        # Record the BUY transaction
        self._record_transaction(db, symbol, "BUY", quantity, buy_price)

        db.commit()
        db.refresh(holding)
        return holding

    def remove_holding(self, db: Session, symbol: str) -> bool:
        """Remove a holding from the portfolio entirely.

        Args:
            db: SQLAlchemy session.
            symbol: NSE stock symbol.

        Returns:
            ``True`` if the holding was found and removed, ``False`` otherwise.
        """
        symbol = validate_symbol(symbol)
        holding: PortfolioHolding | None = (
            db.query(PortfolioHolding)
            .filter(PortfolioHolding.symbol == symbol)
            .first()
        )

        if holding is None:
            self.logger.warning("Holding %s not found — cannot remove.", symbol)
            return False

        # Record a SELL transaction at the current average price (paper-trade)
        self._record_transaction(
            db, symbol, "SELL", holding.quantity, holding.avg_buy_price
        )

        db.delete(holding)
        db.commit()
        self.logger.info("Removed holding %s from portfolio.", symbol)
        return True

    def get_holdings(self, db: Session) -> list[PortfolioHolding]:
        """Retrieve all portfolio holdings.

        Returns:
            List of :class:`PortfolioHolding` instances sorted by symbol.
        """
        return (
            db.query(PortfolioHolding)
            .order_by(PortfolioHolding.symbol)
            .all()
        )

    def get_holding(self, db: Session, symbol: str) -> PortfolioHolding | None:
        """Retrieve a single holding by symbol.

        Returns:
            The matching :class:`PortfolioHolding` or ``None``.
        """
        symbol = validate_symbol(symbol)
        return (
            db.query(PortfolioHolding)
            .filter(PortfolioHolding.symbol == symbol)
            .first()
        )

    # ------------------------------------------------------------------
    # Portfolio Summary with live prices
    # ------------------------------------------------------------------

    def get_portfolio_summary(self, db: Session) -> dict[str, Any]:
        """Compute a full portfolio summary with live market data.

        For each holding the service fetches the current price via
        :class:`MarketDataService` and calculates unrealized P&L.

        Returns:
            A dictionary with:
                - ``holdings``: list of enriched holding dicts.
                - ``total_invested``, ``total_market_value``,
                  ``total_unrealized_pnl``, ``total_unrealized_pnl_pct``.
                - ``holdings_count``.
                - ``disclaimer``.
        """
        holdings: list[PortfolioHolding] = self.get_holdings(db)

        if not holdings:
            return {
                "holdings": [],
                "total_invested": 0.0,
                "total_market_value": 0.0,
                "total_unrealized_pnl": 0.0,
                "total_unrealized_pnl_pct": 0.0,
                "holdings_count": 0,
                "disclaimer": DISCLAIMER,
            }

        enriched: list[dict] = []
        total_invested: float = 0.0
        total_market_value: float = 0.0

        for h in holdings:
            invested = h.avg_buy_price * h.quantity
            total_invested += invested

            # Fetch live price
            try:
                price_data = self.market_data.get_current_price(h.symbol)
                current_price = price_data.get("price", h.avg_buy_price)
            except Exception as exc:
                self.logger.warning(
                    "Could not fetch live price for %s, using buy price: %s",
                    h.symbol,
                    exc,
                )
                current_price = h.avg_buy_price

            market_value = current_price * h.quantity
            total_market_value += market_value

            unrealized_pnl = market_value - invested
            unrealized_pnl_pct = (
                (unrealized_pnl / invested * 100) if invested > 0 else 0.0
            )

            enriched.append(
                {
                    "symbol": h.symbol,
                    "quantity": h.quantity,
                    "avg_buy_price": round(h.avg_buy_price, 2),
                    "current_price": round(current_price, 2),
                    "market_value": round(market_value, 2),
                    "unrealized_pnl": round(unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
                    "sector": h.sector or "N/A",
                }
            )

        total_unrealized_pnl = total_market_value - total_invested
        total_unrealized_pnl_pct = (
            (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else 0.0
        )

        return {
            "holdings": enriched,
            "total_invested": round(total_invested, 2),
            "total_market_value": round(total_market_value, 2),
            "total_unrealized_pnl": round(total_unrealized_pnl, 2),
            "total_unrealized_pnl_pct": round(total_unrealized_pnl_pct, 2),
            "holdings_count": len(enriched),
            "disclaimer": DISCLAIMER,
        }

    # ------------------------------------------------------------------
    # Transaction recording
    # ------------------------------------------------------------------

    def record_transaction(
        self,
        db: Session,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        notes: str | None = None,
    ) -> Transaction:
        """Record an explicit BUY or SELL transaction.

        This is the public API for external callers.  Internal helpers use
        :meth:`_record_transaction` (which does not commit).

        Returns:
            The created :class:`Transaction` instance.
        """
        symbol = validate_symbol(symbol)
        txn = self._record_transaction(db, symbol, action, quantity, price, notes)
        db.commit()
        db.refresh(txn)
        return txn

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _record_transaction(
        self,
        db: Session,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        notes: str | None = None,
    ) -> Transaction:
        """Create a Transaction row without committing (caller manages commit)."""
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise ValueError(f"Invalid action '{action}'; must be BUY or SELL.")

        txn = Transaction(
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=round(price, 2),
            timestamp=get_ist_now(),
            notes=notes,
        )
        db.add(txn)
        self.logger.debug(
            "Recorded %s transaction: %s qty=%d price=%.2f",
            action,
            symbol,
            quantity,
            price,
        )
        return txn
