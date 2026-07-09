from typing import Dict, Any, List

class StateBuilder:
    def build_state(self, candidate_data: Dict[str, Any]) -> List[float]:
        """
        Normalizes the candidate object into a strictly numerical state vector.
        """
        state = []
        
        # Technical
        state.append(float(candidate_data.get("breakout_score", 50)) / 100.0)
        state.append(float(candidate_data.get("Relative_Strength", 1.0)))
        
        # Market
        regime = candidate_data.get("regime", "Neutral")
        regime_map = {"Strong Bull": 1.0, "Bull": 0.75, "Neutral": 0.5, "Bear": 0.25, "Strong Bear": 0.0}
        state.append(regime_map.get(regime, 0.5))
        state.append(float(candidate_data.get("market_score", 50)) / 100.0)
        
        # AI / ML
        state.append(float(candidate_data.get("consensus_score", 50)) / 100.0)
        state.append(float(candidate_data.get("buy_probability", 0.5)))
        
        # Fill missing with zeros
        state = [float(s) if s == s else 0.0 for s in state] # Handle NaNs just in case
        
        return state
