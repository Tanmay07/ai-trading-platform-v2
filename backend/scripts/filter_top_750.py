import sys
import os
import pandas as pd
import sqlite3
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Find latest Bhavcopy
bhavcopy_files = glob.glob("../data/temp_bhavcopy/*.csv")
if not bhavcopy_files:
    print("No bhavcopy found.")
    sys.exit(1)

latest_bhavcopy = max(bhavcopy_files, key=os.path.getmtime)
print(f"Using {latest_bhavcopy}")

df = pd.read_csv(latest_bhavcopy)
if 'SctySrs' in df.columns and 'TckrSymb' in df.columns and 'TtlTrfVal' in df.columns:
    eq_df = df[df['SctySrs'] == 'EQ'].copy()
    eq_df['TtlTrfVal'] = pd.to_numeric(eq_df['TtlTrfVal'], errors='coerce').fillna(0)
    top_750 = eq_df.sort_values(by='TtlTrfVal', ascending=False).head(750)
    top_symbols = set(top_750['TckrSymb'].unique())
else:
    print("Columns not found, fallback logic needed.")
    sys.exit(1)

print(f"Identified top {len(top_symbols)} symbols by traded value.")

db_path = "../ai_trading_universe.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Reset all to inactive
cursor.execute("UPDATE symbols SET is_active = 0")
conn.commit()

# Set top 750 to active
for sym in top_symbols:
    cursor.execute("UPDATE symbols SET is_active = 1 WHERE symbol = ?", (sym,))
conn.commit()

cursor.execute("SELECT COUNT(*) FROM symbols WHERE is_active = 1")
count = cursor.fetchone()[0]
print(f"Successfully set {count} symbols as active in Universe DB.")
conn.close()
