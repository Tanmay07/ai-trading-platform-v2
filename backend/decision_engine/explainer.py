from typing import Dict, Any

class DecisionExplainer:
    def explain(self, decision: str, tech: Dict[str, Any], val: Dict[str, Any], ctx: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, str]:
        
        # 1. Why this recommendation?
        why_parts = []
        if tech['score'] > 70: why_parts.append(f"Strong bullish momentum (Trend: {tech['metrics']['trend']}, RSI: {tech['metrics']['rsi']}).")
        elif tech['score'] < 30: why_parts.append(f"Technical breakdown (Trend: {tech['metrics']['trend']}, RSI: {tech['metrics']['rsi']}).")
        
        if val['score'] > 70: why_parts.append(f"Attractive valuation with PE at {val['metrics']['pe']}x and EPS growth of {val['metrics']['eps_growth']}%.")
        elif val['score'] < 30: why_parts.append(f"Valuation is stretched (PE: {val['metrics']['pe']}x) relative to growth.")
        
        if ctx['metrics']['is_concentrated']: why_parts.append(f"Position is highly concentrated at {ctx['metrics']['current_weight_pct']}% of portfolio.")
        
        if not why_parts:
            why_parts.append("Metrics are neutral across the board, suggesting a hold.")
            
        why = " ".join(why_parts)
        
        # 2. Why now?
        if tech['metrics']['rsi'] < 35:
            why_now = "Stock is currently in oversold territory, presenting a tactical entry point."
        elif tech['metrics']['rsi'] > 70:
            why_now = "Stock is overbought, increasing the probability of a near-term pullback."
        else:
            why_now = f"Current price action is stable relative to the 50 DMA ({tech['metrics']['sma_50']})."
            
        # 3. Risks
        risks = f"Historical volatility is {risk['metrics']['volatility_pct']}% with a max drawdown of {risk['metrics']['max_drawdown_pct']}%. "
        if risk['score'] < 40:
            risks += "This is considered a high-risk profile."
        else:
            risks += "Risk is within moderate parameters."
            
        return {
            "explanation_why": why,
            "explanation_why_now": why_now,
            "explanation_metrics_changed": "Periodic recalculation based on EOD market data.",
            "explanation_supports_view": f"Technical Score: {tech['score']}, Valuation Score: {val['score']}",
            "explanation_risks": risks,
            "explanation_invalidation": f"A close below Stop Loss or a drop in EPS growth below {val['metrics']['eps_growth']/2}% would invalidate this thesis."
        }
