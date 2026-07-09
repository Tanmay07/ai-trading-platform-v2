import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from typing import List
from app.reinforcement.action_engine import ActionEngine

class PolicyEngine:
    """
    Implements a simple Contextual Bandit / Linear Policy mapping States -> Actions.
    Since actions are continuous (adjust confidence, adjust exposure), we can use Ridge regression
    to predict the optimal adjustment based on State -> Reward mappings.
    """
    def __init__(self):
        self.model = Ridge(alpha=1.0)
        self.is_trained = False
        self.action_engine = ActionEngine()
        
    def train(self, states: List[List[float]], rewards: List[float]):
        if not states or not rewards:
            return
            
        X = np.array(states)
        # We need a target action. In a full RL setup this is tricky.
        # For contextual bandit, if we know the reward of the *taken* action,
        # we can train a model to predict Reward given (State, Action).
        # To simplify the MVP: assume we map State -> Reward directly to learn the value.
        # For the policy, we just return a static neutral action if not properly implementing Actor-Critic.
        # Let's mock the policy weights for now.
        
        self.model.fit(X, rewards)
        self.is_trained = True

    def get_action(self, state: List[float]) -> List[float]:
        if not self.is_trained:
            # Neutral action
            return [0.0, 0.0]
            
        # Mock policy output based on the value (for MVP, let's just generate small adjustments based on state mean)
        val = np.mean(state)
        # If val is high, slightly boost exposure and confidence
        conf_adj = (val - 0.5) * 0.1
        exp_adj = (val - 0.5) * 0.1
        
        return [float(conf_adj), float(exp_adj)]
