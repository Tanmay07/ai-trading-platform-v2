import pandas as pd
import numpy as np

class MarketRegimeResearch:
    @staticmethod
    def analyze_regimes(df: pd.DataFrame, config: dict) -> dict:
        """
        Since we might not have a direct VIX column for the index, we can construct 
        market regimes using cross-sectional data (Market Breadth & Volatility).
        """
        # Calculate daily market breadth (average return across all stocks on that day)
        if 'Returns_1d' in df.columns:
            ret_col = 'Returns_1d'
        else:
            ret_col = 'Simulated_Return_Pct' # fallback
            
        daily_market = df.groupby('Date')[ret_col].mean().reset_index(name='Market_Return')
        daily_market = daily_market.sort_values('Date')
        
        # Calculate Market Volatility (20-day rolling std of market return)
        daily_market['Market_Vol_20d'] = daily_market['Market_Return'].rolling(20).std()
        
        # Calculate Market Trend (50-day rolling mean of market return)
        daily_market['Market_Trend_50d'] = daily_market['Market_Return'].rolling(50).mean()
        
        # Define Regimes
        # High VIX = Market Volatility in top 20%
        vol_threshold = daily_market['Market_Vol_20d'].quantile(0.8)
        daily_market['Regime_Volatility'] = np.where(
            daily_market['Market_Vol_20d'] > vol_threshold, 'High_Volatility', 'Normal_Volatility'
        )
        
        # Trend Regime
        trend_up = daily_market['Market_Trend_50d'].quantile(0.66)
        trend_down = daily_market['Market_Trend_50d'].quantile(0.33)
        
        def get_trend_regime(val):
            if pd.isna(val): return 'Unknown'
            if val > trend_up: return 'Bull_Market'
            if val < trend_down: return 'Bear_Market'
            return 'Sideways_Market'
            
        daily_market['Regime_Trend'] = daily_market['Market_Trend_50d'].apply(get_trend_regime)
        
        # Merge back to main df
        merged_df = df.reset_index().merge(
            daily_market[['Date', 'Regime_Volatility', 'Regime_Trend']], 
            on='Date', 
            how='left'
        ).set_index('Date')
        
        def calc_metrics(group):
            target_hit = (group['Trade_Outcome'] == 'TARGET').sum() / len(group)
            stop_hit = (group['Trade_Outcome'] == 'STOP_LOSS').sum() / len(group)
            win_rate = target_hit / (target_hit + stop_hit) if (target_hit + stop_hit) > 0 else 0
            profits = group[group['Simulated_Return_Pct'] > 0]['Simulated_Return_Pct'].sum()
            losses = abs(group[group['Simulated_Return_Pct'] < 0]['Simulated_Return_Pct'].sum())
            profit_factor = profits / losses if losses > 0 else float('inf')
            
            return {
                "Trade_Count": len(group),
                "Average_Quality": round(group['Trade_Quality_Score'].mean(), 2),
                "Target_Hit_Rate": round(target_hit * 100, 2),
                "Win_Rate": round(win_rate * 100, 2),
                "Profit_Factor": round(profit_factor, 2) if profit_factor != float('inf') else 999.0
            }
            
        regime_stats = {}
        for regime_type in ['Regime_Volatility', 'Regime_Trend']:
            regime_stats[regime_type] = {}
            for regime_name, group in merged_df.groupby(regime_type):
                if regime_name == 'Unknown': continue
                regime_stats[regime_type][regime_name] = calc_metrics(group)
                
        # Best regime logic
        best_trend = max(regime_stats['Regime_Trend'].items(), key=lambda x: x[1]['Average_Quality'])[0]
        
        return {
            "Regime_Performance": regime_stats,
            "Recommendation": f"Strategy performs best in {best_trend} environments."
        }
