from typing import Dict, Any

class StrategyGenerator:
    def generate_strategy(self, hypothesis: str) -> Dict[str, Any]:
        """
        Converts text hypothesis into programmatic entry/exit thresholds.
        """
        return {
            "hypothesis": hypothesis,
            "entry_rsi_min": 60,
            "exit_rsi_max": 80,
            "stop_loss_pct": 0.05
        }
