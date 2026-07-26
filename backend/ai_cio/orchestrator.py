import logging
from typing import Dict, Any, List
from .agents.portfolio_analyst import PortfolioAnalystAgent
from .agents.market_strategist import MarketStrategistAgent
from .schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

class AICIOService:
    """
    Module 1 - Orchestrator.
    Coordinates the sub-agents and synthesizes a final response.
    """
    def __init__(self):
        self.portfolio_analyst = PortfolioAnalystAgent()
        self.market_strategist = MarketStrategistAgent()
        
    async def handle_chat(self, request: ChatRequest, portfolio_context: Dict[str, Any], market_context: Dict[str, Any]) -> ChatResponse:
        """
        Routes the user's natural language query to the appropriate agents, 
        collects their insights, and synthesizes the final reply.
        """
        logger.info(f"AI-CIO processing query: '{request.query}' for portfolio {request.portfolio_id}")
        
        # In a full LLM setup, an LLM Router would decide which agents to call.
        # Here we just call both and synthesize.
        
        pa_insight = await self.portfolio_analyst.analyze(request.query, portfolio_context)
        ms_insight = await self.market_strategist.analyze(request.query, market_context)
        
        # Synthesize final response (mocked Synthesis)
        final_reply = f"{pa_insight}\n\nFrom a market perspective: {ms_insight}"
        
        return ChatResponse(
            reply=final_reply,
            sources=["PortfolioAnalyst", "MarketStrategist"],
            suggested_actions=["Review HDFCBANK exposure", "Read RBI Policy Update"]
        )
