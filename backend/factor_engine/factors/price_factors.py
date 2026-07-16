import pandas as pd
import numpy as np
from factor_engine.core.dynamic_weighting import InstitutionalFactor

class TrendFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Trend_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        weights = self.get_weights()
        
        # 1. EMA Alignment (Close > EMA20 > EMA50 > EMA200)
        ema_score = pd.Series(0.0, index=df.index)
        if all(c in df.columns for c in ['Close', 'EMA_20', 'EMA_50', 'EMA_200']):
            ema_score += (df['Close'] > df['EMA_20']).astype(float) * 25
            ema_score += (df['EMA_20'] > df['EMA_50']).astype(float) * 25
            ema_score += (df['EMA_50'] > df['EMA_200']).astype(float) * 50
        
        # 2. ADX (Trend Strength)
        adx_score = self._normalize_0_100(df.get('ADX_14', pd.Series(50, index=df.index)))
        
        # 3. Trend Persistence (Consecutive higher closes / HH HL logic proxy)
        persistence_score = self._normalize_0_100(df.get('Returns_5d', pd.Series(0, index=df.index)))
        
        # Combine using weights
        w_ema = weights.get('ema_alignment', 0.4)
        w_adx = weights.get('adx', 0.3)
        w_per = weights.get('trend_persistence', 0.3)
        
        composite = (ema_score * w_ema) + (adx_score * w_adx) + (persistence_score * w_per)
        return self._normalize_0_100(composite)

class RelativeStrengthFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Relative_Strength_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        weights = self.get_weights()
        
        # We proxy relative strength via Returns compared to index if available, else just momentum
        rs_nifty = self._normalize_0_100(df.get('Returns_5d', pd.Series(0, index=df.index)))
        rs_sector = self._normalize_0_100(df.get('Returns_1d', pd.Series(0, index=df.index)))
        
        composite = (
            rs_nifty * weights.get('vs_nifty50', 0.4) +
            rs_sector * weights.get('vs_sector', 0.4) +
            rs_nifty * weights.get('rolling_outperformance', 0.2)
        )
        return self._normalize_0_100(composite)

class BreakoutQualityFactor(InstitutionalFactor):
    def __init__(self, config: dict, adaptive_mode: bool = False):
        super().__init__("Breakout_Quality_Factor", config, adaptive_mode)

    def calculate(self, df: pd.DataFrame) -> pd.Series:
        weights = self.get_weights()
        
        # Proxies
        dist_52 = self._normalize_0_100(df.get('Close', pd.Series(0, index=df.index))) # Placeholder
        vol_comp = self._normalize_0_100(df.get('Volume', pd.Series(0, index=df.index))) # Placeholder
        
        composite = (dist_52 * weights.get('dist_to_52w_high', 0.5)) + (vol_comp * weights.get('volatility_compression', 0.5))
        return self._normalize_0_100(composite)
