import pandas as pd

def generate_cross_sectional_features(panel_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates cross-sectional ranking features across the entire universe.
    Expects a panel DataFrame with 'Date' as index and a 'Symbol' column.
    Alternatively, a MultiIndex ['Date', 'Symbol'].
    """
    if 'Symbol' not in panel_df.columns:
        # If not formatted as panel, skip cross-sectional to avoid errors
        return panel_df
        
    df = panel_df.copy()
    
    # Calculate ranks grouped by Date
    # Note: Requires features to already be computed (e.g., ROC_10, Trend_Strength_Score, etc.)
    
    rank_features = {}
    
    # Momentum Ranking
    if 'ROC_20' in df.columns:
        rank_features['Mom_20_Pct_Rank'] = df.groupby(level=0)['ROC_20'].rank(pct=True)
        
    # Trend Ranking
    if 'Trend_Strength_Score' in df.columns:
        rank_features['Trend_Score_Pct_Rank'] = df.groupby(level=0)['Trend_Strength_Score'].rank(pct=True)
        
    # Volatility Ranking (Low = 0, High = 1)
    if 'ATR_Expansion' in df.columns:
        rank_features['Vol_Expansion_Pct_Rank'] = df.groupby(level=0)['ATR_Expansion'].rank(pct=True)
        
    # Liquidity Ranking
    if 'Avg_Vol_20' in df.columns:
        rank_features['Liquidity_Pct_Rank'] = df.groupby(level=0)['Avg_Vol_20'].rank(pct=True)
        
    # Risk Ranking (High Drawdown = low rank or high rank depending on convention)
    if 'Current_Drawdown' in df.columns:
        rank_features['Drawdown_Pct_Rank'] = df.groupby(level=0)['Current_Drawdown'].rank(pct=True)
        
    for col, values in rank_features.items():
        df[col] = values
        
    return df
