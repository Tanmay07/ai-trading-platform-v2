from typing import Dict, Any

class CapitalAllocator:
    def allocate_capital(self) -> Dict[str, float]:
        """
        Dynamically shifts total fund capital bounds between active strategies based on regime.
        """
        return {
            "Swing Breakout": 0.40,
            "Momentum": 0.35,
            "Cash": 0.25
        }
