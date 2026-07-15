import logging
from training_framework.optimization.training_runner import TrainingRunner

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    runner = TrainingRunner()
    runner.run_training_cycle()
