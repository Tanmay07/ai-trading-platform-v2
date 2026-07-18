import logging
import threading
import time
from operations.orchestrator.workflow_engine import WorkflowEngine

logger = logging.getLogger("Scheduler")

class Scheduler:
    def __init__(self, engine: WorkflowEngine):
        self.engine = engine
        self._running = False
        
    def start(self):
        self._running = True
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()
        logger.info("Scheduler started.")
        
    def _run_loop(self):
        while self._running:
            # In a real system, use cron logic. 
            # For the prototype, we expose manual triggers via API.
            time.sleep(60)
            
    def stop(self):
        self._running = False
