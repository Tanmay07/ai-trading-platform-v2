class PositionManager:
    def reconcile_positions(self, broker_positions: list, db_positions: list) -> bool:
        """
        Detects mismatch between DB and Broker.
        """
        # MVP: Return True if counts match
        return len(broker_positions) == len(db_positions)
