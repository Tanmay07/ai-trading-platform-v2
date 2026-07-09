import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MarketReplayEngine:
    """
    Archives intraday snapshots (quotes, candidate queue, events) 
    so the market can be perfectly replayed for walk-forward validation.
    """
    
    def __init__(self, base_path: str = "data/market_replay"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _get_daily_dir(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = self.base_path / today
        daily_dir.mkdir(exist_ok=True)
        return daily_dir
        
    def archive_snapshot(self, snapshot_type: str, data: Any):
        """
        Saves a snapshot to disk.
        Types: 'quotes', 'candidates', 'events', 'priorities'
        """
        try:
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{timestamp}_{snapshot_type}.json"
            filepath = self._get_daily_dir() / filename
            
            with open(filepath, "w") as f:
                json.dump(data, f)
                
            logger.debug(f"Archived {snapshot_type} snapshot to {filepath}")
        except Exception as e:
            logger.error(f"Failed to archive snapshot: {e}")
            
    def get_snapshots_for_day(self, date_str: str, snapshot_type: str) -> List[str]:
        """Lists available snapshots for a given day."""
        daily_dir = self.base_path / date_str
        if not daily_dir.exists():
            return []
            
        files = list(daily_dir.glob(f"*_{snapshot_type}.json"))
        return [str(f) for f in sorted(files)]
