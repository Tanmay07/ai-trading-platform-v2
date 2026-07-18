import pandas as pd
import numpy as np
df = pd.read_parquet('backend/data/dataset_v4.parquet')
df['Leaky_Close'] = df.groupby('Symbol')['Close'].shift(-1)
series = df['Leaky_Close']
future_close = df['Close'].shift(-1)
match_mask = np.isfinite(series) & np.isfinite(future_close)
if match_mask.sum() > 0:
    exact_matches = np.isclose(series[match_mask], future_close[match_mask]).mean()
    print(f"Exact Matches: {exact_matches}")
