from typing import Dict, Any
from abc import ABC, abstractmethod

class CommitteeVote:
    def __init__(self, member_name: str, vote: str, confidence: int, reason: str = ""):
        self.member_name = member_name
        self.vote = vote # 'APPROVE', 'REVIEW', 'REJECT'
        self.confidence = confidence # 0-100
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "member_name": self.member_name,
            "vote": self.vote,
            "confidence": self.confidence,
            "reason": self.reason
        }

class CommitteeMember(ABC):
    """
    Plugin-based interface for Investment Committee Members.
    Every intelligence engine must implement this interface to cast a vote.
    """
    
    @property
    @abstractmethod
    def member_name(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, trade_context: Dict[str, Any]) -> CommitteeVote:
        """
        Evaluate the trade context and return a CommitteeVote.
        """
        pass
