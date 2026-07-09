import pytest
import asyncio
from app.ai.technical_agent import TechnicalAgent
from app.ai.breakout_agent import BreakoutAgent
from app.ai.momentum_agent import MomentumAgent
from app.ai.volume_agent import VolumeAgent
from app.ai.market_agent import MarketAgent
from app.ai.macro_agent import MacroAgent
from app.ai.sentiment_agent import SentimentAgent
from app.ai.risk_agent import RiskAgent
from app.ai.portfolio_agent import PortfolioAgent
from app.ai.consensus_engine import ConsensusEngine, ConsensusResult
from app.ai.adaptive_weight_engine import AdaptiveWeightEngine
from app.ai.supervisor_agent import SupervisorAgent
from app.ai.explainability_engine import ExplainabilityEngine
from app.ai.base_agent import AgentResponse

@pytest.mark.asyncio
async def test_technical_agent():
    agent = TechnicalAgent()
    data = {"ATR_14": 1, "Close": 100, "EMA_20": 110, "EMA_50": 100, "RSI_14": 60}
    res = await agent.evaluate(data)
    assert res.recommendation == "BUY"
    assert res.score > 70
    assert len(res.reasons) > 0

@pytest.mark.asyncio
async def test_breakout_agent():
    agent = BreakoutAgent()
    data = {"breakout_score": 90, "VCP_Pattern": True, "Dist_to_Res": 1}
    res = await agent.evaluate(data)
    assert res.recommendation == "BUY"

@pytest.mark.asyncio
async def test_momentum_agent():
    agent = MomentumAgent()
    res = await agent.evaluate({"Relative_Strength": 1.1, "MACD": 2, "MACD_Signal": 1})
    assert res.recommendation == "BUY"

@pytest.mark.asyncio
async def test_volume_agent():
    agent = VolumeAgent()
    res = await agent.evaluate({"Relative_Volume": 3.0, "OBV_Trend": "Up"})
    assert res.score == 95

def test_consensus_engine():
    engine = ConsensusEngine()
    r1 = AgentResponse(score=90, confidence=90, recommendation="BUY", agent_name="AgentA")
    r2 = AgentResponse(score=20, confidence=90, recommendation="SELL", agent_name="AgentB")
    
    weights = {"AgentA": 0.8, "AgentB": 0.2}
    res = engine.calculate([r1, r2], weights)
    
    assert res.dominant_recommendation == "BUY"
    assert res.agreement_percent == 80.0
    assert res.final_score == 76.0

def test_adaptive_weights():
    engine = AdaptiveWeightEngine()
    w_bull = engine.get_weights("Strong Bull")
    w_bear = engine.get_weights("Bear")
    
    assert w_bull["TechnicalAgent"] == 0.30
    assert w_bear["RiskAgent"] == 0.30

def test_supervisor():
    sup = SupervisorAgent()
    cons = ConsensusResult(
        final_score=80, 
        agreement_percent=50, 
        conflict_score=50, 
        dominant_recommendation="BUY",
        weighted_confidence=80
    )
    # High conflict should downgrade BUY to HOLD
    res = sup.finalize_decision(cons, [], "Neutral")
    assert res["final_recommendation"] == "HOLD"
    
def test_explainability():
    engine = ExplainabilityEngine()
    r1 = AgentResponse(score=90, confidence=90, recommendation="BUY", agent_name="AgentA", reasons=["+ Good factor", "- Bad factor"])
    res = engine.generate_explanation([r1])
    assert "top_positive_factors" in res
    assert "good factor" in res["human_readable_summary"].lower()
