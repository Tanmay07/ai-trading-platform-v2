from typing import Dict, Any
from app.hfos.ai_committee import AICommittee

class InvestmentCommittee:
    def __init__(self):
        self.agents = AICommittee()
        self.required_votes = 4
        
    def review_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chairperson summarizes votes.
        """
        votes = self.agents.vote_on_trade(recommendation)
        buy_votes = sum(1 for v in votes if v["vote"] == "BUY")
        
        approved = buy_votes >= self.required_votes
        
        return {
            "status": "APPROVED" if approved else "REJECTED",
            "votes_for": buy_votes,
            "total_votes": len(votes),
            "reason": "Majority consensus reached." if approved else "Insufficient votes."
        }
