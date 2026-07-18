from adaptive_learning.db import AdaptiveLearningDB
import pandas as pd

class AIVsHumanAnalytics:
    def __init__(self):
        self.db = AdaptiveLearningDB()
        
    def get_analytics(self):
        with self.db.get_connection() as conn:
            # Get journal stats
            journal_df = pd.read_sql_query("SELECT * FROM investment_journal", conn)
            
            if journal_df.empty:
                return {
                    "total_recommendations": 0,
                    "approved": 0,
                    "ignored": 0,
                    "overridden": 0,
                    "ai_accuracy": 0.0,
                    "human_accuracy": 0.0,
                    "override_success_rate": 0.0
                }
                
            total = len(journal_df)
            approved = len(journal_df[journal_df['human_decision'] == 'APPROVED'])
            ignored = len(journal_df[journal_df['human_decision'] == 'IGNORED'])
            overridden = len(journal_df[journal_df['human_decision'] == 'OVERRIDDEN'])
            
            # Simple simulation of accuracy based on outcomes (outcome > 0 is success)
            # In real system, we'd wait for positions to close.
            completed = journal_df.dropna(subset=['outcome_return'])
            if len(completed) > 0:
                ai_correct = len(completed[(completed['recommendation'] == 'BUY') & (completed['outcome_return'] > 0)])
                ai_accuracy = ai_correct / len(completed) if len(completed) > 0 else 0
                
                overrides = completed[completed['human_decision'] == 'OVERRIDDEN']
                human_correct = len(overrides[overrides['outcome_return'] > 0])
                override_success = human_correct / len(overrides) if len(overrides) > 0 else 0
            else:
                ai_accuracy = 0.0
                override_success = 0.0
                
            return {
                "total_recommendations": total,
                "approved": approved,
                "ignored": ignored,
                "overridden": overridden,
                "ai_accuracy": ai_accuracy,
                "human_accuracy": override_success, # simplification
                "override_success_rate": override_success
            }
