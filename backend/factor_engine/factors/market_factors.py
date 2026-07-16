import pandas as pd
import numpy as np
from factor_engine.core.dynamic_weighting import InstitutionalFactor

class VolatilityFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Volatility_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        atr_exp = self._normalize_0_100(df.get('ATR_14', pd.Series(0, index=df.index)))
        boll = self._normalize_0_100(df.get('Close', pd.Series(0, index=df.index))) # Placeholder
        return self._normalize_0_100(atr_exp * 0.5 + boll * 0.5)

class LiquidityFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Liquidity_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        rel_vol = self._normalize_0_100(df.get('Volume', pd.Series(0, index=df.index)))
        turnover = self._normalize_0_100(df.get('Volume', pd.Series(0, index=df.index)))
        return self._normalize_0_100(rel_vol * 0.5 + turnover * 0.5)

class MarketBreadthFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Market_Breadth_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        # Assumes breadth is precalculated or we just use a constant proxy per date
        return pd.Series(75.0, index=df.index)

class RegimeFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Regime_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(80.0, index=df.index)

class RiskFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Risk_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(85.0, index=df.index)

class MomentumFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Momentum_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        rsi = self._normalize_0_100(df.get('RSI_14', pd.Series(50, index=df.index)))
        return rsi

class InstitutionalActivityFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Institutional_Activity_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(60.0, index=df.index)
