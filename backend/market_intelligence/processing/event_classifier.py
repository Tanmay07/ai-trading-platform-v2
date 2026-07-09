import logging

logger = logging.getLogger(__name__)

class EventClassifier:
    """Classifies news into actionable taxonomy (Earnings, Contracts, Macro)."""
    
    def __init__(self):
        self.categories = {
            "Earnings": ["q1", "q2", "q3", "q4", "quarterly results", "net profit", "ebitda", "revenue"],
            "Corporate": ["dividend", "bonus", "split", "buyback", "rights issue", "merger", "acquisition"],
            "Business": ["order", "contract", "capacity expansion", "patent", "approval"],
            "Risk": ["litigation", "penalty", "sebi", "income tax", "strike", "shutdown"],
            "Macro": ["rbi", "inflation", "interest rates", "budget", "election", "crude"]
        }
        
    def classify(self, text: str) -> str:
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
                
        return "General"
