from typing import Dict, Any
from app.config_portfolio import portfolio_config

class ScenarioEngine:
    def run_stress_test(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs scenarios like "Market Crash" (-10%)
        """
        total_value = portfolio.get("total_value", 1000000.0)
        
        crash_impact = total_value * portfolio_config.stress_test.market_crash
        
        return {
            "market_crash_scenario_pnl": round(crash_impact, 2),
            "volatility_spike_scenario_var": round(total_value * -0.05, 2)
        }
