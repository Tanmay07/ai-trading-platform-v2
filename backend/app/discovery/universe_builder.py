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
        import json
        from pathlib import Path
        
        self.logger.info(f"Building dynamic universe of top {limit} liquid stocks from Bhavcopy...")
        universe = self.bhavcopy_service.get_top_liquid_stocks(limit=limit)
        
        # Ensure specific user-requested stocks are always included in the scan
        custom_watchlist = []
        
        # Also include portfolio stocks so they are always evaluated
        portfolio_file = Path(__file__).resolve().parent.parent.parent / "portfolio_data.json"
        if portfolio_file.exists():
            try:
                with open(portfolio_file, "r") as f:
                    portfolio_data = json.load(f)
                    for item in portfolio_data:
                        symbol = item.get("symbol")
                        # Add suffix if missing
                        if symbol and not symbol.endswith(".BO") and not symbol.endswith(".NS") and "BEES" not in symbol and "CASE" not in symbol:
                            symbol += ".NS"
                        if symbol and symbol not in custom_watchlist:
                            custom_watchlist.append(symbol)
            except Exception as e:
                self.logger.error(f"Failed to load portfolio stocks into universe: {e}")
                
        for stock in custom_watchlist:
            if stock not in universe:
                universe.append(stock)
                
        self.logger.info(f"Final universe size: {len(universe)}")
        return universe
