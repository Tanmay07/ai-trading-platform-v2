class LiquidityEngine:
    def validate_execution(self, trade_volume: int, average_daily_volume: int, max_participation: float) -> bool:
        """
        Validates if a trade can realistically be executed without extreme market impact.
        """
        if average_daily_volume <= 0:
            return False
            
        participation_rate = trade_volume / float(average_daily_volume)
        return participation_rate <= max_participation
