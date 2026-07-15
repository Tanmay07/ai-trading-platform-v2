import json
import logging
from pathlib import Path
from datetime import datetime

from app.research_lab.diagnostics.prediction_analyzer import PredictionAnalyzer
from app.research_lab.diagnostics.confusion_analysis import ConfusionAnalysis
from app.research_lab.diagnostics.threshold_analysis import ThresholdAnalysis
from app.research_lab.diagnostics.feature_diagnostics import FeatureDiagnostics
from app.research_lab.analytics.sector_analysis import SectorAnalysis
from app.research_lab.analytics.regime_analysis import RegimeAnalysis
from app.research_lab.analytics.confidence_analysis import ConfidenceAnalysis
from app.research_lab.analytics.error_analysis import ErrorAnalysis

logger = logging.getLogger("ResearchReport")

class ResearchReportGenerator:
    def __init__(self):
        self.analyzer = PredictionAnalyzer()
        self.output_dir = Path("data/research")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path = self.output_dir / "latest_diagnostic_report.json"
        
    def generate_report(self):
        logger.info("Generating Model Diagnostic Report...")
        
        # 1. Initialize Analyzer (runs inference on test set)
        self.analyzer.initialize()
        df = self.analyzer.get_test_data()
        
        # 2. Instantiate diagnostic modules
        conf_analysis = ConfusionAnalysis(self.analyzer)
        thresh_analysis = ThresholdAnalysis(self.analyzer)
        feat_analysis = FeatureDiagnostics(self.analyzer)
        
        sec_analysis = SectorAnalysis(self.analyzer)
        reg_analysis = RegimeAnalysis(self.analyzer)
        cal_analysis = ConfidenceAnalysis(self.analyzer)
        err_analysis = ErrorAnalysis(self.analyzer)
        
        # 3. Run Analysis
        label_dist = conf_analysis.analyze_label_distribution(df)
        thresholds_data = thresh_analysis.analyze_thresholds(df)
        best_threshold_data = thresh_analysis.recommend_optimal_threshold(thresholds_data)
        
        best_threshold = best_threshold_data["optimal_threshold"]
        
        confusion_matrix = conf_analysis.generate_confusion_matrix(df, threshold=best_threshold)
        feature_ranking = feat_analysis.generate_feature_ranking(df)
        
        sector_perf = sec_analysis.analyze_sectors(df, threshold=best_threshold)
        best_sector = sector_perf[0] if sector_perf and "error" not in sector_perf[0] else None
        worst_sector = sector_perf[-1] if sector_perf and "error" not in sector_perf[-1] else None
        
        regime_perf = reg_analysis.analyze_regimes(df, threshold=best_threshold)
        calibration_data = cal_analysis.analyze_calibration(df)
        error_data = err_analysis.analyze_errors(df, threshold=best_threshold)
        
        # 4. Construct Report
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "model_version": self.analyzer.registry.get_production_model()[3].get("version", "unknown"),
            "test_samples": len(df),
            "label_distribution": label_dist,
            "threshold_analysis": {
                "thresholds": thresholds_data,
                "recommendation": best_threshold_data
            },
            "confusion_matrix": confusion_matrix,
            "sector_analysis": {
                "best_sector": best_sector,
                "worst_sector": worst_sector,
                "all_sectors": sector_perf
            },
            "regime_analysis": regime_perf,
            "calibration_quality": calibration_data,
            "feature_diagnostics": feature_ranking,
            "error_analysis": error_data,
            "improvement_recommendations": [
                label_dist.get("warning") if label_dist.get("warning") else "Label balance is adequate.",
                calibration_data.get("warning") if calibration_data.get("warning") else "Calibration is stable.",
                f"Consider optimizing feature engineering around top features: {', '.join([f['feature'] for f in feature_ranking[:3]])}"
            ]
        }
        
        # Filter out None strings
        report["improvement_recommendations"] = [r for r in report["improvement_recommendations"] if r]
        
        # 5. Save Report
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=4)
            
        logger.info(f"Diagnostic report saved to {self.report_path}")
        return report
        
    def get_latest_report(self):
        if self.report_path.exists():
            with open(self.report_path, "r") as f:
                return json.load(f)
        return {"error": "No diagnostic report generated yet."}
