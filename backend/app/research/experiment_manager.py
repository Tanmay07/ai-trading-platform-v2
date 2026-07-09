from typing import Dict, Any

class ExperimentManager:
    def log_experiment(self, experiment_id: str, results: Dict[str, Any]):
        """
        Stores the inputs and outputs of a research run.
        """
        print(f"[EXPERIMENT_LOG] {experiment_id} completed: {results}")
