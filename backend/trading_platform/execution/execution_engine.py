import logging
import yaml
import os
from typing import Dict, Any, List
from trading_platform.brokers.broker_factory import BrokerFactory
from trading_platform.oms.order_manager import OrderManager
from trading_platform.oms.position_manager import PositionManager
from trading_platform.oms.risk_validator import RiskValidator
from app.notifications.notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """
    Core engine that receives trading signals (from AI models or user) and routes them through the OMS.
    """
    def __init__(self):
        self.broker = BrokerFactory.get_broker()
        self.order_manager = OrderManager()
        self.position_manager = PositionManager()
        self.risk_validator = RiskValidator()
        self.notifier = NotificationManager()
        
        # Load config for execution mode
        config_path = os.path.join(os.path.dirname(__file__), "../../../config/trading.yaml")
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception:
            self.config = {"execution_mode": "manual"}
            
    def process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives an AI trading signal, validates it, and generates an order payload.
        """
        symbol = signal.get("symbol")
        action = signal.get("action", "BUY") # BUY / SELL
        confidence = signal.get("confidence", 0.5)
        current_price = signal.get("current_price", 100.0) # Mock price
        
        # 1. Size Position (Simple fixed for now, e.g., 50 shares)
        # In a real system, use Kelly Criterion or % of portfolio
        quantity = 50
        
        order_payload = {
            "symbol": symbol,
            "side": action,
            "quantity": quantity,
            "price": current_price,
            "order_type": "MARKET"
        }
        
        # 2. Validate Risk
        portfolio = self.position_manager.get_portfolio_summary()
        val_res = self.risk_validator.validate_order(symbol, quantity, current_price, action, portfolio)
        
        if not val_res["valid"]:
            logger.warning(f"Order rejected by Risk Validator: {val_res['reason']}")
            self.notifier.notify(f"Risk Reject: {symbol} - {val_res['reason']}")
            return {"status": "REJECTED", "reason": val_res["reason"]}
            
        # 3. Execution Mode Check
        mode = self.config.get("execution_mode", "manual")
        if mode == "manual":
            # Just save to DB as PENDING for user approval
            order_payload["status"] = "PENDING_APPROVAL"
            order_payload["message"] = "Awaiting manual approval"
            self.order_manager.save_order(order_payload)
            self.notifier.notify(f"Pending Trade Approval: {action} {quantity} {symbol}")
            return order_payload
            
        # 4. Autonomous Execution
        return self.execute_order(order_payload)
        
    def execute_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sends the order to the broker and records the result."""
        res = self.broker.place_order(
            symbol=order_payload["symbol"],
            quantity=order_payload["quantity"],
            side=order_payload["side"],
            order_type=order_payload["order_type"],
            price=order_payload["price"]
        )
        
        # Update order payload with broker response
        order_payload["order_id"] = res.get("order_id")
        order_payload["status"] = res.get("status", "FAILED")
        order_payload["message"] = res.get("message", "")
        
        # Save to DB
        self.order_manager.save_order(order_payload)
        self.notifier.notify(f"Order {order_payload['status']}: {order_payload['side']} {order_payload['quantity']} {order_payload['symbol']}")
        
        return order_payload
