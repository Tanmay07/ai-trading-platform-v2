import asyncio
from app.data.historical_data_service import HistoricalDataService
from app.data.market_data_service import MarketDataService
from app.features.feature_pipeline import FeaturePipeline

mds = MarketDataService()
hds = HistoricalDataService(mds)
fp = FeaturePipeline()

df = hds.get_historical_data("RELIANCE.NS", "3y", "1d")
print("Raw df shape:", df.shape)

df_feat = fp.compute_all_features(df)
print("Features df shape:", df_feat.shape)
print("NaNs per column in features:")
print(df_feat.isna().sum().sort_values(ascending=False).head(10))

# Also apply ML labels logic
df_feat["future_return"] = df_feat["Close"].pct_change(periods=5).shift(-5)
df_clean = df_feat.dropna()
print("Clean df shape:", df_clean.shape)
