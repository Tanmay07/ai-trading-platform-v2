from adaptive_learning.db import AdaptiveLearningDB

class InvestmentJournal:
    def __init__(self):
        self.db = AdaptiveLearningDB()
        
    def update_human_decision(self, recommendation_id: int, decision: str):
        """
        Decision should be 'APPROVED' or 'IGNORED' or 'OVERRIDDEN'
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE investment_journal
                SET human_decision = ?
                WHERE id = ?
            ''', (decision, recommendation_id))
            conn.commit()
            
    def record_outcome(self, recommendation_id: int, outcome_return: float, lessons: str = None):
        """
        Record the final return from the trade for future learning.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE investment_journal
                SET outcome_return = ?, lessons_learned = ?
                WHERE id = ?
            ''', (outcome_return, lessons, recommendation_id))
            conn.commit()
            
    def get_recent_entries(self, limit: int = 50):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM investment_journal 
                ORDER BY date DESC, id DESC 
                LIMIT ?
            ''', (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
