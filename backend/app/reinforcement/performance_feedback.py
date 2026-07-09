from datetime import datetime
from app.reinforcement.experience_buffer import ExperienceBuffer
from app.reinforcement.reward_engine import RewardEngine

class PerformanceFeedback:
    def __init__(self):
        self.buffer = ExperienceBuffer()
        self.reward_engine = RewardEngine()
        
    def log_completed_trade(self, state: list, action: dict, trade_result: dict, market_regime: str, model_version: str, ai_consensus: float):
        """
        Called by Paper Trading Engine when a trade closes.
        """
        reward = self.reward_engine.calculate_reward(trade_result)
        
        experience = {
            "timestamp": datetime.utcnow().isoformat(),
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": [], # Simplified for episodic trades
            "trade_outcome": trade_result,
            "market_regime": market_regime,
            "model_version": model_version,
            "ai_consensus": ai_consensus
        }
        
        self.buffer.add_experience(experience)
