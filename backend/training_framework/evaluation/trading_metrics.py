import numpy as np
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger("TradingMetrics")

def calculate_advanced_trading_metrics(
    y_true: pd.Series, 
    y_pred_binary: pd.Series, 
    trade_returns: pd.Series
) -> Dict[str, Any]:
    """
    Calculates quantitative finance metrics for the model's predictions.
    
    y_true: Boolean series if the signal was actually a success (hit the target return).
    y_pred_binary: Boolean series if the model fired a signal (1 for fire, 0 for hold).
    trade_returns: The actual future return over the holding period (e.g. Target_Return_5d).
    """
    if len(y_true) == 0:
        return {}
        
    # Ensure they are aligned
    mask = y_pred_binary == 1
    
    if not mask.any():
        logger.warning("No positive predictions, cannot calculate trading metrics.")
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0
        }
        
    taken_trades = trade_returns[mask]
    
    total_trades = len(taken_trades)
    winning_trades = taken_trades[taken_trades > 0]
    losing_trades = taken_trades[taken_trades <= 0]
    
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    
    gross_profit = winning_trades.sum() if len(winning_trades) > 0 else 0
    gross_loss = abs(losing_trades.sum()) if len(losing_trades) > 0 else 0
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    avg_return = taken_trades.mean()
    
    # Risk adjusted metrics (assuming 252 trading days for annualization)
    daily_rf = 0.05 / 252 # 5% risk free rate
    excess_returns = taken_trades - daily_rf
    
    std_dev = taken_trades.std()
    sharpe_ratio = (excess_returns.mean() / std_dev) * np.sqrt(252) if std_dev > 0 else 0
    
    downside_returns = taken_trades[taken_trades < 0]
    downside_std = downside_returns.std()
    sortino_ratio = (excess_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    # Drawdown calculation (assuming sequential compounding across the entire vector, though in reality they overlap)
    cumulative = (1 + taken_trades).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    return {
        "total_trades": int(total_trades),
        "win_rate": round(float(win_rate), 4),
        "profit_factor": round(float(profit_factor), 4),
        "avg_return": round(float(avg_return), 4),
        "sharpe_ratio": round(float(sharpe_ratio), 4),
        "sortino_ratio": round(float(sortino_ratio), 4),
        "max_drawdown": round(float(max_drawdown), 4)
    }
