import pandas as pd

class StatisticsGenerator:
    @staticmethod
    def generate_stats(df: pd.DataFrame) -> dict:
        total_rows = len(df)
        symbols = int(df['symbol'].nunique()) if 'symbol' in df.columns else 0
        
        # Trade Outcome Stats
        target_hits = int((df['Trade_Outcome'] == 'TARGET').sum()) if 'Trade_Outcome' in df.columns else 0
        stop_hits = int((df['Trade_Outcome'] == 'STOP_LOSS').sum()) if 'Trade_Outcome' in df.columns else 0
        timeouts = int((df['Trade_Outcome'] == 'TIMEOUT').sum()) if 'Trade_Outcome' in df.columns else 0
        
        target_hit_pct = round(target_hits / total_rows * 100, 2) if total_rows > 0 else 0
        stop_hit_pct = round(stop_hits / total_rows * 100, 2) if total_rows > 0 else 0
        timeout_pct = round(timeouts / total_rows * 100, 2) if total_rows > 0 else 0
        
        # Label balances
        pos_baseline = int(df['Label_Baseline'].sum()) if 'Label_Baseline' in df.columns else 0
        pos_success = int(df['Label_TradeSuccess'].sum()) if 'Label_TradeSuccess' in df.columns else 0
        pos_ranking = int(df['Label_Ranking'].sum()) if 'Label_Ranking' in df.columns else 0
        
        # Quality
        avg_quality = round(float(df['Trade_Quality_Score'].mean()), 2) if 'Trade_Quality_Score' in df.columns else 0.0
        
        # Quality Categories
        quality_counts = df['Trade_Quality_Category'].value_counts().to_dict() if 'Trade_Quality_Category' in df.columns else {}
        
        return {
            "Total_Rows": total_rows,
            "Total_Symbols": symbols,
            "Target_Hit_Pct": target_hit_pct,
            "Stop_Loss_Pct": stop_hit_pct,
            "Timeout_Pct": timeout_pct,
            "Label_Baseline_Positives": pos_baseline,
            "Label_TradeSuccess_Positives": pos_success,
            "Label_Ranking_Positives": pos_ranking,
            "Average_Trade_Quality": avg_quality,
            "Quality_Categories": quality_counts
        }
