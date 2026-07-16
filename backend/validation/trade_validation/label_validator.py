import pandas as pd
import numpy as np

class LabelValidator:
    """
    Validates the generated labels (Baseline and Trade Success) 
    and outputs statistical summaries to prove correct distribution.
    """
    @staticmethod
    def audit_baseline_label(df: pd.DataFrame, target_return: float = 5.0, epsilon: float = 1e-5) -> dict:
        col = 'Label_Baseline'
        if col not in df.columns:
            return {"error": "Label_Baseline not found"}
            
        total = len(df)
        pos = df[col].sum()
        neg = total - pos
        pos_pct = (pos / total) * 100.0 if total > 0 else 0.0
        
        # simulated returns for the baseline logic
        if 'Simulated_Return_Pct' in df.columns:
            sim_ret = df['Simulated_Return_Pct']
            
            # Analyze just the positive samples to see what their min return was
            pos_mask = df[col] == 1
            if pos > 0:
                pos_ret = sim_ret[pos_mask]
                min_fwd = pos_ret.min()
                max_fwd = pos_ret.max()
                avg_fwd = pos_ret.mean()
                med_fwd = pos_ret.median()
                quantiles = pos_ret.quantile([0.05, 0.25, 0.50, 0.75, 0.95]).to_dict()
            else:
                min_fwd = max_fwd = avg_fwd = med_fwd = 0.0
                quantiles = {}
                
            return {
                "Total_Observations": int(total),
                "Positive_Labels": int(pos),
                "Negative_Labels": int(neg),
                "Positive_Pct": round(pos_pct, 2),
                "Min_Forward_Return": round(min_fwd, 4),
                "Max_Forward_Return": round(max_fwd, 4),
                "Average_Forward_Return": round(avg_fwd, 4),
                "Median_Forward_Return": round(med_fwd, 4),
                "Percentiles": quantiles
            }
        
        return {"error": "Simulated_Return_Pct not found"}
