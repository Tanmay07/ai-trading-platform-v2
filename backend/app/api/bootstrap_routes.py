from fastapi import APIRouter
from bootstrap.manager.bootstrap_manager import BootstrapManager
import asyncio

router = APIRouter(prefix="/api/bootstrap", tags=["Bootstrap Orchestrator"])
manager = BootstrapManager()

@router.get("/preflight")
async def get_preflight_estimation():
    return await manager.run_preflight()
    
@router.post("/start")
async def start_bootstrap():
    # In production, this would be dispatched to a background worker (e.g., Celery or asyncio.create_task)
    # For now, we kick it off async to not block the API
    asyncio.create_task(manager.run_bootstrap())
    return {"status": "started", "execution_id": manager.execution_id}

@router.get("/status/{execution_id}")
def get_bootstrap_status(execution_id: str):
    return manager.get_status(execution_id)

@router.get("/progress")
def get_progress():
    # Legacy wrapper for older UI if it still hits this endpoint
    status = manager.get_status(manager.execution_id)
    return {"status": "Running", "metrics": {}}
