"""
ATR Stop Loss Engine
"""
import pandas as pd
from typing import Dict, Any
from app.config_yaml import trading_config

class StopLossEngine:
    def __init__(self):
        self.atr_multiplier = trading_config.risk_management.atr_multiplier

    def calculate_stop_loss(self, df: pd.DataFrame, entry_price: float) -> Dict[str, Any]:
        """
        Calculates stop loss based on ATR, swing lows, and structural support.
        Expects df to have 'Low' and 'atr_14' columns.
        """
        if df.empty or 'atr_14' not in df.columns or 'Low' not in df.columns:
            return {}
            
        latest_atr = df['atr_14'].iloc[-1]
        
        # Recent swing low (e.g. 20-day min)
        recent_swing_low = df['Low'].tail(20).min()
        
        # Support Level (e.g., Bollinger Band lower, if available, otherwise just swing low)
        support_level = df['bb_lower'].iloc[-1] if 'bb_lower' in df.columns else recent_swing_low
        
        atr_stop = entry_price - (latest_atr * self.atr_multiplier)
        
        # Safest stop is the minimum of the three logical stops to avoid being wicked out
        selected_stop = min(atr_stop, recent_swing_low, support_level)
        
        # Bound it to ensure it's not nonsensically low (max 50% drawdown)
        selected_stop = max(selected_stop, entry_price * 0.5)
        
        total_risk = entry_price - selected_stop
        
        return {
            "atr": round(latest_atr, 2),
            "swing_low": round(recent_swing_low, 2),
            "support": round(support_level, 2),
            "selected_stop": round(selected_stop, 2),
            "total_risk": round(total_risk, 2)
        }
