import numpy as np
import pandas as pd
import logging

logger = logging.getLogger("InvestmentEvaluator")

class InvestmentEvaluator:
    def __init__(self, initial_capital: float = 1000000.0, max_positions: int = 10):
        self.initial_capital = initial_capital
        self.max_positions = max_positions
        
    def evaluate(self, df: pd.DataFrame, target_col: str, probas: np.ndarray) -> dict:
        """
        Vectorized historical backtest to compute investment metrics.
        
        Args:
            df: Validation dataset containing 'Date', 'Symbol', 'Close' and forward return columns.
            target_col: Name of the forward return column (e.g., 'Target_Forward_Return').
            probas: Model predictions for the positive class.
            
        Returns:
            Dictionary of investment metrics (CAGR, Sharpe, Drawdown, etc.)
        """
        if target_col not in df.columns:
            logger.warning(f"Target return column {target_col} not found. Cannot evaluate investment metrics.")
            return {}
            
        eval_df = df[['Date', 'Symbol', target_col]].copy()
        eval_df['prob'] = probas
        
        # Group by Date to pick top K stocks per day
        daily_returns = []
        
        for date, group in eval_df.groupby('Date'):
            # Pick top K predictions where prob > 0.5
            buys = group[group['prob'] > 0.5].nlargest(self.max_positions, 'prob')
            if len(buys) == 0:
                daily_returns.append(0.0)
            else:
                # Equal weight allocation among chosen positions
                avg_ret = buys[target_col].mean()
                daily_returns.append(avg_ret)
                
        if not daily_returns:
            return self._empty_metrics()
            
        returns = np.array(daily_returns)
        
        # Compute Metrics
        metrics = {}
        
        metrics['Win_Rate'] = float(np.mean(returns > 0)) if len(returns) > 0 else 0.0
        metrics['Average_Return_per_Trade'] = float(np.mean(returns))
        metrics['Median_Return'] = float(np.median(returns))
        
        # Annualized metrics (assuming daily trading, 252 days/yr)
        annualized_return = np.mean(returns) * 252
        annualized_vol = np.std(returns) * np.sqrt(252)
        metrics['Annualized_Return'] = float(annualized_return)
        metrics['Portfolio_Volatility'] = float(annualized_vol)
        metrics['CAGR'] = metrics['Annualized_Return'] # Approximation
        
        metrics['Sharpe_Ratio'] = float(annualized_return / annualized_vol) if annualized_vol > 0 else 0.0
        
        # Downside risk for Sortino
        downside = returns[returns < 0]
        downside_vol = np.std(downside) * np.sqrt(252) if len(downside) > 0 else 0
        metrics['Sortino_Ratio'] = float(annualized_return / downside_vol) if downside_vol > 0 else 0.0
        
        # Drawdown
        cumulative = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        metrics['Max_Drawdown'] = float(max_drawdown)
        
        metrics['Calmar_Ratio'] = float(annualized_return / max_drawdown) if max_drawdown > 0 else 0.0
        
        # Profit factor
        gross_profits = returns[returns > 0].sum()
        gross_losses = np.abs(returns[returns < 0].sum())
        metrics['Profit_Factor'] = float(gross_profits / gross_losses) if gross_losses > 0 else float('inf')
        
        return metrics
        
    def _empty_metrics(self):
        return {
            'Win_Rate': 0.0,
            'Average_Return_per_Trade': 0.0,
            'Median_Return': 0.0,
            'Annualized_Return': 0.0,
            'Portfolio_Volatility': 0.0,
            'CAGR': 0.0,
            'Sharpe_Ratio': 0.0,
            'Sortino_Ratio': 0.0,
            'Max_Drawdown': 0.0,
            'Calmar_Ratio': 0.0,
            'Profit_Factor': 0.0
        }
