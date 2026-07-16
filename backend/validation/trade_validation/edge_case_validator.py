import pandas as pd

class EdgeCaseValidator:
    """
    Automatically identifies edge cases (missing OHLCV, 0 volume, gap-ups).
    """
    @staticmethod
    def audit_edge_cases(df: pd.DataFrame) -> dict:
        edge_cases = {}
        
        if 'Volume' in df.columns:
            zero_vol = df[df['Volume'] == 0]
            edge_cases['Zero_Volume_Days'] = len(zero_vol)
            
        if 'Open' in df.columns and 'Simulated_Exit_Price' in df.columns:
            # We can't perfectly audit gaps without the target/stop variables,
            # but we can check if Simulated_Return_Pct is completely outside bounds for non-timeouts
            # A stop loss is 2.5%, but if gap down is 5%, return will be -5%.
            if 'Simulated_Return_Pct' in df.columns and 'Trade_Outcome' in df.columns:
                gaps_down = df[(df['Trade_Outcome'] == 'STOP_LOSS') & (df['Simulated_Return_Pct'] < -2.6)]
                gaps_up = df[(df['Trade_Outcome'] == 'TARGET') & (df['Simulated_Return_Pct'] > 5.1)]
                
                edge_cases['Gap_Down_Stop_Outs'] = len(gaps_down)
                edge_cases['Gap_Up_Target_Hits'] = len(gaps_up)
                
        # Missing OHLCV
        missing_count = 0
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                missing_count += df[col].isna().sum()
        edge_cases['Missing_OHLCV_Values'] = int(missing_count)
        
        return edge_cases
