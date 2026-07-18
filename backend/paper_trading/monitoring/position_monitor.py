import pandas as pd
from datetime import datetime
from adaptive_learning.db import AdaptiveLearningDB
from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio
import logging

import os

logger = logging.getLogger("PositionMonitor")

class PositionMonitor:
    def __init__(self, dataset_path: str = None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dataset_v5.parquet')
        self.db = AdaptiveLearningDB()
        self.dataset_path = dataset_path
        self.portfolio = VirtualPortfolio()
        
    def run_daily_mtm(self):
        """
        Runs daily Mark-To-Market for the virtual portfolio.
        Reads the latest price for open positions from the dataset.
        """
        df = pd.read_parquet(self.dataset_path)
        if 'Date' in df.index.names:
            df = df.reset_index()
        latest_date = df['Date'].max()
        latest_data = df[df['Date'] == latest_date].set_index('Symbol')
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, symbol, quantity, entry_price FROM positions WHERE status = 'OPEN'")
            open_positions = cursor.fetchall()
            
            total_unrealized_pnl = 0.0
            
            for pos in open_positions:
                pos_id, sym, qty, entry_price = pos
                if sym in latest_data.index:
                    current_price = latest_data.loc[sym, 'Close']
                    unrealized = (current_price - entry_price) * qty
                    total_unrealized_pnl += unrealized
                else:
                    logger.warning(f"Could not find latest price for {sym}")
                    
            # Update Cash Snapshot
            cursor.execute("SELECT cash_balance FROM portfolio_history ORDER BY date DESC LIMIT 1")
            res = cursor.fetchone()
            current_cash = res[0] if res else self.portfolio.initial_capital
            
            total_value = current_cash + total_unrealized_pnl + sum(qty * entry_price for _, _, qty, entry_price in open_positions)
            
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio_history (date, cash_balance, unrealized_pnl, total_value)
                VALUES (?, ?, ?, ?)
            ''', (today, current_cash, total_unrealized_pnl, total_value))
            
            conn.commit()
        logger.info(f"Daily MTM complete. Total Value: {total_value}, Unrealized PnL: {total_unrealized_pnl}")
