from typing import Dict, Any, List

class DriftDetector:
    def detect_drift(self, performance_metrics: Dict[str, Any], thresholds: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes performance metrics against configured thresholds to flag drift.
        """
        drift_report = {
            "prediction_drift": False,
            "feature_drift": False,
            "strategy_drift": False,
            "warnings": []
        }
        
        if performance_metrics.get("status") == "NO_DATA":
            return drift_report
            
        win_rate = performance_metrics.get("win_rate", 0.0)
        attr = performance_metrics.get("subsystem_attribution", {})
        
        win_rate_min = thresholds.get("win_rate_min", 0.45)
        
        # Simulated logic based on Phase F4 feedback
        if win_rate < win_rate_min:
            drift_report["strategy_drift"] = True
            drift_report["warnings"].append(f"Win rate ({win_rate:.2f}) dropped below threshold ({win_rate_min}). Strategy degradation detected.")
            
        if attr.get("prediction", 0) < 0:
            drift_report["prediction_drift"] = True
            drift_report["warnings"].append(f"Prediction layer attribution is negative ({attr.get('prediction')}). Model calibration may be drifting.")
            
        return drift_report
