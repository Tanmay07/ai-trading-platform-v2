from fastapi import APIRouter
from pydantic import BaseModel
from adaptive_learning.recommendations.recommendation_engine import RecommendationEngine
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio
from adaptive_learning.engine.journal import InvestmentJournal
from paper_trading.monitoring.position_monitor import PositionMonitor
from adaptive_learning.drift.model_drift_detector import ModelDriftDetector
from adaptive_learning.analytics.ai_vs_human import AIVsHumanAnalytics

router = APIRouter()

class ManualTrade(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    ai_confidence: float = None
    recommendation_id: int = None

class ManualExit(BaseModel):
    position_id: int
    exit_price: float
    exit_reason: str
    
class JournalDecision(BaseModel):
    recommendation_id: int
    decision: str

@router.get("/recommendations")
def get_daily_recommendations():
    engine = RecommendationEngine()
    recs = engine.generate_daily_recommendations(top_k=5)
    return {"recommendations": recs}

@router.post("/trade/entry")
def record_manual_entry(trade: ManualTrade):
    portfolio = VirtualPortfolio()
    portfolio.record_manual_entry(trade.symbol, trade.quantity, trade.entry_price, trade.ai_confidence)
    
    if trade.recommendation_id:
        journal = InvestmentJournal()
        journal.update_human_decision(trade.recommendation_id, "APPROVED")
        
    return {"status": "Trade recorded successfully"}

@router.post("/trade/exit")
def record_manual_exit(trade: ManualExit):
    portfolio = VirtualPortfolio()
    portfolio.record_manual_exit(trade.position_id, trade.exit_price, trade.exit_reason)
    return {"status": "Exit recorded successfully"}

@router.get("/portfolio")
def get_portfolio_summary():
    portfolio = VirtualPortfolio()
    monitor = PositionMonitor()
    
    # Force a live MTM update before returning
    monitor.run_daily_mtm()
    
    return {"portfolio": portfolio.get_portfolio_summary()}

@router.get("/journal")
def get_journal():
    journal = InvestmentJournal()
    return {"journal": journal.get_recent_entries()}

@router.post("/journal/decision")
def update_journal_decision(req: JournalDecision):
    journal = InvestmentJournal()
    journal.update_human_decision(req.recommendation_id, req.decision)
    return {"status": "Updated decision"}

@router.get("/analytics/ai_vs_human")
def get_ai_vs_human_analytics():
    analytics = AIVsHumanAnalytics()
    return analytics.get_analytics()

@router.get("/analytics/drift")
def get_model_drift():
    detector = ModelDriftDetector()
    return {"drift": detector.check_drift()}
