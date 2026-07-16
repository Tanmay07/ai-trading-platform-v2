import pandas as pd
import numpy as np

class SectorResearch:
    @staticmethod
    def analyze_sectors(df: pd.DataFrame) -> dict:
        if 'sector' not in df.columns:
            return {"error": "Sector data missing"}
            
        sector_stats = []
        for sector, group in df.groupby('sector'):
            if len(group) < 500:
                continue
                
            avg_quality = group['Trade_Quality_Score'].mean()
            target_hit = (group['Trade_Outcome'] == 'TARGET').sum() / len(group)
            stop_hit = (group['Trade_Outcome'] == 'STOP_LOSS').sum() / len(group)
            win_rate = target_hit / (target_hit + stop_hit) if (target_hit + stop_hit) > 0 else 0
            
            # Profit Factor = (Gross Profit) / (Gross Loss)
            # Simulated_Return_Pct exists and contains the return for the trade
            profits = group[group['Simulated_Return_Pct'] > 0]['Simulated_Return_Pct'].sum()
            losses = abs(group[group['Simulated_Return_Pct'] < 0]['Simulated_Return_Pct'].sum())
            profit_factor = profits / losses if losses > 0 else float('inf')
            
            avg_ret = group['Simulated_Return_Pct'].mean()
            
            # Holding period calculation
            # If trade outcome is TARGET, it's Days_To_Target, else if STOP_LOSS it's Days_To_Stop, else 7
            holding_period = group.apply(
                lambda row: row['Days_To_Target'] if row['Trade_Outcome'] == 'TARGET' 
                else (row['Days_To_Stop'] if row['Trade_Outcome'] == 'STOP_LOSS' else 7), 
                axis=1
            ).mean()
            
            sector_stats.append({
                "Sector": sector,
                "Trade_Count": len(group),
                "Average_Quality": round(avg_quality, 2),
                "Target_Hit_Rate": round(target_hit * 100, 2),
                "Stop_Loss_Rate": round(stop_hit * 100, 2),
                "Win_Rate": round(win_rate * 100, 2),
                "Average_Return": round(avg_ret, 2),
                "Profit_Factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.0,
                "Average_Holding_Period": round(holding_period, 2)
            })
            
        # Sort by Quality Score to find top/bottom
        sector_stats = sorted(sector_stats, key=lambda x: x['Average_Quality'], reverse=True)
        
        return {
            "Top_Performing_Sectors": sector_stats[:10],
            "Bottom_Performing_Sectors": sector_stats[-10:],
            "All_Sectors": sector_stats
        }
