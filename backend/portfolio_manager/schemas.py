from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from portfolio_manager.models import PortfolioStatus, TransactionType

class TransactionBase(BaseModel):
    symbol: str
    transaction_type: TransactionType
    quantity: float
    price: float
    charges: Optional[float] = 0.0
    taxes: Optional[float] = 0.0
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    portfolio_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    name: str
    currency: Optional[str] = "INR"
    base_capital: Optional[float] = 0.0
    investment_objective: Optional[str] = None
    benchmark_index: Optional[str] = "NIFTY50"

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: int
    created_date: datetime
    last_updated: datetime
    status: PortfolioStatus
    user_id: str

    class Config:
        from_attributes = True

class HoldingResponse(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    exchange: str = "NSE"
    quantity: float
    average_buy_price: float
    total_invested: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pct: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    portfolio_weight: Optional[float] = None
    last_updated: Optional[datetime] = None

class PortfolioSummaryResponse(BaseModel):
    portfolio_id: int
    total_portfolio_value: float
    total_invested: float
    cash_balance: float
    unrealized_pnl: float
    unrealized_pct: float
    realized_pnl: float
    today_pnl: Optional[float] = None
    today_pct: Optional[float] = None
    number_of_holdings: int
    health_score: Optional[float] = None
    risk_score: Optional[float] = None
    diversification_score: Optional[float] = None
