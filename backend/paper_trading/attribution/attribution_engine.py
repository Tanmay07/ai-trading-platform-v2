from typing import Dict, Any
from paper_trading.attribution.feedback_repository import FeedbackRepository

class AttributionEngine:
    def __init__(self):
        self.repository = FeedbackRepository()
        
    def attribute_trade(self, closed_position: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines which decision layer added or destroyed value.
        """
        ret = closed_position.get("return_pct", 0.0)
        reason = closed_position.get("exit_reason", "")
        context = closed_position.get("context", {})
        
        # Simple heuristic attribution model for MVP
        attribution = {
            "prediction_layer": 0,
            "portfolio_layer": 0,
            "execution_layer": 0,
            "summary": ""
        }
        
        if ret > 0:
            if "TARGET" in reason:
                attribution["prediction_layer"] += 1
                attribution["execution_layer"] += 1
                attribution["summary"] = "Strong prediction combined with excellent execution target planning."
            else:
                attribution["prediction_layer"] += 1
                attribution["portfolio_layer"] += 1
                attribution["summary"] = "Profitable exit but premature compared to targets. Good baseline prediction."
        else:
            if "STOP_LOSS" in reason:
                # Did it gap down or just slowly bleed?
                # If we entered with low confidence, prediction takes the blame.
                conf = context.get("prediction", {}).get("confidence", 0)
                if conf < 80:
                    attribution["prediction_layer"] -= 1
                    attribution["summary"] = "Poor prediction quality caused stop loss hit."
                else:
                    attribution["execution_layer"] -= 1
                    attribution["summary"] = "Prediction was confident, but execution stop loss might have been too tight."
            elif "TIME_EXIT" in reason:
                 attribution["prediction_layer"] -= 1
                 attribution["summary"] = "Prediction failed to materialize within the expected holding period."
                 
        # Save to Feedback Repository (Phase F5 Data Pipeline)
        self.repository.store_trade_feedback(closed_position, attribution)
        
        return attribution
