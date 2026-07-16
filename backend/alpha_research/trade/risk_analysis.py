import pandas as pd
import numpy as np

class RiskAnalysis:
    @staticmethod
    def analyze_risk(df: pd.DataFrame) -> dict:
        """
        Analyzes MFE (Maximum Favorable Excursion) and MAE (Maximum Adverse Excursion)
        to recommend optimal Stop Loss and Profit Target.
        """
        # MFE distribution for winning trades (TARGET or TIMEOUT > 0)
        winning_trades = df[df['Simulated_Return_Pct'] > 0]
        losing_trades = df[df['Simulated_Return_Pct'] < 0]
        
        mfe_75th = round(winning_trades['MFE_Pct'].quantile(0.75), 2) if len(winning_trades) > 0 else 5.0
        mae_75th = round(losing_trades['MAE_Pct'].quantile(0.25), 2) if len(losing_trades) > 0 else -3.0 # Note: MAE is negative
        
        # Risk Reward Ratio
        avg_win = round(winning_trades['Simulated_Return_Pct'].mean(), 2) if len(winning_trades) > 0 else 5.0
        avg_loss = round(abs(losing_trades['Simulated_Return_Pct'].mean()), 2) if len(losing_trades) > 0 else 3.0
        
        rr_ratio = round(avg_win / avg_loss, 2) if avg_loss > 0 else 0
        
        return {
            "MFE_Distribution": {
                "Mean": round(df['MFE_Pct'].mean(), 2),
                "75th_Percentile_Winners": mfe_75th
            },
            "MAE_Distribution": {
                "Mean": round(df['MAE_Pct'].mean(), 2),
                "75th_Percentile_Losers": mae_75th
            },
            "Risk_Reward": {
                "Average_Win": avg_win,
                "Average_Loss": avg_loss,
                "Ratio": rr_ratio
            },
            "Recommendations": {
                "Optimal_Profit_Target": mfe_75th,
                "Optimal_Stop_Loss": mae_75th
            }
        }
