from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from ai_cio.schemas import ChatRequest, ChatResponse, MorningBriefingResponse
from ai_cio.orchestrator import AICIOService
from ai_cio.reports.morning_brief import ReportGenerator
from ai_cio.database import get_db, ConversationLog
from app.infrastructure.auth.jwt_auth import get_current_user
from portfolio_manager.portfolio_service import PortfolioService
from portfolio_manager.database import get_db as get_portfolio_db
from market_data.service import MarketDataService
from market_data.providers.jugaad_provider import JugaadProvider

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def aicio_chat(
    req: ChatRequest,
    user: dict = Depends(get_current_user),
    ai_db: Session = Depends(get_db),
    port_db: Session = Depends(get_portfolio_db)
):
    # Construct Contexts
    mds = MarketDataService(JugaadProvider())
    ps = PortfolioService(port_db, mds)
    holdings = ps.get_holdings(req.portfolio_id, user["user_id"])
    
    portfolio_context = {
        "holdings": [{"symbol": h.symbol, "shares": h.shares, "current_value": h.current_value} for h in holdings]
    }
    
    market_context = {
        "recent_events": [{"event": "RBI Policy", "impact": "HIGH"}] # Mocked for now
    }
    
    # Save user message
    user_msg = ConversationLog(
        user_id=user["user_id"],
        portfolio_id=req.portfolio_id,
        role="user",
        message=req.query
    )
    ai_db.add(user_msg)
    ai_db.commit()
    
    # Orchestrate AI response
    aicio = AICIOService()
    response = await aicio.handle_chat(req, portfolio_context, market_context)
    
    # Save AI response
    ai_msg = ConversationLog(
        user_id=user["user_id"],
        portfolio_id=req.portfolio_id,
        role="assistant",
        message=response.reply,
        context_used_json={"sources": response.sources}
    )
    ai_db.add(ai_msg)
    ai_db.commit()
    
    return response

@router.get("/briefing", response_model=MorningBriefingResponse)
def get_morning_briefing(
    portfolio_id: int,
    user: dict = Depends(get_current_user)
):
    rg = ReportGenerator()
    return rg.generate_morning_brief(portfolio_context={}, market_context={})
