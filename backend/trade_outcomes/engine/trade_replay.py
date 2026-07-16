import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple
from trade_outcomes.engine.mfe_mae_calculator import MFEMAECalculator
from trade_outcomes.engine.trade_quality_scorer import TradeQualityScorer

logger = logging.getLogger("TradeReplay")

class TradeReplayEngine:
    """
    Simulates trades historically using High and Low price action to calculate MFE, MAE, 
    and precise trade outcomes (Target Hit, Stop Loss Hit, Timeout).
    Executes at T+1 Open to prevent look-ahead bias and capture slippage/gaps.
    """
    def __init__(self, holding_period: int = 7, target_pct: float = 5.0, stop_loss_pct: float = 2.5, quality_weights: dict = None):
        self.holding_period = holding_period
        self.target_pct = target_pct
        self.stop_loss_pct = stop_loss_pct
        
        if quality_weights is None:
            quality_weights = {'profit': 0.3, 'risk': 0.2, 'reward_risk': 0.2, 'speed': 0.15, 'volatility': 0.15}
        self.scorer = TradeQualityScorer(weights=quality_weights, holding_period=holding_period)
        
    def replay_symbol_history(self, symbol_df: pd.DataFrame) -> pd.DataFrame:
        """
        Replays all trades for a single symbol using T+1 Open execution.
        Expects a DataFrame with 'Open', 'Close', 'High', 'Low' columns sorted by Date.
        """
        if not {'Open', 'Close', 'High', 'Low'}.issubset(symbol_df.columns):
            logger.error("Missing required columns (Open, Close, High, Low) for trade replay.")
            return symbol_df
            
        open_prices = symbol_df['Open'].values
        close_prices = symbol_df['Close'].values
        high_prices = symbol_df['High'].values
        low_prices = symbol_df['Low'].values
        
        n_rows = len(symbol_df)
        
        mfe_arr = np.zeros(n_rows)
        mae_arr = np.zeros(n_rows)
        outcome_arr = np.empty(n_rows, dtype=object)
        days_to_target = np.full(n_rows, -1)
        days_to_stop = np.full(n_rows, -1)
        exit_price_arr = np.zeros(n_rows)
        quality_score_arr = np.zeros(n_rows)
        category_arr = np.empty(n_rows, dtype=object)
        
        # We simulate executing at the OPEN of the NEXT day
        for i in range(n_rows - 1): # cannot execute on the very last day
            # Signal generated on day i
            # Execute on day i+1 Open
            entry_price = open_prices[i + 1]
            if entry_price <= 0:
                continue
                
            target_price = entry_price * (1 + self.target_pct / 100.0)
            stop_price = entry_price * (1 - self.stop_loss_pct / 100.0)
            
            # Look ahead up to holding period from T+1
            start_eval_idx = i + 1
            max_idx = min(start_eval_idx + self.holding_period, n_rows)
            
            forward_highs = high_prices[start_eval_idx : max_idx]
            forward_lows = low_prices[start_eval_idx : max_idx]
            forward_opens = open_prices[start_eval_idx : max_idx]
            
            excursions = MFEMAECalculator.calculate_excursions(entry_price, forward_highs, forward_lows)
            mfe_arr[i] = excursions['mfe_pct']
            mae_arr[i] = excursions['mae_pct']
            
            outcome = "TIMEOUT"
            final_exit = close_prices[max_idx - 1] 
            
            # Daily Range for volatility efficiency
            daily_ranges = []
            
            # Step represents days held. Day 0 is T+1
            for step, (d_high, d_low, d_open) in enumerate(zip(forward_highs, forward_lows, forward_opens)):
                # Calculate daily range %
                if d_open > 0:
                    daily_ranges.append((d_high - d_low) / d_open * 100.0)
                    
                # Note: If there's an overnight gap, the open price might instantly hit stop loss
                if d_open <= stop_price:
                    outcome = "STOP_LOSS"
                    days_to_stop[i] = step + 1
                    final_exit = d_open # Gapped below stop loss, executed at open
                    break
                elif d_open >= target_price:
                    outcome = "TARGET"
                    days_to_target[i] = step + 1
                    final_exit = d_open # Gapped above target, executed at open
                    break
                    
                hit_target = d_high >= target_price
                hit_stop = d_low <= stop_price
                
                if hit_stop and hit_target:
                    outcome = "STOP_LOSS"
                    days_to_stop[i] = step + 1
                    final_exit = stop_price
                    break
                elif hit_stop:
                    outcome = "STOP_LOSS"
                    days_to_stop[i] = step + 1
                    final_exit = stop_price
                    break
                elif hit_target:
                    outcome = "TARGET"
                    days_to_target[i] = step + 1
                    final_exit = target_price
                    break
                    
            outcome_arr[i] = outcome
            exit_price_arr[i] = final_exit
            
            # Calculate Trade Quality Score
            avg_daily_range = np.mean(daily_ranges) if len(daily_ranges) > 0 else 0.0
            score_data = self.scorer.score_trade(
                outcome=outcome,
                mfe=mfe_arr[i],
                mae=mae_arr[i],
                days_to_target=days_to_target[i],
                avg_daily_range_pct=avg_daily_range,
                stop_loss_pct=self.stop_loss_pct
            )
            quality_score_arr[i] = score_data['score']
            category_arr[i] = score_data['category']
            
        # The very last row cannot be executed
        outcome_arr[n_rows - 1] = "INVALID"
        category_arr[n_rows - 1] = "Avoid"
            
        # Append to dataframe
        symbol_df = symbol_df.copy()
        symbol_df['MFE_Pct'] = mfe_arr
        symbol_df['MAE_Pct'] = mae_arr
        symbol_df['Trade_Outcome'] = outcome_arr
        symbol_df['Days_To_Target'] = days_to_target
        symbol_df['Days_To_Stop'] = days_to_stop
        symbol_df['Simulated_Exit_Price'] = exit_price_arr
        symbol_df['Trade_Quality_Score'] = quality_score_arr
        symbol_df['Trade_Quality_Category'] = category_arr
        
        # Calculate theoretical PnL from Entry (T+1 Open) to Exit
        # We need an array for Entry Price to calculate this vectorize, but we can do it via shift
        symbol_df['Simulated_Entry_Price'] = symbol_df['Open'].shift(-1)
        symbol_df['Simulated_Return_Pct'] = ((symbol_df['Simulated_Exit_Price'] - symbol_df['Simulated_Entry_Price']) / symbol_df['Simulated_Entry_Price']) * 100.0
        
        return symbol_df
