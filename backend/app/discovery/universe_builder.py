"""
Universe Builder

Defines the stock universe for the Discovery Engine.
Handles loading Nifty 50, Nifty Midcap, and the broader NSE universe.
"""

from typing import List
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Hardcoded MVP list for Nifty 50 to prevent Yahoo Finance bans during development
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "ADANIENT.NS", "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS",
    "NTPC.NS", "AXISBANK.NS", "DMART.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ULTRACEMCO.NS", "ASIANPAINT.NS", "COALINDIA.NS", "BAJAJFINSV.NS",
    "BAJAJ-AUTO.NS", "POWERGRID.NS", "NESTLEIND.NS", "WIPRO.NS", "M&M.NS",
    "IOC.NS", "JIOFIN.NS", "HAL.NS", "DLF.NS", "ADANIPOWER.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "SIEMENS.NS", "IRFC.NS", "VBL.NS", "ZOMATO.NS",
    "PIDILITIND.NS", "GRASIM.NS", "SBILIFE.NS", "BEL.NS", "LTIM.NS"
]

class UniverseBuilder:
    def __init__(self):
        self.logger = get_logger(__name__)

    def get_nifty_50(self) -> List[str]:
        """Returns the Nifty 50 constituent symbols."""
        return NIFTY_50

    def get_nifty_500(self) -> List[str]:
        """
        Returns the Nifty 500 constituent symbols.
        For MVP, returns NIFTY 50 to avoid rate limits.
        """
        # TODO: Load from a static CSV or NSE website
        self.logger.warning("get_nifty_500 returning Nifty 50 to prevent rate limits.")
        return self.get_nifty_50()
        
    def get_full_universe(self) -> List[str]:
        """
        Returns the entire NSE tradable universe (2000+ stocks).
        """
        self.logger.warning("get_full_universe returning Nifty 50 to prevent rate limits.")
        return self.get_nifty_50()
