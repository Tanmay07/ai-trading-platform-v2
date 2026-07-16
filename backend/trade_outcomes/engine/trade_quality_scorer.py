import numpy as np

class TradeQualityScorer:
    """
    Calculates an Institutional Trade Quality Score (0-100) based on multiple dimensions of trade execution.
    """
    def __init__(self, weights: dict, holding_period: int):
        self.w_profit = weights.get('profit', 0.30)
        self.w_risk = weights.get('risk', 0.20)
        self.w_rr = weights.get('reward_risk', 0.20)
        self.w_speed = weights.get('speed', 0.15)
        self.w_vol = weights.get('volatility', 0.15)
        self.holding_period = holding_period
        
    def score_trade(self, outcome: str, mfe: float, mae: float, days_to_target: int, avg_daily_range_pct: float, stop_loss_pct: float) -> dict:
        """
        Scores a single trade based on its excursion and outcome.
        Returns the individual component scores and the final score (0-100).
        """
        # 1. Profit Achievement
        score_profit = 0.0
        if outcome == 'TARGET':
            score_profit = 100.0
        elif outcome == 'TIMEOUT' and mfe > 0:
            score_profit = 50.0 
            
        # 2. Risk Efficiency: Inverse of MAE
        mae_abs = abs(mae)
        score_risk = max(0.0, 100.0 * (1.0 - (mae_abs / stop_loss_pct))) if mae_abs <= stop_loss_pct else 0.0
        
        # 3. Reward / Risk: MFE / max(MAE, 0.1%)
        mae_denom = max(mae_abs, 0.1)
        # Cap RR at 10
        rr_ratio = max(0.0, min(mfe / mae_denom, 10.0))
        score_rr = (rr_ratio / 10.0) * 100.0
        
        # 4. Speed: Faster = Better
        if outcome == 'TARGET' and days_to_target > 0:
            # 1 day = ~100, 7 days = ~14
            score_speed = ((self.holding_period - days_to_target + 1) / self.holding_period) * 100.0
        else:
            score_speed = 0.0
            
        # 5. Volatility Efficiency
        # We assume 5% average daily range is max volatile for a valid trade
        score_vol = max(0.0, 100.0 * (1.0 - (avg_daily_range_pct / 5.0)))
        
        # Final weighted score
        final_score = (
            score_profit * self.w_profit +
            score_risk * self.w_risk +
            score_rr * self.w_rr +
            score_speed * self.w_speed +
            score_vol * self.w_vol
        )
        
        final_score = float(np.clip(final_score, 0.0, 100.0))
        
        # Categorize
        if final_score >= 90: category = "Exceptional Breakout"
        elif final_score >= 75: category = "High Conviction Swing"
        elif final_score >= 60: category = "Good Swing Opportunity"
        elif final_score >= 40: category = "Watchlist"
        else: category = "Avoid"
        
        return {
            "score": final_score,
            "category": category,
            "profit_score": score_profit,
            "risk_score": score_risk,
            "rr_score": score_rr,
            "speed_score": score_speed,
            "vol_score": score_vol
        }
