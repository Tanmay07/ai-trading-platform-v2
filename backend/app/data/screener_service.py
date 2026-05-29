import asyncio
from typing import Any, Dict, List

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Pre-categorized top Nifty stocks by Sector for instant loading without yf.info overhead
SECTOR_MAP = {
    "Technology": [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"
    ],
    "Financial Services": [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS",
        "BAJFINANCE.NS", "BAJAJFINSV.NS"
    ],
    "Energy": [
        "RELIANCE.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "COALINDIA.NS"
    ],
    "Consumer Defensive": [
        "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"
    ],
    "Automobiles": [
        "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"
    ],
    "Basic Materials": [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "ADANIENT.NS"
    ],
    "Healthcare": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"
    ],
    "Industrials": [
        "LT.NS", "ULTRACEMCO.NS", "GRASIM.NS", "ADANIPORTS.NS"
    ],
    "Communication Services": [
        "BHARTIARTL.NS"
    ],
    "Consumer Cyclical": [
        "ASIANPAINT.NS", "TITAN.NS"
    ]
}

class ScreenerService:
    """Service to fetch and categorize stocks by sector."""
    
    def __init__(self):
        self._sector_cache = SECTOR_MAP
        
    async def get_sectors(self) -> Dict[str, List[str]]:
        """Returns the sector groupings for the universe."""
        return self._sector_cache
