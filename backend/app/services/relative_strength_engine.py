"""
Relative Strength Engine
Calculates RS vs Market and Sector.
"""
import pandas as pd
from typing import Dict, Any, Optional
from app.config_technical import technical_config

class RelativeStrengthEngine:
    def __init__(self):
        self.periods = technical_config.relative_strength.periods

    def _calc_rs(self, df_stock: pd.DataFrame, df_bench: pd.DataFrame, period: int) -> float:
        if len(df_stock) < period or len(df_bench) < period:
            return 0.0
            
        stock_ret = (df_stock['Close'].iloc[-1] - df_stock['Close'].iloc[-period]) / df_stock['Close'].iloc[-period]
        bench_ret = (df_bench['Close'].iloc[-1] - df_bench['Close'].iloc[-period]) / df_bench['Close'].iloc[-period]
        
        return (stock_ret - bench_ret) * 100

    def analyze(self, df: pd.DataFrame, df_market: pd.DataFrame, df_sector: Optional[pd.DataFrame]) -> Dict[str, Any]:
        if df is None or df_market is None or df.empty or df_market.empty:
            return {"rs_score": 0, "outperformance_percent": 0}
            
        period_rs_market = []
        period_rs_sector = []
        
        for p in self.periods:
            rs_m = self._calc_rs(df, df_market, p)
            period_rs_market.append(rs_m)
            
            if df_sector is not None and not df_sector.empty:
                rs_s = self._calc_rs(df, df_sector, p)
                period_rs_sector.append(rs_s)
                
        avg_rs_market = sum(period_rs_market) / len(period_rs_market) if period_rs_market else 0
        avg_rs_sector = sum(period_rs_sector) / len(period_rs_sector) if period_rs_sector else 0
        
        # Base score starts at 50. Positive RS adds to the score. Capped at 100.
        score = 50 + avg_rs_market + (avg_rs_sector * 0.5)
        score = min(100, max(0, score))
        
        return {
            "rs_score": round(score, 2),
            "outperformance_percent": round(avg_rs_market, 2),
            "rs_market_20d": round(period_rs_market[0], 2) if len(period_rs_market) > 0 else 0,
            "rs_market_50d": round(period_rs_market[1], 2) if len(period_rs_market) > 1 else 0,
            "rs_sector_20d": round(period_rs_sector[0], 2) if len(period_rs_sector) > 0 else 0,
            "rs_sector_50d": round(period_rs_sector[1], 2) if len(period_rs_sector) > 1 else 0,
        }
