from typing import Dict, Any, List
from app.backtesting.event_driven_simulator import EventDrivenSimulator

class BacktestEngine:
    def __init__(self):
        self.simulator = EventDrivenSimulator()
        
    def run_backtest(self, strategy_trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Wraps the simulator and outputs structured backtest reports.
        """
        results = self.simulator.process_events(strategy_trades)
        return {
            "status": "COMPLETED",
            "results": results
        }
