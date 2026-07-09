from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from app.reinforcement.learning_scheduler import LearningScheduler
from app.reinforcement.policy_registry import PolicyRegistry
from app.reinforcement.experience_buffer import ExperienceBuffer

router = APIRouter(prefix="/api/reinforcement", tags=["Reinforcement Learning"])

@router.get("/policy")
def get_policy() -> Dict[str, Any]:
    registry = PolicyRegistry()
    policy, metadata = registry.load_active_policy()
    return {
        "active_policy": metadata.get("version") if metadata else "none",
        "metadata": metadata if metadata else "No active policy"
    }

@router.get("/performance")
def get_performance() -> Dict[str, Any]:
    # Placeholder for aggregate performance metrics over policies
    return {"status": "ok", "message": "Performance metrics not yet implemented in MVP"}

@router.get("/rewards")
def get_rewards() -> Dict[str, Any]:
    buffer = ExperienceBuffer()
    count = buffer.get_count()
    return {"status": "ok", "experience_count": count}

def run_learning():
    scheduler = LearningScheduler()
    scheduler.execute_learning_run()

@router.post("/retrain")
def trigger_retrain(background_tasks: BackgroundTasks) -> Dict[str, str]:
    background_tasks.add_task(run_learning)
    return {"status": "accepted", "message": "RL Policy learning queued in background."}
