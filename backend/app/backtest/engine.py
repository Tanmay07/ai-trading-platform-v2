import pandas as pd
import numpy as np
from datetime import datetime, date

from app.config import Settings
from app.features.feature_pipeline import FeaturePipeline
from app.strategies.rule_based_strategy import RuleBasedStrategy
from app.data.historical_data_service import HistoricalDataService
from app.data.market_data_service import MarketDataService
from app.database import get_db, SessionLocal
from app.models.backtest import BacktestRun, BacktestTrade
from app.utils.logger import get_logger


class BacktestEngine:
    """
    High-performance event-driven backtesting engine.

    Simulates the AI Trading Platform strategy over historical data,
    evaluating the RuleBasedStrategy row-by-row to guarantee logic parity
    with live trading.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.settings = Settings()
        self.feature_pipeline = FeaturePipeline()
        self.strategy = RuleBasedStrategy()
        
        # We need historical data to run the backtest
        market_data_service = MarketDataService()
        self.historical_data_service = HistoricalDataService(market_data_service)

        # Backtest parameters
        self.transaction_cost_pct = 0.001  # 0.1% for slippage + fees
        self.risk_per_trade_pct = 0.20     # Max 20% of capital per trade
        self.risk_free_rate = 0.07         # ~7% for Indian market

    def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100_000.0,
    ) -> dict:
        """
        Execute a full backtest for a single symbol.

        Args:
            symbol: Ticker symbol (e.g., RELIANCE.NS)
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            initial_capital: Starting capital

        Returns:
            Dict containing performance metrics and trades.
        """
        self.logger.info("Starting backtest for %s from %s to %s", symbol, start_date, end_date)

        # 1. Fetch data
        # We need data *before* start_date to warm up technical indicators (e.g., 200 SMA)
        warmup_days = 300
        start_dt = pd.to_datetime(start_date)
        fetch_start = (start_dt - pd.Timedelta(days=warmup_days)).strftime("%Y-%m-%d")

        df_raw = self.historical_data_service.get_historical_data(
            symbol, start_date=fetch_start, end_date=end_date
        )

        if df_raw is None or df_raw.empty:
            raise ValueError(f"No historical data found for {symbol}")

        # 2. Compute features for the entire timeline (Vectorized)
        df_features = self.feature_pipeline.compute_all_features(df_raw)

        # 3. Filter down to the actual backtest window
        mask = (df_features.index >= start_date) & (df_features.index <= end_date)
        df = df_features.loc[mask].copy()

        if df.empty:
            raise ValueError("No data available within the specified backtest window after warmup.")

        # 4. Initialize simulation state
        capital = initial_capital
        position = 0          # Number of shares held
        entry_price = 0.0
        entry_date = None
        stop_loss = 0.0
        take_profit = 0.0

        trades = []
        portfolio_values = []
        dates = df.index.tolist()

        # Iterate day by day
        for i in range(len(df)):
            row = df.iloc[i]
            current_date = dates[i]
            # Use current day's Close to evaluate signals, but we will execute trades
            # at the next day's Open (simulated below).
            # If we don't have next day's open, we'll use current Close as fallback.
            current_close = float(row['Close'])
            
            # Record portfolio value at close
            current_value = capital + (position * current_close)
            portfolio_values.append(current_value)

            # --- Check open position ---
            if position > 0:
                # Did we hit Stop Loss or Take Profit?
                # Check current day's Low and High
                current_low = float(row['Low'])
                current_high = float(row['High'])
                
                exit_price = None
                exit_reason = None

                if current_low <= stop_loss:
                    # Slippage simulation: we get out at the stop loss or the open if it gapped down
                    current_open = float(row['Open'])
                    exit_price = min(stop_loss, current_open)
                    exit_reason = "STOP_LOSS"
                elif current_high >= take_profit:
                    # Gapped up above target
                    current_open = float(row['Open'])
                    exit_price = max(take_profit, current_open)
                    exit_reason = "TAKE_PROFIT"
                else:
                    # Evaluate strategy to see if we should sell manually
                    # In a real backtest, we might not have ML or Sentiment easily mockable
                    # so we pass None to rely strictly on technicals for the backtest
                    signals = self.strategy.analyze_row(row, sentiment_data=None, ml_prediction=None)
                    score = signals.get("combined_score", 0.0)
                    if score <= self.settings.SELL_THRESHOLD:
                        # Manual exit signal. Execute at next open, but for simplicity
                        # if this is the last day, execute at close.
                        if i + 1 < len(df):
                            exit_price = float(df.iloc[i + 1]['Open'])
                        else:
                            exit_price = current_close
                        exit_reason = "SIGNAL"

                if exit_price is not None:
                    # Execute SELL
                    exit_price_net = exit_price * (1 - self.transaction_cost_pct)
                    revenue = position * exit_price_net
                    capital += revenue

                    return_pct = (exit_price_net - entry_price) / entry_price
                    holding_days = (current_date - entry_date).days

                    trades.append({
                        "symbol": symbol,
                        "action": "SELL",
                        "entry_date": entry_date.date() if isinstance(entry_date, datetime) else entry_date,
                        "entry_price": entry_price,
                        "exit_date": current_date.date() if isinstance(current_date, datetime) else current_date,
                        "exit_price": exit_price,
                        "return_pct": return_pct,
                        "holding_days": holding_days,
                        "reason": exit_reason
                    })

                    position = 0
                    entry_price = 0.0
                    entry_date = None
                    stop_loss = 0.0
                    take_profit = 0.0
                
                continue  # Already in a position, just check exits

            # --- Check for new entry ---
            if position == 0:
                signals = self.strategy.analyze_row(row, sentiment_data=None, ml_prediction=None)
                score = signals.get("combined_score", 0.0)

                if score >= self.settings.BUY_THRESHOLD:
                    # We have a BUY signal. Enter at the next available Open price.
                    if i + 1 < len(df):
                        exec_price = float(df.iloc[i + 1]['Open'])
                        exec_date = dates[i + 1]
                    else:
                        break # Cannot enter on the last day of the dataset

                    exec_price_net = exec_price * (1 + self.transaction_cost_pct)

                    # Calculate position size
                    trade_capital = capital * self.risk_per_trade_pct
                    shares_to_buy = int(trade_capital // exec_price_net)

                    if shares_to_buy > 0:
                        position = shares_to_buy
                        capital -= (shares_to_buy * exec_price_net)
                        entry_price = exec_price_net
                        entry_date = exec_date

                        # Set SL and TP based on ATR (Average True Range)
                        atr = float(row.get('atr', current_close * 0.02))
                        if np.isnan(atr):
                            atr = current_close * 0.02
                        
                        # Use a 2x ATR stop loss and 3x ATR target
                        stop_loss = entry_price - (2 * atr)
                        take_profit = entry_price + (3 * atr)

        # 5. Close out open position at the end of the backtest
        if position > 0:
            final_close = float(df.iloc[-1]['Close'])
            final_close_net = final_close * (1 - self.transaction_cost_pct)
            capital += position * final_close_net
            
            return_pct = (final_close_net - entry_price) / entry_price
            holding_days = (dates[-1] - entry_date).days

            trades.append({
                "symbol": symbol,
                "action": "SELL",
                "entry_date": entry_date.date() if isinstance(entry_date, datetime) else entry_date,
                "entry_price": entry_price,
                "exit_date": dates[-1].date() if isinstance(dates[-1], datetime) else dates[-1],
                "exit_price": final_close,
                "return_pct": return_pct,
                "holding_days": holding_days,
                "reason": "END_OF_BACKTEST"
            })
            
            # Update the last portfolio value to reflect closed position
            portfolio_values[-1] = capital

        # 6. Calculate Metrics
        final_capital = capital
        total_return = (final_capital - initial_capital) / initial_capital

        winning_trades = [t for t in trades if t["return_pct"] > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0.0

        # Calculate Max Drawdown
        if portfolio_values:
            pv_series = pd.Series(portfolio_values)
            rolling_max = pv_series.cummax()
            drawdowns = (pv_series - rolling_max) / rolling_max
            max_drawdown = float(drawdowns.min())
        else:
            max_drawdown = 0.0

        # Calculate Sharpe Ratio
        if len(portfolio_values) > 1:
            pv_series = pd.Series(portfolio_values)
            daily_returns = pv_series.pct_change().dropna()
            if len(daily_returns) > 0 and daily_returns.std() != 0:
                # Annualize daily return
                annual_return = daily_returns.mean() * 252
                annual_vol = daily_returns.std() * np.sqrt(252)
                sharpe_ratio = float((annual_return - self.risk_free_rate) / annual_vol)
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0

        metrics = {
            "initial_capital": initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "win_rate": win_rate,
            "total_trades": len(trades),
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio
        }

        # 7. Persist to Database
        db_gen = get_db()
        db = next(db_gen)
        try:
            run_record = BacktestRun(
                strategy_name="Hybrid AI Strategy (Technicals)",
                start_date=pd.to_datetime(start_date).date(),
                end_date=pd.to_datetime(end_date).date(),
                initial_capital=initial_capital,
                final_capital=final_capital,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                total_trades=len(trades),
                config={"symbol": symbol, "risk_per_trade": self.risk_per_trade_pct}
            )
            db.add(run_record)
            db.commit()
            db.refresh(run_record)

            # Insert trades
            for t in trades:
                trade_record = BacktestTrade(
                    backtest_run_id=run_record.id,
                    symbol=t["symbol"],
                    action=t["action"],
                    entry_date=t["entry_date"],
                    entry_price=t["entry_price"],
                    exit_date=t["exit_date"],
                    exit_price=t["exit_price"],
                    return_pct=t["return_pct"],
                    holding_days=t["holding_days"]
                )
                db.add(trade_record)
            
            db.commit()
            metrics["run_id"] = run_record.id

        finally:
            db.close()

        return {
            "metrics": metrics,
            "trades": trades,
            "portfolio_history": portfolio_values
        }
