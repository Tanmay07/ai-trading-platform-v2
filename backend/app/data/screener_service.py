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

from app.data.s3_service import S3StorageService
from app.data.universe_fetcher import UniverseFetcherService

class ScreenerService:
    """Service to fetch and categorize stocks by sector."""
    
    def __init__(self):
        self.s3_service = S3StorageService()
        self.universe_fetcher = UniverseFetcherService()
        self.cache_key = "universe_sectors.json"
        
    async def get_sectors(self) -> Dict[str, List[str]]:
        """Returns the sector groupings for the universe."""
        # Try to fetch from S3 cache
        loop = asyncio.get_running_loop()
        
        try:
            cached_data = await loop.run_in_executor(
                None, self.s3_service.download_json, self.cache_key
            )
            if cached_data:
                logger.info("Loaded sector universe from S3 cache")
                return cached_data
        except Exception as exc:
            logger.warning("Failed to load universe cache from S3: %s", exc)
            
        # If cache miss, try to scrape it
        try:
            logger.info("S3 cache missing. Scraping NIFTY 50 universe...")
            scraped_data = await loop.run_in_executor(
                None, self.universe_fetcher.refresh_universe_cache
            )
            return scraped_data
        except Exception as exc:
            logger.error("Failed to scrape universe, falling back to static map: %s", exc)
            return SECTOR_MAP
