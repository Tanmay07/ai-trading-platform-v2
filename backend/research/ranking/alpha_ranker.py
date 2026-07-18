from typing import Dict, Any

class AlphaRanker:
    """
    Ranks Candidate features based on the Phase G1 objective weighting criteria.
    Trading Performance (35%), IC (20%), Stability (20%), SHAP (10%), MI (10%), Cost (5%).
    """
    def generate_score(self, statistical: Dict[str, float], trading: Dict[str, float], stability: Dict[str, float]) -> float:
        # Normalize mock values to 0-1 scale for scoring
        
        # 1. Trading (35%)
        # Profit Factor 1.0 -> 0, 2.5 -> 1.0
        pf_score = max(0.0, min(1.0, (trading.get("profit_factor", 1.0) - 1.0) / 1.5))
        # Precision 0.2 -> 0, 0.6 -> 1.0
        prec_score = max(0.0, min(1.0, (trading.get("precision_at_20", 0.2) - 0.2) / 0.4))
        trading_comp = ((pf_score + prec_score) / 2) * 35.0
        
        # 2. Information Coefficient (20%)
        # IC 0.0 -> 0, 0.08 -> 1.0
        ic_score = max(0.0, min(1.0, statistical.get("ic", 0.0) / 0.08))
        ic_comp = ic_score * 20.0
        
        # 3. Stability (20%)
        # Stability score is already 0-1
        stab_comp = stability.get("overall_stability_score", 0.0) * 20.0
        
        # 4. SHAP (10%)
        shap_score = max(0.0, min(1.0, statistical.get("shap_importance", 0.0) / 0.15))
        shap_comp = shap_score * 10.0
        
        # 5. Mutual Information (10%)
        mi_score = max(0.0, min(1.0, statistical.get("mutual_information", 0.0) / 0.5))
        mi_comp = mi_score * 10.0
        
        # 6. Cost (5%) - Assume perfect for MVP
        cost_comp = 5.0
        
        total_score = trading_comp + ic_comp + stab_comp + shap_comp + mi_comp + cost_comp
        
        return round(total_score, 2)
