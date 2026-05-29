import requests
from bs4 import BeautifulSoup

def fetch_nifty50():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    tables = soup.find_all('table', {'id': 'constituents'})
    if not tables:
        tables = soup.find_all('table', {'class': 'wikitable'})

    for i, table in enumerate(tables):
        head = [th.text.strip() for th in table.find_all('th')]
        
        symbols = []
        if 'Symbol' in head:
            sym_idx = head.index('Symbol')
            sector_idx = -1
            for j, h in enumerate(head):
                if 'Sector' in h:
                    sector_idx = j
                    break
            
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) > sym_idx:
                    sym = cols[sym_idx].text.strip()
                    sec = cols[sector_idx].text.strip() if sector_idx != -1 else "Unknown"
                    if sym:
                        symbols.append(f"{sym}.NS ({sec})")
            print(f"Symbols: {symbols[:10]}")
            return symbols

fetch_nifty50()
