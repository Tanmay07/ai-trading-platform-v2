from typing import Dict, Any, Tuple
import yaml

class OrderSimulator:
    def __init__(self):
        with open("config/paper_trading.yaml", "r") as f:
            self.config = yaml.safe_load(f)["paper_trading"]
            
    def simulate_fill(self, intended_price: float, shares: float, order_type: str = "BUY") -> Tuple[float, float]:
        """
        Simulates execution slippage and brokerage to return actual fill price and total cost/revenue.
        """
        slippage_bps = self.config["slippage"].get("basis_points", 10) if self.config["slippage"].get("enabled") else 0
        brokerage_bps = self.config["brokerage"].get("rate_bps", 5) if self.config["brokerage"].get("enabled") else 0
        
        # Calculate slippage impact
        slippage_pct = slippage_bps / 10000.0
        if order_type == "BUY":
            fill_price = intended_price * (1 + slippage_pct) # Worse price for buy
        else:
            fill_price = intended_price * (1 - slippage_pct) # Worse price for sell
            
        gross_value = fill_price * shares
        brokerage_cost = gross_value * (brokerage_bps / 10000.0)
        
        if order_type == "BUY":
            net_cost = gross_value + brokerage_cost
            return fill_price, net_cost
        else:
            net_revenue = gross_value - brokerage_cost
            return fill_price, net_revenue
