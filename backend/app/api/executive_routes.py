from fastapi import APIRouter
from pydantic import BaseModel
from executive_intelligence.cio_dashboard import CIODashboardEngine
from executive_intelligence.research_workspace import ResearchWorkspace

router = APIRouter()

@router.get("/dashboard")
def get_executive_dashboard():
    engine = CIODashboardEngine()
    try:
        data = engine.generate_dashboard()
        return {"dashboard": data}
    except Exception as e:
        return {"error": str(e)}

@router.get("/research/{symbol}")
def get_stock_research(symbol: str):
    workspace = ResearchWorkspace()
    try:
        data = workspace.get_stock_research(symbol)
        return {"research": data}
    except Exception as e:
        return {"error": str(e)}
