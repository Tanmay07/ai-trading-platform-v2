import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Synthesizes fundamental, technical, and portfolio context data to generate 
    an institutional-grade investment recommendation for a single holding.
    """
    
    def generate_recommendation(self, 
                                symbol: str, 
                                fundamental: Dict[str, Any], 
                                technical: Dict[str, Any], 
                                context: Dict[str, Any],
                                current_price: float) -> Dict[str, Any]:
        
        f_score = fundamental.get("fundamental_score", 50)
        t_score = technical.get("technical_score", 50)
        allocation = context.get("allocations", {}).get(symbol, 0)
        
        confidence = (f_score + t_score) / 2
        
        recommendation = "Hold"
        reasoning = []
        target_price = current_price * 1.15
        stop_loss = current_price * 0.90
        expected_holding_period = "12 Months"
        
        # Base logic for fundamental + technical
        if f_score > 80 and t_score > 70:
            recommendation = "Strong Buy"
            reasoning.append(f"Outstanding fundamentals (Score: {f_score}) and bullish technicals (Score: {t_score}).")
            target_price = current_price * 1.25
        elif f_score > 70 and t_score > 60:
            recommendation = "Buy More"
            reasoning.append(f"Strong fundamental growth (Revenue: {fundamental.get('revenue_growth')}%) with supportive technicals.")
        elif f_score > 60:
            recommendation = "Accumulate"
            reasoning.append(f"Solid fundamentals. Good opportunity to accumulate on dips.")
            target_price = current_price * 1.1
        elif f_score < 30 and t_score < 30:
            recommendation = "Exit Immediately"
            reasoning.append(f"Severe fundamental deterioration and broken technical trend.")
            confidence = 100 - confidence # High confidence in selling bad stock
            target_price = current_price * 0.8
        elif f_score < 40 or t_score < 40:
            recommendation = "Sell"
            reasoning.append(f"Weak fundamentals (PE: {fundamental.get('pe')}) or technical breakdown.")
            confidence = 100 - confidence
            target_price = current_price * 0.9
        else:
            recommendation = "Hold"
            reasoning.append(f"Fairly valued. Hold while 50 DMA ({technical.get('ema_50')}) remains intact.")

        # Override logic based on Portfolio Context (Position Sizing)
        if allocation > 20: # Example threshold
            if recommendation in ["Strong Buy", "Buy More", "Accumulate"]:
                recommendation = "Hold"
                reasoning.append(f"Downgraded to Hold because this stock already forms {allocation}% of your portfolio. Manage single-stock exposure risk.")
        elif allocation > 10 and recommendation == "Strong Buy":
            recommendation = "Trim Position"
            reasoning.append(f"Fundamentally strong, but forms {allocation}% of portfolio. Trim to book partial profits and reduce risk.")

        # Refine Reasoning with evidence (per user requirements)
        if recommendation == "Sell":
            reasoning.append(f"PE has expanded to {fundamental.get('pe')}x.")
            if fundamental.get("revenue_growth") < 10:
                reasoning.append(f"Revenue growth has slowed to {fundamental.get('revenue_growth')}%.")
            if technical.get("rsi") > 70:
                reasoning.append(f"RSI at {technical.get('rsi')} indicating overbought conditions.")
                
        return {
            "recommendation": recommendation,
            "reasoning": " ".join(reasoning),
            "target_price": round(target_price, 2),
            "stop_loss": round(stop_loss, 2),
            "expected_holding_period": expected_holding_period,
            "confidence": round(confidence, 1),
            "risk_rating": "High" if fundamental.get("debt_to_equity", 0) > 2 or technical.get("adx", 0) > 30 else "Moderate"
        }
