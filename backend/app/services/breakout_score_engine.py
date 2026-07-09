"""
Breakout Score Engine
Aggregates technical sub-scores into a final 0-100 probability.
"""
from typing import Dict, Any
from app.config_technical import technical_config

class BreakoutScoreEngine:
    def __init__(self):
        self.weights = technical_config.breakout_score_weights

    def score(
        self, 
        mtf_score: float, 
        rs_score: float, 
        pattern_quality: float, 
        sector_score: float, 
        price_action_score: float, 
        vwap_score: float, 
        support_dist: float
    ) -> Dict[str, Any]:
        """
        Calculates the final composite score based on configured weights.
        """
        mtf = (mtf_score / 100) * self.weights.multi_timeframe
        rs = (rs_score / 100) * self.weights.relative_strength
        pat = (pattern_quality / 100) * self.weights.breakout_patterns
        
        # Sector score normalization (0-100 range roughly)
        sec_norm = max(0, min(100, 50 + sector_score))
        sec = (sec_norm / 100) * self.weights.sector_rotation
        
        pa = (price_action_score / 100) * self.weights.price_action
        vwap = (vwap_score / 100) * self.weights.vwap
        
        # Support score (closer to support = better risk/reward)
        sr = 0.5
        if 0 < support_dist < 5:
            sr = 1.0
        elif support_dist > 15:
            sr = 0.2
        sr_weighted = sr * self.weights.support_resistance
        
        total_score = (mtf + rs + pat + sec + pa + vwap + sr_weighted) * 100
        total_score = round(min(100, max(0, total_score)), 2)
        
        grade = "D"
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
            
        return {
            "breakout_score": total_score,
            "breakout_grade": grade,
            "breakout_probability": round(total_score * 0.85, 2)
        }
