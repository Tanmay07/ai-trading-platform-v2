"""
Sector Rotation Engine
Ranks sectors and provides sector context for a stock.
"""
import pandas as pd
from typing import Dict, Any

class SectorRotationEngine:
    def __init__(self):
        self.sector_ranks = {}

    def pre_calculate_ranks(self, sector_dfs: Dict[str, pd.DataFrame], market_df: pd.DataFrame):
        """
        Calculates and caches the rank of all sectors based on relative strength and momentum.
        """
        scores = {}
        for sector, df in sector_dfs.items():
            if df is None or df.empty or len(df) < 50:
                continue
                
            # Momentum (20-day return)
            mom = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20] * 100
            
            # Trend (Price > EMA50)
            ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
            trend_score = 20 if df['Close'].iloc[-1] > ema50 else 0
            
            # RS vs Market (20-day)
            market_ret = 0
            if market_df is not None and not market_df.empty and len(market_df) >= 20:
                market_ret = (market_df['Close'].iloc[-1] - market_df['Close'].iloc[-20]) / market_df['Close'].iloc[-20] * 100
                
            rs = mom - market_ret
            
            # Simplified Volume expansion check (last 5 days vs 20 days)
            vol_score = 0
            if 'Volume' in df.columns:
                vol_5d = df['Volume'].tail(5).mean()
                vol_20d = df['Volume'].tail(20).mean()
                if vol_5d > vol_20d:
                    vol_score = 10
                    
            total_score = mom + trend_score + rs + vol_score
            scores[sector] = {
                "momentum": round(mom, 2),
                "trend": "Bullish" if df['Close'].iloc[-1] > ema50 else "Bearish",
                "rs": round(rs, 2),
                "score": round(total_score, 2)
            }
            
        # Rank by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        self.sector_ranks = {
            sector: {**data, "rank": i + 1, "total_sectors": len(ranked)}
            for i, (sector, data) in enumerate(ranked)
        }

    def analyze(self, sector: str) -> Dict[str, Any]:
        """
        Returns the rotation data for a specific sector.
        """
        # We perform loose matching in case of naming discrepancies
        matched_sector = None
        for s in self.sector_ranks.keys():
            if s.lower() in sector.lower() or sector.lower() in s.lower():
                matched_sector = s
                break
                
        if not matched_sector:
            return {
                "sector_rank": 999,
                "sector_score": 0,
                "sector_momentum": 0,
                "sector_trend": "Unknown"
            }
            
        return {
            "sector_rank": self.sector_ranks[matched_sector]["rank"],
            "sector_score": self.sector_ranks[matched_sector]["score"],
            "sector_momentum": self.sector_ranks[matched_sector]["momentum"],
            "sector_trend": self.sector_ranks[matched_sector]["trend"]
        }
