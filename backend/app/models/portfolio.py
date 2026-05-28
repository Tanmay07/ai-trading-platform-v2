"""
Portfolio ORM Models

Defines PortfolioHolding and Transaction tables.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class PortfolioHolding(Base):
    """Represents a stock holding in the paper-trading portfolio."""

    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    avg_buy_price = Column(Float, nullable=False, default=0.0)
    added_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sector = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PortfolioHolding(symbol={self.symbol!r}, qty={self.quantity})>"


class Transaction(Base):
    """Represents a BUY or SELL transaction."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    action = Column(String(4), nullable=False)  # BUY or SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction({self.action} {self.quantity}x {self.symbol!r} @ {self.price})>"
