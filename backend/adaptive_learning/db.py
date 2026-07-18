import sqlite3
import os
import json

class AdaptiveLearningDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'paper_trading.db')
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Virtual Portfolio - Open Positions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                ai_confidence REAL,
                status TEXT DEFAULT 'OPEN',
                exit_date TEXT,
                exit_price REAL,
                exit_reason TEXT
            )
            ''')
            
            # Virtual Portfolio - Cash and Value Snapshots
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                date TEXT PRIMARY KEY,
                cash_balance REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                total_value REAL NOT NULL
            )
            ''')
            
            # Investment Journal / Recommendations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS investment_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                confidence REAL,
                expected_return REAL,
                shap_explanation TEXT,
                human_decision TEXT,
                outcome_return REAL,
                lessons_learned TEXT
            )
            ''')
            
            # Drift Tracking
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_drift (
                date TEXT PRIMARY KEY,
                prediction_drift_score REAL,
                feature_drift_score REAL,
                retraining_recommended BOOLEAN
            )
            ''')
            
            conn.commit()
