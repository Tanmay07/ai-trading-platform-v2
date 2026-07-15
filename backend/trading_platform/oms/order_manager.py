import sqlite3
import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderManager:
    """
    Manages the lifecycle of all trading orders, persisting them to a local SQLite database.
    """
    def __init__(self, db_path: str = "trading_orders.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), f"../../../{db_path}")
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    quantity INTEGER,
                    side TEXT,
                    order_type TEXT,
                    price REAL,
                    status TEXT,
                    timestamp TEXT,
                    message TEXT,
                    meta TEXT
                )
            """)
            conn.commit()
            
    def save_order(self, order_data: Dict[str, Any]):
        """Persists or updates an order in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO orders 
                (id, symbol, quantity, side, order_type, price, status, timestamp, message, meta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_data.get("order_id"),
                order_data.get("symbol"),
                order_data.get("quantity"),
                order_data.get("side"),
                order_data.get("order_type", "MARKET"),
                order_data.get("price", 0.0),
                order_data.get("status", "PENDING"),
                order_data.get("timestamp", datetime.now().isoformat()),
                order_data.get("message", ""),
                json.dumps(order_data.get("meta", {}))
            ))
            conn.commit()
            
    def get_order(self, order_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if row:
                return dict(row)
        return {}
        
    def get_all_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM orders ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]
