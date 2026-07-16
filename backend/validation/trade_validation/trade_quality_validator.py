import pandas as pd
import numpy as np
from scipy.stats import skew

class TradeQualityValidator:
    @staticmethod
    def audit_quality_distribution(df: pd.DataFrame) -> dict:
        if 'Trade_Quality_Score' not in df.columns:
            return {"error": "Trade_Quality_Score missing"}
            
        scores = df['Trade_Quality_Score'].dropna()
        if len(scores) == 0:
            return {"error": "No scores"}
            
        # Histogram
        hist, bin_edges = np.histogram(scores, bins=10, range=(0, 100))
        hist_dict = {f"{int(bin_edges[i])}-{int(bin_edges[i+1])}": int(hist[i]) for i in range(len(hist))}
        
        mean_score = scores.mean()
        median_score = scores.median()
        std_score = scores.std()
        skew_score = skew(scores)
        
        return {
            "Mean": round(float(mean_score), 2),
            "Median": round(float(median_score), 2),
            "Standard_Deviation": round(float(std_score), 2),
            "Skewness": round(float(skew_score), 2),
            "Histogram": hist_dict,
            "Flag_Collapsed": bool(std_score < 5.0) # Flag if the distribution is too tight
        }
