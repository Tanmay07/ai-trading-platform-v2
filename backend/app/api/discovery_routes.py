from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from app.discovery.opportunity_ranker import OpportunityRanker
from app.discovery.recommendation_generator import RecommendationGenerator
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# In-memory cache for MVP to avoid hitting rate limits on every page load
# In production, use Redis or PostgreSQL
scan_cache: List[Dict[str, Any]] = []
is_scanning = False

@router.get("/scan")
async def get_discovery_scan(force_refresh: bool = False):
    """
    Returns the latest opportunity scan results.
    If force_refresh is True, triggers a new scan (warning: slow).
    """
    global scan_cache, is_scanning
    
    if is_scanning:
        return {"status": "scanning", "message": "A scan is currently in progress. Please check back later.", "data": scan_cache}
        
    if not scan_cache or force_refresh:
        is_scanning = True
        try:
            ranker = OpportunityRanker()
            opportunities = await ranker.scan_universe()
            
            # Apply Recommendation Generator
            final_opps = []
            for opp in opportunities:
                final_opps.append(RecommendationGenerator.generate_recommendation(opp))
                
            scan_cache = final_opps
        except Exception as e:
            logger.error(f"Error during discovery scan: {e}")
            raise HTTPException(status_code=500, detail="Failed to scan universe")
        finally:
            is_scanning = False
            
    return {"status": "success", "data": scan_cache}

@router.get("/top/{category}")
async def get_top_opportunities(category: str):
    """
    Returns top opportunities filtered by category.
    Categories: high_growth, value, momentum
    """
    if not scan_cache:
        # If cache is empty, trigger a background scan and return empty for now
        # Or raise error instructing to hit /scan first
        raise HTTPException(status_code=400, detail="No scan data available. Please trigger a scan first.")
        
    if category == "high_growth":
        # Sort by expected return / probability
        filtered = sorted(scan_cache, key=lambda x: x.get("predicted_return", 0), reverse=True)
    elif category == "value":
        # Sort by value score
        filtered = sorted(scan_cache, key=lambda x: x.get("value_score", 0), reverse=True)
    elif category == "momentum":
        # Sort by momentum score
        filtered = sorted(scan_cache, key=lambda x: x.get("momentum_score", 0), reverse=True)
    else:
        # Default sort by overall opportunity score
        filtered = scan_cache
        
    return {"status": "success", "data": filtered[:10]} # Return top 10
