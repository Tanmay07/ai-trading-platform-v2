class SimulationEnvironment:
    def run_replay(self, experiences: list, policy_engine):
        """
        Simulates how the current policy would have acted on historical experiences.
        """
        results = []
        for exp in experiences:
            action = policy_engine.get_action(exp.get("state", []))
            results.append({"original_reward": exp.get("reward"), "simulated_action": action})
        return results
