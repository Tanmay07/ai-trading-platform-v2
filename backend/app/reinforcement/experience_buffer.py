import sqlite3
import json
from pathlib import Path

class ExperienceBuffer:
    def __init__(self):
        self.db_path = "./data/experience_buffer.db"
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                state TEXT,
                action TEXT,
                reward REAL,
                next_state TEXT,
                trade_outcome TEXT,
                market_regime TEXT,
                model_version TEXT,
                ai_consensus REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add_experience(self, exp: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO experiences 
            (timestamp, state, action, reward, next_state, trade_outcome, market_regime, model_version, ai_consensus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exp.get("timestamp"),
            json.dumps(exp.get("state", {})),
            json.dumps(exp.get("action", {})),
            exp.get("reward", 0.0),
            json.dumps(exp.get("next_state", {})),
            json.dumps(exp.get("trade_outcome", {})),
            exp.get("market_regime", "Neutral"),
            exp.get("model_version", "v1"),
            exp.get("ai_consensus", 50.0)
        ))
        conn.commit()
        conn.close()

    def sample_batch(self, batch_size: int = 32):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM experiences ORDER BY RANDOM() LIMIT ?", (batch_size,))
        rows = c.fetchall()
        conn.close()
        
        columns = ["id", "timestamp", "state", "action", "reward", "next_state", "trade_outcome", "market_regime", "model_version", "ai_consensus"]
        return [dict(zip(columns, row)) for row in rows]
        
    def get_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM experiences")
        count = c.fetchone()[0]
        conn.close()
        return count
