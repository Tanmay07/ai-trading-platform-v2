from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date as dt_date

class MarketQuote(BaseModel):
    """Normalized live/latest market quote."""
    symbol: str = Field(..., description="Trading symbol")
    exchange: str = Field(default="NSE", description="Exchange name")
    timestamp: datetime = Field(..., description="Timestamp of the quote")
    open: float = Field(..., description="Open price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Current/Close price")
    previous_close: float = Field(..., description="Previous close price")
    last_price: float = Field(..., description="Last traded price")
    volume: int = Field(..., description="Trading volume")
    vwap: Optional[float] = Field(None, description="Volume Weighted Average Price")
    upper_circuit: Optional[float] = Field(None, description="Upper circuit limit")
    lower_circuit: Optional[float] = Field(None, description="Lower circuit limit")
    week_52_high: Optional[float] = Field(None, description="52 Week High")
    week_52_low: Optional[float] = Field(None, description="52 Week Low")
    validation_score: Optional[int] = Field(100, description="Data quality validation score")

class HistoricalCandle(BaseModel):
    """Normalized historical OHLCV data."""
    date: dt_date = Field(..., description="Trading date")
    open: float
    high: float
    low: float
    close: float
    adjusted_close: Optional[float] = None
    volume: int

class CorporateAction(BaseModel):
    """Corporate actions like Dividends, Splits."""
    symbol: str
    ex_date: dt_date
    purpose: str
    record_date: Optional[dt_date] = None

class MarketStatus(BaseModel):
    """Current status of the exchange."""
    exchange: str = "NSE"
    status: str = Field(..., description="Pre Open, Open, Close, Holiday, Weekend")
    timestamp: datetime
    message: Optional[str] = None
    
class IndexData(BaseModel):
    """Normalized index data."""
    index_name: str
    current_value: float
    open: float
    high: float
    low: float
    previous_close: float
    percent_change: float
