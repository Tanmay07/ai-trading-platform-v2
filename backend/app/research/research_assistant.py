from app.research.knowledge_base import KnowledgeBase

class ResearchAssistant:
    def __init__(self):
        self.kb = KnowledgeBase()
        
    def summarize_findings(self) -> str:
        """
        AI Agent summarizes recent experiments for the user.
        """
        return "Based on recent experiments, RSI thresholds < 30 are underperforming in the current volatility regime."
