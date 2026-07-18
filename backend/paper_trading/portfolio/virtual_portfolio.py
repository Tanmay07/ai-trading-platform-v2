from adaptive_learning.db import AdaptiveLearningDB
from datetime import datetime
import json
import logging

logger = logging.getLogger("VirtualPortfolio")

class VirtualPortfolio:
    def __init__(self, initial_capital: float = 1000000.0, transaction_cost_pct: float = 0.001):
        self.db = AdaptiveLearningDB()
        self.initial_capital = initial_capital
        self.transaction_cost_pct = transaction_cost_pct
        self._ensure_initial_snapshot()
        
    def _ensure_initial_snapshot(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cash_balance FROM portfolio_history ORDER BY date ASC LIMIT 1")
            res = cursor.fetchone()
            if not res:
                today = datetime.now().strftime("%Y-%m-%d")
                cursor.execute('''
                    INSERT INTO portfolio_history (date, cash_balance, unrealized_pnl, total_value)
                    VALUES (?, ?, ?, ?)
                ''', (today, self.initial_capital, 0.0, self.initial_capital))
                conn.commit()

    def record_manual_entry(self, symbol: str, quantity: float, entry_price: float, ai_confidence: float = None):
        """
        Records a human-approved trade entry.
        """
        cost = quantity * entry_price
        fee = cost * self.transaction_cost_pct
        total_deduction = cost + fee
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check cash
            cursor.execute("SELECT cash_balance FROM portfolio_history ORDER BY date DESC LIMIT 1")
            current_cash = cursor.fetchone()[0]
            
            if current_cash < total_deduction:
                logger.warning(f"Insufficient cash for {symbol}. Needed: {total_deduction}, Available: {current_cash}")
                # We still allow it for paper trading, but log a warning.
            
            # Insert Position
            cursor.execute('''
                INSERT INTO positions (symbol, entry_date, entry_price, quantity, ai_confidence, status)
                VALUES (?, ?, ?, ?, ?, 'OPEN')
            ''', (symbol, today, entry_price, quantity, ai_confidence))
            
            # Update Cash Snapshot
            new_cash = current_cash - total_deduction
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio_history (date, cash_balance, unrealized_pnl, total_value)
                VALUES (?, ?, ?, (SELECT total_value FROM portfolio_history ORDER BY date DESC LIMIT 1))
            ''', (today, new_cash, 0.0)) # PnL will be updated via MTM
            
            conn.commit()
            
    def record_manual_exit(self, position_id: int, exit_price: float, exit_reason: str):
        """
        Records a human-initiated exit for an open position.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity, entry_price, symbol FROM positions WHERE id = ? AND status = 'OPEN'", (position_id,))
            res = cursor.fetchone()
            
            if not res:
                raise ValueError("Open position not found.")
                
            quantity, entry_price, symbol = res
            
            proceeds = quantity * exit_price
            fee = proceeds * self.transaction_cost_pct
            net_proceeds = proceeds - fee
            
            # Update Position
            cursor.execute('''
                UPDATE positions
                SET status = 'CLOSED', exit_date = ?, exit_price = ?, exit_reason = ?
                WHERE id = ?
            ''', (today, exit_price, exit_reason, position_id))
            
            # Update Cash
            cursor.execute("SELECT cash_balance FROM portfolio_history ORDER BY date DESC LIMIT 1")
            current_cash = cursor.fetchone()[0]
            new_cash = current_cash + net_proceeds
            
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio_history (date, cash_balance, unrealized_pnl, total_value)
                VALUES (?, ?, ?, (SELECT total_value FROM portfolio_history ORDER BY date DESC LIMIT 1))
            ''', (today, new_cash, 0.0))
            
            conn.commit()
            
    def get_portfolio_summary(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio_history ORDER BY date DESC LIMIT 1")
            hist = cursor.fetchone()
            
            cursor.execute("SELECT * FROM positions WHERE status = 'OPEN'")
            columns = [desc[0] for desc in cursor.description]
            positions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if not hist:
                return {}
                
            return {
                "date": hist[0],
                "cash_balance": hist[1],
                "unrealized_pnl": hist[2],
                "total_value": hist[3],
                "open_positions": positions
            }
