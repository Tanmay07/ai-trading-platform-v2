from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DecisionCategory(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY_MORE = "Buy More"
    ACCUMULATE = "Accumulate"
    HOLD = "Hold"
    WATCH_CLOSELY = "Watch Closely"
    TRIM_POSITION = "Trim Position"
    BOOK_PARTIAL_PROFIT = "Book Partial Profit"
    SELL = "Sell"
    EXIT_IMMEDIATELY = "Exit Immediately"

class RecommendationObject(BaseModel):
    symbol: str
    decision: DecisionCategory
    confidence: float = Field(..., ge=0.0, le=100.0)
    target_price_1: float
    target_price_2: float
    stop_loss: float
    expected_holding_period: str
    expected_cagr: float
    risk_level: str
    position_size_recommendation: float # Percentage
    last_review: datetime
    next_review_trigger: str
    
    technical_score: float = Field(0.0, ge=0.0, le=100.0)
    valuation_score: float = Field(0.0, ge=0.0, le=100.0)
    portfolio_context_score: float = Field(0.0, ge=0.0, le=100.0)
    risk_score: float = Field(0.0, ge=0.0, le=100.0)
    
    explanation_why: str
    explanation_why_now: str
    explanation_metrics_changed: str
    explanation_supports_view: str
    explanation_risks: str
    explanation_invalidation: str
