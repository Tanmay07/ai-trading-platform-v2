import time
import logging
from typing import Callable
import yaml

logger = logging.getLogger("RetryManager")

class RetryManager:
    def __init__(self):
        with open("config/operations.yaml", "r") as f:
            config = yaml.safe_load(f)["operations"]["retries"]
            self.max_attempts = config.get("max_attempts", 3)
            self.backoff = config.get("backoff_seconds", 5)
            
    def execute_with_retry(self, func: Callable, task_name: str, *args, **kwargs) -> bool:
        """
        Executes a callable, retrying on failure up to max_attempts.
        """
        for attempt in range(1, self.max_attempts + 1):
            try:
                func(*args, **kwargs)
                return True
            except Exception as e:
                logger.warning(f"Task '{task_name}' failed on attempt {attempt}/{self.max_attempts}: {str(e)}")
                if attempt < self.max_attempts:
                    time.sleep(self.backoff)
                    
        logger.error(f"Task '{task_name}' completely failed after {self.max_attempts} attempts.")
        return False
