from app.config_backtesting import backtesting_config

class SlippageEngine:
    def calculate_slippage_pct(self, volatility: float) -> float:
        """
        Calculates simulated slippage based on market volatility.
        """
        cfg = backtesting_config.slippage
        # Higher volatility = more slippage
        adjusted_slippage = cfg.base_slippage_pct * (1.0 + (volatility * cfg.volatility_multiplier))
        return adjusted_slippage
