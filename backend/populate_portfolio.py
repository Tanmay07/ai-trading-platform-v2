import requests
import math
import json
import os

# Load portfolio data from an external JSON file to keep the script generic
json_file_path = os.path.join(os.path.dirname(__file__), "portfolio_data.json")

try:
    with open(json_file_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: Could not find {json_file_path}. Please create the file with your portfolio data.")
    exit(1)

url = "http://localhost:8000/portfolio"

# Get all current holdings to determine whether to PUT (overwrite) or POST (add)
try:
    r_all = requests.get(url)
    current_holdings = [h["symbol"] for h in r_all.json().get("holdings", [])]
except Exception as e:
    print(f"Failed to fetch current holdings: {e}")
    current_holdings = []

for item in data:
    sym = item.get("symbol")
    qty = item.get("quantity")
    avg_price = item.get("buy_price")
    
    if not sym or qty is None or avg_price is None:
        print(f"Skipping invalid item: {item}")
        continue

    qty = math.floor(qty)
    if qty <= 0:
        continue

    sym_suffix = sym
    if not (sym.endswith(".NS") or sym.endswith(".BO")):
        sym_suffix = f"{sym}.NS"

    payload = {
        "symbol": sym_suffix,
        "quantity": qty,
        "buy_price": avg_price
    }
    try:
        if sym_suffix in current_holdings:
            # Overwrite exact quantity
            r = requests.put(f"{url}/{sym_suffix}", json=payload)
            action = "Updated (Fixed quantity)"
        else:
            # Add new holding
            r = requests.post(url, json=payload)
            action = "Added"

        if r.status_code == 200:
            print(f"{action} {sym_suffix}")
        else:
            print(f"Failed to process {sym_suffix}: {r.text}")
    except Exception as e:
        print(f"Error adding {sym}: {e}")
