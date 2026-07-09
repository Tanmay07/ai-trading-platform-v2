from typing import Dict, Any, List

class PortfolioAllocator:
    def distribute_to_portfolios(self, execution_order: Dict[str, Any], accounts: List[str]) -> List[Dict[str, Any]]:
        """
        Maps a top-level strategy trade into sub-orders for individual client portfolios.
        """
        sub_orders = []
        for acc in accounts:
            sub = execution_order.copy()
            sub["account"] = acc
            sub["quantity"] = 10 # Scaled down for the individual account
            sub_orders.append(sub)
        return sub_orders
