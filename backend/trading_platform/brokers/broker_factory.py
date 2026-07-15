import yaml
import os
import logging
from typing import Optional
from trading_platform.brokers.base_broker import BaseBroker

logger = logging.getLogger(__name__)

class BrokerFactory:
    """
    Instantiates the configured broker based on backend/config/trading.yaml
    """
    _instance: Optional[BaseBroker] = None
    
    @classmethod
    def get_broker(cls) -> BaseBroker:
        if cls._instance is not None:
            return cls._instance
            
        config_path = os.path.join(os.path.dirname(__file__), "../../../config/trading.yaml")
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load trading.yaml: {e}")
            config = {"active_broker": "paper"}
            
        active = config.get("active_broker", "paper")
        
        if active == "zerodha":
            from trading_platform.brokers.zerodha_broker import ZerodhaBroker
            cls._instance = ZerodhaBroker(config.get("zerodha", {}))
        else:
            from trading_platform.brokers.paper_broker import PaperBroker
            cls._instance = PaperBroker(config.get("paper_trading", {}))
            
        return cls._instance
