import random
from typing import Dict, Any, List

class ScenarioAnalysis:
    """
    Evaluates optimized portfolios against historical stress scenarios.
    """
    def run_stress_tests(self, weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Returns stress test results.
        """
        # Determine how concentrated the portfolio is to mock realistic impacts
        concentration = sum([w**2 for w in weights.values()]) / 10000.0 # HHI proxy
        
        scenarios = [
            {"name": "2008 Financial Crisis", "base_impact": -45.0},
            {"name": "COVID Crash (2020)", "base_impact": -33.0},
            {"name": "Interest Rate Shock", "base_impact": -15.0},
            {"name": "Flash Crash", "base_impact": -9.0}
        ]
        
        results = []
        resilience_score = 100.0
        
        for s in scenarios:
            # Concentrated portfolios fare worse in stress tests
            impact = s["base_impact"] * (1.0 + concentration)
            # Add some randomness
            impact += random.uniform(-5.0, 5.0)
            impact = round(impact, 2)
            
            # Simple resilience math
            if impact < -30:
                resilience_score -= 15
            elif impact < -15:
                resilience_score -= 5
                
            results.append({
                "scenario_name": s["name"],
                "simulated_drawdown_pct": impact,
                "expected_recovery_days": int(abs(impact) * random.uniform(1.5, 4.0))
            })
            
        return {
            "stress_tests": results,
            "portfolio_resilience_score": max(0.0, min(100.0, round(resilience_score, 1)))
        }
