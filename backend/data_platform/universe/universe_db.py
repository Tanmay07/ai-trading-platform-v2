import sqlite3
import logging
from typing import List, Optional
from data_platform.universe.symbol_master import SymbolMaster
import os

logger = logging.getLogger(__name__)

class UniverseDB:
    def __init__(self, db_path: str = "ai_trading_universe.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), f"../../../{db_path}")
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    symbol TEXT PRIMARY KEY,
                    company_name TEXT,
                    sector TEXT,
                    is_active INTEGER,
                    isin TEXT,
                    listing_date TEXT
                )
            """)
            conn.commit()
            
    def upsert_symbol(self, master: SymbolMaster):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO symbols 
                (symbol, company_name, sector, is_active, isin, listing_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                master.symbol,
                master.company_name,
                master.sector,
                1 if master.is_active else 0,
                master.isin,
                master.listing_date.isoformat() if master.listing_date else None
            ))
            conn.commit()
            
    def get_active_symbols(self) -> List[SymbolMaster]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM symbols WHERE is_active = 1").fetchall()
            return [
                SymbolMaster(
                    symbol=r["symbol"],
                    company_name=r["company_name"],
                    sector=r["sector"],
                    is_active=bool(r["is_active"]),
                    isin=r["isin"]
                )
                for r in rows
            ]
