import logging
from typing import Dict, Any, List
from operations.events.event_bus import bus
from operations.recovery.retry_manager import RetryManager

logger = logging.getLogger("WorkflowEngine")

class WorkflowEngine:
    def __init__(self):
        self.state = {
            "status": "IDLE",
            "stages": {
                "MarketData": "PENDING",
                "Prediction": "PENDING",
                "Portfolio": "PENDING",
                "Execution": "PENDING",
                "Committee": "PENDING",
                "PaperTrading": "PENDING",
                "AdaptiveIntelligence": "PENDING"
            }
        }
        self.retry_manager = RetryManager()
        self._register_subscribers()
        
    def _register_subscribers(self):
        bus.subscribe("MarketDataUpdated", self._on_market_data_updated)
        bus.subscribe("PredictionsGenerated", self._on_predictions_generated)
        bus.subscribe("PortfolioOptimized", self._on_portfolio_optimized)
        bus.subscribe("ExecutionPlanCreated", self._on_execution_plan_created)
        bus.subscribe("CommitteeDecisionsApproved", self._on_committee_approved)
        bus.subscribe("PaperTradingCompleted", self._on_paper_trading_completed)
        bus.subscribe("AdaptiveAnalysisCompleted", self._on_adaptive_completed)
        
    def trigger_workflow(self):
        logger.info("Triggering Daily Workflow")
        self.state["status"] = "RUNNING"
        # Reset stages
        for k in self.state["stages"]:
            self.state["stages"][k] = "PENDING"
            
        self.state["stages"]["MarketData"] = "RUNNING"
        
        # Simulate kicking off the first task wrapped in retry logic
        def mock_fetch_data():
            # Simulate work
            pass
        
        success = self.retry_manager.execute_with_retry(mock_fetch_data, "MarketDataRefresh")
        if success:
            bus.publish("MarketDataUpdated", {"status": "success"})
        else:
            self._fail_workflow("MarketData")

    def _on_market_data_updated(self, event):
        self.state["stages"]["MarketData"] = "COMPLETED"
        self.state["stages"]["Prediction"] = "RUNNING"
        logger.info("MarketData completed. Triggering Prediction Service.")
        # Simulate Prediction Service
        bus.publish("PredictionsGenerated", {"status": "success"})

    def _on_predictions_generated(self, event):
        self.state["stages"]["Prediction"] = "COMPLETED"
        self.state["stages"]["Portfolio"] = "RUNNING"
        logger.info("Prediction completed. Triggering Portfolio Engine.")
        bus.publish("PortfolioOptimized", {"status": "success"})

    def _on_portfolio_optimized(self, event):
        self.state["stages"]["Portfolio"] = "COMPLETED"
        self.state["stages"]["Execution"] = "RUNNING"
        logger.info("Portfolio completed. Triggering Execution Engine.")
        bus.publish("ExecutionPlanCreated", {"status": "success"})

    def _on_execution_plan_created(self, event):
        self.state["stages"]["Execution"] = "COMPLETED"
        self.state["stages"]["Committee"] = "RUNNING"
        logger.info("Execution completed. Triggering Investment Committee.")
        bus.publish("CommitteeDecisionsApproved", {"status": "success"})

    def _on_committee_approved(self, event):
        self.state["stages"]["Committee"] = "COMPLETED"
        self.state["stages"]["PaperTrading"] = "RUNNING"
        logger.info("Committee completed. Triggering Paper Trading.")
        bus.publish("PaperTradingCompleted", {"status": "success"})

    def _on_paper_trading_completed(self, event):
        self.state["stages"]["PaperTrading"] = "COMPLETED"
        self.state["stages"]["AdaptiveIntelligence"] = "RUNNING"
        logger.info("Paper Trading completed. Triggering Adaptive Intelligence.")
        bus.publish("AdaptiveAnalysisCompleted", {"status": "success"})

    def _on_adaptive_completed(self, event):
        self.state["stages"]["AdaptiveIntelligence"] = "COMPLETED"
        self.state["status"] = "COMPLETED"
        logger.info("Daily Workflow Completed Successfully.")
        
    def _fail_workflow(self, stage: str):
        self.state["stages"][stage] = "FAILED"
        self.state["status"] = "FAILED"
        logger.error(f"Workflow Failed at stage: {stage}")
        
    def get_status(self) -> Dict[str, Any]:
        return self.state
