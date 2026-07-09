import sqlite3
import json
from pathlib import Path
from datetime import datetime

class PortfolioRegistry:
    def __init__(self):
        self.db_path = "./data/portfolio_registry.db"
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                holdings TEXT,
                cash REAL,
                total_value REAL,
                metrics TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_snapshot(self, holdings: dict, cash: float, total_value: float, metrics: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO portfolio_snapshots (timestamp, holdings, cash, total_value, metrics)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            json.dumps(holdings),
            cash,
            total_value,
            json.dumps(metrics)
        ))
        conn.commit()
        conn.close()
        
    def get_latest_snapshot(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT holdings, cash, total_value, metrics FROM portfolio_snapshots ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        
        if not row:
            return {"holdings": {}, "cash": 1000000.0, "total_value": 1000000.0, "metrics": {}}
            
        return {
            "holdings": json.loads(row[0]),
            "cash": row[1],
            "total_value": row[2],
            "metrics": json.loads(row[3])
        }
