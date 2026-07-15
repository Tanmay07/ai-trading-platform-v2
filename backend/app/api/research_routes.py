from fastapi import APIRouter
from typing import Dict, Any, List
from app.research_lab.reports.research_report import ResearchReportGenerator

router = APIRouter(prefix="/api/research", tags=["Research Phase 11"])

@router.get("/report")
def get_research_report() -> Dict[str, Any]:
    generator = ResearchReportGenerator()
    return generator.get_latest_report()

@router.get("/thresholds")
def get_thresholds() -> Dict[str, Any]:
    generator = ResearchReportGenerator()
    report = generator.get_latest_report()
    return report.get("threshold_analysis", {})

@router.get("/errors")
def get_errors() -> Dict[str, Any]:
    generator = ResearchReportGenerator()
    report = generator.get_latest_report()
    return report.get("error_analysis", {})

@router.get("/sectors")
def get_sectors() -> Dict[str, Any]:
    generator = ResearchReportGenerator()
    report = generator.get_latest_report()
    return report.get("sector_analysis", {})

@router.get("/regimes")
def get_regimes() -> List[Dict[str, Any]]:
    generator = ResearchReportGenerator()
    report = generator.get_latest_report()
    return report.get("regime_analysis", [])

@router.get("/confidence")
def get_confidence() -> Dict[str, Any]:
    generator = ResearchReportGenerator()
    report = generator.get_latest_report()
    return report.get("calibration_quality", {})

