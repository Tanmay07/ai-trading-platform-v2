import logging
from typing import List, Dict, Any

from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SmartFilter:
    """Evaluates metrics to decide if a stock enters the Candidate Queue."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("market_data")
        self.thresholds = self.config.get("candidate_thresholds", {})
        
        self.candidate_queue: List[str] = []
        self.max_candidates = self.thresholds.get("max_candidates", 500)
        
    def evaluate(self, symbol: str, current_data: Dict[str, Any], historical_context: Dict[str, Any]):
        """
        Runs lightweight rules. If passed, adds to queue.
        Uses historical context (from Feature Store) and current data.
        """
        if not historical_context:
            return False
            
        current_price = current_data.get('price', 0)
        current_vol = current_data.get('volume', 0)
        
        avg_vol = historical_context.get('Vol_SMA_20', 1)
        prev_close = historical_context.get('Close', current_price)
        ema20 = historical_context.get('EMA_20', current_price)
        
        # Calculate live metrics
        rel_vol = current_vol / max(1, avg_vol)
        gap_pct = (current_data.get('open', current_price) - prev_close) / prev_close
        
        dist_ema20 = (current_price - ema20) / ema20
        
        # Check Rules (Example: Configurable thresholds)
        t_rel_vol = self.thresholds.get("relative_volume", 1.5)
        t_gap = self.thresholds.get("gap_pct", 0.02)
        t_dist_ema = self.thresholds.get("breakout_proximity_pct", 0.03) # Repurposing for proximity
        
        passes = False
        if rel_vol > t_rel_vol:
            passes = True
        elif abs(gap_pct) > t_gap:
            passes = True
        elif abs(dist_ema20) < t_dist_ema:
            passes = True
            
        if passes:
            if symbol not in self.candidate_queue:
                self.candidate_queue.append(symbol)
                logger.debug(f"{symbol} added to Candidate Queue.")
        else:
            if symbol in self.candidate_queue:
                self.candidate_queue.remove(symbol)
                
        # Trim queue if too large
        if len(self.candidate_queue) > self.max_candidates:
            # We could trim based on a score, but for now just FIFO
            self.candidate_queue.pop(0)
            
        return passes
        
    def get_candidates(self) -> List[str]:
        return self.candidate_queue.copy()
