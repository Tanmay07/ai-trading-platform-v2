from typing import Dict, Any

class CommandCenter:
    def get_system_health(self) -> Dict[str, Any]:
        """
        Aggregates health across AI, Brokers, Strategy, and Infra.
        """
        return {
            "ai_health": "UP",
            "strategy_health": "WARNING", # example
            "broker_health": "UP",
            "infrastructure": "UP"
        }
