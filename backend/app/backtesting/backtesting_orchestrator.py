from typing import Dict, Any
from app.backtesting.backtest_engine import BacktestEngine
from app.backtesting.monte_carlo_engine import MonteCarloEngine
from app.backtesting.walk_forward_engine import WalkForwardEngine
from app.backtesting.validation_engine import ValidationEngine
from app.backtesting.report_generator import ReportGenerator

class BacktestingOrchestrator:
    def __init__(self):
        self.bt_engine = BacktestEngine()
        self.mc_engine = MonteCarloEngine()
        self.wf_engine = WalkForwardEngine()
        self.validation = ValidationEngine()
        self.report = ReportGenerator()
        
    def validate_strategy(self, strategy_name: str, trades: list) -> Dict[str, Any]:
        """
        Runs the full Phase 8 validation pipeline.
        """
        # 1. Historical Backtest
        bt_res = self.bt_engine.run_backtest(trades)
        
        # 2. Monte Carlo
        mc_res = self.mc_engine.run_simulations(bt_res["results"])
        
        # 3. Walk Forward
        wf_res = self.wf_engine.run_walk_forward(bt_res["results"])
        
        # 4. Final Validation
        val_res = self.validation.validate(bt_res["results"], mc_res)
        
        # 5. Report
        return self.report.generate_report(strategy_name, val_res, bt_res["results"])
