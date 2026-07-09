from app.config_rl import rl_config
import math

class RewardEngine:
    def __init__(self):
        self.weights = rl_config.reward_weights

    def calculate_reward(self, trade_result: dict) -> float:
        """
        Calculates the continuous reward signal for a closed trade.
        """
        profit_pct = trade_result.get("profit_pct", 0.0)
        max_drawdown = trade_result.get("max_drawdown", 0.0)
        holding_period = trade_result.get("holding_period_days", 1)
        
        # Base reward is profit
        reward = profit_pct * self.weights.profit
        
        # Penalize deep drawdowns heavily
        reward -= abs(max_drawdown) * self.weights.drawdown_penalty
        
        # Penalize holding too long (opportunity cost)
        reward -= math.log(max(1, holding_period)) * self.weights.holding_period_penalty
        
        # Bonus if it hit target quickly vs hitting stop loss
        if trade_result.get("hit_target", False):
            reward += self.weights.calibration_bonus
            
        return round(float(reward), 4)
