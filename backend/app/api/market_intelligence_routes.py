from fastapi import APIRouter, BackgroundTasks, Depends
from typing import Dict, Any, List
import logging
from sqlalchemy.orm import Session

from market_intelligence.storage.database import get_db
from market_intelligence.ingestion.news_collector import NewsCollector
from market_intelligence.processing.article_parser import ArticleParser
from market_intelligence.processing.company_tagger import CompanyTagger
from market_intelligence.processing.event_classifier import EventClassifier
from market_intelligence.processing.sentiment_engine import SentimentEngine
from market_intelligence.scoring.news_importance import NewsImportanceScorer
from market_intelligence.memory.market_memory_engine import MarketMemoryEngine
from data_platform.core.config_manager import ConfigManager

router = APIRouter(prefix="/api/news", tags=["Market Intelligence Platform"])
logger = logging.getLogger(__name__)

# Singletons (In production, use dependency injection)
config_manager = ConfigManager()
collector = NewsCollector(config_manager)
tagger = CompanyTagger()
classifier = EventClassifier()
sentiment_engine = SentimentEngine()
scorer = NewsImportanceScorer()
memory = MarketMemoryEngine()

@router.get("/latest")
async def get_latest_news(limit: int = 20, db: Session = Depends(get_db)):
    from market_intelligence.storage.models import Article
    articles = db.query(Article).order_by(Article.published_time.desc()).limit(limit).all()
    return {"articles": articles}

@router.post("/process")
async def process_news_pipeline(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers the full pipeline: Fetch -> Parse -> Tag -> Classify -> Sentiment -> Score"""
    
    def run_pipeline():
        logger.info("Starting Market Intelligence Pipeline...")
        # 1. Ingestion & Deduplication
        new_articles = collector.fetch_all(db)
        if not new_articles:
            logger.info("No new articles to process.")
            return
            
        # 2. Process each new article
        for article in new_articles:
            # Parse
            clean_text = ArticleParser.parse_summary(article.summary)
            full_text = f"{article.title} {clean_text}"
            
            # Tag
            tags = tagger.tag_companies(full_text)
            article.company_tags = ",".join(tags) if tags else None
            
            # Classify Event
            event = classifier.classify(full_text)
            article.event_classification = event
            
            # Sentiment
            sent_res = sentiment_engine.analyze(full_text)
            article.sentiment_label = sent_res["label"]
            article.sentiment_score = sent_res["score"]
            article.sentiment_confidence = sent_res["confidence"]
            
            # Score Importance
            importance = scorer.score(article.source, event, sent_res["confidence"])
            article.importance_score = importance
            
            article.processed = True
            
            # DB Update
            db.commit()
            
            # Market Memory Insights
            if tags:
                for symbol in tags:
                    context = memory.get_historical_context(symbol, event, sent_res["label"])
                    if context:
                        insight = memory.generate_insight_text(symbol, event, context)
                        logger.info(f"MARKET MEMORY INSIGHT: {insight}")
                        # In production, this insight is routed to D2 Feature Store and AI Supervisor.
                        
        logger.info(f"Pipeline complete. Processed {len(new_articles)} articles.")

    background_tasks.add_task(run_pipeline)
    return {"status": "accepted", "message": "Market Intelligence pipeline started in background."}
