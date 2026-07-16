import pandas as pd
import numpy as np

class TechnicalIndicatorAnalysis:
    @staticmethod
    def analyze_indicators(df: pd.DataFrame) -> dict:
        results = {}
        
        # Helper for binning and evaluating
        def evaluate_bin(col_name, bins, labels):
            if col_name not in df.columns:
                return []
            
            df_copy = df[[col_name, 'Trade_Quality_Score']].copy().dropna()
            if len(df_copy) == 0:
                return []
                
            df_copy['bin'] = pd.cut(df_copy[col_name], bins=bins, labels=labels)
            
            stats = []
            for name, group in df_copy.groupby('bin'):
                stats.append({
                    "Range": name,
                    "Count": len(group),
                    "Average_Quality": round(group['Trade_Quality_Score'].mean(), 2) if len(group) > 0 else 0
                })
            return stats
            
        # Analyze RSI if present
        if 'RSI_14' in df.columns:
            results['RSI_14'] = evaluate_bin(
                'RSI_14', 
                bins=[0, 30, 40, 50, 60, 70, 100],
                labels=['0-30 (Oversold)', '30-40', '40-50', '50-60', '60-70', '70-100 (Overbought)']
            )
            
        # Analyze Relative Volume if present (Assuming it's called 'Volume_Rel_20d' or similar, we'll try a generic lookup)
        vol_col = next((c for c in df.columns if 'Volume' in c and 'Rel' in c), None)
        if vol_col:
            results['Relative_Volume'] = evaluate_bin(
                vol_col,
                bins=[0, 0.5, 0.8, 1.2, 2.0, 5.0, 100],
                labels=['< 0.5', '0.5-0.8', '0.8-1.2', '1.2-2.0', '2.0-5.0', '> 5.0']
            )
            
        # MACD Histogram if present
        macd_col = next((c for c in df.columns if 'MACD_Hist' in c), None)
        if macd_col:
            results['MACD_Histogram'] = evaluate_bin(
                macd_col,
                bins=[-np.inf, -2, 0, 2, np.inf],
                labels=['Strong Negative', 'Weak Negative', 'Weak Positive', 'Strong Positive']
            )
            
        return results
