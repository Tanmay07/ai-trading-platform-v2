from app.config_backtesting import backtesting_config

class TransactionCostEngine:
    def calculate_costs(self, trade_value: float, is_buy: bool) -> float:
        """
        Calculates realistic Indian Equity trading costs.
        """
        costs = backtesting_config.costs
        
        brokerage = trade_value * costs.brokerage_pct
        stt = trade_value * costs.stt_pct
        txn_charges = trade_value * costs.exchange_txn_pct
        sebi_charges = trade_value * costs.sebi_pct
        
        # GST is on brokerage + txn charges
        gst = (brokerage + txn_charges) * costs.gst_pct
        
        stamp_duty = (trade_value * costs.stamp_duty_pct) if is_buy else 0.0
        
        total_cost = brokerage + stt + txn_charges + sebi_charges + gst + stamp_duty
        return total_cost
