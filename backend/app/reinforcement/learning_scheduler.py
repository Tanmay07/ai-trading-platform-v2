from app.reinforcement.experience_buffer import ExperienceBuffer
from app.reinforcement.policy_engine import PolicyEngine
from app.reinforcement.policy_registry import PolicyRegistry
from app.config_rl import rl_config
import json

class LearningScheduler:
    def __init__(self):
        self.buffer = ExperienceBuffer()
        self.registry = PolicyRegistry()
        self.config = rl_config.learning_schedules
        
    def execute_learning_run(self) -> dict:
        count = self.buffer.get_count()
        if count < self.config.min_experiences_required:
            return {"status": "skipped", "reason": f"Insufficient experiences: {count} < {self.config.min_experiences_required}"}
            
        batch = self.buffer.sample_batch(rl_config.replay_settings.batch_size)
        
        states = []
        rewards = []
        for exp in batch:
            state = json.loads(exp["state"])
            reward = float(exp["reward"])
            states.append(state)
            rewards.append(reward)
            
        policy = PolicyEngine()
        policy.train(states, rewards)
        
        # In a real environment, we would run it against SimulationEnvironment and only promote if better.
        metrics = {"train_size": len(batch), "notes": "offline learning completed"}
        
        version = self.registry.save_policy(policy, metrics)
        
        return {"status": "success", "version": version, "metrics": metrics}
