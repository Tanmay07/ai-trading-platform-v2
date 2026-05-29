from jugaad_data.nse import NSELive
import requests

try:
    n = NSELive()
    index_data = n.live_index('NIFTY 50')
    print("Fetched Nifty 50!")
    print(list(index_data.keys()))
    if 'data' in index_data:
        print(f"Number of stocks: {len(index_data['data'])}")
        # Print first stock keys to see if sector/industry is there
        if len(index_data['data']) > 0:
            print("First stock keys:", list(index_data['data'][0].keys()))
            print("First stock meta:", index_data['data'][0].get("meta", {}))
except Exception as e:
    print(f"Error: {e}")
