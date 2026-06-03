"""
Universe Builder

Defines the dynamic stock universe for the Discovery Engine by leveraging
the NSE Bhavcopy to identify highly liquid stocks.
"""

from typing import List
from app.utils.logger import get_logger
from app.discovery.bhavcopy_service import BhavcopyService

logger = get_logger(__name__)

class UniverseBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.bhavcopy_service = BhavcopyService()

    def get_scan_universe(self, limit: int = 150) -> List[str]:
        """
        Returns the list of NSE symbols that the Discovery Engine should scan.
        Fetches the top highly-liquid equities from today's Bhavcopy to act
        as a dynamic funnel, avoiding Yahoo Finance rate limits while covering
        the most active part of the 2000-stock universe.
        """
        self.logger.info(f"Building dynamic universe of top {limit} liquid stocks from Bhavcopy...")
        return self.bhavcopy_service.get_top_liquid_stocks(limit=limit)
