import sqlite3
import json
from datetime import datetime
from pathlib import Path

class ExperimentTracker:
    def __init__(self):
        self.db_path = "./data/experiments.db"
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                timestamp TEXT,
                parameters TEXT,
                metrics TEXT,
                features TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_experiment(self, model_name: str, parameters: dict, metrics: dict, features: list):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO experiments (model_name, timestamp, parameters, metrics, features)
            VALUES (?, ?, ?, ?, ?)
        ''', (model_name, datetime.utcnow().isoformat(), json.dumps(parameters), json.dumps(metrics), json.dumps(features)))
        conn.commit()
        conn.close()

    def get_leaderboard(self, metric: str = "roc_auc"):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM experiments", conn)
        conn.close()
        
        if df.empty:
            return []
            
        # Parse metrics
        import pandas as pd
        
        results = []
        for _, row in df.iterrows():
            m = json.loads(row['metrics'])
            if metric in m:
                results.append({
                    "id": row['id'],
                    "model_name": row['model_name'],
                    "timestamp": row['timestamp'],
                    "metric_value": m[metric]
                })
                
        results.sort(key=lambda x: x["metric_value"], reverse=True)
        return results
