from enum import Enum
import logging
from typing import Dict, Any

from data_platform.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class PriorityLevel(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    DORMANT = 5

class PriorityEngine:
    """Manages dynamic priority assignment for stocks."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.get_config("market_data")
        self.rules = self.config.get("priority_rules", {})
        
        # Keep track of priorities
        self.priorities: Dict[str, PriorityLevel] = {}

    def get_priority(self, symbol: str) -> PriorityLevel:
        return self.priorities.get(symbol, PriorityLevel.DORMANT)

    def set_priority(self, symbol: str, level: PriorityLevel):
        old_level = self.get_priority(symbol)
        if old_level != level:
            self.priorities[symbol] = level
            logger.info(f"Priority changed for {symbol}: {old_level.name} -> {level.name}")

    def evaluate_priority(self, symbol: str, metrics: Dict[str, float]) -> PriorityLevel:
        """
        Evaluates a stock's metrics and assigns a new priority.
        Called by the scanner or event trigger engine.
        """
        # A simple rules engine based on config
        # E.g., high relative volume -> HIGH
        
        rel_vol = metrics.get('relative_volume', 1.0)
        gap_pct = metrics.get('gap_pct', 0.0)
        
        if rel_vol > 3.0 or abs(gap_pct) > 0.05:
            new_level = PriorityLevel.CRITICAL
        elif rel_vol > 1.5 or abs(gap_pct) > 0.02:
            new_level = PriorityLevel.HIGH
        elif rel_vol > 1.0:
            new_level = PriorityLevel.MEDIUM
        elif rel_vol > 0.5:
            new_level = PriorityLevel.LOW
        else:
            new_level = PriorityLevel.DORMANT
            
        self.set_priority(symbol, new_level)
        return new_level
        
    def get_refresh_interval_seconds(self, priority: PriorityLevel) -> int:
        name = priority.name.lower()
        rule = self.rules.get(name, {})
        mins = rule.get("refresh_interval_min", 60)
        return mins * 60
