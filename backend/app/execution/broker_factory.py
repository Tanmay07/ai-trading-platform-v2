from app.brokers.paper_adapter import PaperAdapter
from app.brokers.zerodha_adapter import ZerodhaAdapter

class BrokerFactory:
    @staticmethod
    def get_broker(broker_name: str):
        if broker_name == "zerodha":
            return ZerodhaAdapter()
        return PaperAdapter()
