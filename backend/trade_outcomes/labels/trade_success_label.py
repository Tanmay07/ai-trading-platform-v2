import pandas as pd

class TradeSuccessLabeler:
    """
    Generates labels based on actual trade execution outcomes.
    Positive label = Target Hit before Stop Loss
    """
    
    def generate_labels(self, df: pd.DataFrame) -> pd.Series:
        if 'Trade_Outcome' not in df.columns:
            raise ValueError("Trade_Outcome column is missing. Run TradeReplayEngine first.")
            
        return (df['Trade_Outcome'] == 'TARGET').astype(int)
