import pandas as pd
from typing import Dict, Any

class LabelComparator:
    """
    Compares different label strategies to extract summary metrics.
    """
    
    @staticmethod
    def compare(df: pd.DataFrame, label_cols: list) -> Dict[str, Dict[str, Any]]:
        """
        Calculates metrics for each label column provided.
        Returns a dictionary mapping label_col -> metrics.
        """
        results = {}
        total_samples = len(df)
        
        for col in label_cols:
            if col not in df.columns:
                continue
                
            positives = df[col].sum()
            class_balance = (positives / total_samples) * 100.0 if total_samples > 0 else 0
            
            # Mask for only positive samples to calculate average return
            pos_mask = df[col] == 1
            pos_df = df[pos_mask]
            
            # Average Return of positive samples
            avg_return = pos_df['Simulated_Return_Pct'].mean() if 'Simulated_Return_Pct' in pos_df.columns else 0.0
            
            # Metrics across ALL trades for this strategy
            target_hits = (df['Trade_Outcome'] == 'TARGET').sum() if 'Trade_Outcome' in df.columns else 0
            target_hit_rate = (target_hits / total_samples) * 100.0 if total_samples > 0 else 0.0
            
            stop_hits = (df['Trade_Outcome'] == 'STOP_LOSS').sum() if 'Trade_Outcome' in df.columns else 0
            stop_hit_rate = (stop_hits / total_samples) * 100.0 if total_samples > 0 else 0.0
            
            timeout_hits = (df['Trade_Outcome'] == 'TIMEOUT').sum() if 'Trade_Outcome' in df.columns else 0
            timeout_rate = (timeout_hits / total_samples) * 100.0 if total_samples > 0 else 0.0
            
            # Average Holding Period (of positive samples)
            if 'Days_To_Target' in pos_df.columns and 'Days_To_Stop' in pos_df.columns:
                # Merge the days since either one was hit
                days = pos_df['Days_To_Target'].where(pos_df['Trade_Outcome'] == 'TARGET', pos_df['Days_To_Stop'])
                # If timeout, assume 7 days
                days = days.where(pos_df['Trade_Outcome'] != 'TIMEOUT', 7)
                avg_holding = days.mean()
            else:
                avg_holding = 0.0
                
            results[col] = {
                "positive_samples": int(positives),
                "class_balance_pct": round(class_balance, 2),
                "average_return_pct": round(avg_return, 2) if pd.notna(avg_return) else 0.0,
                "target_hit_rate_pct": round(target_hit_rate, 2),
                "stop_loss_rate_pct": round(stop_hit_rate, 2),
                "timeout_rate_pct": round(timeout_rate, 2),
                "average_holding_period": round(avg_holding, 2) if pd.notna(avg_holding) else 0.0,
                "dataset_coverage": total_samples
            }
            
        return results
