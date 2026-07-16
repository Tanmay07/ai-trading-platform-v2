import pandas as pd
import numpy as np

class ExecutionValidator:
    """
    Validates trade replay engine by randomly sampling historical trades.
    """
    @staticmethod
    def sample_trades(df: pd.DataFrame, sample_size: int = 100, seed: int = 42) -> list:
        # We need a dataframe that has entry prices, exits, MFE, MAE, outcome, etc.
        # df must have 'Simulated_Entry_Price' and 'Simulated_Exit_Price'
        
        # Filter to rows that actually had a signal (valid trades)
        valid_df = df[df['Trade_Outcome'] != 'INVALID']
        if len(valid_df) == 0:
            return []
            
        sample = valid_df.sample(n=min(sample_size, len(valid_df)), random_state=seed)
        
        results = []
        for idx, row in sample.iterrows():
            results.append({
                "Date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                "Symbol": row.get('symbol', 'UNKNOWN'),
                "Entry_Price": float(row.get('Simulated_Entry_Price', 0.0)),
                "Exit_Price": float(row.get('Simulated_Exit_Price', 0.0)),
                "MFE_Pct": float(row.get('MFE_Pct', 0.0)),
                "MAE_Pct": float(row.get('MAE_Pct', 0.0)),
                "Outcome": row.get('Trade_Outcome', 'UNKNOWN'),
                "Quality_Score": float(row.get('Trade_Quality_Score', 0.0))
            })
            
        return results
