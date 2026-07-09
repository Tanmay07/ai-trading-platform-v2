class KnowledgeBase:
    def __init__(self):
        self.kb = []
        
    def add_insight(self, insight: str):
        self.kb.append(insight)
        
    def search(self, query: str) -> list:
        return self.kb
