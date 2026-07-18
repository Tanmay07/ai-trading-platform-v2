from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseStrategy(ABC):
    """
    Abstract Base Class that all trading strategies must implement.
    Ensures identical APIs across independent plugins in the Signal Layer.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def generate_signals(self) -> List[Dict[str, Any]]:
        """Generates candidate trading signals based on alpha features."""
        pass

    @abstractmethod
    def score_opportunities(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scores and filters signals based on strategy-specific logic."""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }
