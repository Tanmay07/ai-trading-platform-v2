"""
Discovery Scheduler

Background tasks for running the Opportunity Discovery Engine on a schedule.
"""
import asyncio
from app.utils.logger import get_logger
from app.discovery.opportunity_ranker import OpportunityRanker
from app.discovery.recommendation_generator import RecommendationGenerator
import app.api.discovery_routes as discovery_routes

logger = get_logger(__name__)

async def scheduled_discovery_scan(interval_minutes: int = 15):
    """
    Runs the discovery scan every `interval_minutes` and caches the results
    in the discovery_routes module.
    """
    logger.info(f"Started scheduled discovery scan loop (interval: {interval_minutes}m)")
    
    while True:
        try:
            logger.info("Running scheduled discovery scan...")
            
            # Use global lock from routes if necessary, but here we just overwrite cache
            if not discovery_routes.is_scanning:
                discovery_routes.is_scanning = True
                
                ranker = OpportunityRanker()
                opportunities = await ranker.scan_universe()
                
                final_opps = []
                for opp in opportunities:
                    final_opps.append(RecommendationGenerator.generate_recommendation(opp))
                    
                discovery_routes.scan_cache = final_opps
                discovery_routes.is_scanning = False
                
                logger.info(f"Completed scheduled scan. Cached {len(final_opps)} opportunities.")
            else:
                logger.warning("Scan already in progress. Skipping scheduled run.")
                
        except asyncio.CancelledError:
            logger.info("Scheduled discovery scan stopped.")
            break
        except Exception as e:
            logger.error(f"Error in scheduled discovery scan: {e}")
            discovery_routes.is_scanning = False
            
        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)
