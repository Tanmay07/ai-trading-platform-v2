from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from operations.orchestrator.workflow_engine import WorkflowEngine
from operations.scheduler.scheduler import Scheduler

router = APIRouter(tags=["operations"])

# Global Instances for state persistence in Prototype
workflow_engine = WorkflowEngine()
scheduler = Scheduler(workflow_engine)

@router.post("/run")
def trigger_daily_workflow():
    """
    Manually triggers the autonomous daily workflow orchestration.
    """
    try:
        workflow_engine.trigger_workflow()
        return {"message": "Daily workflow triggered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_workflow_status():
    """
    Retrieves the real-time status of the daily orchestration workflow.
    """
    try:
        return workflow_engine.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
