import logging
from typing import List, Dict, Optional
from datetime import datetime

from data_platform.universe.symbol_master import SymbolMaster
from data_platform.universe.symbol_validator import SymbolValidator

logger = logging.getLogger(__name__)

class UniverseManager:
    """
    Manages the complete NSE equity universe.
    In a real implementation, this would fetch from NSE website (e.g., nseindia.com/api/equity-stock)
    and sync with the local metadata database.
    """
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        
    def fetch_active_universe(self) -> List[SymbolMaster]:
        """
        Fetches the active universe of symbols.
        For Phase D1 bootstrap, if DB is empty, this returns a default seed list.
        """
        if self.db:
            # Query DB for all active symbols
            active_symbols = self.db.get_active_symbols()
            if active_symbols:
                return active_symbols

        logger.info("Database empty or not provided. Returning seed universe.")
        return self._get_seed_universe()

    def add_symbol(self, symbol_data: dict) -> Optional[SymbolMaster]:
        """
        Validates and adds a new symbol to the universe.
        """
        symbol = symbol_data.get('symbol')
        if not SymbolValidator.validate_nse_symbol(symbol):
            logger.error(f"Invalid symbol format: {symbol}")
            return None
            
        isin = symbol_data.get('isin')
        if isin and not SymbolValidator.validate_isin(isin):
            logger.error(f"Invalid ISIN format: {isin}")
            return None
            
        master = SymbolMaster(**symbol_data)
        
        if self.db:
            self.db.upsert_symbol(master)
            
        logger.info(f"Added/Updated symbol: {master.symbol}")
        return master

    def refresh_universe(self):
        """
        Detects new listings, delistings, and updates metadata.
        """
        logger.info("Refreshing NSE universe...")
        # TODO: Implement actual NSE API fetching here
        # E.g., download equity list CSV, parse, and compare with DB
        logger.info("Universe refresh completed.")

    def _get_seed_universe(self) -> List[SymbolMaster]:
        """Returns a basic list of Nifty 50 + Midcap 150 for initial testing."""
        seed_data = [
            {"symbol": "RELIANCE", "company_name": "Reliance Industries Limited", "sector": "Energy"},
            {"symbol": "TCS", "company_name": "Tata Consultancy Services Limited", "sector": "Information Technology"},
            {"symbol": "HDFCBANK", "company_name": "HDFC Bank Limited", "sector": "Financials"},
            {"symbol": "INFY", "company_name": "Infosys Limited", "sector": "Information Technology"},
            {"symbol": "ICICIBANK", "company_name": "ICICI Bank Limited", "sector": "Financials"},
            {"symbol": "BEL", "company_name": "Bharat Electronics Limited", "sector": "Industrials"},
        ]
        return [SymbolMaster(**data) for data in seed_data]
