from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from portfolio_manager.database import Base

class PortfolioStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    BONUS = "BONUS"
    SPLIT = "SPLIT"
    DIVIDEND = "DIVIDEND"
    RIGHTS = "RIGHTS"
    MERGER = "MERGER"
    DEMERGER = "DEMERGER"

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    currency = Column(String, default="INR")
    base_capital = Column(Float, default=0.0)
    created_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    investment_objective = Column(String, nullable=True)
    benchmark_index = Column(String, default="NIFTY50")
    status = Column(Enum(PortfolioStatus), default=PortfolioStatus.ACTIVE)
    user_id = Column(String, index=True) # For multi-tenant RBAC

    transactions = relationship("Transaction", back_populates="portfolio")
    snapshots = relationship("PortfolioSnapshot", back_populates="portfolio")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    transaction_type = Column(Enum(TransactionType))
    quantity = Column(Float)
    price = Column(Float)
    charges = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    portfolio = relationship("Portfolio", back_populates="transactions")


class PortfolioSnapshot(Base):
    """Daily End-of-Day (EOD) snapshots for timeline."""
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    date = Column(DateTime, default=datetime.utcnow)
    total_value = Column(Float)
    invested_value = Column(Float)
    cash_balance = Column(Float)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float)
    daily_return_pct = Column(Float)
    risk_score = Column(Float, nullable=True)
    health_score = Column(Float, nullable=True)

    portfolio = relationship("Portfolio", back_populates="snapshots")
