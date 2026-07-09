import asyncio
from typing import Dict, Any, List

from app.ai.technical_agent import TechnicalAgent
from app.ai.breakout_agent import BreakoutAgent
from app.ai.momentum_agent import MomentumAgent
from app.ai.volume_agent import VolumeAgent
from app.ai.market_agent import MarketAgent
from app.ai.macro_agent import MacroAgent
from app.ai.sentiment_agent import SentimentAgent
from app.ai.risk_agent import RiskAgent
from app.ai.portfolio_agent import PortfolioAgent

from app.ai.adaptive_weight_engine import AdaptiveWeightEngine
from app.ai.consensus_engine import ConsensusEngine
from app.ai.supervisor_agent import SupervisorAgent
from app.ai.explainability_engine import ExplainabilityEngine
from app.ai.base_agent import AgentResponse

class AIOrchestrator:
    def __init__(self):
        self.agents = [
            TechnicalAgent(),
            BreakoutAgent(),
            MomentumAgent(),
            VolumeAgent(),
            MarketAgent(),
            MacroAgent(),
            SentimentAgent(),
            RiskAgent(),
            PortfolioAgent()
        ]
        self.weight_engine = AdaptiveWeightEngine()
        self.consensus_engine = ConsensusEngine()
        self.supervisor = SupervisorAgent()
        self.explainer = ExplainabilityEngine()
        
    async def evaluate_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs all AI agents concurrently on the candidate data.
        """
        # 1. Run all agents concurrently
        tasks = [agent.evaluate(candidate_data) for agent in self.agents]
        responses: List[AgentResponse] = await asyncio.gather(*tasks)
        
        # 2. Get dynamic weights
        market_regime = candidate_data.get("regime", "Neutral")
        weights = self.weight_engine.get_weights(market_regime)
        
        # 3. Compute Consensus
        consensus = self.consensus_engine.calculate(responses, weights)
        
        # 4. Supervisor Decision
        decision = self.supervisor.finalize_decision(consensus, responses, market_regime)
        
        # 5. Explainability
        explanation = self.explainer.generate_explanation(responses)
        
        # Extract individual agent scores for reporting
        agent_scores = {f"{r.agent_name}_Score": r.score for r in responses}
        
        # Combine all into final payload
        return {
            **agent_scores,
            "adaptive_weights": weights,
            **decision,
            **explanation
        }
