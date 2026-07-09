import logging
from typing import Dict, Any, List

from market_data.orchestrator.priority_engine import PriorityEngine, PriorityLevel
from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EventTriggerEngine:
    """
    Detects intraday events (e.g. Volume Spike) and triggers priority bumps.
    """
    
    def __init__(self, priority_engine: PriorityEngine, config_manager: ConfigManager):
        self.priority_engine = priority_engine
        self.config = config_manager.get_config("market_data")
        self.events_config = self.config.get("events", {})
        
        self.event_log: List[Dict[str, Any]] = []

    def process_tick(self, symbol: str, current_price: float, current_vol: int, previous_metrics: Dict[str, float]):
        """
        Takes a new tick and historical context, checks for events.
        """
        if not previous_metrics:
            return
            
        avg_vol = previous_metrics.get('Vol_SMA_20', 1)
        prev_close = previous_metrics.get('Close', current_price)
        
        # Very rough estimation of relative volume intraday
        # In reality, needs time-of-day adjusted volume profile
        current_rel_vol = current_vol / max(1, avg_vol)
        
        pct_change = (current_price - prev_close) / prev_close
        
        events = []
        
        # 1. Volume Explosion
        vol_threshold = self.events_config.get("volume_spike_multiplier", 3.0)
        if current_rel_vol > vol_threshold:
            events.append("VOLUME_EXPLOSION")
            
        # 2. Large Move
        if abs(pct_change) > 0.04:
            events.append("LARGE_MOVE")
            
        if events:
            for event in events:
                logger.info(f"EVENT: {event} triggered for {symbol}")
                self.event_log.append({
                    "symbol": symbol,
                    "event": event,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                })
                
            # Bump priority instantly
            self.priority_engine.set_priority(symbol, PriorityLevel.CRITICAL)
