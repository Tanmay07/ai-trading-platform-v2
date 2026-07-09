from fastapi import APIRouter
from typing import Dict, Any
from app.infrastructure.infrastructure_manager import InfrastructureManager
from app.infrastructure.metrics.prometheus import PrometheusMetrics

router = APIRouter(prefix="/api/admin", tags=["Admin Phase 10"])

@router.get("/system")
def get_system_health() -> Dict[str, Any]:
    manager = InfrastructureManager()
    return manager.check_health()

@router.get("/metrics")
def get_metrics() -> str:
    prom = PrometheusMetrics()
    return prom.get_metrics()
