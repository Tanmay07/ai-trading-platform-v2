import pandas as pd
import yfinance as yf

def fetch_nifty50():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    tables = pd.read_html(url)
    # Usually the Nifty 50 components table is the second one
    for tbl in tables:
        if 'Symbol' in tbl.columns:
            return tbl
    return None

df = fetch_nifty50()
print(df.head())
