"""
Portfolio Service — manages holdings, calculates P&L, and records transactions.

Migrated to AWS S3 Data Lake (Phase 7).

This is for educational and research purposes only, not financial advice.
"""

from __future__ import annotations

from typing import Any, List, Dict
import datetime

from app.data.market_data_service import MarketDataService
from app.data.s3_service import S3StorageService
from app.utils.helpers import DISCLAIMER, get_ist_now, validate_symbol
from app.utils.logger import get_logger

PORTFOLIO_KEY = "portfolio/holdings.json"
TRANSACTIONS_KEY = "portfolio/transactions.json"

class PortfolioService:
    """Manages portfolio holdings and calculates P&L using S3."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.market_data = MarketDataService()
        self.s3 = S3StorageService()

    def _load_holdings(self) -> Dict[str, dict]:
        data = self.s3.download_json(PORTFOLIO_KEY)
        if not data:
            return {}
        # Expected format: { "RELIANCE.NS": { "symbol": "RELIANCE.NS", "quantity": 10, "avg_buy_price": 100 } }
        return data

    def _save_holdings(self, holdings: Dict[str, dict]) -> None:
        self.s3.upload_json(PORTFOLIO_KEY, holdings)

    def _load_transactions(self) -> List[dict]:
        data = self.s3.download_json(TRANSACTIONS_KEY)
        return data if data else []

    def _save_transactions(self, transactions: List[dict]) -> None:
        self.s3.upload_json(TRANSACTIONS_KEY, transactions)

    def add_holding(
        self,
        symbol: str,
        quantity: int,
        buy_price: float,
        sector: str | None = None,
        notes: str | None = None,
    ) -> dict:
        symbol = validate_symbol(symbol)

        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if buy_price <= 0:
            raise ValueError("Buy price must be positive.")

        holdings = self._load_holdings()
        
        if symbol in holdings:
            existing = holdings[symbol]
            total_cost = (existing["avg_buy_price"] * existing["quantity"]) + (buy_price * quantity)
            new_qty = existing["quantity"] + quantity
            existing["avg_buy_price"] = round(total_cost / new_qty, 2)
            existing["quantity"] = new_qty
            existing["updated_at"] = get_ist_now().isoformat()
            if sector:
                existing["sector"] = sector
            if notes:
                existing["notes"] = notes
            holding = existing
        else:
            holding = {
                "symbol": symbol,
                "quantity": quantity,
                "avg_buy_price": round(buy_price, 2),
                "sector": sector,
                "notes": notes,
                "added_at": get_ist_now().isoformat(),
                "updated_at": get_ist_now().isoformat(),
            }
            holdings[symbol] = holding

        self._save_holdings(holdings)
        self.record_transaction(symbol, "BUY", quantity, buy_price, notes)
        return holding

    def update_holding(
        self,
        symbol: str,
        quantity: int,
        buy_price: float,
        sector: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Update a holding by explicitly setting its quantity and average buy price.
        
        This overrides the existing values rather than computing a weighted average.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if buy_price <= 0:
            raise ValueError("Buy price must be positive.")

        symbol = validate_symbol(symbol)
        holdings = self._load_holdings()

        if symbol not in holdings:
            raise ValueError(f"Holding {symbol} not found in portfolio.")

        existing = holdings[symbol]
        existing["quantity"] = quantity
        existing["avg_buy_price"] = round(buy_price, 2)
        existing["updated_at"] = get_ist_now().isoformat()
        if sector is not None:
            existing["sector"] = sector
        if notes is not None:
            existing["notes"] = notes
            
        self._save_holdings(holdings)
        return existing

    def remove_holding(self, symbol: str) -> bool:
        symbol = validate_symbol(symbol)
        holdings = self._load_holdings()

        if symbol not in holdings:
            return False

        holding = holdings[symbol]
        self.record_transaction(symbol, "SELL", holding["quantity"], holding["avg_buy_price"])
        
        del holdings[symbol]
        self._save_holdings(holdings)
        return True

    def get_holdings(self) -> list[dict]:
        holdings = self._load_holdings()
        return list(holdings.values())

    def get_holding(self, symbol: str) -> dict | None:
        symbol = validate_symbol(symbol)
        holdings = self._load_holdings()
        return holdings.get(symbol)

    def get_portfolio_summary(self) -> dict[str, Any]:
        holdings_list = self.get_holdings()

        if not holdings_list:
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

        for h in holdings_list:
            invested = h["avg_buy_price"] * h["quantity"]
            total_invested += invested

            try:
                price_data = self.market_data.get_current_price(h["symbol"])
                current_price = price_data.get("price", h["avg_buy_price"])
            except Exception:
                current_price = h["avg_buy_price"]

            market_value = current_price * h["quantity"]
            total_market_value += market_value

            unrealized_pnl = market_value - invested
            unrealized_pnl_pct = (unrealized_pnl / invested * 100) if invested > 0 else 0.0

            enriched.append(
                {
                    "symbol": h["symbol"],
                    "quantity": h["quantity"],
                    "avg_buy_price": round(h["avg_buy_price"], 2),
                    "current_price": round(current_price, 2),
                    "market_value": round(market_value, 2),
                    "unrealized_pnl": round(unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
                    "sector": h.get("sector") or "N/A",
                }
            )

        total_unrealized_pnl = total_market_value - total_invested
        total_unrealized_pnl_pct = (total_unrealized_pnl / total_invested * 100) if total_invested > 0 else 0.0

        return {
            "holdings": enriched,
            "total_invested": round(total_invested, 2),
            "total_market_value": round(total_market_value, 2),
            "total_unrealized_pnl": round(total_unrealized_pnl, 2),
            "total_unrealized_pnl_pct": round(total_unrealized_pnl_pct, 2),
            "holdings_count": len(enriched),
            "disclaimer": DISCLAIMER,
        }

    def record_transaction(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        notes: str | None = None,
    ) -> dict:
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise ValueError(f"Invalid action '{action}'; must be BUY or SELL.")

        txn = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": round(price, 2),
            "timestamp": get_ist_now().isoformat(),
            "notes": notes,
        }
        transactions = self._load_transactions()
        transactions.append(txn)
        self._save_transactions(transactions)
        return txn
