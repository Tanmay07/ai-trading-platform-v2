import json
import requests
import os

bse_stocks = ["QUASAR", "KRETTOSYS", "HARSHILAGR", "FRANKLININD"]
# Delete the .NS versions from the backend
url = "http://localhost:8000/portfolio"
for stock in bse_stocks:
    sym = f"{stock}.NS"
    print(f"Deleting {sym}...")
    requests.delete(f"{url}/{sym}")

# Update portfolio_data.json
json_path = "portfolio_data.json"
with open(json_path, "r") as f:
    data = json.load(f)

for item in data:
    if item["symbol"] in bse_stocks:
        item["symbol"] = f"{item['symbol']}.BO"
        print(f"Updated {item['symbol']} in JSON")

with open(json_path, "w") as f:
    json.dump(data, f, indent=2)

print("Done cleaning up!")
