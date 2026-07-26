import csv
from io import StringIO
from typing import List
from portfolio_manager.schemas import HoldingResponse, TransactionResponse

class CSVExporter:
    @staticmethod
    def export_holdings(holdings: List[HoldingResponse]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Symbol', 'Quantity', 'Avg Buy Price', 'Total Invested', 'Current Price', 'Market Value', 'Unrealized PnL', 'Weight (%)'])
        
        for h in holdings:
            writer.writerow([
                h.symbol,
                h.quantity,
                f"{h.average_buy_price:.2f}",
                f"{h.total_invested:.2f}",
                f"{h.current_price or 0:.2f}",
                f"{h.current_value or 0:.2f}",
                f"{h.unrealized_pnl or 0:.2f}",
                f"{h.portfolio_weight or 0:.2f}"
            ])
            
        return output.getvalue()
