import csv
from typing import List, Dict, Any
from io import StringIO
from portfolio_manager.schemas import TransactionCreate
from portfolio_manager.models import TransactionType
from datetime import datetime

class CSVImporter:
    @staticmethod
    def parse_transactions(csv_content: str) -> List[TransactionCreate]:
        reader = csv.DictReader(StringIO(csv_content))
        transactions = []
        for row in reader:
            transactions.append(TransactionCreate(
                symbol=row['symbol'],
                transaction_type=TransactionType(row['transaction_type'].upper()),
                quantity=float(row['quantity']),
                price=float(row['price']),
                charges=float(row.get('charges', 0.0)),
                taxes=float(row.get('taxes', 0.0)),
                notes=row.get('notes', ''),
                timestamp=datetime.fromisoformat(row['timestamp']) if 'timestamp' in row and row['timestamp'] else datetime.utcnow()
            ))
        return transactions
