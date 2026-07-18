from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from event_intelligence.ingestion.news_collector import NewsCollector
from event_intelligence.extraction.event_extractor import EventExtractor
from event_intelligence.classification.significance_engine import SignificanceEngine
from event_intelligence.impact.impact_estimator import ImpactEstimator
from event_intelligence.memory.causal_learning_engine import CausalLearningEngine
from event_intelligence.alpha.event_alpha import EventAlphaGenerator

router = APIRouter(tags=["event_intelligence"])

news_collector = NewsCollector()
event_extractor = EventExtractor()
significance_engine = SignificanceEngine()
impact_estimator = ImpactEstimator()
causal_engine = CausalLearningEngine()
alpha_generator = EventAlphaGenerator()

@router.get("/live")
def get_live_events():
    """
    Runs the full Event Intelligence Pipeline and returns structured events.
    """
    try:
        # 1. Ingest
        raw_news = news_collector.fetch_recent_news()
        
        processed_events = []
        for article in raw_news:
            # 2. Extract
            event = event_extractor.extract_event(article)
            
            # 3. Classify Significance
            event = significance_engine.score_event(event)
            
            # 4. Impact Estimation (Knowledge Graph)
            event = impact_estimator.estimate_impact(event)
            
            # 5. Causal Memory Query
            event = causal_engine.query_event_memory(event)
            
            processed_events.append(event)
            
        # 6. Alpha Generation
        new_alphas = alpha_generator.generate_candidates(processed_events)
        
        return {
            "events": processed_events,
            "new_alpha_candidates": new_alphas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
