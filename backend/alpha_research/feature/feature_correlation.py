import pandas as pd
import numpy as np

class FeatureCorrelation:
    @staticmethod
    def analyze_correlations(df: pd.DataFrame) -> dict:
        """
        Calculates Pearson and Spearman correlation against Trade_Quality_Score
        """
        meta_cols = [
            'symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
            'sector', 'industry', 'market_cap_bucket', 'tradability_score',
            'Simulated_Entry_Price', 'Simulated_Exit_Price', 'MFE_Pct', 'MAE_Pct',
            'Days_To_Target', 'Days_To_Stop', 'Trade_Outcome', 'Trade_Quality_Score',
            'Trade_Quality_Category', 'Label_Baseline', 'Label_TradeSuccess', 'Label_Ranking',
            'Feature_Version', 'Label_Version', 'Trade_Engine_Version',
            'Dataset_Version', 'Feature_Generation_Timestamp', 'Simulated_Return_Pct',
            'Returns_1d', 'Target_Return_5d', 'Returns_5d'
        ]
        
        feature_cols = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]
        
        # Take a sample to compute rank correlations faster
        sample_df = df.sample(n=min(50000, len(df)), random_state=42).dropna(subset=feature_cols + ['Trade_Quality_Score'])
        
        results = []
        for col in feature_cols:
            pearson = sample_df[col].corr(sample_df['Trade_Quality_Score'], method='pearson')
            spearman = sample_df[col].corr(sample_df['Trade_Quality_Score'], method='spearman')
            
            results.append({
                "Feature": col,
                "Pearson_Correlation": round(float(pearson), 4) if not np.isnan(pearson) else 0.0,
                "Spearman_Correlation": round(float(spearman), 4) if not np.isnan(spearman) else 0.0
            })
            
        return {
            "Correlations": sorted(results, key=lambda x: abs(x['Spearman_Correlation']), reverse=True)
        }
