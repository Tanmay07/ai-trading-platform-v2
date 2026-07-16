import pandas as pd
from scipy.stats import spearmanr, kendalltau

class RankingValidator:
    @staticmethod
    def audit_ranking_correlation(df: pd.DataFrame) -> dict:
        if 'Trade_Quality_Score' not in df.columns or 'Simulated_Return_Pct' not in df.columns:
            return {"error": "Required columns missing"}
            
        # Drop NaNs
        clean_df = df.dropna(subset=['Trade_Quality_Score', 'Simulated_Return_Pct'])
        if len(clean_df) == 0:
            return {"error": "No data"}
            
        spearman_corr, sp_p = spearmanr(clean_df['Trade_Quality_Score'], clean_df['Simulated_Return_Pct'])
        kendall_corr, kd_p = kendalltau(clean_df['Trade_Quality_Score'], clean_df['Simulated_Return_Pct'])
        
        # We can also compute pearson
        pearson_corr = clean_df['Trade_Quality_Score'].corr(clean_df['Simulated_Return_Pct'], method='pearson')
        
        # Let's check daily overlap
        # To do daily overlap, we need to group by Date
        # Wait, grouping by Date and ranking might be slow across 750k rows for a quick audit,
        # but let's just sample a few dates
        sample_dates = clean_df.index.unique()[:50] # Just 50 days
        overlaps_20 = []
        overlaps_50 = []
        
        for date in sample_dates:
            day_data = clean_df[clean_df.index == date]
            if len(day_data) < 50:
                continue
                
            top_ret = day_data.nlargest(20, 'Simulated_Return_Pct').index
            top_qual = day_data.nlargest(20, 'Trade_Quality_Score').index
            overlaps_20.append(len(set(top_ret).intersection(set(top_qual))) / 20.0)
            
            top_ret_50 = day_data.nlargest(50, 'Simulated_Return_Pct').index
            top_qual_50 = day_data.nlargest(50, 'Trade_Quality_Score').index
            overlaps_50.append(len(set(top_ret_50).intersection(set(top_qual_50))) / 50.0)
            
        avg_overlap_20 = sum(overlaps_20)/len(overlaps_20) if overlaps_20 else 0.0
        avg_overlap_50 = sum(overlaps_50)/len(overlaps_50) if overlaps_50 else 0.0

        return {
            "Pearson_Correlation": round(float(pearson_corr), 4),
            "Spearman_Correlation": round(float(spearman_corr), 4),
            "Kendall_Correlation": round(float(kendall_corr), 4),
            "Spearman_P_Value": float(sp_p),
            "Top_20_Overlap_Pct": round(avg_overlap_20 * 100.0, 2),
            "Top_50_Overlap_Pct": round(avg_overlap_50 * 100.0, 2)
        }
