import yfinance as yf

ticker = yf.Ticker("RELIANCE.NS")
info = ticker.info
print(f"Sector for RELIANCE: {info.get('sector')}")
print(f"Industry for RELIANCE: {info.get('industry')}")
