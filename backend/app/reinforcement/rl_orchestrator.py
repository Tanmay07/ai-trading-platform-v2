from typing import Dict, Any
from app.reinforcement.policy_registry import PolicyRegistry
from app.reinforcement.state_builder import StateBuilder
from app.reinforcement.action_engine import ActionEngine
from app.reinforcement.confidence_optimizer import ConfidenceOptimizer

class RLOrchestrator:
    def __init__(self):
        self.registry = PolicyRegistry()
        self.state_builder = StateBuilder()
        self.action_engine = ActionEngine()
        self.confidence_optimizer = ConfidenceOptimizer()
        
        # Load active policy
        self.policy, self.metadata = self.registry.load_active_policy()
        
    async def process_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the recommendation candidate (post Phase 1-5) and applies RL meta-adjustments.
        """
        if not self.policy:
            # If no policy is trained yet, return a neutral adjustment.
            return {
                "Policy_Version": "neutral",
                "Calibrated_Confidence": candidate_data.get("Confidence", 0),
                "RL_Exposure_Multiplier": 1.0,
                "RL_Decision_Summary": "No active RL policy found. Defaults applied."
            }
            
        state = self.state_builder.build_state(candidate_data)
        raw_action = self.policy.get_action(state)
        action = self.action_engine.decode_action(raw_action)
        
        # Optimize output
        raw_conf = candidate_data.get("Confidence", 0)
        calibrated_conf = self.confidence_optimizer.calibrate(raw_conf, action["confidence_adjustment"])
        
        # Generate summary
        adj_pct = round(action["confidence_adjustment"] * 100, 1)
        exp_pct = round((action["exposure_multiplier"] - 1.0) * 100, 1)
        
        summary = f"RL applied {adj_pct}% adjust to confidence, and {exp_pct}% to exposure."
        
        return {
            "Policy_Version": self.metadata.get("version", "unknown"),
            "Calibrated_Confidence": calibrated_conf,
            "RL_Exposure_Multiplier": action["exposure_multiplier"],
            "RL_Decision_Summary": summary,
            # We also pass the RL state and action out so the Paper Trading Engine can later log it
            "RL_State": state,
            "RL_Action": action
        }
