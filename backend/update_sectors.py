import json

SECTOR_MAP = {
    "Financial Services": [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS",
        "INDUSINDBK.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "HDFCAMC.NS", "SBI_LIFE.NS", "HDFCLIFE.NS", "ICICIGI.NS",
        "ICICIPRULI.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS"
    ],
    "Technology": [
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", 
        "MPHASIS.NS", "TATAELXSI.NS", "KPITTECH.NS", "CYIENT.NS", "ZENSARTECH.NS", "SONACOMS.NS"
    ],
    "Consumer Defensive": [
        "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "GODREJCP.NS",
        "MARICO.NS", "COLPAL.NS", "UBL.NS", "MCDOWELL-N.NS", "VBL.NS", "PGHH.NS", "EMAMILTD.NS"
    ],
    "Energy": [
        "RELIANCE.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "COALINDIA.NS", "IOC.NS", "BPCL.NS", "GAIL.NS",
        "HINDPETRO.NS", "PETRONET.NS", "IGL.NS", "MGL.NS", "ATGL.NS", "OIL.NS", "NHPC.NS"
    ],
    "Automobiles": [
        "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS",
        "ASHOKLEY.NS", "BOSCHLTD.NS", "MRF.NS", "BALKRISIND.NS", "APOLLOTYRE.NS", "MOTHERSON.NS", "TIINDIA.NS"
    ],
    "Healthcare": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "MAXHEALTH.NS", "LUPIN.NS",
        "AUROPHARMA.NS", "TORNTPHARM.NS", "BIOCON.NS", "SYNGENE.NS", "IPCALAB.NS", "GLENMARK.NS", "LAURUSLABS.NS"
    ],
    "Industrials": [
        "LT.NS", "SIEMENS.NS", "ABB.NS", "HAL.NS", "BEL.NS", "CGPOWER.NS", "BHEL.NS", "CUMMINSIND.NS",
        "AIAENG.NS", "THERMAX.NS", "HONAUT.NS", "POLYCAB.NS", "KEI.NS", "APARINDS.NS"
    ],
    "Basic Materials": [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "ULTRACEMCO.NS", "GRASIM.NS", "AMBUJACEM.NS",
        "SHREECEM.NS", "ACC.NS", "DALBHARAT.NS", "RAMCOCEM.NS", "PIDILITIND.NS", "SRF.NS", "NAVINFLUOR.NS", "PIIND.NS"
    ],
    "Consumer Cyclical": [
        "ASIANPAINT.NS", "TITAN.NS", "TRENT.NS", "PAGEIND.NS", "BATAINDIA.NS", "RELAXO.NS", "ABFRL.NS",
        "BERGEPAINT.NS", "KANSAINER.NS", "INDIHOTEL.NS", "JUBIQUANT.NS", "DEVYANI.NS", "ZOMATO.NS", "NYKAA.NS"
    ],
    "Communication Services": [
        "BHARTIARTL.NS", "IDEA.NS", "INDUSINDBK.NS", "TATACOMM.NS", "ROUTE.NS", "TEJASNET.NS", "HFCL.NS"
    ],
    "Real Estate": [
        "DLF.NS", "MACROTECH.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS", "SOBHA.NS"
    ]
}

content = ""
with open("app/data/screener_service.py", "r") as f:
    content = f.read()

import re
# Replace SECTOR_MAP
new_content = re.sub(r'SECTOR_MAP = \{.*?\}', f'SECTOR_MAP = {json.dumps(SECTOR_MAP, indent=4)}', content, flags=re.DOTALL)
with open("app/data/screener_service.py", "w") as f:
    f.write(new_content)

print("Updated SECTOR_MAP")
