import pandas as pd
import json
import logging
import os
import yaml
from validation.trade_validation.execution_validator import ExecutionValidator
from validation.trade_validation.label_validator import LabelValidator
from validation.trade_validation.trade_quality_validator import TradeQualityValidator
from validation.trade_validation.ranking_validator import RankingValidator
from validation.trade_validation.leakage_validator import LeakageValidator
from validation.trade_validation.edge_case_validator import EdgeCaseValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ValidationEngine")

DATASET_PATH = "data/ml_datasets/dataset_v1.parquet"
REPORT_PATH = "data/models/validation_report.json"
CONFIG_PATH = "config/validation.yaml"

def generate_report():
    if not os.path.exists(DATASET_PATH):
        logger.error(f"Dataset not found at {DATASET_PATH}")
        return
        
    df = pd.read_parquet(DATASET_PATH)
    
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)["validation_rules"]
        
    logger.info("Running Baseline Label Audit...")
    # First, let's regenerate the baseline label to ensure the fix is applied.
    from trade_outcomes.labels.baseline_label import BaselineLabeler
    df['Label_Baseline'] = BaselineLabeler(target_return=5.0).generate_labels(df)
    
    label_audit = LabelValidator.audit_baseline_label(df, epsilon=config['float_epsilon'])
    
    logger.info("Running Execution Replay Audit...")
    replay_audit = ExecutionValidator.sample_trades(df, sample_size=config['replay_sample_size'], seed=config['random_seed'])
    
    logger.info("Running Trade Quality Distribution Audit...")
    quality_audit = TradeQualityValidator.audit_quality_distribution(df)
    
    logger.info("Running Ranking Correlation Audit...")
    ranking_audit = RankingValidator.audit_ranking_correlation(df)
    
    logger.info("Running Leakage Audit...")
    leakage_audit = LeakageValidator.audit_leakage(df)
    
    logger.info("Running Edge Case Audit...")
    edge_case_audit = EdgeCaseValidator.audit_edge_cases(df)
    
    report = {
        "Baseline_Label_Audit": label_audit,
        "Trade_Success_Audit": {
            # Since LabelComparator was fixed, we can just run it
            # But the user asked for total target hits, etc.
            "Total_Trades": len(df),
            "Target_Hit_Pct": round(len(df[df['Trade_Outcome'] == 'TARGET']) / len(df) * 100, 2) if len(df) > 0 else 0,
            "Stop_Loss_Pct": round(len(df[df['Trade_Outcome'] == 'STOP_LOSS']) / len(df) * 100, 2) if len(df) > 0 else 0,
            "Timeout_Pct": round(len(df[df['Trade_Outcome'] == 'TIMEOUT']) / len(df) * 100, 2) if len(df) > 0 else 0,
            "Invalid_Pct": round(len(df[df['Trade_Outcome'] == 'INVALID']) / len(df) * 100, 2) if len(df) > 0 else 0
        },
        "Execution_Replay_Audit_Sample": replay_audit,
        "Quality_Distribution_Audit": quality_audit,
        "Ranking_Correlation_Audit": ranking_audit,
        "Leakage_Audit": leakage_audit,
        "Edge_Case_Audit": edge_case_audit
    }
    
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Validation complete. Report saved to {REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
