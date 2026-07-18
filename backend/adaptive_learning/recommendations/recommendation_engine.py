from typing import Dict, Any, List

class RecommendationEngine:
    def generate_recommendations(self, performance: Dict[str, Any], drift_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates actionable recommendations based on analytics and drift.
        Does NOT automatically trigger retraining.
        """
        recs = []
        
        if performance.get("status") == "NO_DATA":
            return recs
            
        attr = performance.get("subsystem_attribution", {})
        
        if drift_report.get("prediction_drift"):
            recs.append({
                "priority": "HIGH",
                "owner": "Prediction Service",
                "recommendation": "Review recent model calibration or trigger Retraining Pipeline.",
                "evidence": f"Prediction attribution is negative ({attr.get('prediction')}) across recent sample.",
                "expected_impact": "Restore trade quality accuracy to baseline."
            })
            
        if attr.get("execution", 0) < 0:
            recs.append({
                "priority": "MEDIUM",
                "owner": "Execution Planning",
                "recommendation": "Adjust ATR multiplier to widen stop losses.",
                "evidence": f"Execution attribution is negative ({attr.get('execution')}). Stops may be too tight.",
                "expected_impact": "Reduce premature stop-outs in volatile regimes."
            })
            
        if not recs:
            recs.append({
                "priority": "LOW",
                "owner": "All Systems",
                "recommendation": "Maintain current configurations.",
                "evidence": "All subsystems are performing within expected baseline parameters.",
                "expected_impact": "Stable continued operation."
            })
            
        return recs
