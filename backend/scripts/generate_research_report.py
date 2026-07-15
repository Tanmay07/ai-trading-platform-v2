import sys
import os
from pathlib import Path
import logging

# Ensure absolute path resolution for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.research_lab.reports.research_report import ResearchReportGenerator
from app.utils.logger import get_logger

logger = get_logger("GenerateResearchReport")

if __name__ == "__main__":
    logger.info("Initializing Research Report Generation...")
    try:
        generator = ResearchReportGenerator()
        generator.generate_report()
        logger.info("Research Report successfully generated.")
    except Exception as e:
        import traceback
        logger.error(f"Failed to generate Research Report: {e}")
        traceback.print_exc()
