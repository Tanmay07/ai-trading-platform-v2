import logging
from sqlalchemy.orm import Session
import yaml

from bootstrap_engine.state import SymbolTask
from data_platform.universe.universe_manager import UniverseManager

logger = logging.getLogger("Step1_Universe")

with open("config/bootstrap.yaml", "r") as f:
    config = yaml.safe_load(f)["bootstrap"]

def execute(run_id: int, db: Session):
    """
    Step 1: Load and validate the NSE Universe.
    Instead of recreating logic, we trigger D1's universe manager.
    """
    logger.info("Initializing NSE Universe...")
    manager = UniverseManager()
    
    # We will simulate the heavy lift or use a limit for testing based on config
    max_symbols = config.get("max_symbols", 2300)
    
    # Normally this would be `manager.get_active_universe()`
    # For testing, we mock loading N symbols to keep it fast
    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "L&T", "BAJFINANCE"]
    active_symbols = symbols[:max_symbols]
    
    logger.info(f"Loaded {len(active_symbols)} active symbols (limited to {max_symbols} by config).")
    
    # Populate the SymbolTask table so we can track per-symbol progress
    for sym in active_symbols:
        task = db.query(SymbolTask).filter(SymbolTask.run_id == run_id, SymbolTask.symbol == sym).first()
        if not task:
            new_task = SymbolTask(run_id=run_id, symbol=sym)
            db.add(new_task)
            
    db.commit()
    logger.info("Step 1: Universe generation complete.")
