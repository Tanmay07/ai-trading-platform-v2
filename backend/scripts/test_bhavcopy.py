from jugaad_data.nse import bhavcopy_save
import os
from datetime import date, timedelta
import pandas as pd

target_date = date.today()
while target_date.weekday() > 4:
    target_date -= timedelta(days=1)

dest_dir = "data/temp_bhavcopy"
os.makedirs(dest_dir, exist_ok=True)
print(f"Downloading for {target_date}...")
try:
    file_path = bhavcopy_save(target_date, dest_dir)
    print(f"File saved to: {file_path}")
    with open(file_path, 'r') as f:
        print(f.read()[:500])
except Exception as e:
    print(f"Error: {e}")
