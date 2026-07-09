class ConfidenceOptimizer:
    def calibrate(self, raw_confidence: float, policy_adjustment: float) -> float:
        """
        Applies the RL policy's confidence adjustment to the AI Supervisor's raw confidence.
        """
        # policy_adjustment is like -0.05 or +0.02
        adj = raw_confidence * (1.0 + policy_adjustment)
        return round(max(0.0, min(100.0, adj)), 2)
