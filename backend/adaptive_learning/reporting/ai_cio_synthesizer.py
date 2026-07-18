from typing import Dict, Any, List

class AICIOSynthesizer:
    def generate_briefing(self, performance: Dict[str, Any], drift: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """
        Synthesizes diagnostics into an executive summary (Programmatic implementation for MVP).
        """
        if performance.get("status") == "NO_DATA":
            return "AI-CIO Briefing: Insufficient data in the Feedback Repository to generate an executive summary. Please run the Paper Trading Engine to generate trade outcomes."
            
        win_rate = performance.get("win_rate", 0)
        health_score = int(win_rate * 100)
        health_status = "Healthy" if health_score > 50 else "Degraded"
        
        briefing = f"System Health: {health_score}/100 ({health_status})\n\n"
        
        # Diagnostics
        if drift.get("prediction_drift") or drift.get("strategy_drift"):
            briefing += "System diagnostics indicate performance degradation. "
            if drift.get("prediction_drift"):
                briefing += "Specifically, prediction quality appears to be drifting, contributing negatively to recent outcomes. "
            if drift.get("strategy_drift"):
                briefing += f"The overall win rate has dropped to {win_rate*100:.1f}%. "
        else:
            briefing += "System diagnostics indicate stable operations across prediction, portfolio, and execution layers. "
            
        # Recommendations
        briefing += "\n\nRecommendations:\n"
        high_pri = [r for r in recommendations if r["priority"] == "HIGH"]
        if high_pri:
            briefing += "I do not recommend immediate automated retraining. Instead, I advise the following manual review: "
            briefing += high_pri[0]["recommendation"] + " "
            briefing += f"Evidence: {high_pri[0]['evidence']}"
        else:
            briefing += "No structural or model changes are recommended at this time. Continue monitoring live performance."
            
        return briefing
