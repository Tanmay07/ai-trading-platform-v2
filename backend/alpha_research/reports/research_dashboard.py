import pandas as pd
import yaml
import json
import logging
import datetime

from alpha_research.market.sector_research import SectorResearch
from alpha_research.market.market_regime import MarketRegimeResearch
from alpha_research.feature.feature_research import FeatureResearch
from alpha_research.feature.feature_correlation import FeatureCorrelation
from alpha_research.trade.holding_period_analysis import HoldingPeriodAnalysis
from alpha_research.trade.risk_analysis import RiskAnalysis
from alpha_research.technical.indicator_analysis import TechnicalIndicatorAnalysis
from alpha_research.reports.alpha_discovery import AlphaDiscovery
from alpha_research.reports.roadmap_generator import RoadmapGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaResearchEngine")

class ResearchDashboard:
    def __init__(self):
        with open("config/alpha_research.yaml", "r") as f:
            self.config = yaml.safe_load(f)["alpha_research"]
        with open("config/trade_labels.yaml", "r") as f:
            self.trade_config = yaml.safe_load(f)["trade_rules"]
            
    def run_all(self):
        logger.info("Loading Canonical Dataset V2 (Read-Only)...")
        df = pd.read_parquet(self.config['dataset_path'])
        
        # Meta stats
        meta = {
            "Dataset_Version": str(df['Dataset_Version'].iloc[0]) if 'Dataset_Version' in df.columns else "Unknown",
            "Research_Date": datetime.datetime.utcnow().isoformat(),
            "Total_Trades": len(df),
            "Symbols_Covered": df['symbol'].nunique() if 'symbol' in df.columns else 0,
            "Average_Trade_Quality": round(df['Trade_Quality_Score'].mean(), 2) if 'Trade_Quality_Score' in df.columns else 0.0
        }
        
        logger.info("Running Sector Intelligence...")
        sector_stats = SectorResearch.analyze_sectors(df)
        
        logger.info("Running Market Regime Intelligence...")
        regime_stats = MarketRegimeResearch.analyze_regimes(df, self.config['market_regimes'])
        
        logger.info("Running Risk Intelligence...")
        risk_stats = RiskAnalysis.analyze_risk(df)
        
        logger.info("Running Holding Period Optimization...")
        holding_stats = HoldingPeriodAnalysis.analyze_holding_periods(df, self.config, self.trade_config)
        
        logger.info("Running Feature Correlation...")
        correlation_stats = FeatureCorrelation.analyze_correlations(df)
        
        logger.info("Running Feature Intelligence (SHAP Proxy via Surrogate)...")
        feature_stats = FeatureResearch.analyze_features(df, self.config['feature_importance'])
        
        logger.info("Running Technical Indicator Intelligence...")
        indicator_stats = TechnicalIndicatorAnalysis.analyze_indicators(df)
        
        logger.info("Synthesizing Alpha Discoveries...")
        discoveries = AlphaDiscovery.discover_alpha(indicator_stats, correlation_stats, feature_stats, self.config)
        
        logger.info("Generating Roadmap...")
        roadmap = RoadmapGenerator.generate_roadmap(feature_stats, sector_stats, risk_stats, regime_stats)
        
        report = {
            "Overview": meta,
            "Sector_Intelligence": sector_stats,
            "Market_Intelligence": regime_stats,
            "Risk_Intelligence": risk_stats,
            "Holding_Period_Intelligence": holding_stats,
            "Feature_Intelligence": feature_stats,
            "Feature_Correlation": correlation_stats,
            "Technical_Intelligence": indicator_stats,
            "Alpha_Discoveries": discoveries,
            "Recommendation_Center": roadmap
        }
        
        logger.info(f"Saving Alpha Research Report to {self.config['report_path']}...")
        with open(self.config['report_path'], "w") as f:
            json.dump(report, f, indent=4)
            
        logger.info("Alpha Research Phase Complete!")

if __name__ == "__main__":
    ResearchDashboard().run_all()
