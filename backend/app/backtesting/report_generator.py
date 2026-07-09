from typing import Dict, Any
from datetime import datetime

class ReportGenerator:
    def generate_report(self, strategy_name: str, validation_results: Dict[str, Any], bt_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an institutional JSON report.
        """
        return {
            "strategy": strategy_name,
            "generated_at": datetime.utcnow().isoformat(),
            "validation_status": validation_results["status"],
            "validation_score": validation_results["score"],
            "reasons": validation_results["reasons"],
            "cagr": bt_results.get("simulated_cagr"),
            "max_drawdown": bt_results.get("simulated_drawdown")
        }
