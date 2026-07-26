import pytest
from ai_cio.orchestrator import AICIOService
from ai_cio.schemas import ChatRequest

@pytest.mark.asyncio
async def test_aicio_orchestrator():
    aicio = AICIOService()
    
    req = ChatRequest(
        portfolio_id=1,
        query="summarize my portfolio and today's market"
    )
    
    portfolio_context = {
        "holdings": [{"symbol": "HDFCBANK", "shares": 100, "current_value": 150000}]
    }
    
    market_context = {
        "recent_events": [{"event": "RBI Policy Update", "impact": "HIGH"}]
    }
    
    response = await aicio.handle_chat(req, portfolio_context, market_context)
    
    assert response is not None
    assert "HDFCBANK" in response.reply
    assert "RBI" in response.reply
    assert "PortfolioAnalyst" in response.sources
    assert "MarketStrategist" in response.sources
