from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List
import logging

from data_platform.core.config_manager import ConfigManager
from market_data.orchestrator.market_data_orchestrator import MarketDataOrchestrator
from market_data.scanner.universe_scanner import UniverseScanner
from market_data.monitoring.api_usage_monitor import ApiUsageMonitor

router = APIRouter(prefix="/api/market", tags=["Market Data Platform"])
logger = logging.getLogger(__name__)

# Singletons
config_manager = ConfigManager()
orchestrator = MarketDataOrchestrator(config_manager)
scanner = UniverseScanner(orchestrator, config_manager)
monitor = ApiUsageMonitor()

@router.get("/health")
async def get_market_health() -> Dict[str, Any]:
    return {"status": "ok", "service": "Market Data Platform"}

@router.get("/cache")
async def get_cache_stats() -> Dict[str, Any]:
    return orchestrator.cache.get_stats()

@router.get("/usage")
async def get_api_usage() -> Dict[str, Any]:
    return monitor.get_usage()

@router.get("/candidates")
async def get_candidates() -> Dict[str, Any]:
    candidates = scanner.get_candidate_queue()
    return {
        "count": len(candidates),
        "queue": candidates
    }

@router.post("/refresh")
async def refresh_universe(background_tasks: BackgroundTasks, universe_size: int = 50) -> Dict[str, Any]:
    """Trigger a manual refresh cycle (for a subset to avoid giant requests in dev)."""
    # Just a mock universe for now
    mock_universe = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"][:universe_size]
    
    def background_refresh():
        orchestrator.execute_refresh_cycle(mock_universe)
        
    background_tasks.add_task(background_refresh)
    return {"status": "accepted", "message": f"Refresh cycle started for {len(mock_universe)} symbols."}

@router.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Triggers the Universe Scanner to rebuild the Candidate Queue."""
    mock_universe = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "ITC", "SBI", "LNT", "BAJFINANCE"]
    
    def background_scan():
        scanner.run_scan(mock_universe)
        
    background_tasks.add_task(background_scan)
    return {"status": "accepted", "message": "Universe scan started."}
