import os
import sys
import pandas as pd
import json

# Setup python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from feature_platform.validation.validation_pipeline import ValidationPipeline

def run_validation():
    print("Loading Dataset V4...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_v4.parquet')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
        
    df = pd.read_parquet(data_path)
    
    # Intentionally inject a leaky feature for validation testing
    print("Injecting leaky feature for validation testing...")
    df['Leaky_Close'] = df.groupby('Symbol')['Close'].shift(-1)
    
    print(f"Dataset V4 loaded. Shape: {df.shape}")
    
    # Exclude base columns from validation
    exclude = ['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
    feature_cols = [c for c in df.columns if c not in exclude]
    
    print(f"Starting Validation Pipeline on {len(feature_cols)} features...")
    pipeline = ValidationPipeline()
    
    # Run pipeline
    registry_data = pipeline.validate_dataset(df, feature_cols)
    features_meta = registry_data.get("features", {})
    
    print(f"Validation complete. Registry has {len(features_meta)} entries.")
    
    # Analyze Results
    approved = []
    rejected = []
    experimental = []
    
    total_score = 0
    for name, meta in features_meta.items():
        status = meta["status"]
        if status == "Production Ready":
            approved.append(name)
        elif status == "Rejected":
            rejected.append(name)
        else:
            experimental.append(name)
            
        total_score += meta["composite_score"]
        
    avg_score = total_score / len(features_meta) if features_meta else 0
    
    print("\n--- Validation Summary ---")
    print(f"Total Evaluated: {len(features_meta)}")
    print(f"Production Ready: {len(approved)}")
    print(f"Experimental: {len(experimental)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Average Quality Score: {avg_score:.2f}")
    
    # Save Dataset V5 (Institutional Feature Set V1)
    # Include base columns + approved features
    v5_cols = [c for c in exclude if c in df.columns] + approved
    dataset_v5 = df[v5_cols]
    
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset_v5.parquet')
    dataset_v5.to_parquet(out_path)
    print(f"\nSaved Institutional Feature Set V1 (Dataset V5) to {out_path}. Shape: {dataset_v5.shape}")
    
    # Identify leaky features caught
    leaky_caught = [name for name, meta in features_meta.items() if meta.get("validation_details", {}).get("has_leakage")]
    print(f"Leaky features caught and rejected: {leaky_caught}")

if __name__ == "__main__":
    run_validation()
