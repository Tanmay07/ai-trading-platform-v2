import os
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

router = APIRouter(prefix="/api/datasets", tags=["Dataset Engineering"])
REGISTRY_PATH = "data/models/dataset_registry.json"

@router.get("/current", response_model=Dict[str, Any])
def get_current_dataset():
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="Dataset Registry not found.")
        
    with open(REGISTRY_PATH, "r") as f:
        data = json.load(f)
        
    if not data.get("datasets"):
        raise HTTPException(status_code=404, detail="No datasets registered.")
        
    # The latest is the last one in the list
    return data["datasets"][-1]

@router.get("/", response_model=Dict[str, Any])
def get_all_datasets():
    if not os.path.exists(REGISTRY_PATH):
        return {"datasets": []}
        
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)

def run_builder_task():
    import subprocess
    # Run the dataset_v2_builder in a separate process or call its python method
    subprocess.run(["python3", "dataset_v2/builder/dataset_v2_builder.py"], cwd=os.getcwd())

@router.post("/build")
def build_dataset_v2(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_builder_task)
    return {"message": "Dataset V2 build triggered in the background."}
