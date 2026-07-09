from typing import Optional, Dict, Any
from datetime import date
from pydantic import BaseModel, Field

class SymbolMaster(BaseModel):
    """
    Represents the canonical metadata for an equity symbol in the universe.
    """
    symbol: str = Field(..., description="The stock symbol (e.g., RELIANCE)")
    isin: Optional[str] = Field(None, description="The ISIN code for the equity")
    company_name: Optional[str] = Field(None, description="Full name of the company")
    listing_date: Optional[date] = Field(None, description="Date the equity was listed")
    delisting_date: Optional[date] = Field(None, description="Date the equity was delisted, if applicable")
    sector: Optional[str] = Field(None, description="GICS or NSE sector classification")
    industry: Optional[str] = Field(None, description="Industry classification")
    market_cap_cr: Optional[float] = Field(None, description="Market capitalization in Crores")
    status: str = Field("ACTIVE", description="ACTIVE, DELISTED, or SUSPENDED")

    def is_active(self) -> bool:
        return self.status.upper() == "ACTIVE"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
