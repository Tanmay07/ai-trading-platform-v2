from jugaad_data.nse import bhavcopy_save
import os
from datetime import date, timedelta
import pandas as pd

target_date = date.today()
dest_dir = "data/temp_bhavcopy"
for _ in range(7):
    if target_date.weekday() < 5:
        try:
            file_path = bhavcopy_save(target_date, dest_dir)
            with open(file_path, 'r') as f:
                if "<html" not in f.read(20).lower():
                    df = pd.read_csv(file_path)
                    print(df.columns.tolist())
                    break
        except Exception as e:
            pass
    target_date -= timedelta(days=1)
