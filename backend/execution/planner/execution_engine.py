import yaml
import logging
from typing import List, Dict, Any

from execution.entry.entry_optimizer import EntryOptimizer
from execution.sizing.risk_budget_engine import RiskBudgetEngine
from execution.exits.stop_loss_engine import StopLossEngine
from execution.exits.target_engine import TargetEngine
from execution.exits.trailing_stop_engine import TrailingStopEngine

logger = logging.getLogger("ExecutionEngine")

class ExecutionEngine:
    def __init__(self):
        with open("config/execution_rules.yaml", "r") as f:
            self.config = yaml.safe_load(f)
            
        self.entry_optimizer = EntryOptimizer()
        self.risk_engine = RiskBudgetEngine(
            max_trade_risk=self.config["risk"]["max_trade_risk"],
            max_portfolio_risk=self.config["risk"]["max_portfolio_risk"]
        )
        self.stop_engine = StopLossEngine(multiplier=self.config["execution"]["stop_loss"]["multiplier"])
        self.target_engine = TargetEngine(min_risk_reward=self.config["execution"]["target"]["minimum_rr"])
        self.trailing_engine = TrailingStopEngine(method=self.config["execution"]["trailing_stop"]["method"])
        
    def generate_execution_plans(self, portfolio_positions: List[Dict[str, Any]], total_capital: float) -> Dict[str, Any]:
        """
        Transforms approved portfolio allocations into structured Execution Plans.
        """
        logger.info(f"Generating execution plans for {len(portfolio_positions)} positions.")
        
        execution_plans = []
        rejected_plans = []
        
        for pos in portfolio_positions:
            # 1. Fetch current market data (Mocked for offline framework)
            current_price = pos.get("current_price", 100.0)
            atr = pos.get("atr", current_price * 0.02)
            pos["current_price"] = current_price
            pos["atr"] = atr
            
            # 2. Entry Strategy Optimization
            strategies = self.entry_optimizer.generate_entry_strategies(pos, current_price)
            best_entry = strategies[0] # Pick the highest scoring
            entry_price = best_entry["entry_price"]
            
            # 3. Stop Loss
            stop_loss = self.stop_engine.generate_stop_loss(entry_price, pos)
            
            # 4. Position Sizing & Risk Budget Validation
            sized_pos = self.risk_engine.validate_and_size(pos, entry_price, stop_loss, total_capital)
            
            if sized_pos["risk_status"] == "REJECTED_INVALID_STOP":
                rejected_plans.append(sized_pos)
                continue
                
            # 5. Targets
            t1, t2, stretch, rr = self.target_engine.generate_targets(entry_price, stop_loss)
            
            if rr < self.config["execution"]["target"]["minimum_rr"]:
                sized_pos["risk_status"] = "REJECTED_POOR_RR"
                rejected_plans.append(sized_pos)
                continue
                
            # 6. Build the Structured Execution Plan
            plan = {
                "symbol": pos["symbol"],
                "action": "BUY", # Currently long-only framework
                "capital_allocated": sized_pos["execution_capital"],
                "risk_dollars": sized_pos["risk_dollars"],
                "risk_status": sized_pos["risk_status"],
                "entry_price": entry_price,
                "entry_strategy": best_entry["name"],
                "stop_loss": stop_loss,
                "target_1": t1,
                "target_2": t2,
                "stretch_target": stretch,
                "trailing_stop": self.trailing_engine.generate_trailing_logic(atr),
                "holding_period": pos.get("expected_holding_days", self.config["execution"]["timeout"]["days"]),
                "risk_reward": rr,
                "confidence": pos.get("confidence", 0.0),
                "trade_quality": pos.get("trade_quality_prediction", 0.0),
                "alternative_entries": strategies[1:]
            }
            execution_plans.append(plan)
            
        # 7. Final Portfolio-Level Risk Validation
        if not self.risk_engine.validate_portfolio_budget(execution_plans, total_capital):
            logger.error("Overall portfolio risk exceeded maximum configured limits!")
            # In a full system, this would trigger a global risk-reduction rebalance.
            
        return {
            "status": "success",
            "execution_plans": execution_plans,
            "rejected_plans": rejected_plans,
            "analytics": {
                "total_plans": len(execution_plans),
                "avg_risk_reward": sum(p["risk_reward"] for p in execution_plans) / max(1, len(execution_plans)),
                "total_risk_dollars": sum(p["risk_dollars"] for p in execution_plans),
                "portfolio_risk_pct": sum(p["risk_dollars"] for p in execution_plans) / max(1.0, total_capital)
            }
        }
