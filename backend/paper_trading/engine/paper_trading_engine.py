import logging
import uuid
from typing import Dict, Any, List

from paper_trading.portfolio.virtual_portfolio import VirtualPortfolio
from paper_trading.engine.order_simulator import OrderSimulator
from paper_trading.monitoring.position_monitor import PositionMonitor
# from paper_trading.attribution.attribution_engine import AttributionEngine

logger = logging.getLogger("PaperTradingEngine")

class PaperTradingEngine:
    def __init__(self, attribution_engine=None):
        self.portfolio = VirtualPortfolio()
        self.order_simulator = OrderSimulator()
        self.position_monitor = PositionMonitor()
        self.attribution_engine = attribution_engine
        
    def execute_committee_recommendation(self, recommendation: Dict[str, Any]):
        """
        Takes a BUY recommendation from the Investment Committee and executes it.
        """
        if recommendation.get("final_decision") != "BUY":
            logger.info("Ignoring non-BUY recommendation.")
            return False
            
        symbol = recommendation.get("symbol")
        context = recommendation.get("context_snapshot", {})
        execution_plan = context.get("execution", {})
        
        intended_entry = execution_plan.get("entry_price", 100.0)
        capital_allocated = execution_plan.get("capital_allocated", 10000.0)
        intended_shares = capital_allocated / intended_entry
        
        fill_price, net_cost = self.order_simulator.simulate_fill(intended_entry, intended_shares, "BUY")
        
        success = self.portfolio.add_position(symbol, fill_price, intended_shares, context)
        if success:
            logger.info(f"Paper Trade Executed: Bought {intended_shares} of {symbol} at {fill_price}")
        return success
        
    def process_market_tick(self, market_prices: Dict[str, float]):
        """
        Simulates the passing of time / a new market day.
        """
        # 1. Update prices in portfolio
        self.portfolio.update_market_prices(market_prices)
        
        # 2. Monitor for exits
        exit_signals = self.position_monitor.check_exits(self.portfolio.open_positions)
        
        # 3. Execute exits
        for exit_signal in exit_signals:
            symbol = exit_signal["symbol"]
            intended_exit = exit_signal["exit_price"]
            reason = exit_signal["reason"]
            
            # Find shares to sell
            pos = self.portfolio.open_positions.get(symbol)
            if not pos: continue
            
            fill_price, net_revenue = self.order_simulator.simulate_fill(intended_exit, pos["shares"], "SELL")
            
            self.portfolio.close_position(symbol, fill_price, reason)
            logger.info(f"Paper Trade Exited: Sold {symbol} at {fill_price} due to {reason}")
            
            # 4. Trigger Attribution
            if self.attribution_engine:
                closed_pos = self.portfolio.closed_positions[-1]
                self.attribution_engine.attribute_trade(closed_pos)
                
        return self.portfolio.get_summary()
