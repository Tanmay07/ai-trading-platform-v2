import pandas as pd
import numpy as np
from trade_outcomes.engine.trade_replay import TradeReplayEngine

class HoldingPeriodAnalysis:
    @staticmethod
    def analyze_holding_periods(df: pd.DataFrame, config: dict, trade_config: dict) -> dict:
        periods = config.get('holding_periods', [2,3,4,5,6,7,8,10])
        
        # To avoid a 20-minute simulation, we take a stratified random sample of 20,000 rows
        # ensuring we get a good mix of regimes and sectors.
        sample_size = min(20000, len(df))
        sample_df = df.sample(n=sample_size, random_state=42).copy()
        
        # We need to sort by Date per symbol for TradeReplayEngine
        sample_df = sample_df.reset_index().sort_values(['symbol', 'Date'])
        
        results = {}
        best_period = 7
        best_quality = -1
        
        for period in periods:
            # We don't want to instantiate TradeReplayEngine with default 7, we override it
            engine = TradeReplayEngine(
                holding_period=period,
                target_pct=trade_config['profit_target'],
                stop_loss_pct=trade_config['stop_loss'],
                quality_weights=trade_config.get('quality_weights', None)
            )
            
            replayed_dfs = []
            for sym, group in sample_df.groupby('symbol'):
                replayed_dfs.append(engine.replay_symbol_history(group))
                
            sim_df = pd.concat(replayed_dfs)
            
            # Metrics
            target_hit = (sim_df['Trade_Outcome'] == 'TARGET').sum() / len(sim_df)
            stop_hit = (sim_df['Trade_Outcome'] == 'STOP_LOSS').sum() / len(sim_df)
            profits = sim_df[sim_df['Simulated_Return_Pct'] > 0]['Simulated_Return_Pct'].sum()
            losses = abs(sim_df[sim_df['Simulated_Return_Pct'] < 0]['Simulated_Return_Pct'].sum())
            profit_factor = profits / losses if losses > 0 else float('inf')
            
            avg_qual = round(sim_df['Trade_Quality_Score'].mean(), 2)
            
            results[f"{period}_Days"] = {
                "Average_Quality": avg_qual,
                "Target_Hit_Rate": round(target_hit * 100, 2),
                "Profit_Factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.0,
                "Average_Return": round(sim_df['Simulated_Return_Pct'].mean(), 2),
                "Average_MFE": round(sim_df['MFE_Pct'].mean(), 2),
                "Average_MAE": round(sim_df['MAE_Pct'].mean(), 2)
            }
            
            if avg_qual > best_quality:
                best_quality = avg_qual
                best_period = period
                
        return {
            "Holding_Period_Performance": results,
            "Recommended_Holding_Period": best_period
        }
