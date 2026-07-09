from typing import Dict, Any
from app.config_backtesting import backtesting_config

class ValidationEngine:
    def validate(self, backtest_results: Dict[str, Any], mc_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates the strategy against YAML config thresholds.
        """
        cfg = backtesting_config.validation
        
        cagr = backtest_results.get("simulated_cagr", 0)
        drawdown = backtest_results.get("simulated_drawdown", 1.0)
        win_rate = backtest_results.get("win_rate", 0)
        survival = mc_results.get("survival_probability", 0)
        
        passed = True
        reasons = []
        
        if cagr < cfg.min_cagr:
            passed = False
            reasons.append(f"CAGR {cagr} < Minimum {cfg.min_cagr}")
            
        if drawdown > cfg.max_drawdown:
            passed = False
            reasons.append(f"Drawdown {drawdown} > Maximum {cfg.max_drawdown}")
            
        if win_rate < cfg.min_win_rate:
            passed = False
            reasons.append(f"Win Rate {win_rate} < Minimum {cfg.min_win_rate}")
            
        if survival < cfg.min_monte_carlo_survival:
            passed = False
            reasons.append(f"Monte Carlo Survival {survival} < Minimum {cfg.min_monte_carlo_survival}")
            
        return {
            "status": "APPROVED" if passed else "REJECTED",
            "score": 95 if passed else 45,
            "reasons": reasons
        }
