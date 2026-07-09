"""
Market Score Engine
Creates a single Market Intelligence Score.
"""
from typing import Dict, Any
from app.config_market import market_config

class MarketScoreEngine:
    def __init__(self):
        self.weights = market_config.market_score_weights

    def score(
        self,
        regime_score: float,
        breadth_score: float,
        macro_score: float,
        fii_score: float,
        vol_score: float,
        liq_score: float,
        global_score: float
    ) -> Dict[str, Any]:
        
        reg = regime_score * self.weights.market_regime
        brd = breadth_score * self.weights.market_breadth
        mac = macro_score * self.weights.macro
        fii = fii_score * self.weights.fii_dii
        vol = vol_score * self.weights.volatility
        liq = liq_score * self.weights.liquidity
        glb = global_score * self.weights.global_markets
        
        total = reg + brd + mac + fii + vol + liq + glb
        total = max(0, min(100, total))
        
        grade = "F"
        if total >= 90:
            grade = "A+"
        elif total >= 80:
            grade = "A"
        elif total >= 70:
            grade = "B"
        elif total >= 60:
            grade = "C"
        elif total >= 50:
            grade = "D"
            
        prob_mult = 1.0
        if total >= 80:
            prob_mult = 1.15
        elif total >= 70:
            prob_mult = 1.05
        elif total <= 40:
            prob_mult = 0.8
        elif total <= 20:
            prob_mult = 0.5
            
        return {
            "market_score": round(float(total), 2),
            "market_grade": grade,
            "breakout_probability_multiplier": prob_mult
        }
