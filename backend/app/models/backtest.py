"""
Backtest ORM Models

Defines BacktestRun and BacktestTrade tables.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class BacktestRun(Base):
    """Stores metadata and results of a single backtest run."""

    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Float, nullable=False, default=100_000.0)
    final_capital = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship to individual trades
    trades = relationship("BacktestTrade", back_populates="backtest_run")

    def __repr__(self) -> str:
        return (
            f"<BacktestRun(strategy={self.strategy_name!r}, "
            f"return={self.total_return})>"
        )


class BacktestTrade(Base):
    """Records a single trade executed during a backtest."""

    __tablename__ = "backtest_trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(4), nullable=False)  # BUY or SELL
    entry_date = Column(Date, nullable=True)
    entry_price = Column(Float, nullable=True)
    exit_date = Column(Date, nullable=True)
    exit_price = Column(Float, nullable=True)
    return_pct = Column(Float, nullable=True)
    holding_days = Column(Integer, nullable=True)

    backtest_run = relationship("BacktestRun", back_populates="trades")

    def __repr__(self) -> str:
        return (
            f"<BacktestTrade(symbol={self.symbol!r}, "
            f"action={self.action!r}, return={self.return_pct})>"
        )
