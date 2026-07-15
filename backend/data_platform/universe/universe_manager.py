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
        Detects new listings, delistings, and updates metadata using Bhavcopy.
        """
        logger.info("Refreshing NSE universe using latest Bhavcopy...")
        
        if not self.db:
            logger.error("Cannot refresh universe without database connection.")
            return

        try:
            from jugaad_data.nse import bhavcopy_save
            import pandas as pd
            import os
            from datetime import date, timedelta

            dest_dir = "data/temp_bhavcopy"
            os.makedirs(dest_dir, exist_ok=True)
            
            # Step backward up to 7 days to find a valid Bhavcopy
            target_date = date.today()
            valid_bhavcopy_path = None
            
            for _ in range(7):
                if target_date.weekday() < 5: # 0-4 are Mon-Fri
                    try:
                        file_path = bhavcopy_save(target_date, dest_dir)
                        # Check if it's actually a CSV and not a 404 HTML page
                        with open(file_path, 'r') as f:
                            header = f.read(20)
                            if "<html" not in header.lower() and "<!doctype" not in header.lower():
                                valid_bhavcopy_path = file_path
                                break
                    except Exception as e:
                        pass
                target_date -= timedelta(days=1)
                
            if not valid_bhavcopy_path:
                logger.error("Could not find a valid Bhavcopy in the last 7 days.")
                return
                
            # Read CSV
            df = pd.read_csv(valid_bhavcopy_path)
            
            # The new NSE Bhavcopy uses 'SctySrs' for Series and 'TckrSymb' for Symbol
            if 'SctySrs' in df.columns and 'TckrSymb' in df.columns:
                eq_df = df[df['SctySrs'] == 'EQ']
                symbols = eq_df['TckrSymb'].unique()
            else:
                # Fallback to old format just in case
                eq_df = df[df['SERIES'] == 'EQ']
                symbols = eq_df['SYMBOL'].unique()
            
            added_count = 0
            for symbol in symbols:
                # Add to DB
                master = SymbolMaster(
                    symbol=symbol,
                    company_name=f"{symbol} Limited", # Bhavcopy doesn't have company name
                    sector="Unknown" # Sector mapping can be done via another source later
                )
                self.db.upsert_symbol(master)
                added_count += 1
                
            logger.info(f"Universe refresh completed. {added_count} symbols loaded from Bhavcopy.")
            
        except Exception as e:
            logger.error(f"Failed to refresh universe: {e}")

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
